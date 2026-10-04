# Usage

English | [한국어](usage.ko.md)

For installation, see the [quickstart](quickstart.md).

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
- Links in the Markdown are relative, so move the `.md` file and the artifacts directory together.
- Converting the same PDF again replaces the previous images.

A summary is printed at the end:

```
Done: /home/me/paper.md
  document, 26 pages: 13 pictures (0 decorations removed), 11 equations, 1 code blocks
  about 57,944 characters
  estimated tokens: PDF ~53,900 -> Markdown ~14,600 (+ images ~3,300)
```

## What is changed

| Content | Result |
|---|---|
| Pictures | `![figure](paper_artifacts/p02_1.png)` |
| Display equations | `![equation](paper_artifacts/p05_eq1.png)` |
| Code blocks | `![code](paper_artifacts/p30_code1.png)` |
| Pictures at the same position on at least 25% of the pages (3 pages for small ones) | Removed as decorations |
| Section titled References, Bibliography, or 참고문헌 | Removed up to the next heading of the same level, so appendices stay |
| Slides (more than half of the pages are landscape) | `[p.N]` before the first text of each page |

## Sending to an LLM

- For questions about the text, the `.md` file alone is usually enough.
- Attach the images the question is about, such as an architecture figure or an equation.
- For a page with many inline formulas, convert with `--pages` and attach that page image.

## Token estimate

The last line of the summary is a rough estimate for uploading to an LLM:

| Part | Counted as |
|---|---|
| PDF | All text, plus each page as an image rendered at 150 DPI |
| Markdown | The `.md` file |
| images | All pictures, equations, and code images, if attached |

Text counts 4 ASCII characters or 1 other character (such as Korean) per token. Images follow [Claude's image rule](https://platform.claude.com/docs/en/build-with-claude/vision) for Claude 4.7 and later: scaled down to fit 2576 px and 4,784 tokens, then one token per 28×28 pixel patch. Other models count differently.

## Limitations

- Formulas inside sentences are extracted as plain text, so subscripts and fractions are flattened (`ximg ∈ R3×H0×W0`). Use `--pages` and attach the page image.
- Diagrams drawn with slide shapes may come out as scattered text fragments.
- `--ocr` does not set a language, so Korean OCR can be inaccurate.
