"""Tests for pdf2md_study.pages.

Input: page range text written in each test.
Output: pass or fail of the parsed ranges.
"""

import pytest

from pdf2md_study.pages import LAST_PAGE, parse_page_ranges, split_page_ranges


def test_parse_page_ranges_forms():
    """Single pages, closed ranges, and open ranges are accepted."""
    assert parse_page_ranges("3-7, 10-11, 18, 20-") == [
        (3, 7),
        (10, 11),
        (18, 18),
        (20, LAST_PAGE),
    ]
    assert parse_page_ranges("-5, 9") == [(1, 5), (9, 9)]


def test_parse_page_ranges_sorts_and_merges():
    """Ranges are sorted, and overlapping or adjacent ranges are merged."""
    assert parse_page_ranges("10, 3") == [(3, 3), (10, 10)]
    assert parse_page_ranges("3-7, 8-9, 5") == [(3, 9)]
    assert parse_page_ranges("20-, 25") == [(20, LAST_PAGE)]


@pytest.mark.parametrize(
    "text", ["", "0", "7-3", "a", "3-4-5", "3,,4", "-", "3~7", "3 4"]
)
def test_parse_page_ranges_rejects_invalid(text):
    """Invalid text raises ValueError."""
    with pytest.raises(ValueError):
        parse_page_ranges(text)


def test_split_page_ranges():
    """Ranges are cut into chunks and limited to the last page."""
    assert split_page_ranges([(1, 5), (8, 8), (10, LAST_PAGE)], 11, 2) == [
        (1, 2),
        (3, 4),
        (5, 5),
        (8, 8),
        (10, 11),
    ]


def test_split_page_ranges_rejects_start_after_last_page():
    """A range starting after the last page raises ValueError."""
    with pytest.raises(ValueError, match="page 12 is after the last page"):
        split_page_ranges([(12, 13)], 11, 4)
