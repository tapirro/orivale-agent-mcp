"""End-to-end offline stdio pipe & SSRF validation tests for `orivale-mcp`."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "PYTHONUNBUFFERED": "1"}


class TestOrivaleMcpServer(unittest.TestCase):
    def test_interactive_pipe_handshake_without_eof(self) -> None:
        """Verify `server.py` answers `initialize` and `tools/list` immediately over a live open pipe."""
        proc = subprocess.Popen(
            [sys.executable, "-m", "orivale_mcp.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=ENV,
        )
        assert proc.stdin is not None and proc.stdout is not None
        try:
            init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}}
            proc.stdin.write((json.dumps(init_req) + "\n").encode("utf-8"))
            proc.stdin.flush()
            init_resp = json.loads(proc.stdout.readline().decode("utf-8"))
            self.assertEqual(init_resp["result"]["serverInfo"]["version"], "1.4.0")
            self.assertIn("tools", init_resp["result"]["capabilities"])
            self.assertIn("resources", init_resp["result"]["capabilities"])
            self.assertIn("prompts", init_resp["result"]["capabilities"])

            proc.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
            proc.stdin.write(b'{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}\n')
            proc.stdin.flush()
            tools_resp = json.loads(proc.stdout.readline().decode("utf-8"))
            tools = tools_resp["result"]["tools"]
            self.assertEqual(len(tools), 8)
            for t in tools:
                self.assertIn("annotations", t)
                self.assertFalse(t["inputSchema"].get("additionalProperties", True))

            # SSRF guard must reject private metadata IPs locally without touching network
            ssrf_req = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "orivale_clean_markdown", "arguments": {"url": "https://169.254.169.254/latest"}},
            }
            proc.stdin.write((json.dumps(ssrf_req) + "\n").encode("utf-8"))
            proc.stdin.flush()
            ssrf_resp = json.loads(proc.stdout.readline().decode("utf-8"))
            self.assertTrue(ssrf_resp["result"]["isError"])
        finally:
            proc.stdin.close()
            proc.stdout.close()
            if proc.stderr is not None:
                proc.stderr.close()
            proc.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
