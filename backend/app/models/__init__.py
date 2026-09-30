# Import all models so SQLAlchemy registers them with the metadata
from app.models.profile import RiskProfile, UserProfile
from app.models.portfolio import PortfolioModel, PortfolioAllocation, UserPortfolio, UserPortfolioPosition
from app.models.instrument import AssetClass, Instrument, InstrumentReturn
from app.models.market import RawMarketScrape, MarketPriceHistory
