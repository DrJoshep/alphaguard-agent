import pytest

from alphaguard.agent import AlphaGuardAgent
from alphaguard.config import Settings
from alphaguard.models import Position


class FakeClient:
    async def ticker_24h(self, symbol):
        return {
            "lastPrice": "100",
            "priceChangePercent": "2.0",
            "quoteVolume": "1000000",
        }

    async def klines(self, symbol, interval="1h", limit=24):
        rows = []
        for i in range(24):
            price = 100 + i * 0.2
            rows.append([0, 0, 0, 0, price, 0, 0, 1000, 0, 0, 0, 0])
        return rows


@pytest.mark.asyncio
async def test_agent_builds_report():
    agent = AlphaGuardAgent(FakeClient(), Settings())
    report = await agent.analyze(
        [Position(symbol="BTCUSDT", quantity=1)],
        ["BTCUSDT"],
    )
    assert report.portfolio_value == 100
    assert len(report.scenarios) == 3
    assert report.risk_score >= 0
