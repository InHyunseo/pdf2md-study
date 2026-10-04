# 빠른 시작

[English](quickstart.md) | 한국어

새 컴퓨터에서 첫 PDF 변환까지.

## 1. Git과 uv 설치

uv가 맞는 Python 버전을 알아서 설치하므로 Python은 따로 설치하지 않아도 된다.

**Ubuntu / WSL2**

```bash
sudo apt update && sudo apt install -y git
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**macOS**

```bash
xcode-select --install
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell)**

```powershell
winget install --id Git.Git -e
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

설치 후 터미널을 새로 열어야 `git`과 `uv`가 잡힌다.

## 2. 코드 받기와 의존성 설치

```bash
git clone https://github.com/InHyunseo/pdf2md-study.git
cd pdf2md-study
uv sync
```

`uv sync`가 Docling과 PyTorch(약 6GB)를 내려받느라 몇 분 걸린다.

## 3. PDF 변환

```bash
uv run pdf2md-study path/to/paper.pdf
```

PDF 옆에 `paper.md`와 `paper_artifacts/`가 생긴다. 첫 실행 때는 Docling 모델(약 1GB)도 내려받는다.

Windows에서는 Windows 경로를 그대로 쓰면 된다.

```powershell
uv run pdf2md-study "C:\Users\me\Desktop\paper.pdf"
```

WSL2에서는 Windows 경로를 먼저 바꾼다.

```bash
uv run pdf2md-study "$(wslpath 'C:\Users\me\Desktop\paper.pdf')"
```

4번까지 한 뒤 `~/.bashrc`에 이 함수를 넣으면 Windows 경로를 알아서 바꿔준다.

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

## 4. 어느 폴더에서나 쓰기 (선택)

```bash
uv tool install -e .
pdf2md-study path/to/paper.pdf
```

`-e`는 명령을 이 폴더에 연결한다. `git pull`하면 명령도 같이 최신이 된다.

다음: 모든 옵션은 [사용법](usage.ko.md).
