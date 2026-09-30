from sqlalchemy import Column, BigInteger, Integer, String, Numeric, DateTime, Date, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class RawMarketScrape(Base):
    __tablename__ = 'raw_market_scrapes'

    scrape_id = Column(BigInteger, primary_key=True, autoincrement=True)
    source_feed = Column(String(50), nullable=False)
    ticker_or_scheme = Column(String(50))
    http_status = Column(Integer, default=200, nullable=False)
    raw_payload = Column(JSONB, nullable=False)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class MarketPriceHistory(Base):
    __tablename__ = 'market_price_history'

    instrument_id = Column(Integer, ForeignKey('instruments.instrument_id', ondelete='CASCADE'), primary_key=True)
    price_date = Column(Date, primary_key=True)
    nav_or_close = Column(Numeric(12, 4), nullable=False)
    day_high = Column(Numeric(12, 4))
    day_low = Column(Numeric(12, 4))
    volume = Column(BigInteger, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
