-- 0. FALLBACK: Mock Neon Auth if not enabled
CREATE SCHEMA IF NOT EXISTS neon_auth;
CREATE TABLE IF NOT EXISTS neon_auth.users_sync (
    id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- NOTE: neon_auth.users_sync is created and managed by Neon Auth.
-- If already present from Neon Auth, the above IF NOT EXISTS ensures no conflict.
-- All user_id columns are TEXT (UUID), not INT.

-- 1. RISK_PROFILES (seeded)
CREATE TABLE risk_profiles (
    risk_profile_id SERIAL PRIMARY KEY,
    profile_name    VARCHAR(50)  NOT NULL,
    min_score       INT          NOT NULL,
    max_score       INT          NOT NULL,
    description     TEXT
);

-- Local FinPulse identity (authentication is issued by FastAPI, not Neon Auth)
CREATE TABLE app_users (
    user_id TEXT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_salt TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 2. USER_PROFILES
CREATE TABLE user_profiles (
    profile_id               SERIAL PRIMARY KEY,
    user_id                  TEXT UNIQUE REFERENCES app_users(user_id) ON DELETE CASCADE,
    monthly_income           NUMERIC(12,2),
    monthly_expenses         NUMERIC(12,2),
    investment_amount        NUMERIC(12,2),
    investment_horizon_years INT,
    investment_goal          VARCHAR(100),
    risk_score               INT,
    risk_profile_id          INT REFERENCES risk_profiles(risk_profile_id),
    updated_at               TIMESTAMP DEFAULT NOW()
);

-- 3. ASSET_CLASSES (seeded)
CREATE TABLE asset_classes (
    asset_class_id SERIAL PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    description    TEXT
);

-- 4. PORTFOLIO_MODELS (seeded)
CREATE TABLE portfolio_models (
    model_id        SERIAL PRIMARY KEY,
    model_name      VARCHAR(100) NOT NULL,
    risk_profile_id INT REFERENCES risk_profiles(risk_profile_id),
    description     TEXT
);

-- 5. PORTFOLIO_ALLOCATIONS (seeded)
CREATE TABLE portfolio_allocations (
    allocation_id         SERIAL PRIMARY KEY,
    model_id              INT REFERENCES portfolio_models(model_id),
    asset_class_id        INT REFERENCES asset_classes(asset_class_id),
    allocation_percentage NUMERIC(5,2) NOT NULL,
    CONSTRAINT chk_pa_pct CHECK (allocation_percentage > 0 AND allocation_percentage <= 100)
);

-- 6. SUB_ALLOCATION_TEMPLATES (seeded)
CREATE TABLE sub_allocation_templates (
    template_id    SERIAL PRIMARY KEY,
    model_id       INT REFERENCES portfolio_models(model_id),
    asset_class_id INT REFERENCES asset_classes(asset_class_id)
);

-- 7. INSTRUMENTS (seeded)
CREATE TABLE instruments (
    instrument_id   SERIAL PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    ticker          VARCHAR(30),
    asset_class_id  INT REFERENCES asset_classes(asset_class_id),
    instrument_type VARCHAR(50),
    fund_house      VARCHAR(100),
    is_active       BOOLEAN DEFAULT TRUE
);

-- 8. INSTRUMENT_ALLOCATIONS (seeded)
CREATE TABLE instrument_allocations (
    inst_allocation_id    SERIAL PRIMARY KEY,
    template_id           INT REFERENCES sub_allocation_templates(template_id),
    instrument_id         INT REFERENCES instruments(instrument_id),
    allocation_percentage NUMERIC(5,2) NOT NULL
);

-- 9. USER_PORTFOLIOS
CREATE TABLE user_portfolios (
    portfolio_id     SERIAL PRIMARY KEY,
    user_id          TEXT REFERENCES app_users(user_id) ON DELETE CASCADE,
    model_id         INT  REFERENCES portfolio_models(model_id),
    total_investment NUMERIC(14,2) NOT NULL,
    is_active        BOOLEAN DEFAULT TRUE,
    version          INT     DEFAULT 1,
    generated_at     TIMESTAMP DEFAULT NOW()
);

-- 10. USER_PORTFOLIO_POSITIONS
CREATE TABLE user_portfolio_positions (
    position_id           SERIAL PRIMARY KEY,
    portfolio_id          INT REFERENCES user_portfolios(portfolio_id) ON DELETE CASCADE,
    instrument_id         INT REFERENCES instruments(instrument_id),
    allocation_percentage NUMERIC(5,2),
    allocated_amount      NUMERIC(14,2)
);

-- 11. INSTRUMENT_RETURNS (seeded)
CREATE TABLE instrument_returns (
    return_id          SERIAL PRIMARY KEY,
    instrument_id      INT REFERENCES instruments(instrument_id),
    period             VARCHAR(10) NOT NULL,
    return_percentage  NUMERIC(6,2),
    recorded_at        DATE DEFAULT CURRENT_DATE
);

-- 12. AUDIT_LOG (auto via trigger)
CREATE TABLE audit_log (
    log_id     SERIAL PRIMARY KEY,
    user_id    TEXT REFERENCES app_users(user_id),
    action     VARCHAR(100) NOT NULL,
    metadata   JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_user_profiles_user_id   ON user_profiles(user_id);
CREATE INDEX idx_user_portfolios_user_id  ON user_portfolios(user_id);
CREATE INDEX idx_portfolio_alloc_model    ON portfolio_allocations(model_id);
CREATE INDEX idx_positions_portfolio_id   ON user_portfolio_positions(portfolio_id);
CREATE INDEX idx_audit_user_id            ON audit_log(user_id);
CREATE INDEX idx_instr_returns_instrument ON instrument_returns(instrument_id);
