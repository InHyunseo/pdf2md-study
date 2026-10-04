"""Tests for pdf2md_study.layout.

Input: small DoclingDocument objects built with docling-core in each test.
Output: pass or fail of the layout analysis results.
"""

from docling_core.types.doc import (
    BoundingBox,
    ContentLayer,
    DocItemLabel,
    DoclingDocument,
    ProvenanceItem,
    Size,
)

from pdf2md_study.layout import ImageNamer, hide_decorations, is_slides, mark_pages

PORTRAIT = Size(width=600, height=800)
LANDSCAPE = Size(width=800, height=600)


def make_document(page_count: int, size: Size = PORTRAIT) -> DoclingDocument:
    """Empty document with page_count pages of the given size."""
    document = DoclingDocument(name="test")
    for page_no in range(1, page_count + 1):
        document.add_page(page_no=page_no, size=size)
    return document


def provenance(
    page_no: int, left: float, top: float, right: float, bottom: float
) -> ProvenanceItem:
    """Provenance on a page with a top-left origin bounding box in points."""
    return ProvenanceItem(
        page_no=page_no,
        bbox=BoundingBox(l=left, t=top, r=right, b=bottom),
        charspan=(0, 0),
    )


def test_hide_decorations_repeated_on_every_page():
    """A picture at the same position on every page is hidden."""
    document = make_document(4)
    logos = [
        document.add_picture(prov=provenance(page_no, 500, 10, 590, 60))
        for page_no in range(1, 5)
    ]
    figure = document.add_picture(prov=provenance(2, 50, 200, 550, 600))

    assert hide_decorations(document) == 4
    assert all(logo.content_layer == ContentLayer.FURNITURE for logo in logos)
    assert figure.content_layer == ContentLayer.BODY


def test_hide_decorations_tolerates_small_shift():
    """Pictures shifted by a few points still count as the same position."""
    document = make_document(3)
    for page_no, shift in zip(range(1, 4), (0, 3, -3)):
        document.add_picture(prov=provenance(page_no, 500 + shift, 10, 590 + shift, 60))
    assert hide_decorations(document) == 3


def test_hide_decorations_small_picture_on_few_pages():
    """A small picture repeated on 3 of 20 pages is hidden."""
    document = make_document(20)
    for page_no in (1, 5, 9):
        document.add_picture(prov=provenance(page_no, 10, 10, 40, 40))
    assert hide_decorations(document) == 3


def test_hide_decorations_large_picture_on_few_pages():
    """A large picture repeated on 3 of 20 pages is kept."""
    document = make_document(20)
    for page_no in (1, 5, 9):
        document.add_picture(prov=provenance(page_no, 50, 200, 550, 600))
    assert hide_decorations(document) == 0


def test_hide_decorations_picture_on_two_pages():
    """A picture repeated on only 2 pages is kept."""
    document = make_document(2)
    for page_no in (1, 2):
        document.add_picture(prov=provenance(page_no, 10, 10, 40, 40))
    assert hide_decorations(document) == 0


def test_is_slides():
    """Documents with mostly landscape pages are slides."""
    assert is_slides(make_document(3, LANDSCAPE))
    assert not is_slides(make_document(3, PORTRAIT))
    assert not is_slides(make_document(0))


def test_mark_pages_first_text_only():
    """Only the first text of each page gets a page label."""
    document = make_document(2, LANDSCAPE)
    title = document.add_text(
        label=DocItemLabel.TEXT, text="Title", prov=provenance(1, 10, 10, 300, 40)
    )
    body = document.add_text(
        label=DocItemLabel.TEXT, text="Body", prov=provenance(1, 10, 50, 300, 80)
    )
    second = document.add_text(
        label=DocItemLabel.TEXT, text="Next", prov=provenance(2, 10, 10, 300, 40)
    )
    mark_pages(document)
    assert (title.text, body.text, second.text) == ("[p.1] Title", "Body", "[p.2] Next")


def test_mark_pages_skips_code():
    """Code is not labeled, and the label goes to the next text on the page."""
    document = make_document(1, LANDSCAPE)
    code = document.add_code(text="x = 1", prov=provenance(1, 10, 10, 300, 40))
    text = document.add_text(
        label=DocItemLabel.TEXT, text="Body", prov=provenance(1, 10, 50, 300, 80)
    )
    mark_pages(document)
    assert (code.text, text.text) == ("x = 1", "[p.1] Body")


def test_image_namer_counts_per_page_and_kind():
    """Numbers restart for each page and each kind."""
    document = make_document(2)
    first = document.add_picture(prov=provenance(1, 0, 0, 10, 10))
    second = document.add_picture(prov=provenance(2, 0, 0, 10, 10))
    namer = ImageNamer(page_count=2)
    names = [namer(first), namer(first), namer(first, "eq"), namer(second)]
    assert names == ["p01_1.png", "p01_2.png", "p01_eq1.png", "p02_1.png"]


def test_image_namer_pads_to_page_count():
    """Page numbers are padded to the digits of the page count."""
    assert ImageNamer(page_count=120).page_name(7) == "p007"
