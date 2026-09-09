-- 1. Complex JOIN with GROUP BY: Portfolio Summary by User and Asset Class
-- This query aggregates the total amount invested by each user in every asset class.
SELECT 
    u.name AS user_name,
    ac.name AS asset_class,
    SUM(upp.allocated_amount) AS total_invested
FROM neon_auth.users_sync u
JOIN user_portfolios up ON u.id = up.user_id AND up.is_active = TRUE
JOIN user_portfolio_positions upp ON up.portfolio_id = upp.portfolio_id
JOIN instruments i ON upp.instrument_id = i.instrument_id
JOIN asset_classes ac ON i.asset_class_id = ac.asset_class_id
GROUP BY u.name, ac.name
ORDER BY u.name, total_invested DESC;

-- 2. Subquery and Window Function: Determining User Risk Deviation
-- Compares a user's actual risk score with the average risk score of all users in the same risk profile.
SELECT 
    u.name,
    rp.profile_name,
    up.risk_score AS actual_score,
    ROUND(AVG(up.risk_score) OVER(PARTITION BY rp.risk_profile_id), 2) AS avg_profile_score,
    up.risk_score - AVG(up.risk_score) OVER(PARTITION BY rp.risk_profile_id) AS deviation_from_avg
FROM user_profiles up
JOIN neon_auth.users_sync u ON up.user_id = u.id
JOIN risk_profiles rp ON up.risk_profile_id = rp.risk_profile_id;

-- 3. CTE (Common Table Expression): Blended Historical Return for a Model
-- Calculates the estimated 1Y return for 'Balanced Growth Model' based on its allocations.
WITH ModelAllocations AS (
    SELECT 
        ia.instrument_id,
        (pa.allocation_percentage * ia.allocation_percentage) / 100 AS true_weight
    FROM portfolio_models pm
    JOIN portfolio_allocations pa ON pm.model_id = pa.model_id
    JOIN sub_allocation_templates sat ON sat.model_id = pm.model_id AND sat.asset_class_id = pa.asset_class_id
    JOIN instrument_allocations ia ON ia.template_id = sat.template_id
    WHERE pm.model_name = 'Balanced Growth Model'
)
SELECT 
    SUM((ma.true_weight * ir.return_percentage) / 100) AS blended_1Y_return
FROM ModelAllocations ma
JOIN instrument_returns ir ON ma.instrument_id = ir.instrument_id
WHERE ir.period = '1Y';

-- 4. Rollup / Cube: Investment Distribution across Types
-- Provides a rollup report showing subtotals by Asset Class and grand total.
SELECT 
    COALESCE(ac.name, 'ALL ASSET CLASSES') AS asset_class,
    COALESCE(i.instrument_type, 'ALL TYPES') AS instrument_type,
    SUM(upp.allocated_amount) AS total_amount
FROM user_portfolio_positions upp
JOIN instruments i ON upp.instrument_id = i.instrument_id
JOIN asset_classes ac ON i.asset_class_id = ac.asset_class_id
GROUP BY ROLLUP(ac.name, i.instrument_type);

-- 5. Using the Custom Trigger Audit Data: Action Velocity
-- Analyzes how many portfolios were generated per user in the last 7 days.
SELECT 
    u.name,
    COUNT(al.log_id) AS portfolio_generations,
    MAX(al.created_at) AS last_generated
FROM audit_log al
JOIN neon_auth.users_sync u ON al.user_id = u.id
WHERE al.action = 'PORTFOLIO_GENERATED'
AND al.created_at >= NOW() - INTERVAL '7 days'
GROUP BY u.name
HAVING COUNT(al.log_id) > 1;
