#!/usr/bin/env python3
"""Zero-dependency stdio MCP server & bridge to https://ori.mantissa.id/mcp (x402 + Apify Dual-Rail).

Answers `initialize`, `ping`, `tools/list`, `resources/list`, `resources/read`, `prompts/list`,
and `prompts/get` locally in-memory (including inside offline `--network=none` Docker inspection
sandboxes such as Glama) with full MCP 2025-03-26 tool annotations and unbuffered pipe I/O.
"""

from __future__ import annotations

import ipaddress
import json
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_MCP_URL = "https://ori.mantissa.id/mcp"
SERVER_INFO: dict[str, str] = {
    "name": "orivale-agent-intelligence",
    "version": "1.4.0",
}

DOMAIN_PATTERN = r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z]{2,})+$"
HTTPS_URL_PATTERN = r"^https://[^\s/$.?#].[^\s]*$"
EVM_ADDRESS_PATTERN = r"^0x[0-9a-fA-F]{40}$"


def _ro_ann(title: str, *, open_world: bool = True) -> dict[str, Any]:
    return {
        "title": title,
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": open_world,
    }


X402_PAYMENT_PROP: dict[str, Any] = {
    "type": "string",
    "minLength": 16,
    "maxLength": 8192,
    "description": (
        "Optional Base64-encoded x402 PAYMENT-SIGNATURE header token (Base or Solana USDC) to unlock "
        "the full unredacted payload. Omit to receive the instant free preview tier."
    ),
}

STATIC_TOOLS_SPEC: list[dict[str, Any]] = [
    {
        "name": "orivale_dual_rail_catalog",
        "description": (
            "Return the complete machine-readable catalog of Orivale Dual-Rail endpoints, USDC prices, "
            "CAIP-2 settlement addresses (Base eip155:8453 & Solana), and all 8 Apify Store Pay-Per-Event "
            "cloud actors. Call this tool first to discover capabilities, pricing, or batch scraper slugs; "
            "do not call it to extract content from a specific domain or URL."
        ),
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        "annotations": _ro_ann("Orivale Dual-Rail Service Catalog", open_world=False),
    },
    {
        "name": "orivale_bounties_radar",
        "description": (
            "Scan live zero-KYC crypto, code, and AI-agent bounties filtered for fake-escrow honeypots, "
            "submission dilution, and quantitative Expected Value (EV). Returns a free top-3 preview by "
            "default, or the full ranked feed when `x402_payment` ($0.005 USDC) is supplied. On invalid "
            "category, returns an `isError: true` validation message."
        ),
        "inputSchema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["all", "content", "agent", "code"],
                    "default": "all",
                    "description": "Opportunity vertical filter (`all`, `content`, `agent`, or `code`).",
                },
                "x402_payment": X402_PAYMENT_PROP,
            },
        },
        "annotations": _ro_ann("Zero-KYC Crypto & Agent Bounties Radar"),
    },
    {
        "name": "orivale_clean_markdown",
        "description": (
            "Fetch a single public `https://` web page and extract clean RAG-ready Markdown, page title, "
            "and pricing entities with navigation and cookie clutter stripped. Use this for general web "
            "articles and documentation (use `orivale_youtube_transcript_hooks` for video pages, or Apify "
            "`ultra-liquid/ai-agent-clean-markdown-rag` for >50 URLs). Rejects private/loopback SSRF hosts."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["url"],
            "additionalProperties": False,
            "properties": {
                "url": {
                    "type": "string",
                    "minLength": 10,
                    "maxLength": 2048,
                    "pattern": HTTPS_URL_PATTERN,
                    "description": "Public `https://` web page URL to convert into clean Markdown.",
                },
                "x402_payment": X402_PAYMENT_PROP,
            },
        },
        "annotations": _ro_ann("Clean URL-to-Markdown Extractor"),
    },
    {
        "name": "orivale_b2b_domain_enrich",
        "description": (
            "Enrich a B2B company root domain with hiring/API buying-intent signals, an ICP fit score "
            "(0-100), and a ready-to-send 2-line outbound icebreaker. Use this tool for GTM lead scoring "
            "and outreach copy; use `orivale_tech_stack_signal` instead when you need deep 30+ framework, "
            "analytics pixel, and security-header fingerprinting."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["domain"],
            "additionalProperties": False,
            "properties": {
                "domain": {
                    "type": "string",
                    "minLength": 4,
                    "maxLength": 253,
                    "pattern": DOMAIN_PATTERN,
                    "description": "Bare company root domain without protocol or path (e.g. `stripe.com`).",
                },
                "x402_payment": X402_PAYMENT_PROP,
            },
        },
        "annotations": _ro_ann("B2B Company Domain Buying-Signal Enricher"),
    },
    {
        "name": "orivale_tech_stack_signal",
        "description": (
            "Fingerprint 30+ web technologies on a company domain across Frontend, CDN, Analytics/Pixels, "
            "CRM/Support, Payments, Auth, and HTTP Security Headers. Use this for technical architecture "
            "discovery; use `orivale_b2b_domain_enrich` for ICP scoring and cold-email icebreakers, or "
            "`orivale_shopify_competitor` for e-commerce SKU pricing."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["domain"],
            "additionalProperties": False,
            "properties": {
                "domain": {
                    "type": "string",
                    "minLength": 4,
                    "maxLength": 253,
                    "pattern": DOMAIN_PATTERN,
                    "description": "Target company domain name without scheme (e.g. `linear.app`).",
                },
                "x402_payment": X402_PAYMENT_PROP,
            },
        },
        "annotations": _ro_ann("B2B Tech-Stack & Pixel Fingerprinter"),
    },
    {
        "name": "orivale_youtube_transcript_hooks",
        "description": (
            "Extract video title, channel metadata, timestamped chapters, transcript/caption excerpt, "
            "and 3 short-form viral hook angles from a public `https://` YouTube or video URL. Use this "
            "specifically for video pages; use `orivale_clean_markdown` for standard HTML articles."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["url"],
            "additionalProperties": False,
            "properties": {
                "url": {
                    "type": "string",
                    "minLength": 12,
                    "maxLength": 2048,
                    "pattern": HTTPS_URL_PATTERN,
                    "description": "Public `https://` YouTube watch/shorts or video page URL.",
                },
                "x402_payment": X402_PAYMENT_PROP,
            },
        },
        "annotations": _ro_ann("YouTube Chapters, Transcript & Hook Extractor"),
    },
    {
        "name": "orivale_shopify_competitor",
        "description": (
            "Analyze a Shopify or DTC e-commerce storefront domain for live SKU pricing distribution, "
            "discount/markdown share, and 3 counter-positioning ad angles. If the domain is not an "
            "e-commerce storefront, returns structured diagnostic guidance suggesting `orivale_b2b_domain_enrich`."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["domain"],
            "additionalProperties": False,
            "properties": {
                "domain": {
                    "type": "string",
                    "minLength": 4,
                    "maxLength": 253,
                    "pattern": DOMAIN_PATTERN,
                    "description": "Shopify or e-commerce storefront domain without scheme (e.g. `allbirds.com`).",
                },
                "x402_payment": X402_PAYMENT_PROP,
            },
        },
        "annotations": _ro_ann("Shopify Competitor Price & Ad-Angle Analyzer"),
    },
    {
        "name": "orivale_base_contract_audit",
        "description": (
            "Audit a Base Mainnet (CAIP-2 `eip155:8453`) smart contract or relayer wallet address for "
            "deployed EVM bytecode presence, transaction nonce activity, stalled-relayer risk, and USDC "
            "balance (`$0.005` `x402_payment` unlocks full balance & bytecode preview). Requires a 42-char "
            "`0x`-prefixed hex address."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["address"],
            "additionalProperties": False,
            "properties": {
                "address": {
                    "type": "string",
                    "minLength": 42,
                    "maxLength": 42,
                    "pattern": EVM_ADDRESS_PATTERN,
                    "description": "42-character `0x`-prefixed hexadecimal EVM address on Base Mainnet.",
                },
                "x402_payment": X402_PAYMENT_PROP,
            },
        },
        "annotations": _ro_ann("Base Smart-Contract & Relayer Auditor"),
    },
]

