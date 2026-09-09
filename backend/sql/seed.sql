-- 1. RISK PROFILES
INSERT INTO risk_profiles (risk_profile_id, profile_name, min_score, max_score, description) VALUES
(1, 'Conservative', 0, 25, 'Focus on capital preservation with minimal risk.'),
(2, 'Moderately Conservative', 26, 50, 'Balanced approach leaning towards safety.'),
(3, 'Moderate', 51, 75, 'Balanced growth and risk.'),
(4, 'Aggressive', 76, 100, 'High growth potential, accepts significant volatility.');

-- 2. ASSET CLASSES
INSERT INTO asset_classes (asset_class_id, name, description) VALUES
(1, 'Equity', 'Stocks and equity mutual funds'),
(2, 'Debt', 'Bonds and debt funds'),
(3, 'Gold', 'Physical gold, Gold ETFs or SGBs'),
(4, 'Cash', 'Liquid funds and cash equivalents'),
(5, 'International', 'Global equity and foreign assets'),
(6, 'Real Estate', 'REITs and property-backed securities');

-- 3. PORTFOLIO MODELS
INSERT INTO portfolio_models (model_id, model_name, risk_profile_id, description) VALUES
(1, 'Capital Preservation Model', 1, 'Designed for zero to low risk investors.'),
(2, 'Cautious Growth Model', 2, 'For low to moderate risk investors.'),
(3, 'Balanced Growth Model', 3, 'For moderate risk investors.'),
(4, 'High Growth Model', 4, 'For aggressive investors seeking maximum returns.');

-- 4. PORTFOLIO ALLOCATIONS
-- Conservative: 20% Equity, 60% Debt, 10% Gold, 10% Cash
INSERT INTO portfolio_allocations (model_id, asset_class_id, allocation_percentage) VALUES
(1, 1, 20.00), (1, 2, 60.00), (1, 3, 10.00), (1, 4, 10.00);

-- Moderately Conservative: 40% Equity, 40% Debt, 10% Gold, 10% Cash
INSERT INTO portfolio_allocations (model_id, asset_class_id, allocation_percentage) VALUES
(2, 1, 40.00), (2, 2, 40.00), (2, 3, 10.00), (2, 4, 10.00);

-- Moderate: 60% Equity, 25% Debt, 10% Gold, 5% Cash
INSERT INTO portfolio_allocations (model_id, asset_class_id, allocation_percentage) VALUES
(3, 1, 60.00), (3, 2, 25.00), (3, 3, 10.00), (3, 4, 5.00);

-- Aggressive: 80% Equity, 10% Debt, 5% Gold, 5% International
INSERT INTO portfolio_allocations (model_id, asset_class_id, allocation_percentage) VALUES
(4, 1, 80.00), (4, 2, 10.00), (4, 3, 5.00), (4, 5, 5.00);

-- 5. MEASURES / SUB-ALLOCATIONS TEMPLATES
-- Model 1
INSERT INTO sub_allocation_templates (template_id, model_id, asset_class_id) VALUES
(1, 1, 1), (2, 1, 2), (3, 1, 3), (4, 1, 4);

-- Model 2
INSERT INTO sub_allocation_templates (template_id, model_id, asset_class_id) VALUES
(5, 2, 1), (6, 2, 2), (7, 2, 3), (8, 2, 4);

-- Model 3
INSERT INTO sub_allocation_templates (template_id, model_id, asset_class_id) VALUES
(9, 3, 1), (10, 3, 2), (11, 3, 3), (12, 3, 4);

-- Model 4
INSERT INTO sub_allocation_templates (template_id, model_id, asset_class_id) VALUES
(13, 4, 1), (14, 4, 2), (15, 4, 3), (16, 4, 5);

