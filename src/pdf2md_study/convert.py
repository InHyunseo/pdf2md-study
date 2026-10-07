"""Run the Docling pipeline and write study-ready Markdown.

Input: a PDF path and an output directory.
Output: <name>.md and <name>_artifacts/ (pictures, equations, code, optional page images)
in the output directory, and a ConversionResult with counts.
Pages are converted PAGES_PER_CALL at a time and written out before the next ones,
so memory use does not grow with the page count.
"""

import ctypes
import re
import shutil
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import huggingface_hub.utils
from docling.backend.docling_parse_backend import ThreadedDoclingParseDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.settings import DEFAULT_PAGE_RANGE
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.exceptions import ConversionError
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline, ThreadedItem
from docling_core.types.doc import (
    ContentLayer,
    DocItem,
    DocItemLabel,
    DoclingDocument,
    ImageRefMode,
    PictureItem,
)
from PIL import Image, ImageOps
from tqdm import tqdm
from transformers.utils import logging as transformers_logging

from pdf2md_study.layout import (
    BODY,
    ImageNamer,
    equation_box,
    find_decorations,
    is_slides,
    mark_pages,
    page_box,
)
from pdf2md_study.markdown import (
    PICTURE_MARKER,
    REGION_MARKER,
    fill_pictures,
    replace_regions,
    strip_references,
)
from pdf2md_study.pages import split_page_ranges
from pdf2md_study.tokens import image_tokens, page_image_tokens, text_tokens

IMAGE_SCALE = 2.0  # resolution multiplier for cropped images
INK_LEVEL = 215  # gray pixels darker than this are ink in equation images
INK_MARGIN = 3.0  # white margin in points around an equation image
INK_BREAK = 5.0  # blank height in points that ends an equation (e.g. a footnote rule)
PAGES_PER_CALL = 4  # pages Docling converts together; memory use grows with this

# Hide the "Loading weights" bar shown on every model load, keep model download bars.
transformers_logging.disable_progress_bar()
huggingface_hub.utils.enable_progress_bars()


def find_malloc_trim():
    """glibc malloc_trim, or None on systems without glibc (macOS, Windows, musl)."""
    try:
        return ctypes.CDLL("libc.so.6").malloc_trim
    except (OSError, AttributeError):
        return None


# Returns memory freed by the threads of Docling and OCR to the OS; glibc keeps it otherwise.
MALLOC_TRIM = find_malloc_trim()


@dataclass
class ConversionResult:
    """Output path and counts of one conversion."""

    markdown_path: Path
    page_count: int
    slides: bool
    picture_count: int
    decoration_count: int
    equation_count: int
    code_count: int
    page_image_count: int
    character_count: int
    pdf_tokens: int
    markdown_tokens: int
    image_tokens: int


class ProgressPipeline(StandardPdfPipeline):
    """Docling's PDF pipeline that advances ProgressPipeline.progress for each finished page."""

    progress: tqdm | None = None

    def _release_page_resources(self, item: ThreadedItem) -> None:
        super()._release_page_resources(item)
        if ProgressPipeline.progress is not None:
            ProgressPipeline.progress.update()


def build_converter(ocr: bool, latex: bool) -> DocumentConverter:
    """Docling converter with the docling-parse backend and page images enabled."""
    options = PdfPipelineOptions()
    options.do_ocr = ocr
    options.ocr_options.force_full_page_ocr = ocr
    options.do_formula_enrichment = latex
    options.images_scale = IMAGE_SCALE
    options.generate_page_images = True
    options.generate_picture_images = True
    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=ProgressPipeline,
                pipeline_options=options,
                backend=ThreadedDoclingParseDocumentBackend,
            )
        }
    )


def ink_band(rows: list[bool], start: int, end: int, gap: int) -> tuple[int, int]:
    """First and last row of the ink joined to rows[start:end] by blanks shorter than gap."""
    top, bottom = start, end - 1
    for step, edge in ((-1, start - 1), (1, end)):
        blank = 0
        y = edge
        while 0 <= y < len(rows) and blank < gap:
            if rows[y]:
                blank = 0
                top, bottom = min(top, y), max(bottom, y)
            else:
                blank += 1
            y += step
    return top, bottom


