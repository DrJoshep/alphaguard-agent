from __future__ import annotations

from math import sqrt

from .models import MarketSnapshot, Position


def portfolio_weights(
    positions: list[Position], prices: dict[str, float]
) -> tuple[float, dict[str, float]]:
    values = {p.symbol: p.quantity * prices.get(p.symbol, 0.0) for p in positions}
    total = sum(values.values())
    if total <= 0:
        return 0.0, {k: 0.0 for k in values}
    return total, {k: v / total for k, v in values.items()}


def concentration_score(weights: dict[str, float]) -> float:
    if not weights:
        return 0.0
    hhi = sum(w * w for w in weights.values())
    # HHI=1 means one asset; lower is more diversified.
    return min(100.0, hhi * 100.0)


def risk_score(snapshots: list[MarketSnapshot], weights: dict[str, float]) -> float:
    concentration = concentration_score(weights)

    weighted_vol = 0.0
    weighted_negative_momentum = 0.0
    for s in snapshots:
        w = weights.get(s.symbol, 0.0)
        weighted_vol += w * min(s.volatility, 20.0)
        weighted_negative_momentum += w * max(-s.momentum, 0.0)

    # Explainable 0–100 heuristic, not a prediction model.
    score = 35.0
    score += concentration * 0.35
    score += min(weighted_vol * 2.0, 20.0)
    score += min(weighted_negative_momentum * 4.0, 15.0)
    return max(0.0, min(100.0, score))


def regime(snapshots: list[MarketSnapshot]) -> str:
    if not snapshots:
        return "neutral"
    avg = sum(x.momentum for x in snapshots) / len(snapshots)
    vol = sum(x.volatility for x in snapshots) / len(snapshots)
    if avg > 0.75 and vol < 6:
        return "bullish"
    if avg < -0.75 or vol > 10:
        return "bearish"
    return "neutral"
