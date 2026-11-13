# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.3.x   | :white_check_mark: |
| < 1.3   | :x:                |

## Architecture & Security Design

- **Zero External Python Dependencies**: `orivale-mcp` uses only the Python standard library (`json`, `ssl`, `urllib.request`, `sys`) with TLS certificate verification enforced (`ssl.create_default_context()`).
- **Read-Only Non-Destructive Tools**: All 8 MCP tools declare `readOnlyHint: true` and `destructiveHint: false` under MCP `2025-03-26` tool annotations. None of the tools modify local files, execute shell commands, or mutate remote customer accounts.
- **Strict SSRF Protection**: Remote URL/domain extraction on `https://ori.mantissa.id` resolves DNS records before connecting and blocks loopback, RFC1918 private networks, link-local metadata (`169.254.169.254`), multicast, and internal hostnames across both initial requests and HTTP redirects.
- **Non-Root Container Execution**: The official `Dockerfile` runs under an unprivileged `mcpuser` account.
- **Keyless Optional Payments**: Free preview tiers require zero API keys or credentials; optional `x402` micropayments use signed EIP-3009 / SPL USDC payment headers without sharing wallet private keys.

## Reporting a Vulnerability

Please report security issues privately via [GitHub Private Vulnerability Reporting](https://github.com/tapirro/orivale-agent-mcp/security/advisories/new) or email `security@mantissa.id`. We acknowledge reports within 24 hours and aim to release fixes within 72 hours.
