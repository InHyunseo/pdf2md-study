"""Tests for pdf2md_study.tokens.

Input: text, image sizes, and page sizes written in each test.
Output: pass or fail of the token estimates.
"""

import pytest

from pdf2md_study.tokens import image_tokens, page_image_tokens, text_tokens

STANDARD_TIER = {"maximum_long_edge": 1568, "maximum_tokens": 1568}


def test_text_tokens_ascii():
    """Four ASCII characters make one token."""
    assert text_tokens("abcd" * 10) == 10


def test_text_tokens_korean():
    """Each non-ASCII character makes one token."""
    assert text_tokens("파라미터") == 4


def test_text_tokens_mixed_rounds_up():
    """Mixed text adds both parts and rounds up."""
    assert text_tokens("ab 한글") == 3


def test_text_tokens_empty():
    """Empty text has no tokens."""
    assert text_tokens("") == 0


@pytest.mark.parametrize(
    ("width", "height", "tokens"),
    [
        (200, 200, 64),
        (1000, 1000, 1296),
        (1092, 1092, 1521),
        (1920, 1080, 2691),
        (2000, 1500, 3888),
        (3840, 2160, 4784),
    ],
)
def test_image_tokens_high_resolution_tier(width, height, tokens):
    """Token counts match the table in Claude's vision documentation."""
    assert image_tokens(width, height) == tokens


@pytest.mark.parametrize(
    ("width", "height", "tokens"),
    [
        (200, 200, 64),
        (1092, 1092, 1521),
        (1920, 1080, 1560),
        (2000, 1500, 1564),
        (3840, 2160, 1560),
    ],
)
def test_image_tokens_standard_tier(width, height, tokens):
    """Token counts with standard-tier limits match the documentation table."""
    assert image_tokens(width, height, **STANDARD_TIER) == tokens


def test_image_tokens_portrait_same_as_landscape():
    """Swapping width and height gives the same tokens."""
    assert image_tokens(1080, 1920) == image_tokens(1920, 1080)


def test_image_tokens_empty_image():
    """An image with no area has no tokens."""
    assert image_tokens(0, 100) == 0


def test_page_image_tokens_letter_page():
    """A letter-size page at 150 DPI is 1275 x 1650 pixels."""
    assert page_image_tokens(612, 792) == image_tokens(1275, 1650) == 46 * 59
