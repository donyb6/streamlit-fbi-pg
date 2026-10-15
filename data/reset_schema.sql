-- Gold layer
DROP TABLE IF EXISTS gold_offense_facts;
DROP TABLE IF EXISTS gold_dim_agency;
DROP TABLE IF EXISTS gold_dim_state;
DROP TABLE IF EXISTS gold_dim_offense;

-- Silver layer
DROP TABLE IF EXISTS silver_summarized_offenses;
DROP TABLE IF EXISTS silver_agencies;

-- Bronze layer
DROP TABLE IF EXISTS bronze_summarized_offenses;
DROP TABLE IF EXISTS bronze_agencies;