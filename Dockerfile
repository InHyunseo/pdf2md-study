# CPU-only image with the Docling models included, so it runs without downloads.
# Build: docker build -t pdf2md-study .
# Run:   docker run --rm --user "$(id -u):$(id -g)" -v "$PWD:/data" pdf2md-study paper.pdf
FROM python:3.14-slim

# Shared libraries that opencv-python (pulled in by rapidocr) needs.
RUN apt-get update \
 && apt-get install -y --no-install-recommends libgl1 libglib2.0-0t64 libxcb1 \
 && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.12.22 /uv /bin/uv

WORKDIR /app

# Dependencies first, so code changes do not reinstall them.
# Same versions as uv.lock, but PyTorch from the CPU-only index.
COPY pyproject.toml uv.lock ./
RUN uv export --locked --no-dev --no-emit-project --no-hashes -o constraints.txt \
 && uv pip install --system --no-cache --torch-backend cpu -c constraints.txt -r pyproject.toml

# Models for the default pipeline (layout, tableformer), --latex (code_formula), --ocr (rapidocr).
ENV DOCLING_ARTIFACTS_PATH=/models
RUN docling-tools models download -o /models layout tableformer code_formula rapidocr

COPY README.md LICENSE ./
COPY src ./src
RUN uv pip install --system --no-cache --no-deps .

WORKDIR /data
ENTRYPOINT ["pdf2md-study"]
