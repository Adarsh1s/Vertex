from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.profile import UserProfile
from app.models.portfolio import PortfolioModel
from app.schemas.portfolio import PortfolioGenerateRequest, PortfolioResponse, PortfolioSummary
from app.services.portfolio_engine import generate_portfolio_transaction

router = APIRouter()

@router.post("/generate", response_model=PortfolioResponse)
async def generate_portfolio(
    request: PortfolioGenerateRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    
    if not profile or not profile.risk_profile_id or not profile.investment_amount:
        raise HTTPException(status_code=400, detail="Incomplete user profile. Complete onboarding and questionnaire first.")

    model_result = await db.execute(select(PortfolioModel).where(PortfolioModel.risk_profile_id == profile.risk_profile_id))
    model = model_result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=400, detail="No portfolio model found for this risk profile.")

    portfolio_id = await generate_portfolio_transaction(
        user_id=user_id,
        model_id=model.model_id,
        total_investment=float(profile.investment_amount),
        db=db
    )
    
    return await get_current_portfolio(user_id, db)

@router.get("/current", response_model=PortfolioResponse)
async def get_current_portfolio(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text("SELECT * FROM user_portfolio_summary WHERE user_id = :user_id AND is_active = TRUE"),
        {"user_id": user_id}
    )
    rows = result.mappings().all()

    if not rows:
        raise HTTPException(status_code=404, detail="No active portfolio found")
    
    positions = [PortfolioSummary(**row) for row in rows]
    first = positions[0]
    
    return PortfolioResponse(
        portfolio_id=first.portfolio_id,
        model_name=first.model_name,
        risk_profile=first.risk_profile,
        total_investment=first.total_investment,
        version=first.version,
        generated_at=first.generated_at,
        positions=positions
    )

@router.get("/history")
async def get_portfolio_history(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text("""
            SELECT portfolio_id, version, total_investment, is_active, generated_at, model_name 
            FROM user_portfolios up
            JOIN portfolio_models pm ON up.model_id = pm.model_id
            WHERE up.user_id = :user_id
            ORDER BY version DESC
        """),
        {"user_id": user_id}
    )
    return result.mappings().all()

@router.get("/summary")
async def get_portfolio_summary(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text("""
        SELECT asset_class, SUM(allocation_percentage) as total_percentage, SUM(allocated_amount) as total_amount
        FROM user_portfolio_summary
        WHERE user_id = :user_id AND is_active = TRUE
        GROUP BY asset_class
        """),
        {"user_id": user_id}
    )
    return result.mappings().all()

@router.get("/expected-returns")
async def get_expected_returns(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text("""
        WITH w_ret AS (
            SELECT
                ups.instrument_id,
                ups.allocation_percentage,
                ir.period,
                ir.return_percentage
            FROM user_portfolio_summary ups
            JOIN instrument_returns ir ON ups.instrument_id = ir.instrument_id
            WHERE ups.user_id = :user_id AND ups.is_active = TRUE
        )
        SELECT
            period,
            SUM(allocation_percentage * return_percentage / 100) AS blended_return
        FROM w_ret
        GROUP BY period
        ORDER BY period
        """),
        {"user_id": user_id}
    )
    return result.mappings().all()

@router.get("/compare/{risk_level}")
async def compare_portfolio(
    risk_level: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text("""
        SELECT 
            pm.model_name,
            ac.name as asset_class,
            SUM(pa.allocation_percentage) as allocation_percentage
        FROM portfolio_models pm
        JOIN risk_profiles rp ON pm.risk_profile_id = rp.risk_profile_id
        JOIN portfolio_allocations pa ON pm.model_id = pa.model_id
        JOIN asset_classes ac ON pa.asset_class_id = ac.asset_class_id
        WHERE rp.profile_name ILIKE :risk_level
        GROUP BY pm.model_name, ac.name
        """),
        {"risk_level": "%" + risk_level + "%"}
    )
    return result.mappings().all()