STATIC_RESOURCES_SPEC: list[dict[str, Any]] = [
    {
        "uri": "orivale://catalog/dual-rail",
        "name": "Orivale Dual-Rail x402 & Apify Store Catalog",
        "mimeType": "application/json",
        "description": "Complete static directory of x402 USDC endpoints and Apify Store Pay-Per-Event scrapers.",
    }
]

STATIC_PROMPTS_SPEC: list[dict[str, Any]] = [
    {
        "name": "b2b_account_recon",
        "description": "Run a two-step B2B technical and buying-signal recon on a company domain.",
        "arguments": [
            {"name": "domain", "description": "Bare company domain (e.g. stripe.com)", "required": True}
        ],
    }
]


def _validate_tool_arguments(name: str, args: dict[str, Any]) -> str | None:
    """Local pre-flight SSRF & schema validation before forwarding over HTTPS."""
    if name in ("orivale_clean_markdown", "orivale_youtube_transcript_hooks"):
        url = str(args.get("url") or "").strip()
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname:
            return "Parameter `url` must be a valid public `https://` URL."
        host = parsed.hostname.lower()
        if host in ("localhost", "metadata.google.internal") or host.endswith((".local", ".internal")):
            return "Refused private/internal hostname in `url`."
        try:
            ip = ipaddress.ip_address(host)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return "Refused non-public IP address in `url`."
        except ValueError:
            pass
    elif name in ("orivale_b2b_domain_enrich", "orivale_tech_stack_signal", "orivale_shopify_competitor"):
        dom = str(args.get("domain") or "").strip()
        if not re.match(DOMAIN_PATTERN, dom):
            return "Parameter `domain` must be a bare public domain such as `stripe.com` (omit `https://`)."
    elif name == "orivale_base_contract_audit":
        addr = str(args.get("address") or "").strip()
        if not re.match(EVM_ADDRESS_PATTERN, addr):
            return "Parameter `address` must be a 42-character `0x`-prefixed hexadecimal EVM address."
    elif name == "orivale_bounties_radar":
        cat = str(args.get("category") or "all")
        if cat not in ("all", "content", "agent", "code"):
            return "Parameter `category` must be one of: `all`, `content`, `agent`, `code`."
    return None


