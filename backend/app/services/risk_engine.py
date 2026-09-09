from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

async def calculate_risk_score(answers: list[int]) -> int:
    score = sum(answers)
    return min(score, 100)

async def get_risk_profile_from_db(score: int, db: AsyncSession) -> int:
    result = await db.execute(
        text("SELECT get_risk_profile_id(:score)"),
        {"score": score}
    )
    return result.scalar()
