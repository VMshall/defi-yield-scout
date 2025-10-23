"""
FastAPI application for DeFi Yield Scout.
Serves the frontend and exposes yield scouting API.
"""

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

from .scout import scout_yield_strategies

app = FastAPI(
    title="DeFi Yield Scout API",
    description="DeFi yield strategy scout — AI-powered yield opportunities with risk-adjusted rankings",
    version="1.0.0"
)

frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


class ScoutRequest(BaseModel):
    token: str
    amount: float
    risk_tolerance: Literal["conservative", "medium", "aggressive"] = "medium"

    @field_validator("token")
    @classmethod
    def token_must_be_valid(cls, v: str) -> str:
        v = v.strip().upper()
        if not v or len(v) > 10:
            raise ValueError("Token symbol must be 1-10 characters")
        return v

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v


class Strategy(BaseModel):
    protocol: str
    protocol_type: str
    apy_range: str
    apy_low: float
    apy_high: float
    risk_level: str
    description: str
    key_risks: list[str]
    risk_adjusted_score: float
    recommendation: str


class ScoutResponse(BaseModel):
    token: str
    amount: float
    risk_tolerance: str
    strategies: list[Strategy]
    top_pick: str
    summary: str
    disclaimer: str


@app.get("/")
async def serve_frontend():
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "DeFi Yield Scout API running. Frontend not found."}


@app.post("/api/scout", response_model=ScoutResponse)
async def scout_yields(request: ScoutRequest):
    """
    Scout DeFi yield strategies for a given token, amount, and risk tolerance.
    Returns strategies ranked by risk-adjusted score.
    """
    try:
        result = scout_yield_strategies(
            token=request.token,
            amount=request.amount,
            risk_tolerance=request.risk_tolerance
        )
        return ScoutResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scouting failed: {str(e)}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "defi-yield-scout"}
