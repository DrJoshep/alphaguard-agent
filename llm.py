from __future__ import annotations

import json


def generate_narrative(report_facts: dict, api_key: str, model: str) -> str | None:
    """Optional LLM narration. Quantitative facts remain the source of truth."""
    if not api_key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

    client = OpenAI(api_key=api_key)
    prompt = f"""
You are AlphaGuard, a cautious crypto market analyst.
Turn the structured facts below into a concise portfolio-risk briefing.

Rules:
- Do not claim certainty or guaranteed returns.
- Do not invent prices or facts.
- Do not issue a direct buy/sell instruction.
- Clearly distinguish observed facts from scenarios.
- Mention the most important invalidation condition.
- Keep it under 180 words.

FACTS:
{json.dumps(report_facts, indent=2)}
"""
    response = client.responses.create(model=model, input=prompt)
    return response.output_text.strip()
