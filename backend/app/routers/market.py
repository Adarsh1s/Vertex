from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, List, Dict, Any
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.market_crawler import MarketCrawlerService

router = APIRouter()

@router.post("/crawl")
async def trigger_market_crawl():
    """
    Trigger the Scrapling Anti-Bot Crawler on demand.
    Bypasses WAF/Cloudflare to ingest AMFI NAVs and Market Quotes,
    lands raw JSONB in Bronze Lake, upserts into Silver Partitioned Warehouse,
    and refreshes the Gold Materialized View.
    """
    try:
        result = await MarketCrawlerService.crawl_and_ingest()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Market crawl ingestion failed: {str(e)}")

@router.get("/lake/raw")
async def get_raw_lake_scrapes(
    limit: int = Query(20, ge=1, le=100),
    ticker: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Inspect the Bronze Data Lake: retrieves unparsed semi-structured JSONB payloads
    from raw_market_scrapes. Demonstrates NoSQL document storage in PostgreSQL.
    """
    query = """
        SELECT scrape_id, source_feed, ticker_or_scheme, http_status, 
               raw_payload, scraped_at
        FROM raw_market_scrapes
    """
    params: Dict[str, Any] = {"limit": limit}
    if ticker:
        query += " WHERE ticker_or_scheme = :ticker"
        params["ticker"] = ticker
    query += " ORDER BY scraped_at DESC LIMIT :limit;"

    res = await db.execute(text(query), params)
    rows = res.fetchall()
    return [
        {
            "scrape_id": r[0],
            "source_feed": r[1],
            "ticker_or_scheme": r[2],
            "http_status": r[3],
            "raw_payload": r[4],
            "scraped_at": str(r[5])
        }
        for r in rows
    ]

@router.get("/prices/latest")
async def get_latest_market_prices(db: AsyncSession = Depends(get_db)):
    """
    Gold Tier Query: Retrieves pre-aggregated financial metrics from 
    mv_instrument_performance_metrics (materialized view with rolling stats & volatility).
    """
    query = """
        SELECT 
            instrument_id, instrument_name, ticker, asset_class, 
            instrument_type, latest_date, latest_price, 
            avg_historical_price, price_volatility_stddev, data_points_count
        FROM mv_instrument_performance_metrics
        ORDER BY asset_class, instrument_name;
    """
    res = await db.execute(text(query))
    rows = res.fetchall()
    return [
        {
            "instrument_id": r[0],
            "instrument_name": r[1],
            "ticker": r[2],
            "asset_class": r[3],
            "instrument_type": r[4],
            "latest_date": str(r[5]),
            "latest_price": float(r[6]),
            "avg_historical_price": float(r[7]),
            "price_volatility_stddev": float(r[8]),
            "data_points_count": r[9]
        }
        for r in rows
    ]

@router.get("/history/{instrument_id}")
async def get_instrument_history(
    instrument_id: int,
    start_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Silver Tier Time-Series Query: Fetches chronological price rows from 
    declaratively partitioned market_price_history.
    Postgres automatically executes partition pruning.
    """
    query = """
        SELECT 
            mph.price_date, mph.nav_or_close, mph.day_high, mph.day_low, 
            mph.volume, i.ticker, i.name
        FROM market_price_history mph
        JOIN instruments i ON mph.instrument_id = i.instrument_id
        WHERE mph.instrument_id = :inst_id
    """
    params: Dict[str, Any] = {"inst_id": instrument_id}
    if start_date:
        query += " AND mph.price_date >= :start_date::date"
        params["start_date"] = start_date
    query += " ORDER BY mph.price_date ASC;"

    res = await db.execute(text(query), params)
    rows = res.fetchall()
    return [
        {
            "price_date": str(r[0]),
            "nav_or_close": float(r[1]),
            "day_high": float(r[2]) if r[2] else None,
            "day_low": float(r[3]) if r[3] else None,
            "volume": r[4],
            "ticker": r[5],
            "name": r[6]
        }
        for r in rows
    ]

@router.get("/telemetry/partitions")
async def get_partition_telemetry(db: AsyncSession = Depends(get_db)):
    """
    DBMS Telemetry: Queries PostgreSQL catalog tables (pg_class, pg_inherits)
    to inspect physical partition distribution and storage metrics.
    """
    query = """
        SELECT 
            c.relname AS partition_name,
            pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size,
            (SELECT count(*) FROM market_price_history) AS parent_total_rows,
            c.reltuples::bigint AS estimated_tuples
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND c.relname LIKE 'market_price_history%'
        ORDER BY c.relname;
    """
    res = await db.execute(text(query))
    rows = res.fetchall()
    
    # Exact row counts for key tables
    counts = {}
    for p in ['market_price_history_2025', 'market_price_history_2026', 'market_price_history_future', 'raw_market_scrapes']:
        try:
            cnt_res = await db.execute(text(f"SELECT COUNT(*) FROM {p}"))
            counts[p] = cnt_res.scalar()
        except Exception:
            counts[p] = 0

    return {
        "partitions": [
            {
                "partition_name": r[0],
                "total_size": r[1],
                "exact_rows": counts.get(r[0], r[3])
            }
            for r in rows
        ],
        "bronze_lake_rows": counts.get("raw_market_scrapes", 0)
    }

@router.get("/portfolio-drift")
async def get_portfolio_drift(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Live Portfolio Drift Analytics: Compares active portfolio valuation
    (revalued using latest market prices) against model target allocation percentages.
    Detects rebalancing drift (>= 5% threshold).
    """
    query = """
        WITH ActivePositions AS (
            SELECT 
                upp.position_id,
                upp.instrument_id,
                i.name AS instrument_name,
                i.ticker,
                ac.asset_class_id,
                ac.name AS asset_class,
                upp.allocated_amount AS original_allocated_amount,
                COALESCE(mv.latest_price, 100.0) AS latest_market_price,
                ROUND(upp.allocated_amount * COALESCE(mv.latest_price / NULLIF(mv.avg_historical_price, 0), 1.0), 2) AS live_market_value
            FROM user_portfolios up
            JOIN user_portfolio_positions upp ON up.portfolio_id = upp.portfolio_id
            JOIN instruments i ON upp.instrument_id = i.instrument_id
            JOIN asset_classes ac ON i.asset_class_id = ac.asset_class_id
            LEFT JOIN mv_instrument_performance_metrics mv ON i.instrument_id = mv.instrument_id
            WHERE up.user_id = :user_id AND up.is_active = TRUE
        ),
        ClassAggregates AS (
            SELECT 
                asset_class_id,
                asset_class,
                SUM(original_allocated_amount) AS class_original_amount,
                SUM(live_market_value) AS class_live_value
            FROM ActivePositions
            GROUP BY asset_class_id, asset_class
        ),
        TotalValuation AS (
            SELECT 
                COALESCE(SUM(class_original_amount), 0) AS total_original,
                COALESCE(SUM(class_live_value), 0) AS total_live
            FROM ClassAggregates
        ),
        UserTargetAllocations AS (
            SELECT 
                pa.asset_class_id,
                pa.allocation_percentage AS target_weight_pct
            FROM user_profiles upr
            JOIN portfolio_models pm ON upr.risk_profile_id = pm.risk_profile_id
            JOIN portfolio_allocations pa ON pm.model_id = pa.model_id
            WHERE upr.user_id = :user_id
        )
        SELECT 
            ca.asset_class_id,
            ca.asset_class,
            ca.class_original_amount,
            ca.class_live_value,
            ROUND(
                CASE WHEN tv.total_live > 0 
                     THEN (ca.class_live_value / tv.total_live) * 100 
                     ELSE 0 END, 2
            ) AS current_weight_pct,
            COALESCE(uta.target_weight_pct, 0) AS target_weight_pct,
            ROUND(
                (CASE WHEN tv.total_live > 0 
                      THEN (ca.class_live_value / tv.total_live) * 100 
                      ELSE 0 END) - COALESCE(uta.target_weight_pct, 0), 2
            ) AS drift_pct,
            tv.total_original,
            tv.total_live
        FROM ClassAggregates ca
        CROSS JOIN TotalValuation tv
        LEFT JOIN UserTargetAllocations uta ON ca.asset_class_id = uta.asset_class_id
        ORDER BY ABS(
            (CASE WHEN tv.total_live > 0 
                  THEN (ca.class_live_value / tv.total_live) * 100 
                  ELSE 0 END) - COALESCE(uta.target_weight_pct, 0)
        ) DESC;
    """
    res = await db.execute(text(query), {"user_id": user_id})
    rows = res.fetchall()

    if not rows:
        return {
            "has_portfolio": False,
            "message": "No active portfolio found for current user.",
            "classes": [],
            "drift_alerts": []
        }

    total_orig = float(rows[0][7]) if rows else 0
    total_live = float(rows[0][8]) if rows else 0

    classes = []
    drift_alerts = []
    for r in rows:
        c_weight = float(r[4])
        t_weight = float(r[5])
        drift = float(r[6])
        class_data = {
            "asset_class_id": r[0],
            "asset_class": r[1],
            "original_amount": float(r[2]),
            "live_value": float(r[3]),
            "current_weight_pct": c_weight,
            "target_weight_pct": t_weight,
            "drift_pct": drift,
            "drift_severity": "HIGH" if abs(drift) >= 5.0 else ("MEDIUM" if abs(drift) >= 2.5 else "NORMAL")
        }
        classes.append(class_data)
        if abs(drift) >= 5.0:
            direction = "Overweight" if drift > 0 else "Underweight"
            drift_alerts.append(
                f"{r[1]} is {direction} by {abs(drift):.1f}% points against your target model."
            )

    return {
        "has_portfolio": True,
        "total_original_investment": total_orig,
        "total_live_valuation": total_live,
        "portfolio_gain_loss": round(total_live - total_orig, 2),
        "portfolio_gain_loss_pct": round(((total_live - total_orig) / total_orig) * 100, 2) if total_orig > 0 else 0,
        "classes": classes,
        "drift_alerts": drift_alerts,
        "needs_rebalancing": len(drift_alerts) > 0
    }
