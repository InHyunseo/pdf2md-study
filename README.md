# pdf2md-study

[![CI](https://github.com/InHyunseo/pdf2md-study/actions/workflows/ci.yml/badge.svg)](https://github.com/InHyunseo/pdf2md-study/actions/workflows/ci.yml)

English | [한국어](https://github.com/InHyunseo/pdf2md-study/blob/main/README.ko.md)

Convert papers and lecture slides (PDF) into study-ready Markdown for LLMs — equations and code kept as images, logos and references stripped.

Built on [Docling](https://github.com/docling-project/docling).

## Why

Uploading a PDF to an LLM sends the text and an image of every page. The Markdown is several times smaller and keeps what matters for studying. Each conversion prints an estimate like these:

| Document | PDF | Markdown | + images |
|---|---|---|---|
| 26-page paper | ~53,900 tokens | ~14,600 | ~3,300 |
| 39-page lecture slides | ~116,400 tokens | ~6,700 | ~18,300 |

## Features

- Equations and code are cropped as images, so nothing is lost to recognition errors.
- Logos and decorations repeated across pages are removed.
- The references section is removed.
- Slides get a `[p.N]` label on each page.
- Images are named by page: `p04_1.png`, `p05_eq1.png`, `p30_code1.png`.

## Get started

With [uv](https://docs.astral.sh/uv/) installed:

```bash
uv tool install pdf2md-study
pdf2md-study paper.pdf
```

`paper.md` and `paper_artifacts/` appear next to the PDF.

- [Quickstart](https://github.com/InHyunseo/pdf2md-study/blob/main/docs/quickstart.md): step by step on Ubuntu, WSL2, macOS, and Windows
- [Usage](https://github.com/InHyunseo/pdf2md-study/blob/main/docs/usage.md): options, output, and tips for sending to an LLM

## Development

```bash
git clone https://github.com/InHyunseo/pdf2md-study.git
cd pdf2md-study
uv sync
uv run pytest
uv run ruff check
```

Pull requests run lint and tests on Ubuntu, Windows, and macOS.

## License

[MIT](https://github.com/InHyunseo/pdf2md-study/blob/main/LICENSE)
