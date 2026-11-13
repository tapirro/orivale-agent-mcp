# Changelog

All notable changes to `orivale-mcp` (`io.github.tapirro/orivale-agent-mcp`) are documented in this file.

## [1.3.1] - 2026-11-13

### Added
- Added `orivale_tech_stack_signal` tool (`GET/POST /v1/x402/tech-stack-signal`) for 30+ B2B tech-stack, pixel, CRM, billing, and security-header fingerprinting.
- Added `orivale_youtube_transcript_hooks` tool (`GET/POST /v1/x402/youtube-transcript-hooks`) for YouTube/video metadata, chapters, caption/description excerpts, and 3 viral hook angles.
- Added MCP `2025-03-26` tool `annotations` (`title`, `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) and `additionalProperties: false` input schemas across all 8 tools.
- Added `SECURITY.md` and non-root `mcpuser` execution in `Dockerfile`.

### Fixed
- Answered `initialize`, `ping`, and `tools/list` locally in-memory in `orivale_mcp.server` so offline `--network=none` container sandboxes (such as Glama's Docker inspector) inspect schemas deterministically without requiring network egress.

## [1.3.0] - 2026-11-13

### Added
- Published `io.github.tapirro/orivale-agent-mcp` to the Official Anthropic/GitHub MCP Registry via GitHub Actions OIDC (`server.json`).
- Added keyless `/v1/x402/llm` inference endpoint, OpenAPI 3.1 spec (`/openapi.json`), and `/llms.txt`.
