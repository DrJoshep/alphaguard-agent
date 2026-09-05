from alphaguard.models import MarketSnapshot, Position
from alphaguard.risk import concentration_score, portfolio_weights, risk_score


def snap(symbol, momentum=0, volatility=2):
    return MarketSnapshot(
        symbol=symbol,
        price=100,
        change_24h=0,
        quote_volume_24h=1_000_000,
        momentum=momentum,
        volatility=volatility,
        volume_regime="normal",
    )


def test_weights_sum_to_one():
    total, weights = portfolio_weights(
        [Position(symbol="BTCUSDT", quantity=1), Position(symbol="ETHUSDT", quantity=2)],
        {"BTCUSDT": 100, "ETHUSDT": 50},
    )
    assert total == 200
    assert abs(sum(weights.values()) - 1) < 1e-9


def test_concentration():
    assert concentration_score({"BTCUSDT": 1.0}) == 100
    assert concentration_score({"BTCUSDT": 0.5, "ETHUSDT": 0.5}) == 50


def test_risk_is_bounded():
    value = risk_score([snap("BTCUSDT", -4, 20)], {"BTCUSDT": 1})
    assert 0 <= value <= 100
