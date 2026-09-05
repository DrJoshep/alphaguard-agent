from __future__ import annotations

import statistics

from .binance import BinancePublicClient
from .config import Settings
from .llm import generate_narrative
from .models import AgentReport, MarketSnapshot, Position
from .risk import portfolio_weights, regime, risk_score
from .scenarios import build_scenarios


def _momentum(closes: list[float]) -> float:
    if len(closes) < 2 or closes[0] == 0:
        return 0.0
    # Normalized return expressed as a small score.
    pct = (closes[-1] / closes[0] - 1) * 100
    return max(-5.0, min(5.0, pct))


def _volatility(closes: list[float]) -> float:
    if len(closes) < 3:
        return 0.0
    returns = [
        (closes[i] / closes[i - 1] - 1) * 100
        for i in range(1, len(closes))
        if closes[i - 1]
    ]
    if len(returns) < 2:
        return 0.0
    return statistics.pstdev(returns) * (24 ** 0.5)


class AlphaGuardAgent:
    def __init__(self, client: BinancePublicClient, settings: Settings):
        self.client = client
        self.settings = settings

    async def _snapshot(self, symbol: str) -> MarketSnapshot:
        ticker, klines = await self._fetch(symbol)
        closes = [float(k[4]) for k in klines]
        quote_vol = float(ticker["quoteVolume"])
        avg_vol = statistics.mean(float(k[7]) for k in klines) if klines else 0
        current_vol = float(klines[-1][7]) if klines else 0
        ratio = current_vol / avg_vol if avg_vol else 1

        if ratio > 1.4:
            volume_regime = "high"
        elif ratio < 0.7:
            volume_regime = "low"
        else:
            volume_regime = "normal"

        return MarketSnapshot(
            symbol=symbol.upper(),
            price=float(ticker["lastPrice"]),
            change_24h=float(ticker["priceChangePercent"]),
            quote_volume_24h=quote_vol,
            momentum=_momentum(closes),
            volatility=_volatility(closes),
            volume_regime=volume_regime,
        )

    async def _fetch(self, symbol: str):
        import asyncio
        return await asyncio.gather(
            self.client.ticker_24h(symbol),
            self.client.klines(symbol, "1h", 24),
        )

    async def analyze(self, positions: list[Position], symbols: list[str]) -> AgentReport:
        snapshots = [await self._snapshot(s) for s in symbols]
        prices = {x.symbol: x.price for x in snapshots}
        total, weights = portfolio_weights(positions, prices)

        portfolio_return = 0.0
        for p in positions:
            snap = next((x for x in snapshots if x.symbol == p.symbol), None)
            if snap:
                portfolio_return += weights.get(p.symbol, 0) * snap.change_24h

        score = risk_score(snapshots, weights)
        market_regime = regime(snapshots)
        scenarios = build_scenarios(snapshots)

        findings = []
        if weights:
            largest = max(weights.items(), key=lambda x: x[1])
            findings.append(
                f"Largest concentration is {largest[0].replace('USDT','')}: "
                f"{largest[1] * 100:.1f}% of marked portfolio value."
            )
        high_vol = [x.symbol.replace("USDT", "") for x in snapshots if x.volatility >= 10]
        if high_vol:
            findings.append("High-volatility assets detected: " + ", ".join(high_vol) + ".")
        else:
            findings.append("No analyzed asset currently exceeds the high-volatility threshold.")
        positive = [x.symbol.replace("USDT", "") for x in snapshots if x.momentum > 0.75]
        negative = [x.symbol.replace("USDT", "") for x in snapshots if x.momentum < -0.75]
        findings.append(
            f"Momentum leaders: {', '.join(positive) if positive else 'none'}; "
            f"weakest momentum: {', '.join(negative) if negative else 'none'}."
        )

        facts = {
            "portfolio_value": round(total, 2),
            "portfolio_return_24h": round(portfolio_return, 2),
            "risk_score": round(score, 1),
            "regime": market_regime,
            "findings": findings,
            "assets": [x.model_dump() for x in snapshots],
        }

        summary = (
            f"Current regime is {market_regime}. Portfolio marked value is "
            f"${total:,.2f}, with a 24h return proxy of {portfolio_return:+.2f}%. "
            f"Risk score is {score:.0f}/100. The agent sees this as a scenario analysis, "
            f"not a prediction."
        )

        llm_text = generate_narrative(
            facts, self.settings.openai_api_key, self.settings.openai_model
        )
        if llm_text:
            summary = llm_text

        watch_conditions = [
            "Re-run analysis if the dominant holding moves sharply or its 1h momentum reverses.",
            "Re-check if average volatility expands above the bearish scenario threshold.",
            "Treat a change from normal to high volume as a confirmation signal, not as proof of direction.",
        ]

        return AgentReport(
            portfolio_value=total,
            portfolio_return_24h=portfolio_return,
            risk_score=score,
            regime=market_regime,
            summary=summary,
            findings=findings,
            assets=snapshots,
            scenarios=scenarios,
            watch_conditions=watch_conditions,
        )
