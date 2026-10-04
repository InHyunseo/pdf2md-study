"""Run the Docling pipeline and write study-ready Markdown.

Input: a PDF path and an output directory.
Output: <name>.md and <name>_artifacts/ (pictures, equations, code, optional page images)
in the output directory, and a ConversionResult with counts.
"""

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import (
    DocItemLabel,
    DoclingDocument,
    ImageRefMode,
    PictureItem,
)

from pdf2md_study.layout import (
    BODY,
    ImageNamer,
    hide_decorations,
    is_slides,
    mark_pages,
)
from pdf2md_study.markdown import (
    PICTURE_MARKER,
    REGION_MARKER,
    fill_pictures,
    replace_regions,
    strip_references,
)

IMAGE_SCALE = 2.0  # resolution multiplier for cropped images


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


def build_converter(ocr: bool, latex: bool) -> DocumentConverter:
    """Docling converter with the pypdfium2 backend and page images enabled."""
    options = PdfPipelineOptions()
    options.do_ocr = ocr
    options.do_formula_enrichment = latex
    options.images_scale = IMAGE_SCALE
    options.generate_page_images = True
    options.generate_picture_images = True
    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=options, backend=PyPdfiumDocumentBackend
            )
        }
    )


def regions_to_images(
    document: DoclingDocument,
    artifact_dir: Path,
    labels: dict[DocItemLabel, tuple[str, str]],
    namer: ImageNamer,
) -> dict[str, tuple[str, str]]:
    """Save regions of the given labels as PNG and put a marker in their place.

    labels: {DocItemLabel: (kind for the file name, alt text)}
    Returns {marker: (alt text, link)}.
    """
    regions = {}
    for item, _ in document.iterate_items(included_content_layers=BODY):
        if item.label not in labels:
            continue
        image = item.get_image(document)
        if image is None:
            continue
        kind, alt = labels[item.label]
        name = namer(item, kind)
        image.save(artifact_dir / name)
        marker = REGION_MARKER.format(len(regions) + 1)
        item.text = marker
        regions[marker] = (alt, f"{artifact_dir.name}/{name}")
    return regions


def save_pictures(
    document: DoclingDocument, artifact_dir: Path, namer: ImageNamer
) -> list[str | None]:
    """Save body pictures in order and return their links (None where no image exists)."""
    links = []
    for item, _ in document.iterate_items(included_content_layers=BODY):
        if not isinstance(item, PictureItem):
            continue
        image = item.get_image(document)
        if image is None:
            links.append(None)
            continue
        name = namer(item)
        image.save(artifact_dir / name)
        links.append(f"{artifact_dir.name}/{name}")
    return links


def save_pages(document: DoclingDocument, artifact_dir: Path, namer: ImageNamer) -> int:
    """Save every page image into artifact_dir/pages and return the count."""
    page_dir = artifact_dir / "pages"
    page_dir.mkdir(exist_ok=True)
    count = 0
    for page_no, page in document.pages.items():
        if page.image is not None and page.image.pil_image is not None:
            page.image.pil_image.save(page_dir / f"{namer.page_name(page_no)}.png")
            count += 1
    return count


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
) -> ConversionResult:
    """Convert one PDF and write the Markdown and images into output_dir."""
    markdown_path = output_dir / f"{pdf_path.stem}.md"
    artifact_dir = output_dir / (re.sub(r"\s+", "_", pdf_path.stem) + "_artifacts")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    clear_images(artifact_dir)

    document = build_converter(ocr=ocr, latex=latex).convert(pdf_path).document
    namer = ImageNamer(len(document.pages))

    decoration_count = hide_decorations(document)
    labels = {DocItemLabel.CODE: ("code", "code")}
    if not latex:
        labels[DocItemLabel.FORMULA] = ("eq", "equation")
    regions = regions_to_images(document, artifact_dir, labels, namer)
    picture_links = save_pictures(document, artifact_dir, namer)
    slides = is_slides(document)
    if slides:
        mark_pages(document)
    page_image_count = save_pages(document, artifact_dir, namer) if page_images else 0

    markdown = document.export_to_markdown(
        image_mode=ImageRefMode.PLACEHOLDER,
        image_placeholder=PICTURE_MARKER,
        included_content_layers=BODY,
        escape_html=False,
    )
    markdown = fill_pictures(markdown, picture_links)
    markdown = replace_regions(markdown, regions)
    if not keep_references:
        markdown = strip_references(markdown)
    markdown_path.write_text(markdown, encoding="utf-8")

    region_counts = Counter(alt for alt, _ in regions.values())
    return ConversionResult(
        markdown_path=markdown_path,
        page_count=len(document.pages),
        slides=slides,
        picture_count=sum(link is not None for link in picture_links),
        decoration_count=decoration_count,
        equation_count=region_counts["equation"],
        code_count=region_counts["code"],
        page_image_count=page_image_count,
        character_count=len(markdown),
    )
