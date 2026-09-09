-- FinPulse upgrade: run once after schema.sql, views.sql, triggers_functions.sql and seed.sql.
-- The landing + staging tables form a lightweight data lake; the fact tables are the analytics warehouse.

CREATE TABLE IF NOT EXISTS raw_data_imports (
    import_id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES neon_auth.users_sync(id) ON DELETE CASCADE,
    source_file_name VARCHAR(255) NOT NULL,
    source_type VARCHAR(40) NOT NULL DEFAULT 'bank_csv',
    status VARCHAR(30) NOT NULL DEFAULT 'completed',
    total_rows INT NOT NULL DEFAULT 0,
    accepted_rows INT NOT NULL DEFAULT 0,
    rejected_rows INT NOT NULL DEFAULT 0,
    imported_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stg_transaction_rows (
    staging_id BIGSERIAL PRIMARY KEY,
    import_id INT NOT NULL REFERENCES raw_data_imports(import_id) ON DELETE CASCADE,
    row_number INT NOT NULL,
    raw_row JSONB NOT NULL,
    validation_error TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS financial_transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES neon_auth.users_sync(id) ON DELETE CASCADE,
    import_id INT REFERENCES raw_data_imports(import_id) ON DELETE SET NULL,
    transaction_date DATE NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC(14,2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('income', 'expense')),
    category VARCHAR(80) NOT NULL DEFAULT 'Uncategorized',
    fingerprint VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, fingerprint)
);

CREATE TABLE IF NOT EXISTS dim_month (
    month_key DATE PRIMARY KEY,
    calendar_year INT NOT NULL,
    calendar_month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_monthly_spending_snapshots (
    user_id TEXT NOT NULL REFERENCES neon_auth.users_sync(id) ON DELETE CASCADE,
    snapshot_month DATE NOT NULL REFERENCES dim_month(month_key),
    income_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    expense_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    savings_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    transaction_count INT NOT NULL DEFAULT 0,
    refreshed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, snapshot_month)
);

CREATE TABLE IF NOT EXISTS fact_monthly_portfolio_snapshots (
    user_id TEXT NOT NULL REFERENCES neon_auth.users_sync(id) ON DELETE CASCADE,
    snapshot_month DATE NOT NULL REFERENCES dim_month(month_key),
    portfolio_id INT REFERENCES user_portfolios(portfolio_id) ON DELETE SET NULL,
    portfolio_value NUMERIC(14,2) NOT NULL,
    asset_class_count INT NOT NULL DEFAULT 0,
    largest_allocation_pct NUMERIC(5,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, snapshot_month)
);

CREATE TABLE IF NOT EXISTS financial_goals (
    goal_id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES neon_auth.users_sync(id) ON DELETE CASCADE,
    goal_name VARCHAR(120) NOT NULL,
    target_amount NUMERIC(14,2) NOT NULL CHECK (target_amount > 0),
    current_amount NUMERIC(14,2) NOT NULL DEFAULT 0 CHECK (current_amount >= 0),
    target_date DATE NOT NULL,
    expected_return_pct NUMERIC(5,2) NOT NULL DEFAULT 8.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_imports_user_id ON raw_data_imports(user_id, imported_at DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON financial_transactions(user_id, transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_staging_import ON stg_transaction_rows(import_id);

-- Seed missing month dimensions for the past/next five years.
INSERT INTO dim_month (month_key, calendar_year, calendar_month, month_name)
SELECT d::date, EXTRACT(YEAR FROM d)::int, EXTRACT(MONTH FROM d)::int, TO_CHAR(d, 'FMMonth')
FROM generate_series(date_trunc('month', CURRENT_DATE) - INTERVAL '5 years',
                     date_trunc('month', CURRENT_DATE) + INTERVAL '5 years', INTERVAL '1 month') d
ON CONFLICT (month_key) DO NOTHING;
