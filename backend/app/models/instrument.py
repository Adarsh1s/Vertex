from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Boolean, Date, Text
from app.core.database import Base

class AssetClass(Base):
    __tablename__ = 'asset_classes'

    asset_class_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)

class Instrument(Base):
    __tablename__ = 'instruments'

    instrument_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    ticker = Column(String(30))
    asset_class_id = Column(Integer, ForeignKey('asset_classes.asset_class_id'))
    instrument_type = Column(String(50))
    fund_house = Column(String(100))
    is_active = Column(Boolean, default=True)

class InstrumentReturn(Base):
    __tablename__ = 'instrument_returns'

    return_id = Column(Integer, primary_key=True, autoincrement=True)
    instrument_id = Column(Integer, ForeignKey('instruments.instrument_id'), index=True)
    period = Column(String(10), nullable=False)
    return_percentage = Column(Numeric(6, 2))
    recorded_at = Column(Date)
