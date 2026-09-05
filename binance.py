from __future__ import annotations

import httpx


class BinancePublicClient:
    """Read-only public Binance market-data adapter."""

    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def ticker_24h(self, symbol: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self.base_url}/api/v3/ticker/24hr",
                params={"symbol": symbol.upper()},
            )
            r.raise_for_status()
            return r.json()

    async def klines(self, symbol: str, interval: str = "1h", limit: int = 24) -> list:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self.base_url}/api/v3/klines",
                params={"symbol": symbol.upper(), "interval": interval, "limit": limit},
            )
            r.raise_for_status()
            return r.json()
