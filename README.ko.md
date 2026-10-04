# pdf2md-study

[![CI](https://github.com/InHyunseo/pdf2md-study/actions/workflows/ci.yml/badge.svg)](https://github.com/InHyunseo/pdf2md-study/actions/workflows/ci.yml)

[English](README.md) | 한국어

논문과 강의자료 PDF를 LLM 공부용 마크다운으로 바꾼다. 수식과 코드는 그림으로 남기고, 로고와 참고문헌은 지운다.

[Docling](https://github.com/docling-project/docling) 기반이다.

## 왜 필요한가

PDF를 LLM에 올리면 글자와 함께 페이지마다 이미지가 들어간다. 이 도구로 만든 마크다운은 그보다 몇 배 작고, 공부에 필요한 내용은 남긴다.

| 문서 | PDF (대략 토큰) | 마크다운만 | 마크다운 + 그림 전부 |
|---|---|---|---|
| 논문 26쪽 | 5~6만 | 1.5만 | 1.8만 |
| 강의자료 39쪽 | 6~7만 | 8천 | 2.5만 |

## 기능

- 수식과 코드는 그림으로 잘라낸다. 인식 오류로 내용이 깨지지 않는다.
- 여러 페이지에 반복되는 로고와 장식은 지운다.
- 참고문헌 절은 지운다.
- 슬라이드는 페이지마다 첫 줄에 `[p.N]`을 붙인다.
- 그림 이름은 페이지 기준이다: `p04_1.png`, `p05_eq1.png`, `p30_code1.png`.

## 설치

[uv](https://docs.astral.sh/uv/)가 필요하다.

```bash
uv tool install git+https://github.com/InHyunseo/pdf2md-study
```

첫 변환 때 Docling 모델을 내려받느라 몇 분 걸린다.

## 사용법

```bash
pdf2md-study paper.pdf
```

PDF 옆에 `paper.md`와 `paper_artifacts/`가 생긴다.

| 옵션 | 효과 |
|---|---|
| `-o DIR` | 결과를 `DIR`에 저장 |
| `--pages` | 페이지 전체 그림도 저장 |
| `--latex` | 수식을 그림 대신 LaTeX 글자로 인식 |
| `--keep-refs` | 참고문헌 유지 |
| `--ocr` | 이미지 속 글자도 읽음 (스캔본) |

자세한 내용은 [docs/usage.ko.md](docs/usage.ko.md).

## 개발

```bash
git clone https://github.com/InHyunseo/pdf2md-study.git
cd pdf2md-study
uv sync
uv run pytest
uv run ruff check
```

## 라이선스

[MIT](LICENSE)
