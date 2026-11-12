# Orivale Agent Intelligence (`MCP` + `x402` + `Apify` + `n8n`)

Open-source **Dual-Rail Model Context Protocol (MCP)** server and `n8n` workflow templates connecting autonomous AI agents, Claude Desktop, Cursor, Windsurf, and Clay/n8n pipelines to:

1. **Hosted Streamable HTTP MCP (Zero Install)**: `https://ori.mantissa.id/mcp`
2. **Keyless `x402` v2 Commercial APIs (`Base USDC` + `Solana USDC`)**: `https://ori.mantissa.id/.well-known/x402` (settled gaslessly via `PayAI` Facilitator)
3. **Apify Store Cloud Scrapers (`PAY_PER_EVENT` Fiat Billing)**: [`https://apify.com/ultra-liquid`](https://apify.com/ultra-liquid)

---

## Quickstart (30 Seconds)

### Option A — Hosted Streamable HTTP MCP (Claude Code, Cursor, n8n MCP Client)

```json
{
  "mcpServers": {
    "orivale": {
      "url": "https://ori.mantissa.id/mcp"
    }
  }
}
```

### Option B — Local Stdio Bridge via `uvx` (Zero External Dependencies)

```json
{
  "mcpServers": {
    "orivale": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/tapirro/orivale-agent-mcp", "orivale-mcp"]
    }
  }
}
```

---

## Live Dual-Rail Endpoints (`x402` USDC + `Apify Store` PPE)

| Capability | `x402` Endpoint (`ori.mantissa.id`) | Price (`USDC`) | Apify Store Cloud Actor (`apify.com/ultra-liquid`) |
|---|---|---:|---|
| Clean URL-to-Markdown for RAG | `GET /v1/x402/clean-markdown?url=...` | `$0.002` | [`ultra-liquid/ai-agent-clean-markdown-rag`](https://apify.com/ultra-liquid/ai-agent-clean-markdown-rag) |
| B2B Domain Buying-Signal Enricher | `GET /v1/x402/b2b-enrich?domain=...` | `$0.015` | [`ultra-liquid/b2b-lead-signal-enricher`](https://apify.com/ultra-liquid/b2b-lead-signal-enricher) |
| Shopify Competitor Price & Ad Angles | `GET /v1/x402/shopify-competitor?domain=...` | `$0.010` | [`ultra-liquid/shopify-competitor-ad-pain-analyzer`](https://apify.com/ultra-liquid/shopify-competitor-ad-pain-analyzer) |
| Keyless OpenAI Chat Completions | `POST /v1/x402/chat/completions` | `$0.002` | — |
| Base Smart-Contract & Relayer Audit | `GET /v1/x402/contract-audit?address=0x...` | `$0.005` | — |
| Honeypot-Filtered Agent Bounties Feed | `GET /v1/x402/bounties?category=all` | `$0.005` | [`ultra-liquid/reddit-buyer-intent-lead-radar`](https://apify.com/ultra-liquid/reddit-buyer-intent-lead-radar) |
| Google Maps B2B Contact Enricher | — | PPE | [`ultra-liquid/google-maps-b2b-lead-enricher`](https://apify.com/ultra-liquid/google-maps-b2b-lead-enricher) |
| Amazon & Shopify Review Pain Miner | — | PPE | [`ultra-liquid/ecom-review-pain-miner`](https://apify.com/ultra-liquid/ecom-review-pain-miner) |
| TikTok Shop Winning Product Miner | — | PPE | [`ultra-liquid/tiktok-shop-winning-product-miner`](https://apify.com/ultra-liquid/tiktok-shop-winning-product-miner) |
| Viral Video Hook Extractor & Cloner | — | PPE | [`ultra-liquid/viral-video-hook-cloner`](https://apify.com/ultra-liquid/viral-video-hook-cloner) |

---

## Sample Extracted Output (`orivale_b2b_domain_enrich`)

```json
{
  "ok": true,
  "domain": "apify.com",
  "company_title": "Apify: Full-stack web scraping and data extraction platform",
  "tech_and_buying_signals": ["nextjs", "intercom", "cloudflare", "hiring_active", "api_product", "pricing_public"],
  "icp_fit_score": 94,
  "icebreaker_2line": "Noticed apify.com is running nextjs, intercom, cloudflare with active hiring/docs surfaces. Built a drop-in automation workflow tailored for teams scaling that exact setup."
}
```

## Ready-to-Import `n8n` Workflows

Import any JSON template from [`n8n_workflows/`](n8n_workflows/) directly into `n8n` (`Workflows -> Import from File`) and set `APIFY_API_TOKEN`.

## License

MIT
