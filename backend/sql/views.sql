CREATE OR REPLACE VIEW user_portfolio_summary AS
SELECT
    up.user_id                AS user_id,
    COALESCE(u.name, 'User')  AS user_name,
    up.portfolio_id,
    up.version,
    up.is_active,
    up.total_investment,
    up.generated_at,
    pm.model_name,
    rp.profile_name           AS risk_profile,
    ac.name                   AS asset_class,
    i.instrument_id,
    i.name                    AS instrument_name,
    i.ticker,
    i.instrument_type,
    upp.allocation_percentage,
    upp.allocated_amount
FROM user_portfolios up
LEFT JOIN app_users u             ON u.user_id = up.user_id
JOIN portfolio_models pm          ON pm.model_id = up.model_id
JOIN risk_profiles rp             ON rp.risk_profile_id = pm.risk_profile_id
JOIN user_portfolio_positions upp ON upp.portfolio_id = up.portfolio_id
JOIN instruments i                ON i.instrument_id = upp.instrument_id
JOIN asset_classes ac             ON ac.asset_class_id = i.asset_class_id;
