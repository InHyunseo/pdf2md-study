"""Command-line interface of pdf2md-study.

Input: a PDF path and options from the command line.
Output: Markdown and images written by convert_pdf, and a summary on stdout.
"""

import argparse
import sys
from pathlib import Path


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
        help="read text inside images, for scanned PDFs (slower)",
    )
    parser.add_argument(
        "--pages", action="store_true", help="also save an image of every page"
    )
    arguments = parser.parse_args(argv)

    pdf_path = arguments.pdf.resolve()
    if not pdf_path.is_file():
        parser.error(f"file not found: {pdf_path}")
    output_dir = (arguments.output or pdf_path.parent).resolve()

    from pdf2md_study.convert import convert_pdf

    try:
        result = convert_pdf(
            pdf_path,
            output_dir,
            latex=arguments.latex,
            keep_references=arguments.keep_references,
            ocr=arguments.ocr,
            page_images=arguments.pages,
        )
    except KeyboardInterrupt:
        sys.exit(130)

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
