"""Page range selection from the command line.

Input: text such as "-5, 10-11, 18, 20-", and the page count of the PDF.
Output: sorted, merged (start, end) page ranges, 1-based and inclusive,
and the same ranges cut into chunks for conversion.
"""

import re
import sys

RANGE_PATTERN = re.compile(r"(\d+)|(\d*)\s*-\s*(\d*)")
LAST_PAGE = sys.maxsize  # end of an open range such as "20-"


def parse_page_ranges(text: str) -> list[tuple[int, int]]:
    """Page ranges separated by commas: N, A-B, -B (from page 1), or A- (to the last page).

    Raises ValueError on invalid text.
    """
    ranges = []
    for part in text.split(","):
        match = RANGE_PATTERN.fullmatch(part.strip())
        if match is None or not any(match.groups()):
            raise ValueError(f"invalid page range: {part.strip()!r}")
        if match[1]:
            start = end = int(match[1])
        else:
            start = int(match[2]) if match[2] else 1
            end = int(match[3]) if match[3] else LAST_PAGE
        if start < 1 or end < start:
            raise ValueError(f"invalid page range: {part.strip()!r}")
        ranges.append((start, end))

    merged: list[tuple[int, int]] = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def split_page_ranges(
    page_ranges: list[tuple[int, int]], page_count: int, size: int
) -> list[tuple[int, int]]:
    """Ranges limited to the page_count pages of the PDF and cut into chunks of at most size pages.

    Raises ValueError when a range starts after the last page.
    """
    chunks = []
    for start, end in page_ranges:
        if start > page_count:
            raise ValueError(f"page {start} is after the last page ({page_count})")
        last = min(end, page_count)
        chunks += [
            (first, min(first + size - 1, last))
            for first in range(start, last + 1, size)
        ]
    return chunks