def _forward_rpc(payload: dict[str, Any], endpoint: str) -> dict[str, Any] | None:
    parsed_ep = urllib.parse.urlsplit(endpoint)
    if parsed_ep.scheme not in ("https", "http") or not parsed_ep.hostname:
        raise ValueError("ORIVALE_MCP_URL must be a valid HTTP(S) endpoint")
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "orivale-mcp-stdio/1.4.0",
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
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                    "prompts": {"listChanged": False},
                },
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
    if method == "resources/list":
        return {"jsonrpc": "2.0", "id": rpc_id, "result": {"resources": STATIC_RESOURCES_SPEC}}
    if method == "resources/read":
        uri = str(params.get("uri") or "orivale://catalog/dual-rail")
        doc = {
            "service": SERVER_INFO,
            "mcp_endpoint": DEFAULT_MCP_URL,
            "x402_manifest": "https://ori.mantissa.id/.well-known/x402",
            "agent_card": "https://ori.mantissa.id/.well-known/agent.json",
            "apify_store": "https://apify.com/ultra-liquid",
            "tools": [t["name"] for t in STATIC_TOOLS_SPEC],
        }
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(doc, indent=2)}]},
        }
    if method == "prompts/list":
        return {"jsonrpc": "2.0", "id": rpc_id, "result": {"prompts": STATIC_PROMPTS_SPEC}}
    if method == "prompts/get":
        dom = str((params.get("arguments") or {}).get("domain") or "stripe.com")
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "description": f"Two-step technical & GTM recon for {dom}",
                "messages": [
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": (
                                f"1. Call `orivale_tech_stack_signal` with domain='{dom}' to map frameworks & pixels.\n"
                                f"2. Call `orivale_b2b_domain_enrich` with domain='{dom}' to compute ICP fit & outbound copy."
                            ),
                        },
                    }
                ],
            },
        }
    if method == "tools/call":
        t_name = str(params.get("name") or "")
        known = {t["name"] for t in STATIC_TOOLS_SPEC}
        if t_name not in known:
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [{"type": "text", "text": f"Unknown tool '{t_name}'. Call `tools/list` for valid names."}],
                    "isError": True,
                },
            }
        t_args = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
        val_err = _validate_tool_arguments(t_name, t_args)
        if val_err:
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {"content": [{"type": "text", "text": val_err}], "isError": True},
            }
    return _forward_rpc(msg, endpoint)


def _read_next_rpc_message() -> tuple[dict[str, Any] | None, bool, bool]:
    """Read one JSON-RPC message using unbuffered `readline()` (supports both NDJSON and Content-Length)."""
    buf = sys.stdin.buffer
    while True:
        raw_line = buf.readline()
        if not raw_line:
            return None, False, True  # EOF
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.lower().startswith(b"content-length:"):
            length = int(stripped.split(b":", 1)[1].strip())
            while True:
                hdr = buf.readline()
                if not hdr or hdr in (b"\r\n", b"\n"):
                    break
            body = buf.read(length)
            return json.loads(body.decode("utf-8", "replace")), True, False
        return json.loads(stripped.decode("utf-8", "replace")), False, False


def _write_rpc_reply(reply: dict[str, Any], framed: bool) -> None:
    encoded = json.dumps(reply, ensure_ascii=False).encode("utf-8")
    out = sys.stdout.buffer
    if framed:
        out.write(f"Content-Length: {len(encoded)}\r\n\r\n".encode("ascii") + encoded)
    else:
        out.write(encoded + b"\n")
    out.flush()


def main() -> int:
    endpoint = os.environ.get("ORIVALE_MCP_URL", DEFAULT_MCP_URL).strip() or DEFAULT_MCP_URL
    while True:
        framed = False
        try:
            msg, framed, is_eof = _read_next_rpc_message()
            if is_eof:
                break
            if msg is None:
                continue
        except Exception:
            _write_rpc_reply({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Invalid JSON"}}, framed)
            continue
        try:
            reply = _handle_local_or_forward(msg, endpoint)
            if reply is not None and "id" in msg:
                _write_rpc_reply(reply, framed)
        except Exception as exc:
            if "id" in msg:
                _write_rpc_reply(
                    {
                        "jsonrpc": "2.0",
                        "id": msg.get("id"),
                        "error": {"code": -32603, "message": f"Upstream MCP bridge error: {exc}"},
                    },
                    framed,
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
