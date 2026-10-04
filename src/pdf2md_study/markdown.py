"""Markdown post-processing for converted documents.

Input: Markdown exported by Docling, with markers in place of pictures and cropped regions.
Output: Markdown with image links in place of the markers and the references section removed.
"""

import re
import warnings

PICTURE_MARKER = "PDF2MDSTUDYPICTURE"
REGION_MARKER = "PDF2MDSTUDYREGION{:04d}"

HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
REFERENCES_TITLE = re.compile(
    r"^(?:\d+\.?\s*)?(references|bibliography|참고\s*문헌)\s*$", re.IGNORECASE
)


def strip_references(markdown: str) -> str:
    """Remove the references section up to the next heading of the same or higher level."""
    lines, skip_level = [], None
    for line in markdown.splitlines():
        match = HEADING.match(line)
        if match:
            level = len(match.group(1))
            if skip_level is not None and level <= skip_level:
                skip_level = None
            if skip_level is None and REFERENCES_TITLE.match(match.group(2).strip()):
                skip_level = level
                continue
        if skip_level is None:
            lines.append(line)
    return "\n".join(lines) + "\n"


def fill_pictures(markdown: str, links: list[str | None]) -> str:
    """Replace picture markers with image links in order. None removes the marker."""
    parts = markdown.split(PICTURE_MARKER)
    if len(parts) - 1 != len(links):
        warnings.warn(
            f"{len(parts) - 1} picture markers but {len(links)} saved pictures",
            stacklevel=2,
        )
    result = [parts[0]]
    for index, part in enumerate(parts[1:]):
        link = links[index] if index < len(links) else None
        result.append(f"![figure]({link})" if link else "")
        result.append(part)
    return "".join(result)


def replace_regions(markdown: str, regions: dict[str, tuple[str, str]]) -> str:
    """Replace region markers with image links.

    Equations come as $$marker$$ and code as ```language\\nmarker\\n```,
    so the surrounding $$ and code fence are removed with the marker.
    regions: {marker: (alt text, link)}
    """
    for marker, (alt, link) in regions.items():
        pattern = rf"(?:```[^\n]*\n)?\$*[ \t]*{marker}[ \t]*\$*(?:\n```)?"
        image = f"![{alt}]({link})"
        markdown = re.sub(pattern, lambda _, image=image: image, markdown)
    return markdown
