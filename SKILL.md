---
name: orivale-agent-intelligence
description: Dual-Rail AI Agent Intelligence & Web Extraction toolkit exposing hosted MCP tools (https://ori.mantissa.id/mcp), keyless x402 Base/Solana USDC micropayment APIs (https://ori.mantissa.id/.well-known/x402), and 8 Apify Store Pay-Per-Event cloud scrapers (https://apify.com/ultra-liquid). Use when extracting clean Markdown for RAG, enriching B2B company domains for Clay/n8n, auditing Shopify competitor pricing & ad angles, checking Base Mainnet smart-contract/relayer liveness, or discovering verified zero-KYC bounties.
version: 1.2.0
homepage: https://ori.mantissa.id/.well-known/x402
---

# Orivale Agent Intelligence (`MCP` + `x402` + `Apify`)

Connect autonomous agents, Claude Code, Cursor, Windsurf, or `n8n` workflows to Orivale's Dual-Rail data and compute stack:

- **Hosted Streamable HTTP MCP (Zero Install)**: `https://ori.mantissa.id/mcp`
- **Local Stdio MCP Bridge (`uvx`)**: `uvx --from git+https://github.com/tapirro/orivale-agent-mcp orivale-mcp`
- **x402 Discovery Manifest (`Base` + `Solana` USDC)**: `https://ori.mantissa.id/.well-known/x402`
- **Apify Store Cloud Scrapers (`PAY_PER_EVENT`)**: `https://apify.com/ultra-liquid`

## Available MCP Tools

1. `orivale_dual_rail_catalog` — Full live catalog of x402 USDC endpoints and Apify PPE Actors.
2. `orivale_clean_markdown` — Strips HTML/JS clutter from any URL into clean RAG Markdown + pricing entities (`$0.002 USDC` full / free 1,500-char preview).
3. `orivale_b2b_domain_enrich` — Extracts company tech-stack signals, hiring/docs indicators, ICP fit score, and a 2-line personalized outbound icebreaker (`$0.015 USDC`).
4. `orivale_shopify_competitor` — Audits live Shopify storefront SKU pricing distribution, markdown share, and ad counter-angles (`$0.010 USDC`).
5. `orivale_base_contract_audit` — Verifies Base Mainnet (`eip155:8453`) smart-contract bytecode, nonce activity, and USDC relayer balance (`$0.005 USDC`).
6. `orivale_bounties_radar` — Scans open crypto, code & content bounties with fake-escrow honeypot filtering and EV scoring (`$0.005 USDC` full / free top-3 preview).