-- 6. INSTRUMENTS
INSERT INTO instruments (instrument_id, name, ticker, asset_class_id, instrument_type, fund_house, is_active) VALUES
(1, 'Nifty 50 Index Fund - Direct', 'NIFTY50IDX', 1, 'Index Fund', 'Multiple', TRUE),
(2, 'Mirae Asset Large Cap Fund', 'MIRAELC', 1, 'Mutual Fund', 'Mirae Asset', TRUE),
(3, 'Parag Parikh Flexi Cap Fund', 'PPFCF', 1, 'Mutual Fund', 'PPFAS', TRUE),
(4, 'HDFC Mid-Cap Opportunities Fund', 'HDFCMCAP', 1, 'Mutual Fund', 'HDFC', TRUE),
(5, 'SBI Corporate Bond Fund', 'SBICORP', 2, 'Mutual Fund', 'SBI', TRUE),
(6, 'HDFC Short Term Debt Fund', 'HDFCSTD', 2, 'Mutual Fund', 'HDFC', TRUE),
(7, 'Kotak Dynamic Bond Fund', 'KOTAKDYN', 2, 'Mutual Fund', 'Kotak', TRUE),
(8, 'Nippon India Liquid Fund', 'NIPPONLIQ', 4, 'Liquid Fund', 'Nippon India', TRUE),
(9, 'Nippon India Gold ETF', 'GOLDBEES', 3, 'ETF', 'Nippon India', TRUE),
(10, 'Sovereign Gold Bond 2026', 'SGB2026', 3, 'Govt Bond', 'RBI', TRUE),
(11, 'Motilal Oswal Nasdaq 100 ETF', 'MON100', 5, 'ETF', 'Motilal Oswal', TRUE),
(12, 'Embassy Office Parks REIT', 'EMBASSY', 6, 'REIT', 'Embassy', TRUE),
(13, 'SBI Liquid Fund', 'SBILIQ', 4, 'Liquid Fund', 'SBI', TRUE),
(14, 'SBI Gold Fund', 'SBIGOLD', 3, 'Mutual Fund', 'SBI', TRUE);

-- 7. INSTRUMENT ALLOCATIONS
-- Template 1 (Model 1 Equity): 100% Nifty 50
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (1, 1, 100.00);
-- Template 2 (Model 1 Debt): 50% SBI Corp, 50% HDFC STD
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (2, 5, 50.00), (2, 6, 50.00);
-- Template 3 (Model 1 Gold): 100% SGB
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (3, 10, 100.00);
-- Template 4 (Model 1 Cash): 100% Nippon Liq
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (4, 8, 100.00);

-- Template 5 (Model 2 Equity): 50% Nifty 50, 50% Mirae LC
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (5, 1, 50.00), (5, 2, 50.00);
-- Template 6 (Model 2 Debt): 50% SBI Corp, 50% Kotak Dyn
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (6, 5, 50.00), (6, 7, 50.00);
-- Template 7 (Model 2 Gold): 50% Nippon Gold, 50% SGB
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (7, 9, 50.00), (7, 10, 50.00);
-- Template 8 (Model 2 Cash): 100% SBI Liquid
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (8, 13, 100.00);

-- Template 9 (Model 3 Equity): 40% Nifty 50, 40% PPFCF, 20% HDFC Midcap
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (9, 1, 40.00), (9, 3, 40.00), (9, 4, 20.00);
-- Template 10 (Model 3 Debt): 100% SBI Corp
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (10, 5, 100.00);
-- Template 11 (Model 3 Gold): 100% Nippon Gold ETF
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (11, 9, 100.00);
-- Template 12 (Model 3 Cash): 100% Nippon Liq
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (12, 8, 100.00);

-- Template 13 (Model 4 Equity): 30% Nifty 50, 40% PPFCF, 30% HDFC Midcap
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (13, 1, 30.00), (13, 3, 40.00), (13, 4, 30.00);
-- Template 14 (Model 4 Debt): 100% Kotak Dyn
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (14, 7, 100.00);
-- Template 15 (Model 4 Gold): 100% Nippon Gold ETF
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (15, 9, 100.00);
-- Template 16 (Model 4 Intl): 100% MON100
INSERT INTO instrument_allocations (template_id, instrument_id, allocation_percentage) VALUES (16, 11, 100.00);

