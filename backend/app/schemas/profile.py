from pydantic import BaseModel, Field
from typing import Optional

class UserProfileBase(BaseModel):
    monthly_income: float
    monthly_expenses: float
    investment_amount: float
    investment_horizon_years: int
    investment_goal: str

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    profile_id: int
    user_id: str
    risk_score: Optional[int] = None
    risk_profile_id: Optional[int] = None
    risk_profile_name: Optional[str] = None

    class Config:
        from_attributes = True

class QuestionnaireSubmit(BaseModel):
    answers: list[int] = Field(..., description="List of 7 integer scores from the questionnaire")
