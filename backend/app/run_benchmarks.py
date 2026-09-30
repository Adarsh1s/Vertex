import asyncio
import time
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.core.neon_proxy import start_neon_proxy, stop_neon_proxy

async def run_benchmarks():
    if settings.is_neon_host and settings.neon_host:
        await start_neon_proxy(settings.neon_host, listen_port=5434)

    try:
        async with AsyncSessionLocal() as session:
            print("=" * 80)
            print("FinPulse ADVANCED DBMS BENCHMARKS & VERIFICATION")
            print("=" * 80)

            # -----------------------------------------------------------------
            # 1. PARTITION PRUNING BENCHMARK (EXPLAIN ANALYZE)
            # -----------------------------------------------------------------
            print("\n[BENCHMARK 1] Partition Pruning on market_price_history (Range Partitioning)")
            print("Query: SELECT * FROM market_price_history WHERE price_date >= '2026-01-01'")
            query_1 = """
                EXPLAIN ANALYZE
                SELECT mph.instrument_id, mph.price_date, mph.nav_or_close
                FROM market_price_history mph
                WHERE mph.price_date >= '2026-01-01';
            """
            res_1 = await session.execute(text(query_1))
            lines_1 = [r[0] for r in res_1.fetchall()]
            for line in lines_1:
                print(f"  {line}")

            is_pruned = not any("market_price_history_2025" in l for l in lines_1)
            print(f"  >> RESULT: Partition Pruning Verified = {is_pruned} (2025 Partition Pruned Out)")

            # -----------------------------------------------------------------
            # 2. GIN INDEXED JSONB QUERY (SEMI-STRUCTURED DOCUMENT SEARCH)
            # -----------------------------------------------------------------
            print("\n[BENCHMARK 2] GIN Index Containment Search on raw_market_scrapes")
            print("Query: SELECT count(*) FROM raw_market_scrapes WHERE raw_payload @> '{\"source\": \"AMFI India Official\"}'")
            query_2 = """
                EXPLAIN ANALYZE
                SELECT scrape_id, ticker_or_scheme, raw_payload->>'scheme_name' AS scheme_name
                FROM raw_market_scrapes
                WHERE raw_payload @> '{"source": "AMFI India Official"}';
            """
            res_2 = await session.execute(text(query_2))
            for line in res_2.fetchall():
                print(f"  {line[0]}")

            # -----------------------------------------------------------------
            # 3. OLAP WINDOW FUNCTION (LAG & MOVING COMPARISON)
            # -----------------------------------------------------------------
            print("\n[BENCHMARK 3] Analytical Window Function (LAG day-over-day price delta)")
            query_3 = """
                SELECT 
                    i.ticker,
                    mph.price_date,
                    mph.nav_or_close,
                    LAG(mph.nav_or_close, 1) OVER (PARTITION BY mph.instrument_id ORDER BY mph.price_date) AS prev_price,
                    ROUND(
                        ((mph.nav_or_close - LAG(mph.nav_or_close, 1) OVER (PARTITION BY mph.instrument_id ORDER BY mph.price_date))
                        / NULLIF(LAG(mph.nav_or_close, 1) OVER (PARTITION BY mph.instrument_id ORDER BY mph.price_date), 0)) * 100, 2
                    ) AS day_change_pct
                FROM market_price_history mph
                JOIN instruments i ON mph.instrument_id = i.instrument_id
                ORDER BY mph.instrument_id, mph.price_date DESC
                LIMIT 8;
            """
            res_3 = await session.execute(text(query_3))
            print(f"  {'Ticker':<12} {'Date':<12} {'Close (₹)':<12} {'Prev Close':<12} {'Delta %':<10}")
            print("  " + "-" * 56)
            for r in res_3.fetchall():
                prev = f"{r[3]:.2f}" if r[3] else "N/A"
                delta = f"{r[4]:+.2f}%" if r[4] is not None else "N/A"
                print(f"  {r[0]:<12} {str(r[1]):<12} {float(r[2]):<12.2f} {prev:<12} {delta:<10}")

            # -----------------------------------------------------------------
            # 4. MULTI-DIMENSIONAL ROLLUP / CUBE HIERARCHY
            # -----------------------------------------------------------------
            print("\n[BENCHMARK 4] Multi-Dimensional OLAP ROLLUP (Asset Class -> Instrument Type)")
            query_4 = """
                SELECT 
                    COALESCE(ac.name, '== ALL ASSET CLASSES ==') AS asset_class,
                    COALESCE(i.instrument_type, '== ALL TYPES ==') AS instrument_type,
                    COUNT(DISTINCT i.instrument_id) AS instruments_count,
                    ROUND(AVG(mv.latest_price), 2) AS avg_price
                FROM instruments i
                JOIN asset_classes ac ON i.asset_class_id = ac.asset_class_id
                LEFT JOIN mv_instrument_performance_metrics mv ON i.instrument_id = mv.instrument_id
                GROUP BY ROLLUP(ac.name, i.instrument_type);
            """
            res_4 = await session.execute(text(query_4))
            print(f"  {'Asset Class':<26} {'Instrument Type':<20} {'Count':<8} {'Avg Price (₹)':<14}")
            print("  " + "-" * 70)
            for r in res_4.fetchall():
                print(f"  {r[0]:<26} {r[1]:<20} {r[2]:<8} {float(r[3]) if r[3] else 0.0:<14.2f}")

            # -----------------------------------------------------------------
            # 5. MATERIALIZED VIEW SUB-MILLISECOND READ TEST
            # -----------------------------------------------------------------
            print("\n[BENCHMARK 5] Gold Tier Materialized View Sub-Millisecond Speed")
            t0 = time.perf_counter()
            mv_res = await session.execute(text("SELECT COUNT(*) FROM mv_instrument_performance_metrics"))
            t_elapsed_ms = (time.perf_counter() - t0) * 1000
            print(f"  Queried Materialized View in {t_elapsed_ms:.2f} ms (Rows: {mv_res.scalar()})")
            print("=" * 80)
    finally:
        if settings.is_neon_host:
            await stop_neon_proxy()

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
