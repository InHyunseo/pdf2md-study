"""Command-line interface of pdf2md-study.

Input: a PDF path and options from the command line.
Output: Markdown and images written by convert_pdf, and a summary on stdout.
"""

import argparse
import logging
import signal
from pathlib import Path

from pdf2md_study.pages import parse_page_ranges


def stop(signal_number: int, frame: object) -> None:
    """Ctrl+C handler: turn off logging, so Docling's stopping threads print nothing, and stop."""
    logging.disable(logging.CRITICAL)
    raise KeyboardInterrupt


def main(argv: list[str] | None = None) -> None:
    """Parse arguments, convert the PDF, and print a summary."""
    parser = argparse.ArgumentParser(
        prog="pdf2md-study",
        description="Convert a PDF into study-ready Markdown for LLMs.",
    )
    parser.add_argument("pdf", type=Path, help="PDF file to convert")
    parser.add_argument(
        "-o", "--output", type=Path, help="output directory (default: next to the PDF)"
    )
    parser.add_argument(
        "--latex",
        action="store_true",
        help="recognize equations as LaTeX text instead of images (slower, sometimes wrong)",
    )
    parser.add_argument(
        "--keep-refs",
        dest="keep_references",
        action="store_true",
        help="keep the references section",
    )
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="read all page text with OCR, for scans or PDFs with garbled symbols (much slower)",
    )
    parser.add_argument(
        "--pages", action="store_true", help="also save an image of every page"
    )
    parser.add_argument(
        "--page-range",
        metavar="RANGES",
        help='pages to convert, such as "3-7, 10, 20-" (default: all); '
        "write --page-range=-5 when it starts with -",
    )
    arguments = parser.parse_args(argv)

    pdf_path = arguments.pdf.resolve()
    if not pdf_path.is_file():
        parser.error(f"file not found: {pdf_path}")
    output_dir = (arguments.output or pdf_path.parent).resolve()
    page_ranges = None
    if arguments.page_range is not None:
        try:
            page_ranges = parse_page_ranges(arguments.page_range)
        except ValueError as error:
            parser.error(str(error))

    signal.signal(signal.SIGINT, stop)
    try:
        from docling.exceptions import ConversionError

        from pdf2md_study.convert import convert_pdf
    except KeyboardInterrupt:
        parser.exit(130, f"{parser.prog}: interrupted\n")

    try:
        result = convert_pdf(
            pdf_path,
            output_dir,
            latex=arguments.latex,
            keep_references=arguments.keep_references,
            ocr=arguments.ocr,
            page_images=arguments.pages,
            page_ranges=page_ranges,
        )
    except ConversionError as error:
        parser.exit(1, f"{parser.prog}: error: {error}\n")
    except KeyboardInterrupt:
        parser.exit(130, f"{parser.prog}: interrupted\n")

    details = [
        f"{result.picture_count} pictures ({result.decoration_count} decorations removed)",
        f"{result.equation_count} equations",
        f"{result.code_count} code blocks",
    ]
    if result.page_image_count:
        details.append(f"{result.page_image_count} page images")
    print(f"Done: {result.markdown_path}")
    print(
        f"  {'slides' if result.slides else 'document'}, {result.page_count} pages: "
        + ", ".join(details)
    )
    print(f"  about {result.character_count:,} characters")
    print(
        f"  estimated tokens: PDF ~{round(result.pdf_tokens, -2):,}"
        f" -> Markdown ~{round(result.markdown_tokens, -2):,}"
        f" (+ images ~{round(result.image_tokens, -2):,})"
    )
