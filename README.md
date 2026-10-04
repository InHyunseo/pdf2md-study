# pdf2md-study

[![CI](https://github.com/InHyunseo/pdf2md-study/actions/workflows/ci.yml/badge.svg)](https://github.com/InHyunseo/pdf2md-study/actions/workflows/ci.yml)

English | [한국어](README.ko.md)

Convert papers and lecture slides (PDF) into study-ready Markdown for LLMs — equations and code kept as images, logos and references stripped.

Built on [Docling](https://github.com/docling-project/docling).

## Why

Uploading a PDF to an LLM sends the text and an image of every page. The Markdown from this tool is several times smaller and keeps what matters for studying.

| Document | PDF (rough tokens) | Markdown only | Markdown + all images |
|---|---|---|---|
| 26-page paper | 50–60k | 15k | 18k |
| 39-page lecture slides | 60–70k | 8k | 25k |

## Features

- Equations and code are cropped as images, so nothing is lost to recognition errors.
- Logos and decorations repeated on many pages are removed.
- The references section is removed.
- Slides get a `[p.N]` label at the start of each page.
- Images are named by page: `p04_1.png`, `p05_eq1.png`, `p30_code1.png`.

## Install

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv tool install git+https://github.com/InHyunseo/pdf2md-study
```

The first conversion downloads Docling's models, which takes a few minutes.

## Usage

```bash
pdf2md-study paper.pdf
```

This writes `paper.md` and `paper_artifacts/` next to the PDF.

| Option | Effect |
|---|---|
| `-o DIR` | Write output into `DIR` |
| `--pages` | Also save an image of every page |
| `--latex` | Recognize equations as LaTeX text instead of images |
| `--keep-refs` | Keep the references section |
| `--ocr` | Read text inside images (scanned PDFs) |

See [docs/usage.md](docs/usage.md) for details.

## Development

```bash
git clone https://github.com/InHyunseo/pdf2md-study.git
cd pdf2md-study
uv sync
uv run pytest
uv run ruff check
```

## License

[MIT](LICENSE)
