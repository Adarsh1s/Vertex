-- ============================================================================
-- 🎓 VERTEX / FINPULSE: MASTER DATABASE QUERIES & VIVA EXAMINATION SUITE
-- Course: Advanced Database Management Systems (ADBMS)
-- Database Engine: PostgreSQL 16+ (Neon Cloud Serverless)
-- Architecture: Medallion Lakehouse (Bronze Data Lake -> Silver ACID Store -> Gold OLAP)
-- ============================================================================
--
-- 📑 QUICK NAVIGATION INDEX:
-- ----------------------------------------------------------------------------
-- [SECTION 0] DBeaver Connection & Environment Health Check
-- [PART 1]    CORE BUSINESS & APPLICATION QUERIES (SIMPLE & ESSENTIAL)
--             • Query 1:  User Profile & Risk Score Assessment
--             • Query 2:  Target Model Allocation by Risk Profile
--             • Query 3A: GENERATE PORTFOLIO (Step-by-Step ACID Transaction)
--             • Query 3B: GENERATE PORTFOLIO (One-Click Stored Procedure)
--             • Query 4:  View Active Portfolio & Holdings Breakdown
--             • Query 5:  Portfolio Summary by Asset Class (Allocation %)
--             • Query 6:  Blended Expected Returns (1Y, 3Y, 5Y CAGR Projections)
--             • Query 7:  Live Portfolio Valuation & P&L (Live Market Prices)
--             • Query 8:  Portfolio Drift & Rebalance Check (Simple Comparison)
--             • Query 9:  Financial Transactions Ledger & Monthly Spending Facts
--             • Query 10: Financial Goals Tracker & SIP Milestone Progress
--             • Query 11: Automated Audit Trail Verification (Trigger Fired Proof)
-- [PART 2]    ADVANCED ADBMS & VIVA EXAMINATION PROOFS
--             • Query 12: Declarative Range Partition Pruning Proof (Silver Tier)
--             • Query 13: Semi-Structured JSONB Querying with GIN Index (Bronze Tier)
--             • Query 14: Analytical Window Function (Day-over-Day Return % with LAG)
--             • Query 15: Multi-Dimensional OLAP Aggregation (ROLLUP Hierarchy)
--             • Query 16: Gold Tier Materialized View Non-Blocking Concurrent Refresh
--             • Query 17: Star Schema Warehouse ETL Stored Procedure
--             • Query 18: PL/pgSQL Function: Real-Time Portfolio Drift Detection
--             • Query 19: PL/pgSQL Function: Multi-Vector Financial Health Score
-- ============================================================================


-- ============================================================================
-- 🔌 SECTION 0: DBEAVER & SQL CLIENT CONNECTION CREDENTIALS
-- ============================================================================
-- 💡 WHY PORT 5432 SOMETIMES TIMES OUT:
-- Many Indian ISPs (Jio, Airtel, local broadband, college Wi-Fi) block outbound
-- TCP port 5432. If DBeaver says "Connection timed out", use METHOD 1 below.
--
-- ----------------------------------------------------------------------------
-- ⭐ METHOD 1: VIA LOCAL PROXY (PORT 5434) — 100% RELIABLE (RECOMMENDED)
-- ----------------------------------------------------------------------------
-- 1. Double-click 'start_db_proxy.bat' (or run 'python start_db_proxy.py')
--    This tunnels database traffic over HTTPS WebSocket Port 443 (never blocked).
-- 2. In DBeaver -> New Database Connection -> PostgreSQL:
--    [Main Tab]
--      • Connect by:      Host
--      • Host:            127.0.0.1   (or localhost)
--      • Port:            5434
--      • Database:        FinPulse
--      • Authentication:  Database Native
--      • Username:        neondb_owner
--      • Password:        npg_Nknlf8FTow7Q
--    [SSL Tab]
--      • [ ] UNCHECK "Use SSL" (Leave disabled - local proxy already handles encryption)
-- 3. Click "Test Connection" -> Connected!
--
-- ----------------------------------------------------------------------------
-- 🌐 METHOD 2: DIRECT NEON CLOUD (PORT 5432) — REQUIRES UNRESTRICTED NETWORK
-- ----------------------------------------------------------------------------
-- If your network allows outbound port 5432:
-- [Main Tab]
--   • Connect by:      Host
--   • Host:            ep-long-meadow-a10ypauu-pooler.ap-southeast-1.aws.neon.tech
--   • Port:            5432
--   • Database:        FinPulse
--   • Authentication:  Database Native
--   • Username:        neondb_owner
--   • Password:        npg_Nknlf8FTow7Q
-- [SSL Tab] (MANDATORY for direct Neon connections)
--   • [x] CHECK "Use SSL"
--   • SSL mode: "require" (or "verify-full")
-- [Alternative JDBC String]
--   • jdbc:postgresql://ep-long-meadow-a10ypauu-pooler.ap-southeast-1.aws.neon.tech:5432/FinPulse?sslmode=require
-- ============================================================================

-- 🧪 QUICK HEALTH CHECK: Run this first to confirm active database connection
SELECT 
    current_database() AS connected_database,
    current_user       AS connected_user,
    version()          AS postgresql_version,
    inet_server_addr() AS server_ip,
    NOW()              AS session_timestamp;


