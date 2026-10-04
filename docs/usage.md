# Usage

English | [한국어](usage.ko.md)

## Command

```bash
pdf2md-study <pdf> [-o DIR] [--pages] [--latex] [--keep-refs] [--ocr]
```

| Option | Effect |
|---|---|
| `-o DIR`, `--output DIR` | Output directory. Default: the directory of the PDF |
| `--pages` | Also save an image of every page into `<name>_artifacts/pages/` |
| `--latex` | Recognize equations as LaTeX text instead of cropping them. Slower, and complex equations can come out wrong |
| `--keep-refs` | Keep the references section |
| `--ocr` | Read text inside images. For scanned PDFs. Slower |

## Output

```
paper.md
paper_artifacts/
├── p02_1.png        picture 1 on page 2
├── p05_eq1.png      equation 1 on page 5
├── p30_code1.png    code 1 on page 30
└── pages/           only with --pages
    └── p01.png
```

- Spaces in the file name become `_` in the artifacts directory name.
- Links in the Markdown are relative, so keep the `.md` file and the artifacts directory together.
- Converting the same PDF again replaces the previous images.

## What is changed

| Content | Result |
|---|---|
| Pictures | `![figure](paper_artifacts/p02_1.png)` |
| Display equations | `![equation](paper_artifacts/p05_eq1.png)` |
| Code blocks | `![code](paper_artifacts/p30_code1.png)` |
| Pictures at the same position on at least 25% of the pages (or 3 pages for small ones) | Removed as decorations |
| Section titled References, Bibliography, or 참고문헌 | Removed up to the next heading of the same level, so appendices stay |
| Slides (more than half of the pages are landscape) | `[p.N]` before the first text of each page |

## Sending to an LLM

- For text questions, the `.md` file alone is usually enough.
- Attach the images the question is about, such as an architecture figure or an equation.
- For a page with many inline formulas, convert with `--pages` and attach that page image.

## Limitations

- Formulas inside sentences are extracted as plain text, so subscripts and fractions are flattened (`ximg ∈ R3×H0×W0`). Use `--pages` and attach the page image.
- Diagrams drawn with slide shapes may come out as scattered text fragments.
- `--ocr` does not set a language, so Korean OCR can be inaccurate.

## Windows paths in WSL

Pass Windows paths through `wslpath`:

```bash
pdf2md-study "$(wslpath 'C:\Users\me\Desktop\paper.pdf')"
```
