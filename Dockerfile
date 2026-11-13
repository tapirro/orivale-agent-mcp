# For MCP directories that inspect servers by building & running this container (e.g. Glama):
# Answers `initialize`, `ping`, `tools/list`, `resources/list`, and `prompts/list` in-memory
# with zero network access (`--network=none`), unbuffered stdio, and non-root execution.
FROM python:3.12-slim
LABEL io.modelcontextprotocol.server.name="io.github.tapirro/orivale-agent-mcp"
LABEL org.opencontainers.image.source="https://github.com/tapirro/orivale-agent-mcp"
LABEL org.opencontainers.image.licenses="MIT"
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir . && chown -R mcpuser:mcpuser /app
USER mcpuser
ENTRYPOINT ["orivale-mcp"]
