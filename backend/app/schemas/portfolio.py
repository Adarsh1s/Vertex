from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PortfolioSummary(BaseModel):
    user_id: str
    user_name: Optional[str] = None
    portfolio_id: int
    version: int
    is_active: bool
    total_investment: float
    generated_at: datetime
    model_name: str
    risk_profile: str
    asset_class: str
    instrument_id: int
    instrument_name: str
    ticker: Optional[str] = None
    instrument_type: Optional[str] = None
    allocation_percentage: float
    allocated_amount: float

    class Config:
        from_attributes = True

class PortfolioResponse(BaseModel):
    portfolio_id: int
    model_name: str
    risk_profile: str
    total_investment: float
    version: int
    generated_at: datetime
    positions: List[PortfolioSummary]

class PortfolioGenerateRequest(BaseModel):
    pass
