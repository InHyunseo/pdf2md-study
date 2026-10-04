"""Rough token estimates for sending a PDF or the converted Markdown to an LLM.

Input: text, image sizes in pixels, and page sizes in points.
Output: estimated token counts. Images follow Claude's published rule:
scale down to fit the long-edge and token limits, then one token per 28x28 patch.
Text is estimated from character counts.
"""

import math

ASCII_CHARACTERS_PER_TOKEN = 4
NON_ASCII_CHARACTERS_PER_TOKEN = 1
PATCH_SIZE = 28
# High-resolution tier (Claude 4.7 and later)
MAXIMUM_LONG_EDGE = 2576
MAXIMUM_IMAGE_TOKENS = 4784
PAGE_RENDER_DPI = 150


def text_tokens(text: str) -> int:
    """Estimated tokens of text: 4 ASCII characters or 1 other character per token."""
    ascii_count = sum(character.isascii() for character in text)
    non_ascii_count = len(text) - ascii_count
    return math.ceil(
        ascii_count / ASCII_CHARACTERS_PER_TOKEN
        + non_ascii_count / NON_ASCII_CHARACTERS_PER_TOKEN
    )


def patch_count(width: int, height: int) -> int:
    """Number of 28x28 patches that cover the image."""
    return math.ceil(width / PATCH_SIZE) * math.ceil(height / PATCH_SIZE)


def image_tokens(
    width: int,
    height: int,
    maximum_long_edge: int = MAXIMUM_LONG_EDGE,
    maximum_tokens: int = MAXIMUM_IMAGE_TOKENS,
) -> int:
    """Tokens of an image after scaling it to the largest size within the limits."""
    if width <= 0 or height <= 0:
        return 0
    long_edge, short_edge = max(width, height), min(width, height)
    ratio = short_edge / long_edge
    for scaled_long in range(min(long_edge, maximum_long_edge), 0, -1):
        scaled_short = max(1, math.floor(scaled_long * ratio + 0.5))
        tokens = patch_count(scaled_long, scaled_short)
        if tokens <= maximum_tokens:
            return tokens
    return 1


def page_image_tokens(width_points: float, height_points: float) -> int:
    """Estimated tokens of a PDF page rendered as an image at PAGE_RENDER_DPI."""
    pixels_per_point = PAGE_RENDER_DPI / 72
    return image_tokens(
        round(width_points * pixels_per_point), round(height_points * pixels_per_point)
    )
