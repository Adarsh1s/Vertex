from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.profile import UserProfile
from app.schemas.profile import QuestionnaireSubmit
from app.services.risk_engine import calculate_risk_score, get_risk_profile_from_db

router = APIRouter()

@router.post("/submit")
async def submit_questionnaire(
    submission: QuestionnaireSubmit,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if len(submission.answers) != 7:
        raise HTTPException(status_code=400, detail="Must provide exactly 7 answers")

    score = await calculate_risk_score(submission.answers)
    profile_id = await get_risk_profile_from_db(score, db)

    await db.execute(
        update(UserProfile)
        .where(UserProfile.user_id == user_id)
        .values(
            risk_score=score,
            risk_profile_id=profile_id
        )
    )
    await db.commit()

    return {
        "message": "Questionnaire submitted successfully",
        "risk_score": score,
        "risk_profile_id": profile_id
    }
