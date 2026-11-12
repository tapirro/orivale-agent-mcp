#!/usr/bin/env python3
"""Zero-dependency stdio MCP bridge to https://ori.mantissa.id/mcp (x402 + Apify Dual-Rail)."""

from __future__ import annotations

import json
import os
import ssl
import sys
import urllib.request
from typing import Any

DEFAULT_MCP_URL = "https://ori.mantissa.id/mcp"


def _forward_rpc(payload: dict[str, Any], endpoint: str) -> dict[str, Any] | None:
    method = str(payload.get("method") or "")
    if method.startswith("notifications/"):
        return None
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "orivale-mcp-stdio/1.2.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, context=ctx, timeout=25.0) as resp:
        raw = resp.read().decode("utf-8", "replace").strip()
        return json.loads(raw) if raw else None


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
            reply = _forward_rpc(msg, endpoint)
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
