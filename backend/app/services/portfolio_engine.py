from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException

async def generate_portfolio_transaction(user_id: str, model_id: int, total_investment: float, db: AsyncSession):
    try:
        # 1. Deactivate old portfolios
        await db.execute(
            text("UPDATE user_portfolios SET is_active = FALSE WHERE user_id = :user_id AND is_active = TRUE;"),
            {"user_id": user_id}
        )

        # 2. Insert new portfolio (DB trigger fires here → writes audit_log)
        result = await db.execute(
            text("""
            INSERT INTO user_portfolios (user_id, model_id, total_investment, is_active, version)
            VALUES (
                :user_id, :model_id, :total_investment, TRUE,
                COALESCE((SELECT MAX(version) FROM user_portfolios WHERE user_id = :user_id), 0) + 1
            ) RETURNING portfolio_id;
            """),
            {"user_id": user_id, "model_id": model_id, "total_investment": total_investment}
        )
        portfolio_id = result.scalar()

        # 3. Insert all instrument positions
        await db.execute(
            text("""
            INSERT INTO user_portfolio_positions
                (portfolio_id, instrument_id, allocation_percentage, allocated_amount)
            SELECT
                :portfolio_id,
                ia.instrument_id,
                ROUND(pa.allocation_percentage * ia.allocation_percentage / 100, 2),
                ROUND(:total_investment * pa.allocation_percentage * ia.allocation_percentage / 10000, 2)
            FROM portfolio_allocations pa
            JOIN sub_allocation_templates sat
                ON sat.model_id = pa.model_id AND sat.asset_class_id = pa.asset_class_id
            JOIN instrument_allocations ia ON ia.template_id = sat.template_id
            WHERE pa.model_id = :model_id;
            """),
            {"portfolio_id": portfolio_id, "model_id": model_id, "total_investment": total_investment}
        )

        # Store a monthly fact row for analytics after all positions exist.
        await db.execute(
            text("""
            INSERT INTO fact_monthly_portfolio_snapshots
                (user_id, snapshot_month, portfolio_id, portfolio_value, asset_class_count, largest_allocation_pct)
            SELECT :user_id, date_trunc('month', CURRENT_DATE)::date, :portfolio_id,
                   :total_investment, COUNT(DISTINCT i.asset_class_id),
                   COALESCE(MAX(upp.allocation_percentage), 0)
            FROM user_portfolio_positions upp
            JOIN instruments i ON i.instrument_id = upp.instrument_id
            WHERE upp.portfolio_id = :portfolio_id
            ON CONFLICT (user_id, snapshot_month) DO UPDATE SET
                portfolio_id = EXCLUDED.portfolio_id,
                portfolio_value = EXCLUDED.portfolio_value,
                asset_class_count = EXCLUDED.asset_class_count,
                largest_allocation_pct = EXCLUDED.largest_allocation_pct,
                created_at = NOW();
            """),
            {"user_id": user_id, "portfolio_id": portfolio_id, "total_investment": total_investment}
        )

        # CRITICAL: commit the full ACID transaction
        await db.commit()
        return portfolio_id

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Portfolio generation failed: {str(e)}")