-- ============================================================================
-- 📂 PART 1: CORE BUSINESS & APPLICATION QUERIES (SIMPLE & ESSENTIAL)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- QUERY 1: User Profile & Risk Assessment
-- Concept: Retrieves user financial profile, risk questionnaire score, and
--          matches it with the corresponding risk tolerance profile.
-- ----------------------------------------------------------------------------
SELECT 
    u.user_id,
    u.name AS user_name,
    u.email,
    up.monthly_income,
    up.monthly_expenses,
    up.investment_amount,
    up.investment_horizon_years,
    up.investment_goal,
    up.risk_score,
    rp.profile_name AS assessed_risk_profile,
    rp.description  AS risk_profile_description
FROM app_users u
JOIN user_profiles up ON u.user_id = up.user_id
JOIN risk_profiles rp ON up.risk_profile_id = rp.risk_profile_id
ORDER BY up.updated_at DESC;


-- ----------------------------------------------------------------------------
-- QUERY 2: Target Model Allocation by Risk Profile
-- Concept: Shows the recommended target asset class allocation (Equity, Debt,
--          Gold, Cash, International) for a specific risk profile model.
-- ----------------------------------------------------------------------------
SELECT 
    pm.model_id,
    pm.model_name,
    rp.profile_name AS risk_level,
    ac.name         AS asset_class,
    pa.allocation_percentage,
    ROUND(250000.00 * (pa.allocation_percentage / 100.0), 2) AS target_amount_for_250k
FROM portfolio_models pm
JOIN risk_profiles rp ON pm.risk_profile_id = rp.risk_profile_id
JOIN portfolio_allocations pa ON pm.model_id = pa.model_id
JOIN asset_classes ac ON pa.asset_class_id = ac.asset_class_id
WHERE rp.profile_name = 'Moderate' -- Change to 'Conservative', 'Moderately Conservative', 'Aggressive'
ORDER BY pa.allocation_percentage DESC;


-- ----------------------------------------------------------------------------
-- QUERY 3A: GENERATE PORTFOLIO (Step-by-Step ACID Transaction)
-- Concept: Pure SQL implementation of the robo-advisory generation engine.
--          Executes atomically: deactivates older portfolios, creates a new
--          versioned portfolio header (which automatically fires trg_audit_portfolio),
--          and populates all instrument holdings using model weight templates.
-- ----------------------------------------------------------------------------
BEGIN;

-- Step 1: Deactivate any current active portfolio for the target user
UPDATE user_portfolios 
SET is_active = FALSE 
WHERE user_id = (SELECT user_id FROM user_profiles LIMIT 1) 
  AND is_active = TRUE;

-- Step 2: Insert new portfolio header (Trigger trg_audit_portfolio logs this automatically!)
INSERT INTO user_portfolios (user_id, model_id, total_investment, is_active, version, generated_at)
VALUES (
    (SELECT user_id FROM user_profiles LIMIT 1),
    3, -- Model 3: Balanced Growth Model (Moderate Risk)
    250000.00,
    TRUE,
    COALESCE((SELECT MAX(version) FROM user_portfolios WHERE user_id = (SELECT user_id FROM user_profiles LIMIT 1)), 0) + 1,
    NOW()
);

-- Step 3: Populate instrument positions by joining model allocations & templates
INSERT INTO user_portfolio_positions (portfolio_id, instrument_id, allocation_percentage, allocated_amount)
SELECT 
    currval(pg_get_serial_sequence('user_portfolios', 'portfolio_id')),
    ia.instrument_id,
    ROUND(pa.allocation_percentage * ia.allocation_percentage / 100.0, 2) AS allocation_percentage,
    ROUND(250000.00 * (pa.allocation_percentage * ia.allocation_percentage / 10000.0), 2) AS allocated_amount
FROM portfolio_allocations pa
JOIN sub_allocation_templates sat 
    ON sat.model_id = pa.model_id AND sat.asset_class_id = pa.asset_class_id
JOIN instrument_allocations ia 
    ON ia.template_id = sat.template_id
WHERE pa.model_id = 3;

-- Step 4: Record analytics snapshot in star schema fact table
INSERT INTO fact_monthly_portfolio_snapshots
    (user_id, snapshot_month, portfolio_id, portfolio_value, asset_class_count, largest_allocation_pct, created_at)
SELECT 
    (SELECT user_id FROM user_profiles LIMIT 1),
    date_trunc('month', CURRENT_DATE)::date,
    currval(pg_get_serial_sequence('user_portfolios', 'portfolio_id')),
    250000.00,
    COUNT(DISTINCT i.asset_class_id),
    COALESCE(MAX(upp.allocation_percentage), 0),
    NOW()
FROM user_portfolio_positions upp
JOIN instruments i ON i.instrument_id = upp.instrument_id
WHERE upp.portfolio_id = currval(pg_get_serial_sequence('user_portfolios', 'portfolio_id'))
ON CONFLICT (user_id, snapshot_month) DO UPDATE SET
    portfolio_id = EXCLUDED.portfolio_id,
    portfolio_value = EXCLUDED.portfolio_value,
    asset_class_count = EXCLUDED.asset_class_count,
    largest_allocation_pct = EXCLUDED.largest_allocation_pct,
    created_at = NOW();

