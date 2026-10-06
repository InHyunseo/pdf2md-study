# 빠른 시작

[English](quickstart.md) | 한국어

새 컴퓨터에서 첫 PDF 변환까지.

## 1. uv 설치

uv가 맞는 Python 버전을 알아서 설치하므로 Python은 따로 설치하지 않아도 된다.

**Ubuntu / WSL2**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**macOS**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

설치 후 터미널을 새로 열어야 `uv`가 잡힌다.

## 2. pdf2md-study 설치

```bash
uv tool install pdf2md-study
```

Docling과 PyTorch(약 6GB)를 내려받느라 몇 분 걸린다. 설치 후 `pdf2md-study`가 잡히지 않으면 `uv tool update-shell`을 실행하고 터미널을 새로 연다.

## 3. PDF 변환

```bash
pdf2md-study path/to/paper.pdf
```

PDF 옆에 `paper.md`와 `paper_artifacts/`가 생긴다. 첫 실행 때는 Docling 모델(약 1GB)도 내려받는다.

Windows에서는 Windows 경로를 그대로 쓰면 된다.

```powershell
pdf2md-study "C:\Users\me\Desktop\paper.pdf"
```

WSL2에서는 Windows 경로를 먼저 바꾼다.

```bash
pdf2md-study "$(wslpath 'C:\Users\me\Desktop\paper.pdf')"
```

`~/.bashrc`에 이 함수를 넣으면 Windows 경로를 알아서 바꿔준다.

```bash
tomd() {
    local arguments=()
    local argument converted
    for argument in "$@"; do
        if [[ "$argument" =~ ^[A-Za-z]:[\\/] ]]; then
            converted=$(wslpath -u "$argument") || return 1
            arguments+=("$converted")
        else
            arguments+=("$argument")
        fi
    done
    pdf2md-study "${arguments[@]}"
}
```

```bash
tomd "C:\Users\me\Desktop\paper.pdf"
```

## 4. 업데이트

```bash
uv tool upgrade pdf2md-study
```

## uv 대신 Docker

[Docker](https://docs.docker.com/get-started/get-docker/)가 있다면 1~4단계를 건너뛸 수 있다. 이미지에 Docling 모델이 들어 있고 CPU로 돈다. 첫 실행 때 약 2GB를 내려받는다 (디스크 3.4GB). 이미지는 x86-64용이라 Apple Silicon Mac에서는 에뮬레이션으로 느리게 돈다. 거기서는 uv를 쓴다.

PDF가 있는 폴더에서 실행한다.

**Ubuntu / WSL2 / macOS**

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/data" ghcr.io/inhyunseo/pdf2md-study paper.pdf
```

**Windows (PowerShell)**

```powershell
docker run --rm -v "${PWD}:/data" ghcr.io/inhyunseo/pdf2md-study paper.pdf
```

- `-v`는 현재 폴더를 컨테이너의 `/data`로 공유한다. PDF는 이 폴더나 그 아래에 있어야 하고, 경로는 이 폴더 기준이다. `-o out`은 `./out`에 쓴다.
- `--user`는 결과 파일의 소유자를 나로 만든다. 없으면 Linux와 WSL2에서 root 소유가 된다.
- 옵션은 `pdf2md-study`와 같이 파일 이름 뒤에 붙인다.

WSL2에서는 Windows 폴더로 먼저 이동한다.

```bash
cd "$(wslpath 'C:\Users\me\Desktop')"
```

업데이트하거나 버전을 고정하려면:

```bash
docker pull ghcr.io/inhyunseo/pdf2md-study
docker run ... ghcr.io/inhyunseo/pdf2md-study:0.2.0 paper.pdf
```

다음: 모든 옵션은 [사용법](usage.ko.md).
