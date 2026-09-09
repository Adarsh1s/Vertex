from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class RiskProfile(Base):
    __tablename__ = 'risk_profiles'

    risk_profile_id = Column(Integer, primary_key=True, autoincrement=True)
    profile_name = Column(String(50), nullable=False)
    min_score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    description = Column(Text)

class UserProfile(Base):
    __tablename__ = 'user_profiles'

    profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Text, unique=True, index=True) # UUID TEXT from neon_auth.users_sync
    monthly_income = Column(Numeric(12, 2))
    monthly_expenses = Column(Numeric(12, 2))
    investment_amount = Column(Numeric(12, 2))
    investment_horizon_years = Column(Integer)
    investment_goal = Column(String(100))
    risk_score = Column(Integer)
    risk_profile_id = Column(Integer, ForeignKey('risk_profiles.risk_profile_id'))
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    risk_profile = relationship("RiskProfile")
