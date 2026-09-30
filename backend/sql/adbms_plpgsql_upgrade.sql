-- ============================================================================
-- 🏛️ FinPulse Advanced DBMS: PL/pgSQL Stored Procedures, Functions & Triggers
-- Demonstrates:
-- 1. Stored Procedure: Warehouse ETL aggregation (sp_refresh_monthly_spending_facts)
-- 2. Stored Function: Database-level Financial Health Score (fn_calculate_health_score)
-- 3. Stored Function: Portfolio Drift & Rebalancing Analyzer (fn_detect_portfolio_drift)
-- 4. Database Trigger: Real-time Fact Table Synchronization (trg_sync_spending_facts)
-- 5. Database Trigger: Data Lake Audit Logging (trg_audit_market_scrapes)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. STORED PROCEDURE: Warehouse ETL Refresh for Star Schema
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE sp_refresh_monthly_spending_facts(p_user_id TEXT DEFAULT NULL)
LANGUAGE plpgsql
AS $$
DECLARE
    v_rows_affected INT := 0;
BEGIN
    -- Step 1: Populate calendar dimension for any newly encountered months
    INSERT INTO dim_month (month_key, calendar_year, calendar_month, month_name)
    SELECT DISTINCT 
        date_trunc('month', transaction_date)::date AS m_key,
        EXTRACT(YEAR FROM transaction_date)::int,
        EXTRACT(MONTH FROM transaction_date)::int,
        TO_CHAR(transaction_date, 'FMMonth')
    FROM financial_transactions
    WHERE (p_user_id IS NULL OR user_id = p_user_id)
    ON CONFLICT (month_key) DO NOTHING;

    -- Step 2: Incremental ETL aggregation from curated transactions into fact snapshots
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


-- ----------------------------------------------------------------------------
-- 2. PL/pgSQL FUNCTION: Multi-Vector Financial Health Score (0 - 100)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_calculate_health_score(p_user_id TEXT)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_avg_income NUMERIC(14,2) := 0;
    v_avg_expense NUMERIC(14,2) := 0;
    v_avg_savings NUMERIC(14,2) := 0;
    v_savings_rate NUMERIC(5,2) := 0;
    v_asset_classes_count INT := 0;
    v_active_goals_count INT := 0;
    
    v_savings_score NUMERIC(5,2) := 0;      -- Max 35 pts
    v_diversification_score NUMERIC(5,2) := 0; -- Max 25 pts
    v_goals_score NUMERIC(5,2) := 0;         -- Max 20 pts
    v_stability_score NUMERIC(5,2) := 20.0;  -- Max 20 pts
    v_final_score INT := 0;
    v_grade VARCHAR(20);
