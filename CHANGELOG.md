# Changelog

All notable changes to `orivale-mcp` are documented in this file.

## [1.4.0] - 2026-11-13
### Added
- Unbuffered interactive stdio transport (`sys.stdin.buffer.readline()`) supporting both newline-delimited JSON-RPC 2.0 and `Content-Length` framed messages for zero-deadlock Docker inspection (`Glama`, `MCP Inspector`).
- Local offline support for `resources/list`, `resources/read`, `prompts/list`, and `prompts/get` capabilities.
- Strict JSON Schema parameter patterns (`HTTPS_URL_PATTERN`, `DOMAIN_PATTERN`, `EVM_ADDRESS_PATTERN`) and local pre-flight SSRF protection blocking loopback, link-local, and cloud metadata IPs.
- Automated interactive pipe test suite (`tests/test_mcp_server.py`) and GitHub Actions CI (`.github/workflows/ci.yml`).
- OCI & Official MCP Registry `io.modelcontextprotocol.server.name` Docker labels.

## [1.3.1] - 2026-11-12
### Added
- `glama.json` maintainer manifest, `Dockerfile`, and `SECURITY.md`.
