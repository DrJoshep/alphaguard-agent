from .models import MarketSnapshot, Scenario


def build_scenarios(snapshots: list[MarketSnapshot]) -> list[Scenario]:
    avg_momentum = sum(x.momentum for x in snapshots) / len(snapshots) if snapshots else 0
    avg_vol = sum(x.volatility for x in snapshots) / len(snapshots) if snapshots else 0

    return [
        Scenario(
            label="BULLISH",
            description="Momentum remains positive while volatility stays controlled and volume confirms participation.",
            triggers=[
                "Average momentum > +0.75",
                "No major asset shows a sharp momentum reversal",
                "Volume regime is normal/high",
            ],
        ),
        Scenario(
            label="NEUTRAL",
            description="Markets remain mixed or range-bound; no broad directional confirmation is present.",
            triggers=[
                "-0.75 ≤ average momentum ≤ +0.75",
                "Volatility remains contained",
                "Mixed asset-level signals",
            ],
        ),
        Scenario(
            label="BEARISH",
            description="Momentum deteriorates, volatility expands, or broad participation weakens.",
            triggers=[
                "Average momentum < -0.75",
                "Average volatility > 10",
                "Multiple holdings enter high-volatility conditions",
            ],
        ),
    ]