-- 8. RETURNS
-- Nifty 50 (1)
INSERT INTO instrument_returns (instrument_id, period, return_percentage) VALUES (1, '1Y', 24.5), (1, '3Y', 15.2), (1, '5Y', 14.8);
-- Mirae LC (2)
INSERT INTO instrument_returns (instrument_id, period, return_percentage) VALUES (2, '1Y', 22.1), (2, '3Y', 14.5), (2, '5Y', 14.1);
-- PPFCF (3)
INSERT INTO instrument_returns (instrument_id, period, return_percentage) VALUES (3, '1Y', 28.5), (3, '3Y', 18.2), (3, '5Y', 19.5);
-- HDFC Midcap (4)
INSERT INTO instrument_returns (instrument_id, period, return_percentage) VALUES (4, '1Y', 35.1), (4, '3Y', 22.4), (4, '5Y', 20.1);
-- SBI Corp (5)
INSERT INTO instrument_returns (instrument_id, period, return_percentage) VALUES (5, '1Y', 7.5), (5, '3Y', 6.8), (5, '5Y', 7.2);
-- HDFC STD (6)
INSERT INTO instrument_returns (instrument_id, period, return_percentage) VALUES (6, '1Y', 7.2), (6, '3Y', 6.5), (6, '5Y', 6.9);
-- Kotak Dyn (7)
INSERT INTO instrument_returns (instrument_id, period, return_percentage) VALUES (7, '1Y', 8.1), (7, '3Y', 7.1), (7, '5Y', 7.8);
-- Nippon Liq (8)
INSERT INTO instrument_returns (instrument_id, period, return_percentage) VALUES (8, '1Y', 6.8), (8, '3Y', 5.5), (8, '5Y', 5.2);
-- Nippon Gold ETF (9)
INSERT INTO instrument_returns (instrument_id, period, return_percentage) VALUES (9, '1Y', 12.5), (9, '3Y', 8.2), (9, '5Y', 10.5);
-- SGB (10)
INSERT INTO instrument_returns (instrument_id, period, return_percentage) VALUES (10, '1Y', 12.5), (10, '3Y', 8.2), (10, '5Y', 10.5); 
-- MON100 (11)
INSERT INTO instrument_returns (instrument_id, period, return_percentage) VALUES (11, '1Y', 45.2), (11, '3Y', 18.5), (11, '5Y', 22.1);
-- Embassy (12)
INSERT INTO instrument_returns (instrument_id, period, return_percentage) VALUES (12, '1Y', 15.6), (12, '3Y', 12.1), (12, '5Y', 11.5);
-- SBI Liq (13)
INSERT INTO instrument_returns (instrument_id, period, return_percentage) VALUES (13, '1Y', 6.7), (13, '3Y', 5.4), (13, '5Y', 5.1);
-- SBI Gold (14)
INSERT INTO instrument_returns (instrument_id, period, return_percentage) VALUES (14, '1Y', 12.1), (14, '3Y', 8.0), (14, '5Y', 10.2);

SELECT setval('risk_profiles_risk_profile_id_seq', (SELECT MAX(risk_profile_id) FROM risk_profiles));
SELECT setval('asset_classes_asset_class_id_seq', (SELECT MAX(asset_class_id) FROM asset_classes));
SELECT setval('portfolio_models_model_id_seq', (SELECT MAX(model_id) FROM portfolio_models));
SELECT setval('sub_allocation_templates_template_id_seq', (SELECT MAX(template_id) FROM sub_allocation_templates));
SELECT setval('instruments_instrument_id_seq', (SELECT MAX(instrument_id) FROM instruments));
