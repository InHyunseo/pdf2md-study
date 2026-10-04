# pdf2md-study

[![CI](https://github.com/InHyunseo/pdf2md-study/actions/workflows/ci.yml/badge.svg)](https://github.com/InHyunseo/pdf2md-study/actions/workflows/ci.yml)

[English](https://github.com/InHyunseo/pdf2md-study/blob/main/README.md) | 한국어

논문과 강의자료 PDF를 LLM 공부용 마크다운으로 바꾼다. 수식과 코드는 그림으로 남기고, 로고와 참고문헌은 지운다.

[Docling](https://github.com/docling-project/docling) 기반이다.

## 왜 필요한가

PDF를 LLM에 올리면 글자와 함께 페이지마다 이미지가 들어간다. 마크다운은 그보다 몇 배 작고, 공부에 필요한 내용은 남긴다. 변환할 때마다 이런 추정치가 출력된다.

| 문서 | PDF | 마크다운 | + 그림 |
|---|---|---|---|
| 논문 26쪽 | ~53,900토큰 | ~14,600 | ~3,300 |
| 강의자료 39쪽 | ~116,400토큰 | ~6,700 | ~18,300 |

## 기능

- 수식과 코드는 그림으로 잘라낸다. 인식 오류로 내용이 깨지지 않는다.
- 여러 페이지에 반복되는 로고와 장식은 지운다.
- 참고문헌 절은 지운다.
- 슬라이드는 페이지마다 `[p.N]`을 붙인다.
- 그림 이름은 페이지 기준이다: `p04_1.png`, `p05_eq1.png`, `p30_code1.png`.

## 시작하기

[uv](https://docs.astral.sh/uv/)가 설치돼 있다면:

```bash
uv tool install pdf2md-study
pdf2md-study paper.pdf
```

PDF 옆에 `paper.md`와 `paper_artifacts/`가 생긴다.

- [빠른 시작](https://github.com/InHyunseo/pdf2md-study/blob/main/docs/quickstart.ko.md): Ubuntu, WSL2, macOS, Windows 단계별 설치
- [사용법](https://github.com/InHyunseo/pdf2md-study/blob/main/docs/usage.ko.md): 옵션, 결과물, LLM에 보낼 때 팁

## 개발

```bash
git clone https://github.com/InHyunseo/pdf2md-study.git
cd pdf2md-study
uv sync
uv run pytest
uv run ruff check
```

PR마다 Ubuntu, Windows, macOS에서 lint와 테스트가 돈다.

## 라이선스

[MIT](https://github.com/InHyunseo/pdf2md-study/blob/main/LICENSE)
