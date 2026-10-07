"""Tests for pdf2md_study.markdown.

Input: Markdown strings written in each test.
Output: pass or fail of the post-processing results.
"""

import pytest

from pdf2md_study.markdown import (
    PICTURE_MARKER,
    REGION_MARKER,
    fill_pictures,
    replace_regions,
    strip_references,
)


def test_strip_references_keeps_following_section():
    """References are removed up to the next heading of the same level."""
    markdown = "## Method\ntext\n## References\n[1] paper\n## Appendix\nmore\n"
    assert strip_references(markdown) == "## Method\ntext\n## Appendix\nmore\n"


def test_strip_references_removes_to_end():
    """References at the end are removed to the end of the document."""
    markdown = "## Method\ntext\n## References\n[1] paper\n[2] paper\n"
    assert strip_references(markdown) == "## Method\ntext\n"


def test_strip_references_removes_subsections():
    """Lower-level headings inside references are removed with it."""
    markdown = "## References\n### Books\n[1] book\n## Appendix\n"
    assert strip_references(markdown) == "## Appendix\n"


@pytest.mark.parametrize(
    "title", ["References", "6. References", "BIBLIOGRAPHY", "참고문헌", "참고 문헌"]
)
def test_strip_references_title_variants(title):
    """Numbered, upper-case, and Korean titles are recognized."""
    markdown = f"## Method\ntext\n## {title}\n[1] paper\n"
    assert strip_references(markdown) == "## Method\ntext\n"


def test_strip_references_keeps_other_headings():
    """Headings that only contain the word are kept."""
    markdown = "## Related references in robotics\ntext\n"
    assert strip_references(markdown) == markdown


def test_fill_pictures_in_order():
    """Markers are replaced by links in order, and None removes the marker."""
    markdown = f"a\n{PICTURE_MARKER}\nb\n{PICTURE_MARKER}\nc\n{PICTURE_MARKER}\n"
    links = ["art/p01_1.png", None, "art/p02_1.png"]
    assert fill_pictures(markdown, links) == (
        "a\n![figure](art/p01_1.png)\nb\n\nc\n![figure](art/p02_1.png)\n"
    )


def test_fill_pictures_removes_paragraph():
    """None removes a marker paragraph together with its blank line."""
    markdown = f"a\n\n{PICTURE_MARKER}\n\nb\n"
    assert fill_pictures(markdown, [None]) == "a\n\nb\n"


def test_fill_pictures_warns_on_count_mismatch():
    """A different number of markers and links raises a warning."""
    with pytest.warns(UserWarning, match="2 picture markers but 1 saved pictures"):
        result = fill_pictures(f"{PICTURE_MARKER}\n{PICTURE_MARKER}\n", ["a.png"])
    assert result == "![figure](a.png)\n\n"


def test_replace_regions_equation():
    """An equation marker is replaced together with its $$ wrapper."""
    marker = REGION_MARKER.format(1)
    markdown = f"before\n\n$${marker}$$\n\nafter\n"
    regions = {marker: ("equation", "art/p05_eq1.png")}
    assert replace_regions(markdown, regions) == (
        "before\n\n![equation](art/p05_eq1.png)\n\nafter\n"
    )


def test_replace_regions_code():
    """A code marker is replaced together with its code fence."""
    marker = REGION_MARKER.format(1)
    markdown = f"before\n\n```python\n{marker}\n```\n\nafter\n"
    regions = {marker: ("code", "art/p30_code1.png")}
    assert replace_regions(markdown, regions) == (
        "before\n\n![code](art/p30_code1.png)\n\nafter\n"
    )


def test_replace_regions_keeps_backslash_in_link():
    """Backslashes in links are written as they are."""
    marker = REGION_MARKER.format(1)
    regions = {marker: ("code", r"art\p01_code1.png")}
    assert replace_regions(marker, regions) == r"![code](art\p01_code1.png)"
