from typing import Literal

from pydantic import BaseModel, Field


class Position(BaseModel):
    symbol: str
    quantity: float = Field(ge=0)


class MarketSnapshot(BaseModel):
    symbol: str
    price: float
    change_24h: float
    quote_volume_24h: float
    momentum: float
    volatility: float
    volume_regime: Literal["low", "normal", "high"]


class Scenario(BaseModel):
    label: Literal["BULLISH", "NEUTRAL", "BEARISH"]
    description: str
    triggers: list[str]


class AgentReport(BaseModel):
    portfolio_value: float
    portfolio_return_24h: float
    risk_score: float
    regime: Literal["bullish", "neutral", "bearish"]
    summary: str
    findings: list[str]
    assets: list[MarketSnapshot]
    scenarios: list[Scenario]
    watch_conditions: list[str]
