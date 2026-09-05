import asyncio
import os
from datetime import datetime, timezone

import streamlit as st
from dotenv import load_dotenv

from alphaguard.agent import AlphaGuardAgent
from alphaguard.binance import BinancePublicClient
from alphaguard.config import Settings
from alphaguard.models import Position

load_dotenv()

st.set_page_config(
    page_title="AlphaGuard | Binance Agent OS",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ AlphaGuard")
st.caption("Explainable crypto portfolio intelligence — Binance Agent OS Track A")

with st.sidebar:
    st.header("Portfolio")
    btc = st.number_input("BTC", min_value=0.0, value=0.35, step=0.01)
    eth = st.number_input("ETH", min_value=0.0, value=2.5, step=0.1)
    bnb = st.number_input("BNB", min_value=0.0, value=8.0, step=1.0)
    sol = st.number_input("SOL", min_value=0.0, value=20.0, step=1.0)

    symbols = st.multiselect(
        "Analyze symbols",
        ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT"],
        default=["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"],
    )

    analyze = st.button("🔍 Analyze portfolio", type="primary", use_container_width=True)

positions = [
    Position(symbol="BTCUSDT", quantity=btc),
    Position(symbol="ETHUSDT", quantity=eth),
    Position(symbol="BNBUSDT", quantity=bnb),
    Position(symbol="SOLUSDT", quantity=sol),
]

settings = Settings()
client = BinancePublicClient(settings.binance_base_url)
agent = AlphaGuardAgent(client=client, settings=settings)

if analyze or "report" not in st.session_state:
    with st.spinner("Agent is collecting market context and building the risk brief..."):
        try:
            report = asyncio.run(agent.analyze(positions, symbols))
            st.session_state.report = report
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
            st.stop()

report = st.session_state.report

m1, m2, m3, m4 = st.columns(4)
m1.metric("Portfolio value", f"${report.portfolio_value:,.2f}")
m2.metric("24h P/L proxy", f"{report.portfolio_return_24h:+.2f}%")
m3.metric("Risk score", f"{report.risk_score:.0f}/100")
m4.metric("Regime", report.regime.upper())

st.divider()

left, right = st.columns([1.3, 1])

with left:
    st.subheader("Agent brief")
    st.write(report.summary)

    st.subheader("Key findings")
    for finding in report.findings:
        st.markdown(f"- {finding}")

    st.subheader("Market snapshot")
    rows = []
    for x in report.assets:
        rows.append({
            "Asset": x.symbol.replace("USDT", ""),
            "Price": f"${x.price:,.4f}",
            "24h": f"{x.change_24h:+.2f}%",
            "Momentum": f"{x.momentum:+.2f}",
            "Volatility": f"{x.volatility:.2f}",
            "Volume regime": x.volume_regime,
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

with right:
    st.subheader("Scenarios")
    for scenario in report.scenarios:
        with st.container(border=True):
            st.markdown(f"**{scenario.label}**")
            st.write(scenario.description)
            st.caption("Triggers: " + " · ".join(scenario.triggers))

    st.subheader("Watch conditions")
    for condition in report.watch_conditions:
        st.info(condition)

    st.subheader("Safety boundary")
    st.success("READ-ONLY MODE — no orders or withdrawals are executed.")

st.divider()
st.subheader("Audit trail")
st.caption(
    f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} · "
    f"facts → risk engine → scenarios → optional LLM narrative"
)

with st.expander("Structured agent output"):
    st.json(report.model_dump())
