-- 1. annual rate per 100k by state, year and category (2021 included)
CREATE OR REPLACE VIEW vw_annual_rate_by_state AS
SELECT s.state_abbr, s.state_name, f.year, o.category,
       COUNT(*) AS months_of_data,
       SUM(f.actual_count) AS total_offenses,
       ROUND(SUM(f.actual_count)::numeric / NULLIF(SUM(f.population), 0) * 100000 * 12, 2) AS annual_rate_per_100k
FROM gold_offense_facts f
JOIN gold_dim_state s ON f.state_abbr = s.state_abbr
JOIN gold_dim_offense o ON f.offense_code = o.offense_code
WHERE f.offense_code IN ('V', 'P')
GROUP BY s.state_abbr, s.state_name, f.year, o.category;

-- 2. CA/TX vs WY/VT tier comparison, 2021 excluded
CREATE OR REPLACE VIEW vw_tier_comparison AS
SELECT CASE WHEN s.state_abbr IN ('CA', 'TX') THEN 'High Population (CA/TX)'
            ELSE 'Low Population (WY/VT)' END AS population_tier,
       o.category,
       ROUND(SUM(f.actual_count)::numeric / NULLIF(SUM(f.population), 0) * 100000 * 12, 2) AS annual_rate_per_100k,
       ROUND(SUM(f.clearance_count)::numeric / NULLIF(SUM(f.actual_count), 0), 3) AS clearance_rate
FROM gold_offense_facts f
JOIN gold_dim_state s ON f.state_abbr = s.state_abbr
JOIN gold_dim_offense o ON f.offense_code = o.offense_code
WHERE f.offense_code IN ('V', 'P')
  AND f.year != 2021
GROUP BY population_tier, o.category;

-- 3. annual rate per 100k by state and individual offense type, 2021 excluded
CREATE OR REPLACE VIEW vw_offense_rate_by_state AS
SELECT s.state_abbr, s.state_name, o.offense_name, o.category,
       ROUND(SUM(f.actual_count)::numeric / NULLIF(SUM(f.population), 0) * 100000 * 12, 2) AS annual_rate_per_100k
FROM gold_offense_facts f
JOIN gold_dim_state s ON f.state_abbr = s.state_abbr
JOIN gold_dim_offense o ON f.offense_code = o.offense_code
WHERE f.offense_code NOT IN ('V', 'P')
  AND f.year != 2021
GROUP BY s.state_abbr, s.state_name, o.offense_name, o.category;

-- 4. clearance rate by state, year and category
CREATE OR REPLACE VIEW vw_clearance_by_state AS
SELECT s.state_abbr, s.state_name, f.year, o.category,
       ROUND(SUM(f.clearance_count)::numeric / NULLIF(SUM(f.actual_count), 0), 3) AS clearance_rate
FROM gold_offense_facts f
JOIN gold_dim_state s ON f.state_abbr = s.state_abbr
JOIN gold_dim_offense o ON f.offense_code = o.offense_code
WHERE f.offense_code IN ('V', 'P')
GROUP BY s.state_abbr, s.state_name, f.year, o.category;