from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter()

@router.get("/instruments")
async def get_instruments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT i.instrument_id, i.name, i.ticker, i.instrument_type, i.fund_house, ac.name as asset_class
        FROM instruments i
        JOIN asset_classes ac ON i.asset_class_id = ac.asset_class_id
        WHERE i.is_active = TRUE
    """))
    return result.mappings().all()

@router.get("/risk-profiles")
async def get_risk_profiles(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT * FROM risk_profiles"))
    return result.mappings().all()

@router.get("/portfolio-models")
async def get_portfolio_models(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("""
        SELECT pm.model_id, pm.model_name, pm.description, rp.profile_name as risk_profile
        FROM portfolio_models pm
        JOIN risk_profiles rp ON pm.risk_profile_id = rp.risk_profile_id
    """))
    return result.mappings().all()
