"""Drop-in CrewAI, LangChain & Pure-Python Tool Wrappers for Orivale MCP & x402 APIs."""

from __future__ import annotations

import json
import ssl
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "https://ori.mantissa.id"


def call_orivale_mcp_tool(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    mcp_url: str = f"{DEFAULT_BASE_URL}/mcp",
) -> dict[str, Any]:
    """Invoke any Orivale Streamable HTTP MCP tool (`free preview` or with optional `x402_payment`)."""
    ctx = ssl.create_default_context()
    rpc_body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    req = urllib.request.Request(
        mcp_url,
        data=json.dumps(rpc_body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "orivale-mcp-python/1.3.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, context=ctx, timeout=25.0) as resp:
        envelope = json.loads(resp.read().decode("utf-8", "replace"))
    content = ((envelope.get("result") or {}).get("content") or [{}])[0]
    text = str(content.get("text") or "{}")
    try:
        return json.loads(text)
    except Exception:
        return {"ok": True, "raw": text}


def call_orivale_x402_get(
    path: str,
    params: dict[str, str],
    *,
    payment_signature: str = "",
    base_url: str = DEFAULT_BASE_URL,
) -> dict[str, Any]:
    """Call an Orivale `x402` endpoint directly with optional `PAYMENT-SIGNATURE` header."""
    qs = urllib.parse.urlencode(params)
    url = f"{base_url.rstrip('/')}{path}" + (f"?{qs}" if qs else "")
    hdrs = {"Accept": "application/json", "User-Agent": "orivale-x402-client/1.3.0"}
    if payment_signature.strip():
        hdrs["PAYMENT-SIGNATURE"] = payment_signature.strip()
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers=hdrs, method="GET")
    with urllib.request.urlopen(req, context=ctx, timeout=25.0) as resp:
        return json.loads(resp.read().decode("utf-8", "replace"))


class OrivaleCrewAITools:
    """Zero-dependency tool callables compatible with CrewAI `@tool`, LangChain `StructuredTool`, and AutoGen."""

    @staticmethod
    def clean_markdown(url: str, x402_payment: str = "") -> str:
        """Extract clean RAG-ready Markdown, title, and pricing entities from any public URL."""
        res = call_orivale_mcp_tool("orivale_clean_markdown", {"url": url, "x402_payment": x402_payment})
        return json.dumps(res, ensure_ascii=False)

    @staticmethod
    def b2b_domain_enrich(domain: str, x402_payment: str = "") -> str:
        """Enrich a company domain with tech-stack signals, ICP fit score, and 2-line outbound icebreaker."""
        res = call_orivale_mcp_tool("orivale_b2b_domain_enrich", {"domain": domain, "x402_payment": x402_payment})
        return json.dumps(res, ensure_ascii=False)

    @staticmethod
    def shopify_competitor(domain: str, x402_payment: str = "") -> str:
        """Analyze a Shopify storefront's SKU pricing distribution, markdown %, and ad counter-angles."""
        res = call_orivale_mcp_tool("orivale_shopify_competitor", {"domain": domain, "x402_payment": x402_payment})
        return json.dumps(res, ensure_ascii=False)

    @staticmethod
    def base_contract_audit(address: str) -> str:
        """Audit a Base Mainnet (eip155:8453) smart contract or relayer wallet for bytecode, nonce, and USDC."""
        res = call_orivale_mcp_tool("orivale_base_contract_audit", {"address": address})
        return json.dumps(res, ensure_ascii=False)
