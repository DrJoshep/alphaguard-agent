from alphaguard.models import MarketSnapshot
from alphaguard.scenarios import build_scenarios


def test_three_scenarios():
    s = MarketSnapshot(
        symbol="BTCUSDT",
        price=100,
        change_24h=2,
        quote_volume_24h=1,
        momentum=1,
        volatility=2,
        volume_regime="normal",
    )
    scenarios = build_scenarios([s])
    assert [x.label for x in scenarios] == ["BULLISH", "NEUTRAL", "BEARISH"]
