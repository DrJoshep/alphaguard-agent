import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    binance_base_url: str = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
    agent_os_mcp_url: str = os.getenv(
        "BINANCE_AGENT_OS_MCP_URL", "https://agent.binance.com/mcp/agentic"
    )
    agent_os_bearer_token: str = os.getenv("BINANCE_AGENT_OS_BEARER_TOKEN", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5-mini")
