from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.neon_proxy import start_neon_proxy, stop_neon_proxy
from app.routers import auth, profile, questionnaire, portfolio, reference, finpulse, market

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.is_neon_host and settings.neon_host:
        await start_neon_proxy(settings.neon_host, listen_port=5434)
    yield
    if settings.is_neon_host:
        await stop_neon_proxy()

app = FastAPI(
    title="Vertex API",
    description="Advanced Financial Lakehouse & Real-Time Portfolio Intelligence: Portfolios, Data Lake ETL, Goals, and Drift Telemetry.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile.router, prefix="/profile", tags=["Profile"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(questionnaire.router, prefix="/questionnaire", tags=["Questionnaire"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(reference.router, prefix="/reference", tags=["Reference Data"])
app.include_router(finpulse.router, prefix="/finpulse", tags=["Vertex Intelligence"])
app.include_router(market.router, prefix="/market", tags=["Market & Data Lake"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Vertex API"}
