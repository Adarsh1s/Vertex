-- Replaces Neon Auth as the application identity provider.
-- Existing investment data remains intact; only its user foreign keys are repointed.
CREATE TABLE IF NOT EXISTS app_users (
    user_id TEXT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_salt TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS user_profiles_user_id_fkey;
ALTER TABLE user_portfolios DROP CONSTRAINT IF EXISTS user_portfolios_user_id_fkey;
ALTER TABLE audit_log DROP CONSTRAINT IF EXISTS audit_log_user_id_fkey;
ALTER TABLE raw_data_imports DROP CONSTRAINT IF EXISTS raw_data_imports_user_id_fkey;
ALTER TABLE financial_transactions DROP CONSTRAINT IF EXISTS financial_transactions_user_id_fkey;
ALTER TABLE fact_monthly_spending_snapshots DROP CONSTRAINT IF EXISTS fact_monthly_spending_snapshots_user_id_fkey;
ALTER TABLE fact_monthly_portfolio_snapshots DROP CONSTRAINT IF EXISTS fact_monthly_portfolio_snapshots_user_id_fkey;
ALTER TABLE financial_goals DROP CONSTRAINT IF EXISTS financial_goals_user_id_fkey;

ALTER TABLE user_profiles ADD CONSTRAINT user_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES app_users(user_id) ON DELETE CASCADE;
ALTER TABLE user_portfolios ADD CONSTRAINT user_portfolios_user_id_fkey FOREIGN KEY (user_id) REFERENCES app_users(user_id) ON DELETE CASCADE;
ALTER TABLE audit_log ADD CONSTRAINT audit_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES app_users(user_id) ON DELETE CASCADE;
ALTER TABLE raw_data_imports ADD CONSTRAINT raw_data_imports_user_id_fkey FOREIGN KEY (user_id) REFERENCES app_users(user_id) ON DELETE CASCADE;
ALTER TABLE financial_transactions ADD CONSTRAINT financial_transactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES app_users(user_id) ON DELETE CASCADE;
ALTER TABLE fact_monthly_spending_snapshots ADD CONSTRAINT fact_monthly_spending_snapshots_user_id_fkey FOREIGN KEY (user_id) REFERENCES app_users(user_id) ON DELETE CASCADE;
ALTER TABLE fact_monthly_portfolio_snapshots ADD CONSTRAINT fact_monthly_portfolio_snapshots_user_id_fkey FOREIGN KEY (user_id) REFERENCES app_users(user_id) ON DELETE CASCADE;
ALTER TABLE financial_goals ADD CONSTRAINT financial_goals_user_id_fkey FOREIGN KEY (user_id) REFERENCES app_users(user_id) ON DELETE CASCADE;
