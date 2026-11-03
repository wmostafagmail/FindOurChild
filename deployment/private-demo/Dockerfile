FROM python:3.13.13-slim-bookworm@sha256:355bfa66770995d7e9a0da4b3473b44d0cb451f6b56f5615ad9c39e3c4eca03f
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_PROJECT_ENVIRONMENT=/opt/venv UV_PYTHON_DOWNLOADS=never
WORKDIR /workspace
COPY requirements-bootstrap.txt ./
RUN pip install --no-cache-dir --require-hashes -r requirements-bootstrap.txt
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
ENV PATH="/opt/venv/bin:$PATH" PYTHONPATH="/workspace"
COPY services/demo_deployment ./services/demo_deployment
COPY tools/phase2e ./tools/phase2e
COPY database/owner_only_demo ./database/owner_only_demo
COPY database/owner_deployment ./database/owner_deployment
COPY config/keycloak/realm-template.json ./config/keycloak/realm-template.json
ARG SOURCE_SHA
RUN python -c "import re,json; s='$SOURCE_SHA'; assert re.fullmatch('[a-f0-9]{40}',s);open('/workspace/release.json','w').write(json.dumps({'source_sha':s}))"
USER 10001:10001
