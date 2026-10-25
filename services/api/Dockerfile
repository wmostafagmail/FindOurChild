FROM python:3.13.13-slim-bookworm@sha256:355bfa66770995d7e9a0da4b3473b44d0cb451f6b56f5615ad9c39e3c4eca03f
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_PROJECT_ENVIRONMENT=/opt/venv UV_PYTHON_DOWNLOADS=never
WORKDIR /workspace
COPY requirements-bootstrap.txt ./
RUN pip install --no-cache-dir --require-hashes -r requirements-bootstrap.txt
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --all-groups
ENV PATH="/opt/venv/bin:$PATH" PYTHONPATH="/workspace/services/api:/workspace"
COPY services/api ./services/api
COPY scripts ./scripts
COPY database ./database
COPY docs/contracts ./docs/contracts
RUN useradd --uid 10001 --create-home foc && mkdir /coverage /delivery /notifications && chown 10001:10001 /coverage /delivery /notifications
USER foc
