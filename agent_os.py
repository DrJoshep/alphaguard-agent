from __future__ import annotations

import json
from typing import Any

import httpx


class AgentOSMCPClient:
    """
    Minimal Streamable HTTP MCP client.

    It is intentionally generic: authentication and tool permissions are supplied
    by the user/environment rather than hard-coded into the application.
    """

    def __init__(self, url: str, bearer_token: str = "", timeout: float = 20.0):
        self.url = url
        self.bearer_token = bearer_token
        self.timeout = timeout
        self.session_id: str | None = None
        self.request_id = 0

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        return headers

    @staticmethod
    def _parse_response(response: httpx.Response) -> dict[str, Any]:
        ctype = response.headers.get("content-type", "")
        if "text/event-stream" not in ctype:
            return response.json()

        # MCP servers may return SSE frames. Keep the parser intentionally small:
        # consume the last JSON data event.
        last = None
        for line in response.text.splitlines():
            if line.startswith("data:"):
                payload = line[5:].strip()
                if payload:
                    try:
                        last = json.loads(payload)
                    except json.JSONDecodeError:
                        pass
        if last is None:
            raise RuntimeError("MCP SSE response contained no JSON data event")
        return last

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.url, headers=self._headers(), json=payload)
            response.raise_for_status()
            if "mcp-session-id" in response.headers:
                self.session_id = response.headers["mcp-session-id"]
            return self._parse_response(response)

    def initialize(self) -> dict[str, Any]:
        self.request_id += 1
        return self._post({
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "alphaguard", "version": "0.1.0"},
            },
        })

    def list_tools(self) -> dict[str, Any]:
        self.request_id += 1
        return self._post({
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/list",
            "params": {},
        })

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        self.request_id += 1
        return self._post({
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        })
