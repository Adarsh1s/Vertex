CREATE OR REPLACE FUNCTION get_risk_profile_id(p_score INT)
RETURNS INT AS $$
DECLARE v_profile_id INT;
BEGIN
    SELECT risk_profile_id INTO v_profile_id
    FROM risk_profiles
    WHERE p_score BETWEEN min_score AND max_score
    LIMIT 1;
    RETURN v_profile_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION fn_audit_portfolio_generation()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (user_id, action, metadata)
    VALUES (
        NEW.user_id,
        'PORTFOLIO_GENERATED',
        jsonb_build_object(
            'portfolio_id',    NEW.portfolio_id,
            'model_id',        NEW.model_id,
            'version',         NEW.version,
            'total_investment', NEW.total_investment
        )
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_portfolio
AFTER INSERT ON user_portfolios
FOR EACH ROW EXECUTE FUNCTION fn_audit_portfolio_generation();
