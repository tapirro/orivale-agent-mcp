FROM python:3.12-slim
WORKDIR /app
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir . && chown -R mcpuser:mcpuser /app
USER mcpuser
ENTRYPOINT ["orivale-mcp"]