COMMIT;


-- ----------------------------------------------------------------------------
-- QUERY 3B: GENERATE PORTFOLIO (One-Click Reusable Stored Procedure)
-- Concept: Wraps the entire generation transaction into a single callable
--          stored procedure for easy examiner demo and backend invocation.
-- ----------------------------------------------------------------------------

-- Step 1: Create or replace stored procedure
CREATE OR REPLACE PROCEDURE sp_generate_portfolio(
    p_user_id TEXT,
    p_investment_amount NUMERIC DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_model_id INT;
    v_investment NUMERIC(14,2);
    v_portfolio_id INT;
    v_version INT;
BEGIN
    -- 1. Determine investment amount and model from user profile if not provided
    SELECT 
        COALESCE(p_investment_amount, up.investment_amount, 250000.00),
        pm.model_id
    INTO v_investment, v_model_id
    FROM user_profiles up
    JOIN portfolio_models pm ON up.risk_profile_id = pm.risk_profile_id
    WHERE up.user_id = p_user_id;

    -- Fallback to Model 3 (Balanced Growth) if user profile is missing
    IF v_model_id IS NULL THEN
        v_model_id := 3;
        v_investment := COALESCE(p_investment_amount, 250000.00);
    END IF;

    -- 2. Deactivate previous active portfolio
    UPDATE user_portfolios 
    SET is_active = FALSE 
    WHERE user_id = p_user_id AND is_active = TRUE;

    -- 3. Calculate incremented version number
    SELECT COALESCE(MAX(version), 0) + 1 INTO v_version
    FROM user_portfolios
    WHERE user_id = p_user_id;

    -- 4. Insert new portfolio header (Trigger trg_audit_portfolio fires here)
    INSERT INTO user_portfolios (user_id, model_id, total_investment, is_active, version, generated_at)
    VALUES (p_user_id, v_model_id, v_investment, TRUE, v_version, NOW())
    RETURNING portfolio_id INTO v_portfolio_id;

    -- 5. Insert calculated instrument positions
    INSERT INTO user_portfolio_positions (portfolio_id, instrument_id, allocation_percentage, allocated_amount)
    SELECT
        v_portfolio_id,
        ia.instrument_id,
        ROUND(pa.allocation_percentage * ia.allocation_percentage / 100.0, 2),
        ROUND(v_investment * (pa.allocation_percentage * ia.allocation_percentage / 10000.0), 2)
    FROM portfolio_allocations pa
    JOIN sub_allocation_templates sat 
        ON sat.model_id = pa.model_id AND sat.asset_class_id = pa.asset_class_id
    JOIN instrument_allocations ia 
        ON ia.template_id = sat.template_id
    WHERE pa.model_id = v_model_id;

    -- 6. Update monthly fact snapshot table
    INSERT INTO fact_monthly_portfolio_snapshots
        (user_id, snapshot_month, portfolio_id, portfolio_value, asset_class_count, largest_allocation_pct, created_at)
    SELECT 
        p_user_id, 
        date_trunc('month', CURRENT_DATE)::date, 
        v_portfolio_id,
        v_investment, 
        COUNT(DISTINCT i.asset_class_id),
        COALESCE(MAX(upp.allocation_percentage), 0),
        NOW()
    FROM user_portfolio_positions upp
    JOIN instruments i ON i.instrument_id = upp.instrument_id
    WHERE upp.portfolio_id = v_portfolio_id
    ON CONFLICT (user_id, snapshot_month) DO UPDATE SET
        portfolio_id = EXCLUDED.portfolio_id,
        portfolio_value = EXCLUDED.portfolio_value,
        asset_class_count = EXCLUDED.asset_class_count,
        largest_allocation_pct = EXCLUDED.largest_allocation_pct,
        created_at = NOW();

    RAISE NOTICE 'Portfolio v% generated successfully (Portfolio ID: %) with total capital ₹%', v_version, v_portfolio_id, v_investment;
END;
$$;

-- Step 2: Test Call the Stored Procedure (Generates portfolio for first user)
CALL sp_generate_portfolio((SELECT user_id FROM user_profiles LIMIT 1), 300000.00);


-- ----------------------------------------------------------------------------
-- QUERY 4: View Active Portfolio & Holdings Breakdown
-- Concept: Queries the analytical view 'user_portfolio_summary' to display
--          the complete breakdown of instruments, asset class, ticker,
--          portfolio weight %, and allocated investment amount (₹).
-- ----------------------------------------------------------------------------
SELECT 
    ups.portfolio_id,
    ups.version AS portfolio_version,
    ups.user_name,
    ups.model_name,
    ups.risk_profile,
    ups.asset_class,
    ups.instrument_name,
    ups.ticker,
    ups.instrument_type,
    ups.allocation_percentage AS weight_pct,
    ups.allocated_amount      AS invested_inr,
    ups.generated_at
FROM user_portfolio_summary ups
WHERE ups.is_active = TRUE
ORDER BY ups.portfolio_id DESC, ups.asset_class ASC, ups.allocation_percentage DESC;


-- ----------------------------------------------------------------------------
-- QUERY 5: Portfolio Summary by Asset Class
-- Concept: Aggregates active portfolio positions by asset class (Equity, Debt,
--          Gold, Cash) to confirm total capital distribution and sum of weights.
-- ----------------------------------------------------------------------------
SELECT 
    ups.asset_class,
    COUNT(ups.instrument_id)       AS instruments_count,
    SUM(ups.allocation_percentage) AS total_allocation_pct,
    SUM(ups.allocated_amount)      AS total_invested_inr
FROM user_portfolio_summary ups
WHERE ups.is_active = TRUE
GROUP BY ups.asset_class
ORDER BY total_allocation_pct DESC;


-- ----------------------------------------------------------------------------
-- QUERY 6: Blended Expected Returns (1Y, 3Y, 5Y CAGR Projections)
-- Concept: Computes the overall expected portfolio return CAGR by taking the
--          weighted average return across all instruments for each time horizon.
-- ----------------------------------------------------------------------------
SELECT 
    ir.period AS investment_horizon,
    ROUND(SUM(ups.allocation_percentage * ir.return_percentage / 100.0), 2) AS blended_expected_cagr_pct
FROM user_portfolio_summary ups
JOIN instrument_returns ir ON ups.instrument_id = ir.instrument_id
WHERE ups.is_active = TRUE
GROUP BY ir.period
ORDER BY ir.period;


-- ----------------------------------------------------------------------------
-- QUERY 7: Live Portfolio Valuation & Market Performance
-- Concept: Joins user portfolio positions with live market prices from the
--          Gold Tier Materialized View to calculate live value, P&L, and ROI.
-- ----------------------------------------------------------------------------
SELECT 
    i.ticker,
    i.name                                                      AS instrument_name,
    ac.name                                                     AS asset_class,
    upp.allocated_amount                                        AS invested_capital_inr,
    COALESCE(mv.latest_price, 100.00)                           AS current_market_price,
    ROUND(upp.allocated_amount * (COALESCE(mv.latest_price, 100.0) / NULLIF(mv.avg_historical_price, 0)), 2) 
                                                                AS current_market_value_inr,
    ROUND((upp.allocated_amount * (COALESCE(mv.latest_price, 100.0) / NULLIF(mv.avg_historical_price, 0))) - upp.allocated_amount, 2) 
                                                                AS unrealized_pnl_inr,
    ROUND((((COALESCE(mv.latest_price, 100.0) / NULLIF(mv.avg_historical_price, 0)) - 1.0) * 100.0), 2) 
                                                                AS roi_percentage
FROM user_portfolios up
JOIN user_portfolio_positions upp ON up.portfolio_id = upp.portfolio_id
JOIN instruments i                ON upp.instrument_id = i.instrument_id
JOIN asset_classes ac             ON i.asset_class_id = ac.asset_class_id
LEFT JOIN mv_instrument_performance_metrics mv ON i.instrument_id = mv.instrument_id
WHERE up.is_active = TRUE
ORDER BY invested_capital_inr DESC;


-- ----------------------------------------------------------------------------
-- QUERY 8: Portfolio Drift & Rebalance Check (Simple Comparison)
-- Concept: Compares current asset class weights against target model allocations.
--          Flags any asset class where drift exceeds the 5.0% tolerance band.
-- ----------------------------------------------------------------------------
WITH CurrentAllocations AS (
    SELECT 
        ac.asset_class_id,
        ac.name AS asset_class,
        SUM(upp.allocated_amount) AS actual_amount,
        ROUND((SUM(upp.allocated_amount) / up.total_investment) * 100.0, 2) AS current_weight_pct
    FROM user_portfolios up
    JOIN user_portfolio_positions upp ON up.portfolio_id = upp.portfolio_id
    JOIN instruments i                ON upp.instrument_id = i.instrument_id
    JOIN asset_classes ac             ON i.asset_class_id = ac.asset_class_id
    WHERE up.is_active = TRUE
    GROUP BY ac.asset_class_id, ac.name, up.total_investment
)
SELECT 
    ca.asset_class,
    ca.actual_amount                                      AS invested_inr,
    ca.current_weight_pct,
    pa.allocation_percentage                              AS target_weight_pct,
    ROUND(ca.current_weight_pct - pa.allocation_percentage, 2) AS drift_pct,
    CASE 
        WHEN ABS(ca.current_weight_pct - pa.allocation_percentage) >= 5.0 THEN 'REBALANCE REQUIRED (>= 5%)'
        ELSE 'BALANCED (WITHIN TOLERANCE)'
    END AS rebalance_status
FROM CurrentAllocations ca
JOIN user_portfolios up ON up.is_active = TRUE
JOIN portfolio_allocations pa ON pa.model_id = up.model_id AND pa.asset_class_id = ca.asset_class_id
ORDER BY ABS(ca.current_weight_pct - pa.allocation_percentage) DESC;


-- ----------------------------------------------------------------------------
-- QUERY 9: Financial Transactions Ledger & Monthly Spending Facts
-- Concept: Shows curated Silver Tier ledger with deduplication fingerprints
--          and the pre-aggregated Gold Tier fact snapshots.
-- ----------------------------------------------------------------------------

-- 9A: Recent Transaction Ledger (Silver Tier)
SELECT 
    transaction_date,
    description,
    amount,
    transaction_type,
    category,
    fingerprint
FROM financial_transactions
ORDER BY transaction_date DESC, transaction_id DESC
LIMIT 10;

-- 9B: Monthly Spending Fact Table (Gold Tier Star Schema)
SELECT 
    snapshot_month,
    income_amount,
    expense_amount,
    savings_amount,
    ROUND((savings_amount / NULLIF(income_amount, 0)) * 100, 2) AS savings_rate_pct,
    transaction_count,
    refreshed_at
FROM fact_monthly_spending_snapshots
ORDER BY snapshot_month DESC;


-- ----------------------------------------------------------------------------
-- QUERY 10: Financial Goals Tracker & SIP Milestone Progress
-- Concept: Tracks user-defined financial goals (Retirement, House, Emergency Fund),
--          showing current savings vs target amount and completion percentage.
-- ----------------------------------------------------------------------------
SELECT 
    goal_id,
    goal_name,
    target_amount,
    current_amount,
    target_date,
    expected_return_pct,
    ROUND((current_amount / NULLIF(target_amount, 0)) * 100, 2) AS progress_pct,
    ROUND(target_amount - current_amount, 2)                    AS remaining_gap_inr,
    is_active
FROM financial_goals
ORDER BY target_date ASC;


-- ----------------------------------------------------------------------------
-- QUERY 11: Automated Audit Trail Verification (Trigger Fired Proof)
-- Concept: Verifies that database trigger 'trg_audit_portfolio' automatically
--          logged an immutable audit record when a portfolio was created.
-- ----------------------------------------------------------------------------
SELECT 
    log_id,
    user_id,
    action,
    metadata->>'portfolio_id'    AS portfolio_id,
    metadata->>'model_id'        AS model_id,
    metadata->>'version'         AS portfolio_version,
    metadata->>'total_investment' AS investment_amount,
    created_at                   AS trigger_logged_at
FROM audit_log
WHERE action = 'PORTFOLIO_GENERATED'
ORDER BY created_at DESC
LIMIT 5;



-- ============================================================================
-- 📂 PART 2: ADVANCED ADBMS & VIVA EXAMINATION PROOFS
-- ============================================================================

-- ============================================================================
-- QUERY 12: Declarative Range Partition Pruning Proof
-- Concept: Proves that PostgreSQL's query optimizer inspects partition bounds
--          and completely prunes (skips) unneeded table partitions.
-- Execution Latency: ~0.69 ms
-- ============================================================================

-- Option 12A: Execution Plan Proof (Shows pruning of 'market_price_history_2025')
EXPLAIN ANALYZE
SELECT 
    i.ticker,
    mph.price_date,
    mph.nav_or_close
FROM market_price_history mph
JOIN instruments i ON mph.instrument_id = i.instrument_id
WHERE mph.price_date >= '2026-01-01';

-- Option 12B: Data Row Output (Run in SQL editor to view table records)
SELECT 
    i.ticker,
    i.name           AS instrument_name,
    mph.price_date,
    mph.nav_or_close AS closing_price
FROM market_price_history mph
JOIN instruments i ON mph.instrument_id = i.instrument_id
WHERE mph.price_date >= '2026-01-01'
ORDER BY mph.price_date DESC, i.ticker ASC;

-- EXAMINER DEFENSE:
-- In the EXPLAIN plan, you will observe an 'Append' scanning only
-- 'market_price_history_2026' and 'market_price_history_future'.
-- Notice that 'market_price_history_2025' is pruned out entirely.


-- ============================================================================
-- QUERY 13: Semi-Structured JSONB Querying with GIN Index
-- Concept: Schema-on-Read querying inside raw crawler HTTP payloads
--          stored in the Bronze Data Lake without rigid DDL migrations.
-- Execution Latency: ~1.2 ms
-- ============================================================================

-- Option 13A: Execution Plan Proof (Shows Bitmap Index Scan on GIN index)
EXPLAIN ANALYZE
SELECT 
    scrape_id,
    source_feed,
    ticker_or_scheme,
    raw_payload->>'scheme_code' AS scheme_code,
    raw_payload->>'nav'         AS scraped_nav,
    scraped_at
FROM raw_market_scrapes
WHERE raw_payload @> '{"source": "AMFI India Synthetic Sync"}';

-- Option 13B: Data Row Output (Extracts JSON keys into tabular output)
SELECT 
    scrape_id,
    source_feed,
    ticker_or_scheme,
    raw_payload->>'source'          AS feed_source,
    raw_payload->>'scheme_code'     AS scheme_code,
    raw_payload->>'date'            AS nav_date,
    (raw_payload->>'nav')::numeric  AS scraped_nav,
    scraped_at
FROM raw_market_scrapes
WHERE raw_payload @> '{"source": "AMFI India Synthetic Sync"}'
ORDER BY scrape_id ASC;

-- EXAMINER DEFENSE:
-- Shows the optimizer using 'Bitmap Index Scan on idx_raw_market_scrapes_gin'
-- using jsonb_path_ops for ultra-fast JSON containment (@>).


-- ============================================================================
-- QUERY 14: Analytical Window Function (Day-over-Day Return %)
-- Concept: In-database time-series window calculation using LAG and OVER()
--          partitioned by instrument across chronological price partitions.
-- ============================================================================
SELECT 
    i.ticker,
    i.name           AS instrument_name,
    mph.price_date,
    mph.nav_or_close AS current_price,
    LAG(mph.nav_or_close, 1) OVER (
        PARTITION BY mph.instrument_id 
        ORDER BY mph.price_date
    ) AS prev_close,
    ROUND(
        ((mph.nav_or_close - LAG(mph.nav_or_close, 1) OVER (PARTITION BY mph.instrument_id ORDER BY mph.price_date))
        / NULLIF(LAG(mph.nav_or_close, 1) OVER (PARTITION BY mph.instrument_id ORDER BY mph.price_date), 0)) * 100, 2
    ) AS daily_return_pct
FROM market_price_history mph
JOIN instruments i ON mph.instrument_id = i.instrument_id
ORDER BY mph.instrument_id, mph.price_date DESC;

-- EXAMINER DEFENSE:
-- LAG() accesses the immediately preceding row ordered chronologically within 
-- each instrument boundary without requiring expensive self-joins.


-- ============================================================================
-- QUERY 15: Multi-Dimensional OLAP Aggregation (ROLLUP Hierarchy)
-- Concept: Computes hierarchical grouping sets across multiple dimensions:
--          Asset Class -> Instrument Type -> Grand Total in a single query.
-- ============================================================================
SELECT 
    COALESCE(ac.name, '== ALL ASSET CLASSES (GRAND TOTAL) ==') AS asset_class,
    COALESCE(i.instrument_type, '== ALL SUB-TYPES ==')         AS instrument_type,
    COUNT(DISTINCT i.instrument_id)                            AS instruments_count,
    ROUND(AVG(mv.latest_price), 2)                             AS avg_price,
    ROUND(STDDEV(mv.latest_price), 2)                          AS price_spread_stddev
FROM instruments i
JOIN asset_classes ac ON i.asset_class_id = ac.asset_class_id
LEFT JOIN mv_instrument_performance_metrics mv ON i.instrument_id = mv.instrument_id
GROUP BY ROLLUP(ac.name, i.instrument_type)
ORDER BY ac.name NULLS LAST, i.instrument_type NULLS LAST;

-- EXAMINER DEFENSE:
-- ROLLUP generates n+1 grouping levels in a single scan:
-- (Asset Class, Type) -> (Asset Class) -> (). Ideal for executive dashboards.


-- ============================================================================
-- QUERY 16: Gold Tier Materialized View Non-Blocking Concurrent Refresh
-- Concept: Pre-computes 30-day statistics and executes REFRESH MATERIALIZED
--          VIEW CONCURRENTLY without locking out user read queries.
-- ============================================================================

-- Step A: Execute non-blocking concurrent refresh routine
SELECT sp_refresh_market_gold_layer();

-- Step B: Instant retrieval from pre-aggregated Gold Tier Materialized View
SELECT 
    asset_class,
    instrument_name,
    ticker,
    latest_price,
    avg_historical_price,
    price_volatility_stddev,
    data_points_count,
    latest_date
FROM mv_instrument_performance_metrics
ORDER BY asset_class, latest_price DESC;

-- EXAMINER DEFENSE:
-- REFRESH MATERIALIZED VIEW CONCURRENTLY uses the unique index on instrument_id
-- to apply diffs without taking an ExclusiveLock, enabling zero-downtime reads.


-- ============================================================================
-- QUERY 17: Stored Procedure for Data Warehouse ETL Refresh
-- Routine Name: sp_refresh_monthly_spending_facts(p_user_id TEXT)
-- Purpose: In-database batch aggregation for star schema fact tables.
--          Populates dimension tables and aggregates transactions into 
--          fact_monthly_spending_snapshots using INSERT ... ON CONFLICT DO UPDATE.
-- ============================================================================

-- Step 1: Ensure Stored Procedure is installed/updated
CREATE OR REPLACE PROCEDURE sp_refresh_monthly_spending_facts(p_user_id TEXT DEFAULT NULL)
LANGUAGE plpgsql
AS $$
DECLARE
    v_rows_affected INT := 0;
BEGIN
    -- 1. Populate calendar dimension for any newly encountered months
    INSERT INTO dim_month (month_key, calendar_year, calendar_month, month_name)
    SELECT DISTINCT 
        date_trunc('month', transaction_date)::date AS m_key,
        EXTRACT(YEAR FROM transaction_date)::int,
        EXTRACT(MONTH FROM transaction_date)::int,
        TO_CHAR(transaction_date, 'FMMonth')
    FROM financial_transactions
    WHERE (p_user_id IS NULL OR user_id = p_user_id)
    ON CONFLICT (month_key) DO NOTHING;

    -- 2. Incremental ETL aggregation from transactions into fact snapshots
    INSERT INTO fact_monthly_spending_snapshots
        (user_id, snapshot_month, income_amount, expense_amount, savings_amount, transaction_count, refreshed_at)
    SELECT 
        user_id,
        date_trunc('month', transaction_date)::date AS snapshot_month,
        SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END) AS income,
        SUM(CASE WHEN transaction_type = 'expense' THEN ABS(amount) ELSE 0 END) AS expense,
        SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE -ABS(amount) END) AS savings,
        COUNT(*) AS tx_count,
        NOW()
    FROM financial_transactions
    WHERE (p_user_id IS NULL OR user_id = p_user_id)
    GROUP BY user_id, date_trunc('month', transaction_date)::date
    ON CONFLICT (user_id, snapshot_month) DO UPDATE SET
        income_amount = EXCLUDED.income_amount,
        expense_amount = EXCLUDED.expense_amount,
        savings_amount = EXCLUDED.savings_amount,
        transaction_count = EXCLUDED.transaction_count,
        refreshed_at = NOW();

    GET DIAGNOSTICS v_rows_affected = ROW_COUNT;
    RAISE NOTICE 'sp_refresh_monthly_spending_facts: Refreshed % fact rows for user: %', v_rows_affected, COALESCE(p_user_id, 'ALL');
