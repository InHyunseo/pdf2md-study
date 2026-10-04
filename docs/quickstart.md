# Quickstart

English | [한국어](quickstart.ko.md)

From a fresh machine to your first converted PDF.

## 1. Install Git and uv

uv installs the right Python version by itself, so Python is not needed.

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

Open a new terminal afterwards so that `git` and `uv` are found.

## 2. Get the code and install dependencies

```bash
git clone https://github.com/InHyunseo/pdf2md-study.git
cd pdf2md-study
uv sync
```

`uv sync` downloads Docling and PyTorch (about 6 GB), which takes a few minutes.

## 3. Convert a PDF

```bash
uv run pdf2md-study path/to/paper.pdf
```

`paper.md` and `paper_artifacts/` appear next to the PDF. The first run also downloads Docling's models (about 1 GB).

On Windows, a Windows path works as it is:

```powershell
uv run pdf2md-study "C:\Users\me\Desktop\paper.pdf"
```

In WSL2, convert Windows paths first:

```bash
uv run pdf2md-study "$(wslpath 'C:\Users\me\Desktop\paper.pdf')"
```

After step 4, this function in `~/.bashrc` converts Windows paths for you:

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

## 4. Use it from any folder (optional)

```bash
uv tool install -e .
pdf2md-study path/to/paper.pdf
```

`-e` links the command to this folder, so `git pull` updates it.

Next: [usage](usage.md) for all options.
