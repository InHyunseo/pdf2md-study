# 사용법

[English](usage.md) | 한국어

설치는 [빠른 시작](quickstart.ko.md)을 본다.

## 명령

```bash
pdf2md-study <pdf> [-o DIR] [--pages] [--latex] [--keep-refs] [--ocr]
```

| 옵션 | 효과 |
|---|---|
| `-o DIR`, `--output DIR` | 결과 폴더. 기본값은 PDF가 있는 폴더 |
| `--pages` | 페이지 전체 그림도 `<이름>_artifacts/pages/`에 저장 |
| `--latex` | 수식을 그림으로 자르지 않고 LaTeX 글자로 인식. 느리고, 복잡한 식은 틀릴 수 있다 |
| `--keep-refs` | 참고문헌 유지 |
| `--ocr` | 이미지 속 글자도 읽음. 스캔본용. 느리다 |

## 결과물

```
paper.md
paper_artifacts/
├── p02_1.png        2쪽 그림 1
├── p05_eq1.png      5쪽 수식 1
├── p30_code1.png    30쪽 코드 1
└── pages/           --pages일 때만
    └── p01.png
```

- 파일 이름의 띄어쓰기는 그림 폴더 이름에서 `_`로 바뀐다.
- 마크다운의 링크는 상대 경로라서 `.md` 파일과 그림 폴더를 같이 옮겨야 한다.
- 같은 PDF를 다시 변환하면 이전 그림은 지우고 새로 만든다.

끝나면 요약이 나온다.

```
Done: /home/me/paper.md
  document, 26 pages: 13 pictures (0 decorations removed), 11 equations, 1 code blocks
  about 57,944 characters
  estimated tokens: PDF ~53,900 -> Markdown ~14,600 (+ images ~3,300)
```

## 바뀌는 내용

| 내용 | 결과 |
|---|---|
| 그림 | `![figure](paper_artifacts/p02_1.png)` |
| 따로 떨어진 수식 | `![equation](paper_artifacts/p05_eq1.png)` |
| 코드 블록 | `![code](paper_artifacts/p30_code1.png)` |
| 전체 페이지의 25% 이상에서 같은 자리에 나오는 그림 (작은 그림은 3쪽 이상) | 장식으로 보고 삭제 |
| References, Bibliography, 참고문헌 제목의 절 | 같은 단계의 다음 제목 직전까지 삭제. 뒤의 부록은 남는다 |
| 슬라이드 (가로 페이지가 절반 초과) | 페이지마다 첫 글 앞에 `[p.N]` |

## LLM에 보낼 때

- 글로 묻는 질문은 보통 `.md` 파일 하나면 된다.
- 아키텍처 그림이나 수식처럼 질문 대상인 그림은 같이 첨부한다.
- 문장 속 수식이 많은 페이지는 `--pages`로 변환해서 그 페이지 그림을 첨부한다.

## 토큰 추정

요약 마지막 줄은 LLM에 올릴 때의 대략적인 토큰 수다.

| 항목 | 세는 방법 |
|---|---|
| PDF | 전체 글자 + 페이지마다 150 DPI로 그린 이미지 한 장 |
| Markdown | `.md` 파일 |
| images | 그림·수식·코드 그림 전부를 첨부할 때 |

글자는 ASCII 4자, 그 외 문자(한글 등) 1자를 1토큰으로 센다. 그림은 Claude 4.7 이후 모델의 [이미지 규칙](https://platform.claude.com/docs/en/build-with-claude/vision)을 따른다: 2576px와 4,784토큰 안으로 줄인 뒤 28×28px 칸 하나를 1토큰으로 센다. 다른 모델은 세는 방식이 다르다.

## 한계

- 문장 속 수식은 일반 글자로 추출되어 첨자와 분수가 깨진다 (`ximg ∈ R3×H0×W0`). `--pages`로 페이지 그림을 같이 보낸다.
- 슬라이드 도형으로 그린 다이어그램은 글자 조각으로 흩어질 수 있다.
- `--ocr`은 언어를 지정하지 않아서 한글 인식이 부정확할 수 있다.
