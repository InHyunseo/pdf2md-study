# Quickstart

English | [한국어](quickstart.ko.md)

From a fresh machine to your first converted PDF.

## 1. Install uv

uv installs the right Python version by itself, so Python is not needed.

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

Open a new terminal afterwards so that `uv` is found.

## 2. Install pdf2md-study

```bash
uv tool install pdf2md-study
```

This downloads Docling and PyTorch (about 6 GB), which takes a few minutes. If `pdf2md-study` is not found afterwards, run `uv tool update-shell` and open a new terminal.

## 3. Convert a PDF

```bash
pdf2md-study path/to/paper.pdf
```

`paper.md` and `paper_artifacts/` appear next to the PDF. The first run also downloads Docling's models (about 1 GB).

On Windows, a Windows path works as it is:

```powershell
pdf2md-study "C:\Users\me\Desktop\paper.pdf"
```

In WSL2, convert Windows paths first:

```bash
pdf2md-study "$(wslpath 'C:\Users\me\Desktop\paper.pdf')"
```

This function in `~/.bashrc` converts Windows paths for you:

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

## 4. Update

```bash
uv tool upgrade pdf2md-study
```

## Docker instead of uv

If you have [Docker](https://docs.docker.com/get-started/get-docker/), you can skip steps 1–4. The image includes Docling's models and runs on the CPU. The first run downloads about 2 GB (3.4 GB on disk). The image is built for x86-64, so on Apple Silicon Macs it runs slowly under emulation; use uv there.

Run it in the folder that has the PDF.

**Ubuntu / WSL2 / macOS**

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/data" ghcr.io/inhyunseo/pdf2md-study paper.pdf
```

**Windows (PowerShell)**

```powershell
docker run --rm -v "${PWD}:/data" ghcr.io/inhyunseo/pdf2md-study paper.pdf
```

- `-v` shares the current folder with the container as `/data`. The PDF must be in this folder or below it, and paths are relative to it. `-o out` writes to `./out`.
- `--user` makes you the owner of the output files. Without it, they belong to root on Linux and WSL2.
- Options go after the file name, as with `pdf2md-study`.

In WSL2, move to the Windows folder first:

```bash
cd "$(wslpath 'C:\Users\me\Desktop')"
```

To update, or to use a fixed version:

```bash
docker pull ghcr.io/inhyunseo/pdf2md-study
docker run ... ghcr.io/inhyunseo/pdf2md-study:0.2.0 paper.pdf
```

Next: [usage](usage.md) for all options.
