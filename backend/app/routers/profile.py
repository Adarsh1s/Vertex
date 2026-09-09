from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.profile import UserProfile, RiskProfile
from app.schemas.profile import UserProfileCreate, UserProfileUpdate, UserProfileResponse
import asyncio

router = APIRouter()

@router.post("/create", response_model=UserProfileResponse)
async def create_profile(
    profile_data: UserProfileCreate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    for attempt in range(5):
        try:
            new_profile = UserProfile(
                user_id=user_id,
                **profile_data.model_dump()
            )
            db.add(new_profile)
            await db.commit()
            await db.refresh(new_profile)
            return new_profile
        except Exception as e:
            await db.rollback()
            if attempt < 4:
                await asyncio.sleep(0.3)
            else:
                raise HTTPException(status_code=500, detail="User sync timeout or constraint error")

@router.put("/update", response_model=UserProfileResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for key, value in profile_data.model_dump().items():
        setattr(profile, key, value)
    
    await db.commit()
    await db.refresh(profile)
    return profile

@router.get("/me", response_model=UserProfileResponse)
async def get_profile(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(UserProfile, RiskProfile.profile_name)
        .outerjoin(RiskProfile, UserProfile.risk_profile_id == RiskProfile.risk_profile_id)
        .where(UserProfile.user_id == user_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile, profile_name = row
    response = UserProfileResponse.model_validate(profile)
    response.risk_profile_name = profile_name
    return response
