"""
DeFi yield strategy scout powered by Claude.
Analyzes yield opportunities across lending, LP, staking, and vault protocols.
"""

import json
import os
from typing import Any

import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SCOUT_SYSTEM_PROMPT = """You are an expert DeFi analyst and yield strategist with deep knowledge of:
- Lending protocols (Aave, Compound, Morpho, Spark)
- Liquidity pools and AMMs (Uniswap v3, Curve, Balancer, Velodrome)
- Liquid staking and restaking (Lido, Rocket Pool, EigenLayer, Pendle)
- Yield vaults and aggregators (Yearn, Convex, Beefy, Sommelier)
- Newer high-yield opportunities (real yield protocols, delta-neutral strategies)

You provide realistic, current APY estimates based on historical data and protocol mechanics.
You are honest about risks: smart contract risk, impermanent loss, liquidation risk, depeg risk, etc.
You do NOT make up protocols — only reference established, real protocols."""

RISK_LEVELS = {
    "conservative": "Prioritize capital preservation. Max smart contract risk tolerance. Avoid impermanent loss. Stick to blue-chip assets and battle-tested protocols.",
    "medium": "Balance yield and risk. Accept moderate impermanent loss and some protocol risk. Diversify across strategy types.",
    "aggressive": "Maximize yield. Accept higher impermanent loss, newer protocols, leverage opportunities. Full risk spectrum."
}


def scout_yield_strategies(token: str, amount: float, risk_tolerance: str) -> dict[str, Any]:
    """
    Scout DeFi yield strategies for a given token and risk profile.

    Args:
        token: Token symbol (e.g., ETH, USDC, BTC)
        amount: Amount of tokens to deploy
        risk_tolerance: 'conservative', 'medium', or 'aggressive'

    Returns:
        Dict with strategies array and overall recommendation
    """
    risk_profile = RISK_LEVELS.get(risk_tolerance, RISK_LEVELS["medium"])

    prompt = f"""Analyze yield strategies for the following DeFi position:

Token: {token}
Amount: {amount} {token}
Risk Tolerance: {risk_tolerance}
Risk Profile: {risk_profile}

Generate 5-7 concrete yield strategies across different protocol types.
For each strategy, calculate a risk_adjusted_score from 1-10 where:
- Score = (estimated_mid_apy / max_category_risk_penalty) normalized to 1-10
- Higher score = better risk-adjusted return for this investor's risk profile

Return ONLY valid JSON with this exact structure:
{{
  "strategies": [
    {{
      "protocol": "string - protocol name (e.g., Aave v3, Curve 3pool)",
      "protocol_type": "string - one of: lending, liquidity_pool, staking, vault, restaking",
      "apy_range": "string - e.g., '4.2% - 5.8%'",
      "apy_low": number,
      "apy_high": number,
      "risk_level": "string - one of: low, medium, high, very_high",
      "description": "string - 2-3 sentence strategy explanation",
      "key_risks": ["string array of 2-3 main risks"],
      "risk_adjusted_score": number between 1 and 10,
      "recommendation": "string - specific action for this investor profile"
    }}
  ],
  "top_pick": "string - name of the recommended strategy",
  "summary": "string - 2-3 sentence overall assessment for this token/amount/risk combo",
  "disclaimer": "DeFi carries significant risks. This is not financial advice. Always do your own research."
}}

Rank strategies by risk_adjusted_score descending. Be realistic with APY ranges."""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=3000,
        system=SCOUT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()

    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    result = json.loads(response_text)

    # Normalize and validate
    strategies = []
    for s in result.get("strategies", []):
        strategies.append({
            "protocol": s.get("protocol", "Unknown"),
            "protocol_type": s.get("protocol_type", "other"),
            "apy_range": s.get("apy_range", "N/A"),
            "apy_low": float(s.get("apy_low", 0)),
            "apy_high": float(s.get("apy_high", 0)),
            "risk_level": s.get("risk_level", "medium"),
            "description": s.get("description", ""),
            "key_risks": s.get("key_risks", []),
            "risk_adjusted_score": float(s.get("risk_adjusted_score", 5)),
            "recommendation": s.get("recommendation", "")
        })

    # Sort by risk_adjusted_score descending
    strategies.sort(key=lambda x: x["risk_adjusted_score"], reverse=True)

    return {
        "token": token.upper(),
        "amount": amount,
        "risk_tolerance": risk_tolerance,
        "strategies": strategies,
        "top_pick": result.get("top_pick", strategies[0]["protocol"] if strategies else ""),
        "summary": result.get("summary", ""),
        "disclaimer": result.get("disclaimer", "DeFi carries significant risks. This is not financial advice.")
    }