END;
$$;

-- Step 2: (Optional Seed) Ensure transaction records exist to aggregate:
INSERT INTO financial_transactions (user_id, transaction_date, description, amount, transaction_type, category, fingerprint)
VALUES 
    ('5D5p5KFmPiOJ4_--d7DtdA_u_3K187gv', '2026-08-01', 'Monthly Salary Credit', 85000.00, 'income', 'Salary', 'tx_fp_001'),
    ('5D5p5KFmPiOJ4_--d7DtdA_u_3K187gv', '2026-08-03', 'Apartment Rent', -25000.00, 'expense', 'Housing', 'tx_fp_002'),
    ('5D5p5KFmPiOJ4_--d7DtdA_u_3K187gv', '2026-08-10', 'Grocery Supermarket', -6500.00, 'expense', 'Food & Groceries', 'tx_fp_003'),
    ('5D5p5KFmPiOJ4_--d7DtdA_u_3K187gv', '2026-08-15', 'Electricity & Internet Bill', -3200.00, 'expense', 'Utilities', 'tx_fp_004'),
    ('5D5p5KFmPiOJ4_--d7DtdA_u_3K187gv', '2026-08-20', 'Stock Dividend Payout', 4200.00, 'income', 'Investments', 'tx_fp_005'),
    ('5D5p5KFmPiOJ4_--d7DtdA_u_3K187gv', '2026-09-01', 'Monthly Salary Credit', 85000.00, 'income', 'Salary', 'tx_fp_006'),
    ('5D5p5KFmPiOJ4_--d7DtdA_u_3K187gv', '2026-09-03', 'Apartment Rent', -25000.00, 'expense', 'Housing', 'tx_fp_007'),
    ('5D5p5KFmPiOJ4_--d7DtdA_u_3K187gv', '2026-09-12', 'Electronics & Gadgets', -12500.00, 'expense', 'Shopping', 'tx_fp_008'),
    ('5D5p5KFmPiOJ4_--d7DtdA_u_3K187gv', '2026-09-25', 'Restaurant & Dining', -4800.00, 'expense', 'Dining', 'tx_fp_009'),
    ('5D5p5KFmPiOJ4_--d7DtdA_u_3K187gv', '2026-10-01', 'Monthly Salary Credit', 85000.00, 'income', 'Salary', 'tx_fp_010')
