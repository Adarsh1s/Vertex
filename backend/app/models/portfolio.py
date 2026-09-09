from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Boolean, DateTime, func, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class PortfolioModel(Base):
    __tablename__ = 'portfolio_models'

    model_id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    risk_profile_id = Column(Integer, ForeignKey('risk_profiles.risk_profile_id'))
    description = Column(Text)

class PortfolioAllocation(Base):
    __tablename__ = 'portfolio_allocations'

    allocation_id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(Integer, ForeignKey('portfolio_models.model_id'), index=True)
    asset_class_id = Column(Integer, ForeignKey('asset_classes.asset_class_id'))
    allocation_percentage = Column(Numeric(5, 2), nullable=False)

class UserPortfolio(Base):
    __tablename__ = 'user_portfolios'

    portfolio_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Text, index=True) # UUID TEXT from neon_auth.users_sync
    model_id = Column(Integer, ForeignKey('portfolio_models.model_id'))
    total_investment = Column(Numeric(14, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    generated_at = Column(DateTime, default=func.now())

class UserPortfolioPosition(Base):
    __tablename__ = 'user_portfolio_positions'

    position_id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('user_portfolios.portfolio_id', ondelete='CASCADE'), index=True)
    instrument_id = Column(Integer, ForeignKey('instruments.instrument_id'))
    allocation_percentage = Column(Numeric(5, 2))
    allocated_amount = Column(Numeric(14, 2))