BEGIN
    -- Factor 1: Savings Rate from Fact Table (Last 6 Months)
    SELECT 
        COALESCE(AVG(income_amount), 0),
        COALESCE(AVG(expense_amount), 0),
        COALESCE(AVG(savings_amount), 0)
    INTO v_avg_income, v_avg_expense, v_avg_savings
    FROM fact_monthly_spending_snapshots
    WHERE user_id = p_user_id
      AND snapshot_month >= (CURRENT_DATE - INTERVAL '6 months');

    IF v_avg_income > 0 THEN
        v_savings_rate := ROUND((v_avg_savings / v_avg_income) * 100, 2);
        IF v_savings_rate >= 30 THEN
            v_savings_score := 35.0;
        ELSIF v_savings_rate >= 20 THEN
            v_savings_score := 28.0;
        ELSIF v_savings_rate >= 10 THEN
            v_savings_score := 18.0;
        ELSE
            v_savings_score := 8.0;
        END IF;
    ELSE
        v_savings_score := 15.0; -- Default baseline
    END IF;

    -- Factor 2: Portfolio Diversification (Distinct Asset Classes in Active Portfolio)
    SELECT COUNT(DISTINCT ac.asset_class_id)
    INTO v_asset_classes_count
    FROM user_portfolios up
    JOIN user_portfolio_positions upp ON up.portfolio_id = upp.portfolio_id
    JOIN instruments i ON upp.instrument_id = i.instrument_id
    JOIN asset_classes ac ON i.asset_class_id = ac.asset_class_id
    WHERE up.user_id = p_user_id AND up.is_active = TRUE;

    IF v_asset_classes_count >= 4 THEN
        v_diversification_score := 25.0;
    ELSIF v_asset_classes_count >= 3 THEN
        v_diversification_score := 18.0;
    ELSIF v_asset_classes_count >= 2 THEN
        v_diversification_score := 12.0;
    ELSIF v_asset_classes_count = 1 THEN
        v_diversification_score := 5.0;
    ELSE
        v_diversification_score := 0.0;
    END IF;

    -- Factor 3: Financial Goals Target Coverage
    SELECT COUNT(*) INTO v_active_goals_count
    FROM financial_goals
    WHERE user_id = p_user_id AND is_active = TRUE;

    IF v_active_goals_count >= 3 THEN
        v_goals_score := 20.0;
    ELSIF v_active_goals_count >= 1 THEN
        v_goals_score := 14.0;
    ELSE
        v_goals_score := 5.0;
    END IF;

    -- Total Score Computation
    v_final_score := LEAST(100, GREATEST(0, ROUND(v_savings_score + v_diversification_score + v_goals_score + v_stability_score)::int));

    IF v_final_score >= 80 THEN
        v_grade := 'Excellent';
    ELSIF v_final_score >= 65 THEN
        v_grade := 'Good';
    ELSIF v_final_score >= 50 THEN
        v_grade := 'Moderate';
    ELSE
        v_grade := 'Needs Attention';
    END IF;

    RETURN jsonb_build_object(
        'user_id', p_user_id,
        'final_health_score', v_final_score,
        'rating', v_grade,
        'breakdown', jsonb_build_object(
            'savings_score', v_savings_score,
            'savings_rate_pct', v_savings_rate,
            'diversification_score', v_diversification_score,
            'asset_classes_held', v_asset_classes_count,
            'goals_score', v_goals_score,
            'active_goals_count', v_active_goals_count,
            'stability_score', v_stability_score
        ),
        'evaluated_at', NOW()
    );
END;
$$;


-- ----------------------------------------------------------------------------
-- 3. PL/pgSQL FUNCTION: Real-Time Portfolio Drift & Rebalancing Recommendations
-- ----------------------------------------------------------------------------
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
        JOIN instruments i ON upp.instrument_id = i.instrument_id
        JOIN asset_classes ac ON i.asset_class_id = ac.asset_class_id
        LEFT JOIN mv_instrument_performance_metrics mv ON i.instrument_id = mv.instrument_id
        WHERE up.user_id = p_user_id AND up.is_active = TRUE
    ),
    ClassTotals AS (
        SELECT 
            asset_class_id,
            asset_class,
            SUM(allocated_amount) AS orig_amount,
            SUM(live_value) AS live_amount,
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


-- ----------------------------------------------------------------------------
-- 4. DATABASE TRIGGER: Real-time Fact Synchronization on Transaction Ingestion
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_trg_sync_spending_facts()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_target_user TEXT;
BEGIN
    v_target_user := COALESCE(NEW.user_id, OLD.user_id);
    
    -- Automatically execute warehouse ETL procedure for the affected user
    CALL sp_refresh_monthly_spending_facts(v_target_user);
    
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_sync_spending_facts ON financial_transactions;

CREATE TRIGGER trg_sync_spending_facts
AFTER INSERT OR UPDATE OR DELETE ON financial_transactions
FOR EACH ROW
EXECUTE FUNCTION fn_trg_sync_spending_facts();


-- ----------------------------------------------------------------------------
-- 5. DATABASE TRIGGER: Data Lake Audit Logging on Raw Scrape Ingestion
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_trg_audit_market_scrapes()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO audit_log (user_id, action, metadata)
    VALUES (
        'SYSTEM_CRAWLER',
        'MARKET_DATA_INGESTED',
        jsonb_build_object(
            'scrape_id', NEW.scrape_id,
            'source_feed', NEW.source_feed,
            'ticker_or_scheme', NEW.ticker_or_scheme,
            'http_status', NEW.http_status,
            'payload_bytes', length(NEW.raw_payload::text)
        )
    );
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_audit_market_scrapes ON raw_market_scrapes;

CREATE TRIGGER trg_audit_market_scrapes
AFTER INSERT ON raw_market_scrapes
FOR EACH ROW
EXECUTE FUNCTION fn_trg_audit_market_scrapes();