def equation_image(document: DoclingDocument, item: DocItem) -> Image.Image | None:
    """Equation cropped from the page image with its full height and an even white margin."""
    if not item.prov:
        return None
    page = document.pages[item.prov[0].page_no]
    if page.image is None or page.image.pil_image is None:
        return None
    image = page.image.pil_image
    scale = image.width / page.size.width
    original = item.prov[0].bbox.to_top_left_origin(page.size.height)
    box = equation_box(document, item)
    # A little wider than the box, so glyphs on its left and right edges are not cut.
    region = image.crop(
        (
            max(round((box.l - INK_MARGIN) * scale), 0),
            round(box.t * scale),
            min(round((box.r + INK_MARGIN) * scale), image.width),
            round(box.b * scale),
        )
    )
    mask = region.convert("L").point(lambda v: 255 if v < INK_LEVEL else 0)
    rows = [
        mask.crop((0, y, mask.width, y + 1)).getbbox() is not None
        for y in range(mask.height)
    ]
    top, bottom = ink_band(
        rows,
        round((original.t - box.t) * scale),
        round((original.b - box.t) * scale),
        round(INK_BREAK * scale),
    )
    ink = mask.crop((0, top, mask.width, bottom + 1)).getbbox()
    if ink is None:
        return None
    left, ink_top, right, ink_bottom = ink
    equation = region.crop((left, top + ink_top, right, top + ink_bottom))
    return ImageOps.expand(equation, border=round(INK_MARGIN * scale), fill="white")


def regions_to_images(
    document: DoclingDocument,
    image_dir: Path,
    labels: dict[DocItemLabel, tuple[str, str]],
    namer: ImageNamer,
) -> dict[str, tuple[str, str]]:
    """Save regions of the given labels as PNG into image_dir and put a marker in their place.

    labels: {DocItemLabel: (kind for the file name, alt text)}
    Returns {marker: (alt text, file name)}.
    """
    regions = {}
    for item, _ in document.iterate_items(included_content_layers=BODY):
        if item.label not in labels:
            continue
        if item.label == DocItemLabel.FORMULA:
            image = equation_image(document, item)
        else:
            image = item.get_image(document)
        if image is None:
            continue
        kind, alt = labels[item.label]
        name = namer(item.prov[0].page_no if item.prov else 0, kind)
        image.save(image_dir / name)
        marker = REGION_MARKER.format(len(regions) + 1)
        item.text = marker
        regions[marker] = (alt, name)
    return regions


def save_pictures(
    document: DoclingDocument, image_dir: Path, first_index: int
) -> list[tuple[int, tuple[float, float, float, float] | None, str | None]]:
    """Save body pictures into image_dir as picture<index>.png, counting from first_index.

    Returns (page number, position, file name or None without an image) of each picture in order.
    """
    pictures = []
    for item, _ in document.iterate_items(included_content_layers=BODY):
        if not isinstance(item, PictureItem):
            continue
        page_no, box = page_box(document, item) if item.prov else (0, None)
        image = item.get_image(document)
        name = None
        if image is not None:
            name = f"picture{first_index + len(pictures)}.png"
            image.save(image_dir / name)
        pictures.append((page_no, box, name))
    return pictures


def save_pages(document: DoclingDocument, image_dir: Path, namer: ImageNamer) -> int:
    """Save every page image into image_dir/pages and return the count."""
    page_dir = image_dir / "pages"
    page_dir.mkdir(exist_ok=True)
    count = 0
    for page_no, page in document.pages.items():
        if page.image is not None and page.image.pil_image is not None:
            page.image.pil_image.save(page_dir / f"{namer.page_name(page_no)}.png")
            count += 1
    return count


def estimate_pdf_tokens(document: DoclingDocument) -> int:
    """Estimated tokens of the PDF: all text plus one image per page."""
    text = document.export_to_text(included_content_layers=set(ContentLayer))
    pages = sum(
        page_image_tokens(page.size.width, page.size.height)
        for page in document.pages.values()
    )
    return text_tokens(text) + pages


def saved_image_tokens(artifact_dir: Path) -> int:
    """Estimated tokens of the pictures, equations, and code images in artifact_dir."""
    total = 0
    for path in artifact_dir.glob("*.png"):
        with Image.open(path) as image:
            total += image_tokens(*image.size)
    return total


