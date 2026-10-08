FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY manual ./manual

# Editable install keeps claimledger under /app/src. artifacts_dir() and
# corpus_dir() walk three parents from that file to /app, where Compose
# mounts the hashed JSON and the sample PDFs. A regular install copies the
# package into site-packages and those walks miss both mounts.
# uvicorn is the manual-test process that binds the existing app; it is not
# a product pin in pyproject.toml.
RUN pip install --no-cache-dir -e ".[http,deepseek]" "uvicorn==0.44.0" "pillow==11.1.0"

EXPOSE 8000

CMD ["uvicorn", "manual.ui:build_manual_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
