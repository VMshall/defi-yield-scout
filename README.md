# DeFi Yield Scout

DeFi yield strategy scout — AI-powered yield opportunities with risk-adjusted rankings.

## Problem

DeFi yield opportunities are fragmented across 50+ protocols, making it hard to compare risk-adjusted returns. Investors need to evaluate lending, LP, staking, and vault strategies with proper risk context.

## Solution

Enter a token, amount, and risk tolerance to get AI-curated yield strategies with:
- Protocol type breakdown (lending, LP, staking, vaults)
- APY ranges and risk levels
- Strategy descriptions with key risks
- Risk-adjusted recommendations ranked by score

## Stack

- **Backend**: FastAPI + Anthropic Claude claude-opus-4-6
- **Frontend**: Single-file HTML/JS with Tailwind CSS

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
uvicorn src.api:app --reload
```

Then open http://localhost:8000

## API

`POST /api/scout` — Get yield strategies for a token

```json
{
  "token": "ETH",
  "amount": 10.0,
  "risk_tolerance": "medium"
}
```

Response includes `strategies` array with `protocol`, `apy_range`, `risk_level`, `description`, `risk_adjusted_score`, and `recommendation`.
