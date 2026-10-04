"""Page layout analysis on a converted Docling document.

Input: DoclingDocument produced by Docling.
Output: the same document modified in place (repeated decorations moved out of the body,
page labels added to slides), and short image file names based on page numbers.
"""

from docling_core.types.doc import (
    ContentLayer,
    DocItem,
    DocItemLabel,
    DoclingDocument,
    PictureItem,
)

BODY = {ContentLayer.BODY}
# Pictures at the same position on REPEAT_RATIO of the pages are decorations.
# Pictures under SMALL_AREA of the page need only MINIMUM_REPEAT pages.
REPEAT_RATIO = 0.25
SMALL_AREA = 0.02
MINIMUM_REPEAT = 3
# Position difference, relative to page size, still treated as the same position.
POSITION_TOLERANCE = 0.02


def page_box(
    document: DoclingDocument, item: DocItem
) -> tuple[int, tuple[float, float, float, float]]:
    """Page number of the item and its position relative to page size (left, right, bottom, top)."""
    provenance = item.prov[0]
    size = document.pages[provenance.page_no].size
    bbox = provenance.bbox
    return provenance.page_no, (
        bbox.l / size.width,
        bbox.r / size.width,
        min(bbox.t, bbox.b) / size.height,
        max(bbox.t, bbox.b) / size.height,
    )


def hide_decorations(document: DoclingDocument) -> int:
    """Move pictures repeated at the same position across pages out of the body.

    Returns the number of hidden pictures.
    """
    page_count = len(document.pages)
    groups: list[tuple[tuple, list, set]] = []  # (reference position, pictures, pages)
    for item, _ in document.iterate_items(included_content_layers=BODY):
        if not isinstance(item, PictureItem) or not item.prov:
            continue
        page_no, box = page_box(document, item)
        for reference, items, pages in groups:
            if all(abs(a - b) <= POSITION_TOLERANCE for a, b in zip(reference, box)):
                items.append(item)
                pages.add(page_no)
                break
        else:
            groups.append((box, [item], {page_no}))

    hidden = 0
    for (left, right, bottom, top), items, pages in groups:
        small = (right - left) * (top - bottom) < SMALL_AREA
        if len(pages) >= MINIMUM_REPEAT and (
            small or len(pages) >= page_count * REPEAT_RATIO
        ):
            for item in items:
                item.content_layer = ContentLayer.FURNITURE
            hidden += len(items)
    return hidden


def is_slides(document: DoclingDocument) -> bool:
    """Treat the document as slides when more than half of the pages are landscape."""
    sizes = [page.size for page in document.pages.values()]
    landscape = sum(size.width > size.height for size in sizes)
    return bool(sizes) and landscape * 2 > len(sizes)


def mark_pages(document: DoclingDocument) -> None:
    """Prefix the first text of each page with [p.N]."""
    seen = set()
    for item, _ in document.iterate_items(included_content_layers=BODY):
        if not item.prov or not getattr(item, "text", ""):
            continue
        if item.label in (DocItemLabel.FORMULA, DocItemLabel.CODE):
            continue
        page_no = item.prov[0].page_no
        if page_no not in seen:
            seen.add(page_no)
            item.text = f"[p.{page_no}] {item.text}"


class ImageNamer:
    """Short image file names based on page numbers (p04_1.png, p05_eq1.png)."""

    def __init__(self, page_count: int):
        self.digits = max(2, len(str(page_count)))
        self.counts: dict[tuple[int, str], int] = {}

    def page_name(self, page_no: int) -> str:
        """Zero-padded page name such as p04."""
        return f"p{page_no:0{self.digits}d}"

    def __call__(self, item: DocItem, kind: str = "") -> str:
        """Next file name for the item's page and kind."""
        page_no = item.prov[0].page_no if item.prov else 0
        key = (page_no, kind)
        self.counts[key] = self.counts.get(key, 0) + 1
        return f"{self.page_name(page_no)}_{kind}{self.counts[key]}.png"