def page_chunks(
    pdf_path: Path, page_ranges: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    """Page ranges within the PDF cut into chunks of PAGES_PER_CALL pages.

    Raises ConversionError when a range starts after the last page.
    """
    page_count = InputDocument(
        path_or_stream=pdf_path,
        format=InputFormat.PDF,
        backend=ThreadedDoclingParseDocumentBackend,
    ).page_count
    try:
        return split_page_ranges(page_ranges, page_count, PAGES_PER_CALL)
    except ValueError as error:
        raise ConversionError(f"{pdf_path.name}: {error}") from None


def export_markdown(document: DoclingDocument) -> str:
    """Markdown of the body with a marker in place of each picture."""
    return document.export_to_markdown(
        image_mode=ImageRefMode.PLACEHOLDER,
        image_placeholder=PICTURE_MARKER,
        included_content_layers=BODY,
        escape_html=False,
    )


def clear_images(artifact_dir: Path) -> None:
    """Delete images left from a previous conversion."""
    for path in [*artifact_dir.glob("*.png"), *artifact_dir.glob("pages/*.png")]:
        path.unlink()


def convert_pdf(
    pdf_path: Path,
    output_dir: Path,
    *,
    latex: bool = False,
    keep_references: bool = False,
    ocr: bool = False,
    page_images: bool = False,
    page_ranges: list[tuple[int, int]] | None = None,
) -> ConversionResult:
    """Convert one PDF (all pages, or only page_ranges) and write the Markdown and images.

    Images are written into a work directory first and replace the old ones only
    when the whole conversion succeeds.
    """
    markdown_path = output_dir / f"{pdf_path.stem}.md"
    artifact_dir = output_dir / (re.sub(r"\s+", "_", pdf_path.stem) + "_artifacts")
    work_dir = output_dir / f".{artifact_dir.name}.partial"
    converter = build_converter(ocr=ocr, latex=latex)
    chunks = page_chunks(pdf_path, page_ranges or [DEFAULT_PAGE_RANGE])
    namer = ImageNamer(chunks[-1][1])
    labels = {DocItemLabel.CODE: ("code", "code")}
    if not latex:
        labels[DocItemLabel.FORMULA] = ("eq", "equation")

    plain_parts, slide_parts = [], []  # Markdown of each chunk, without and with [p.N]
    pictures = []  # (page number, position, file name) of every body picture
    sizes = []
    region_counts: Counter = Counter()
    pdf_tokens = page_image_count = 0
    shutil.rmtree(work_dir, ignore_errors=True)
    work_dir.mkdir(parents=True)
    try:
        converter.initialize_pipeline(InputFormat.PDF)
        total = sum(last - first + 1 for first, last in chunks)
        with tqdm(total=total, desc="Converting pages", unit="page") as progress:
            ProgressPipeline.progress = progress
            try:
                for chunk in chunks:
                    document = converter.convert(pdf_path, page_range=chunk).document
                    sizes += [page.size for page in document.pages.values()]
                    pdf_tokens += estimate_pdf_tokens(document)
                    regions = regions_to_images(document, work_dir, labels, namer)
                    region_counts.update(alt for alt, _ in regions.values())
                    links = {
                        marker: (alt, f"{artifact_dir.name}/{name}")
                        for marker, (alt, name) in regions.items()
                    }
                    pictures += save_pictures(document, work_dir, len(pictures))
                    if page_images:
                        page_image_count += save_pages(document, work_dir, namer)
                    plain_parts.append(
                        replace_regions(export_markdown(document), links)
                    )
                    mark_pages(document)
                    slide_parts.append(
                        replace_regions(export_markdown(document), links)
                    )
                    del document
                    if MALLOC_TRIM is not None:
                        MALLOC_TRIM(0)
            finally:
                ProgressPipeline.progress = None

        decorations = find_decorations(
            [(page_no, box) for page_no, box, _ in pictures], len(sizes)
        )
        picture_links: list[str | None] = []
        for index, (page_no, _, temporary) in enumerate(pictures):
            if temporary is None or index in decorations:
                if temporary is not None:
                    (work_dir / temporary).unlink()
                picture_links.append(None)
                continue
            name = namer(page_no)
            (work_dir / temporary).rename(work_dir / name)
            picture_links.append(f"{artifact_dir.name}/{name}")

        slides = is_slides(sizes)
        parts = slide_parts if slides else plain_parts
        markdown = fill_pictures(
            "\n\n".join(part for part in parts if part), picture_links
        )
        if not keep_references:
            markdown = strip_references(markdown)

        artifact_dir.mkdir(parents=True, exist_ok=True)
        clear_images(artifact_dir)
        for path in sorted(work_dir.rglob("*.png")):
            target = artifact_dir / path.relative_to(work_dir)
            target.parent.mkdir(exist_ok=True)
            path.replace(target)
        markdown_path.write_text(markdown, encoding="utf-8")
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

    return ConversionResult(
        markdown_path=markdown_path,
        page_count=len(sizes),
        slides=slides,
        picture_count=sum(link is not None for link in picture_links),
        decoration_count=len(decorations),
        equation_count=region_counts["equation"],
        code_count=region_counts["code"],
        page_image_count=page_image_count,
        character_count=len(markdown),
        pdf_tokens=pdf_tokens,
        markdown_tokens=text_tokens(markdown),
        image_tokens=saved_image_tokens(artifact_dir),
    )
