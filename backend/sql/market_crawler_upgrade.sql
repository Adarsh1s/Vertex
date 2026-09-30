-- ============================================================================
-- FinPulse: Market Crawler & Advanced DBMS Lakehouse Upgrade (Phase 1)
-- Multi-Tier Architecture:
-- 1. Bronze Tier: Unstructured Scrape Data Lake (JSONB + GIN)
-- 2. Silver Tier: Declaratively Partitioned Time-Series Store (BRIN + Composite PK)
-- 3. Gold Tier:   Materialized View OLAP Layer + Refresh Stored Procedure
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. BRONZE TIER: Semi-Structured Raw Web Scrape Lake
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_market_scrapes (
    scrape_id BIGSERIAL PRIMARY KEY,
    source_feed VARCHAR(50) NOT NULL, -- e.g. 'AMFI_NAV', 'YAHOO_FINANCE', 'SCREENER'
    ticker_or_scheme VARCHAR(50),
    http_status INT NOT NULL DEFAULT 200,
    raw_payload JSONB NOT NULL,
    scraped_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Generalized Inverted Index (GIN) using jsonb_path_ops for lightning-fast subdocument containment search
CREATE INDEX IF NOT EXISTS idx_raw_market_scrapes_gin 
ON raw_market_scrapes USING GIN (raw_payload jsonb_path_ops);

CREATE INDEX IF NOT EXISTS idx_raw_market_scrapes_time 
ON raw_market_scrapes (scraped_at DESC);

-- ----------------------------------------------------------------------------
-- 2. SILVER TIER: Declaratively Partitioned Time-Series Table
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS market_price_history (
    instrument_id INT NOT NULL REFERENCES instruments(instrument_id) ON DELETE CASCADE,
    price_date DATE NOT NULL,
    nav_or_close NUMERIC(12, 4) NOT NULL,
    day_high NUMERIC(12, 4),
    day_low NUMERIC(12, 4),
    volume BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (instrument_id, price_date)
) PARTITION BY RANGE (price_date);

-- Yearly Partitions
CREATE TABLE IF NOT EXISTS market_price_history_2025 
PARTITION OF market_price_history
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE IF NOT EXISTS market_price_history_2026 
PARTITION OF market_price_history
FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE TABLE IF NOT EXISTS market_price_history_future 
PARTITION OF market_price_history
FOR VALUES FROM ('2027-01-01') TO ('2030-01-01');

-- BRIN (Block Range Index) on date column: orders of magnitude smaller than B-tree for time-series append workloads
CREATE INDEX IF NOT EXISTS idx_market_price_brin 
ON market_price_history USING BRIN (price_date);

-- Composite B-Tree index for per-instrument chronological range queries
CREATE INDEX IF NOT EXISTS idx_market_price_inst_date 
ON market_price_history (instrument_id, price_date DESC);

-- ----------------------------------------------------------------------------
-- 3. SEED BASELINE HISTORICAL PRICES (2025 & 2026 Baseline data points)
-- ----------------------------------------------------------------------------
INSERT INTO market_price_history (instrument_id, price_date, nav_or_close, day_high, day_low, volume)
VALUES
    -- 2025 Partitions
    (1, '2025-10-01', 25100.50, 25250.00, 25050.00, 1500000),
    (2, '2025-10-01', 115.40, 116.20, 114.90, 85000),
    (3, '2025-10-01', 78.50, 79.10, 78.00, 120000),
    (4, '2025-10-01', 165.20, 166.80, 164.50, 95000),
    (5, '2025-10-01', 42.10, 42.15, 42.05, 45000),
    (6, '2025-10-01', 31.80, 31.85, 31.75, 30000),
    (7, '2025-10-01', 38.90, 39.00, 38.80, 25000),
    (8, '2025-10-01', 1002.50, 1002.60, 1002.40, 500000),
    (9, '2025-10-01', 72.80, 73.50, 72.40, 320000),
    (10, '2025-10-01', 7450.00, 7500.00, 7420.00, 12000),
    (11, '2025-10-01', 148.20, 149.50, 147.80, 210000),
    (12, '2025-10-01', 98.40, 99.60, 97.90, 140000),
    (13, '2025-10-01', 64.20, 65.00, 63.80, 78000),
    (14, '2025-10-01', 375.00, 380.00, 372.00, 60000),

    -- 2026 Partitions
    (1, '2026-01-05', 25650.00, 25800.00, 25550.00, 1800000),
    (2, '2026-01-05', 120.10, 121.00, 119.50, 92000),
    (3, '2026-01-05', 84.20, 85.00, 83.80, 135000),
    (4, '2026-01-05', 178.60, 180.20, 177.50, 110000),
    (5, '2026-01-05', 43.20, 43.25, 43.15, 48000),
    (6, '2026-01-05', 32.50, 32.55, 32.45, 33000),
    (7, '2026-01-05', 40.10, 40.20, 40.00, 28000),
    (8, '2026-01-05', 1018.00, 1018.15, 1017.90, 550000),
    (9, '2026-01-05', 77.40, 78.20, 77.00, 360000),
    (10, '2026-01-05', 7850.00, 7920.00, 7810.00, 15000),
    (11, '2026-01-05', 162.50, 164.00, 161.80, 240000),
    (12, '2026-01-05', 108.90, 110.50, 108.00, 165000),
    (13, '2026-01-05', 71.30, 72.20, 70.80, 85000),
    (14, '2026-01-05', 392.00, 396.50, 389.00, 68000)
ON CONFLICT (instrument_id, price_date) DO NOTHING;

-- ----------------------------------------------------------------------------
-- 4. GOLD TIER: Analytical Materialized View
-- ----------------------------------------------------------------------------
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_instrument_performance_metrics AS
SELECT 
    i.instrument_id,
    i.name AS instrument_name,
    i.ticker,
    ac.name AS asset_class,
    i.instrument_type,
    COALESCE(MAX(mph.price_date), CURRENT_DATE) AS latest_date,
    COALESCE((ARRAY_AGG(mph.nav_or_close ORDER BY mph.price_date DESC))[1], 100.0000) AS latest_price,
    COALESCE(ROUND(AVG(mph.nav_or_close), 2), 100.00) AS avg_historical_price,
    COALESCE(ROUND(STDDEV(mph.nav_or_close), 4), 0.0000) AS price_volatility_stddev,
    COUNT(mph.price_date) AS data_points_count
FROM instruments i
JOIN asset_classes ac ON i.asset_class_id = ac.asset_class_id
LEFT JOIN market_price_history mph ON i.instrument_id = mph.instrument_id
GROUP BY i.instrument_id, i.name, i.ticker, ac.name, i.instrument_type;

-- Unique index required for CONCURRENT refresh (non-blocking OLAP reads)
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_inst_metrics_id 
ON mv_instrument_performance_metrics(instrument_id);

-- ----------------------------------------------------------------------------
-- 5. STORED PROCEDURE / FUNCTION: Refresh Gold Layer
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION sp_refresh_market_gold_layer()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_instrument_performance_metrics;
END;
$$ LANGUAGE plpgsql;
