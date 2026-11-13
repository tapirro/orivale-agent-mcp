#!/usr/bin/env python3
"""Zero-dependency stdio MCP server & bridge to https://ori.mantissa.id/mcp (x402 + Apify Dual-Rail).

Answers `initialize`, `ping`, and `tools/list` locally in-memory (including inside offline `--network=none`
Docker quality/security inspection sandboxes such as Glama) with full MCP 2025-03-26 tool annotations,
and executes live `tools/call` requests against https://ori.mantissa.id/mcp.
"""

from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.request
from typing import Any

DEFAULT_MCP_URL = "https://ori.mantissa.id/mcp"
SERVER_INFO: dict[str, str] = {
    "name": "orivale-agent-intelligence",
    "version": "1.3.1",
}


def _ro_ann(title: str, *, open_world: bool = True) -> dict[str, Any]:
    return {
        "title": title,
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": open_world,
    }


STATIC_TOOLS_SPEC: list[dict[str, Any]] = [
    {
        "name": "orivale_dual_rail_catalog",
        "description": (
            "List all Orivale Dual-Rail AI Agent APIs (x402 Base/Solana USDC micropayments + "
            "Apify Store ultra-liquid Pay-Per-Event cloud scrapers + n8n workflow templates)."
        ),
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "annotations": _ro_ann("Orivale Dual-Rail Service Catalog", open_world=False),
    },
    {
        "name": "orivale_bounties_radar",
        "description": (
            "Scan live zero-KYC crypto, code & content bounties with fake-escrow honeypot filtering "
            "and EV scoring. Free 3-item preview; pass optional x402_payment for full feed."
        ),
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "category": {"type": "string", "description": "Filter category: all | content | agent | code"},
                "x402_payment": {"type": "string", "description": "Optional Base64 x402 PAYMENT-SIGNATURE"},
            },
        },
        "annotations": _ro_ann("Zero-KYC Crypto & Agent Bounties Radar"),
    },
    {
        "name": "orivale_clean_markdown",
        "description": (
            "Extract clean RAG-ready Markdown, title & pricing entities from any public URL. "
            "Free 1,500-char preview; pass x402_payment ($0.002 USDC) for full 18,000-char document."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["url"],
            "additionalProperties": False,
            "properties": {
                "url": {"type": "string", "description": "Public https:// URL to extract"},
                "x402_payment": {"type": "string", "description": "Optional Base64 x402 PAYMENT-SIGNATURE"},
            },
        },
        "annotations": _ro_ann("Clean URL-to-Markdown Extractor"),
    },
    {
        "name": "orivale_b2b_domain_enrich",
        "description": (
            "Enrich a B2B company domain with tech-stack signals, hiring/API indicators, ICP fit score, "
            "and personalized outbound icebreaker for Clay/n8n."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["domain"],
            "additionalProperties": False,
            "properties": {
                "domain": {"type": "string", "description": "Company domain (e.g. stripe.com)"},
                "x402_payment": {"type": "string", "description": "Optional Base64 x402 PAYMENT-SIGNATURE"},
            },
        },
        "annotations": _ro_ann("B2B Company Domain Buying-Signal Enricher"),
    },
    {
        "name": "orivale_tech_stack_signal",
        "description": (
            "Fingerprint 30+ B2B website technologies across Frontend, CDN, Analytics/Pixels, CRM/Support, "
            "Payments, Auth, and Security Headers with actionable GTM outbound angle."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["domain"],
            "additionalProperties": False,
            "properties": {
                "domain": {"type": "string", "description": "Target company domain (e.g. linear.app)"},
                "x402_payment": {"type": "string", "description": "Optional Base64 x402 PAYMENT-SIGNATURE"},
            },
        },
        "annotations": _ro_ann("B2B Tech-Stack & Pixel Fingerprinter"),
    },
    {
        "name": "orivale_youtube_transcript_hooks",
        "description": (
            "Extract YouTube or public video title, channel, timestamped chapters, caption/description "
            "transcript excerpt, and 3 viral hook angles for content & research agents."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["url"],
            "additionalProperties": False,
            "properties": {
                "url": {"type": "string", "description": "Public YouTube or video page https:// URL"},
                "x402_payment": {"type": "string", "description": "Optional Base64 x402 PAYMENT-SIGNATURE"},
            },
        },
        "annotations": _ro_ann("YouTube Chapters, Transcript & Hook Extractor"),
    },
    {
        "name": "orivale_shopify_competitor",
        "description": (
            "Analyze a Shopify / e-commerce store's live SKU pricing distribution, markdown share, "
            "and actionable ad counter-angles."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["domain"],
            "additionalProperties": False,
            "properties": {
                "domain": {"type": "string", "description": "Storefront domain (e.g. allbirds.com)"},
                "x402_payment": {"type": "string", "description": "Optional Base64 x402 PAYMENT-SIGNATURE"},
            },
        },
        "annotations": _ro_ann("Shopify Competitor Price & Ad-Angle Analyzer"),
    },
    {
        "name": "orivale_base_contract_audit",
        "description": (
            "Audit any Base Mainnet (eip155:8453) smart contract or relayer wallet for deployed bytecode, "
            "transaction nonce liveness, and Base USDC balance."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["address"],
            "additionalProperties": False,
            "properties": {
                "address": {"type": "string", "description": "0x... 42-character EVM address on Base"},
            },
        },
        "annotations": _ro_ann("Base Smart-Contract & Relayer Auditor"),
    },
]


def _forward_rpc(payload: dict[str, Any], endpoint: str) -> dict[str, Any] | None:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "orivale-mcp-stdio/1.3.1",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, context=ctx, timeout=25.0) as resp:
        raw = resp.read().decode("utf-8", "replace").strip()
        return json.loads(raw) if raw else None


def _handle_local_or_forward(msg: dict[str, Any], endpoint: str) -> dict[str, Any] | None:
    method = str(msg.get("method") or "")
    if method.startswith("notifications/"):
        return None
    rpc_id = msg.get("id")
    params = msg.get("params") if isinstance(msg.get("params"), dict) else {}

    if method == "initialize":
        client_ver = str(params.get("protocolVersion") or "2025-03-26")
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "protocolVersion": client_ver,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
                "instructions": (
                    "Orivale Agent Intelligence provides 8 read-only Dual-Rail tools: free previews via MCP, "
                    "keyless USDC micropayments via x402 (https://ori.mantissa.id/.well-known/x402), "
                    "and cloud batch scrapers on Apify Store (https://apify.com/ultra-liquid)."
                ),
            },
        }
    if method == "ping":
        return {"jsonrpc": "2.0", "id": rpc_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rpc_id, "result": {"tools": STATIC_TOOLS_SPEC}}
    return _forward_rpc(msg, endpoint)


def main() -> int:
    endpoint = os.environ.get("ORIVALE_MCP_URL", DEFAULT_MCP_URL).strip() or DEFAULT_MCP_URL
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Invalid JSON"}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()
            continue
        try:
            reply = _handle_local_or_forward(msg, endpoint)
            if reply is not None and "id" in msg:
                sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
                sys.stdout.flush()
        except Exception as exc:
            if "id" in msg:
                err = {
                    "jsonrpc": "2.0",
                    "id": msg.get("id"),
                    "error": {"code": -32603, "message": f"Upstream MCP bridge error: {exc}"},
                }
                sys.stdout.write(json.dumps(err) + "\n")
                sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
