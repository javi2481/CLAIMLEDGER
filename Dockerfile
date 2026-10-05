FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
COPY manual ./manual

# The product extra is starlette only. uvicorn is the manual-test process
# that binds the existing app; it is not a product pin in pyproject.toml.
RUN pip install --no-cache-dir ".[http,retrieval]" "uvicorn==0.44.0"

EXPOSE 8000

CMD ["uvicorn", "manual.ui:build_manual_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