ON CONFLICT (user_id, fingerprint) DO NOTHING;

-- Step 3: Execute Stored Procedure
CALL sp_refresh_monthly_spending_facts('5D5p5KFmPiOJ4_--d7DtdA_u_3K187gv');

-- Step 4: Verify Output from Data Warehouse Fact Table
SELECT 
    user_id,
    snapshot_month,
    income_amount,
    expense_amount,
    savings_amount,
    transaction_count,
    refreshed_at
FROM fact_monthly_spending_snapshots
ORDER BY snapshot_month DESC;


-- ============================================================================
-- QUERY 18: Analytical Function for Real-Time Portfolio Drift Detection
-- Routine Name: fn_detect_portfolio_drift(p_user_id TEXT)
-- Purpose: Evaluates live portfolio holdings against live market materialized 
--          views, compares current asset weights against target model allocations,
--          and returns structured JSONB rebalancing recommendations.
-- ============================================================================

-- Step 1: Ensure Function is installed/updated
CREATE OR REPLACE FUNCTION fn_detect_portfolio_drift(p_user_id TEXT)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_has_active BOOLEAN := FALSE;
    v_result JSONB;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM user_portfolios WHERE user_id = p_user_id AND is_active = TRUE
    ) INTO v_has_active;

    IF NOT v_has_active THEN
        RETURN jsonb_build_object('has_portfolio', FALSE, 'message', 'No active portfolio found.');
    END IF;

    WITH ActivePositions AS (
        SELECT 
            ac.asset_class_id,
            ac.name AS asset_class,
            upp.allocated_amount,
            ROUND(upp.allocated_amount * COALESCE(mv.latest_price / NULLIF(mv.avg_historical_price, 0), 1.0), 2) AS live_value
        FROM user_portfolios up
        JOIN user_portfolio_positions upp ON up.portfolio_id = upp.portfolio_id
        JOIN instruments i                ON upp.instrument_id = i.instrument_id
        JOIN asset_classes ac             ON i.asset_class_id = ac.asset_class_id
        LEFT JOIN mv_instrument_performance_metrics mv ON i.instrument_id = mv.instrument_id
        WHERE up.user_id = p_user_id AND up.is_active = TRUE
    ),
    ClassTotals AS (
        SELECT 
            asset_class_id,
            asset_class,
            SUM(allocated_amount) AS orig_amount,
            SUM(live_value)       AS live_amount,
            SUM(SUM(live_value)) OVER () AS total_live_val
        FROM ActivePositions
        GROUP BY asset_class_id, asset_class
    ),
    ModelTargets AS (
        SELECT 
            pa.asset_class_id,
            pa.allocation_percentage AS target_pct
        FROM user_profiles upr
        JOIN portfolio_models pm ON upr.risk_profile_id = pm.risk_profile_id
        JOIN portfolio_allocations pa ON pm.model_id = pa.model_id
        WHERE upr.user_id = p_user_id
    ),
    DriftAnalysis AS (
        SELECT 
            ct.asset_class,
            ct.orig_amount,
            ct.live_amount,
            ROUND((ct.live_amount / NULLIF(ct.total_live_val, 0)) * 100, 2) AS current_pct,
            COALESCE(mt.target_pct, 0) AS target_pct,
            ROUND(((ct.live_amount / NULLIF(ct.total_live_val, 0)) * 100) - COALESCE(mt.target_pct, 0), 2) AS drift_pct,
            CASE 
                WHEN ABS(((ct.live_amount / NULLIF(ct.total_live_val, 0)) * 100) - COALESCE(mt.target_pct, 0)) >= 5.0 
                THEN TRUE ELSE FALSE 
            END AS rebalance_flag
        FROM ClassTotals ct
        LEFT JOIN ModelTargets mt ON ct.asset_class_id = mt.asset_class_id
    )
    SELECT jsonb_build_object(
        'has_portfolio', TRUE,
        'user_id', p_user_id,
        'classes', jsonb_agg(
            jsonb_build_object(
                'asset_class', asset_class,
                'invested_amount', orig_amount,
                'live_market_value', live_amount,
                'current_weight_pct', current_pct,
                'target_weight_pct', target_pct,
                'drift_pct', drift_pct,
                'rebalance_required', rebalance_flag
            )
        ),
        'any_rebalance_required', bool_or(rebalance_flag)
    ) INTO v_result
    FROM DriftAnalysis;

    RETURN v_result;
END;
$$;

-- Step 2: Execute & Produce Output
-- Option 18A (Dynamic): Automatically runs for first active user
SELECT fn_detect_portfolio_drift((SELECT user_id FROM user_portfolios WHERE is_active = TRUE LIMIT 1));

-- Option 18B (Relational Flattened Output via LATERAL):
SELECT 
    p_drift.user_id,
    p_drift.has_portfolio,
    p_drift.any_rebalance_required,
    elem->>'asset_class'                    AS asset_class,
    (elem->>'invested_amount')::numeric     AS invested_amount,
    (elem->>'live_market_value')::numeric   AS live_market_value,
    (elem->>'current_weight_pct')::numeric  AS current_weight_pct,
    (elem->>'target_weight_pct')::numeric   AS target_weight_pct,
    (elem->>'drift_pct')::numeric           AS drift_pct,
    (elem->>'rebalance_required')::boolean  AS rebalance_required
FROM (
    SELECT fn_detect_portfolio_drift((SELECT user_id FROM user_portfolios WHERE is_active = TRUE LIMIT 1)) AS drift_json
) sub,
LATERAL jsonb_to_record(sub.drift_json) AS p_drift(user_id text, has_portfolio bool, any_rebalance_required bool, classes jsonb),
LATERAL jsonb_array_elements(p_drift.classes) AS elem;


-- ============================================================================
-- QUERY 19: Analytical Function for Multi-Vector Financial Health Score
-- Routine Name: fn_calculate_health_score(p_user_id TEXT)
-- Purpose: Evaluates 4 dimensions (Savings Rate, Diversification, Goals, Stability)
--          and returns a composite 0-100 financial health score.
-- ============================================================================

-- Step 1: Execute Function (for first user)
SELECT fn_calculate_health_score((SELECT user_id FROM user_profiles LIMIT 1));

-- Step 2: Flattened Relational Format
SELECT 
    hs.user_id,
    hs.final_health_score,
    hs.rating,
    (hs.breakdown->>'savings_score')::numeric         AS savings_score,
    (hs.breakdown->>'savings_rate_pct')::numeric      AS savings_rate_pct,
    (hs.breakdown->>'diversification_score')::numeric AS diversification_score,
    (hs.breakdown->>'asset_classes_held')::int        AS asset_classes_held,
    (hs.breakdown->>'goals_score')::numeric           AS goals_score,
    (hs.breakdown->>'active_goals_count')::int        AS active_goals_count,
    (hs.breakdown->>'stability_score')::numeric       AS stability_score
FROM (
    SELECT fn_calculate_health_score((SELECT user_id FROM user_profiles LIMIT 1)) AS raw_json
) sub,
LATERAL jsonb_to_record(sub.raw_json) AS hs(
    user_id text,
    final_health_score int,
    rating text,
    breakdown jsonb,
    evaluated_at timestamptz
);
