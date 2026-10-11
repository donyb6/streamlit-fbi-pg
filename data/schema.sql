-- BRONZE LAYER
CREATE TABLE IF NOT EXISTS bronze_agencies (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    state_abbr VARCHAR(2) NOT NULL,
    response_json TEXT NOT NULL,
    extracted_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS bronze_summarized_offenses (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    state_abbr VARCHAR(2) NOT NULL,
    offense_code VARCHAR(10) NOT NULL,
    from_date VARCHAR(7) NOT NULL,
    to_date VARCHAR(7) NOT NULL,
    response_json TEXT,
    http_status INT NOT NULL,
    extracted_at TIMESTAMP NOT NULL
);

-- SILVER LAYER
CREATE TABLE IF NOT EXISTS silver_agencies (
    ori VARCHAR(20) PRIMARY KEY,
    agency_name VARCHAR(255) NOT NULL,
    agency_type_name VARCHAR(50),
    county VARCHAR(100),
    state_abbr VARCHAR(2) NOT NULL,
    state_name VARCHAR(50),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    is_nibrs BOOLEAN,
    nibrs_start_date DATE
);

CREATE TABLE IF NOT EXISTS silver_summarized_offenses (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    state_abbr VARCHAR(2) NOT NULL,
    offense_code VARCHAR(10) NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    state_actual_count INT,
    state_clearance_count INT,
    state_rate_per_100k DECIMAL(10,4),
    state_clearance_rate_per_100k DECIMAL(10,4),
    us_actual_rate DECIMAL(10,4),
    us_clearance_rate DECIMAL(10,4),
    population INT,
    participated_population INT,
    CONSTRAINT uq_silver_state_offense_month
        UNIQUE (state_abbr, offense_code, year, month)
);

-- GOLD LAYER
CREATE TABLE IF NOT EXISTS gold_dim_offense (
    offense_code VARCHAR(10) PRIMARY KEY,
    offense_name VARCHAR(50) NOT NULL,
    category VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS gold_dim_state (
    state_abbr VARCHAR(2) PRIMARY KEY,
    state_name VARCHAR(50) NOT NULL,
    region VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS gold_dim_agency (
    ori VARCHAR(20) PRIMARY KEY,
    agency_name VARCHAR(255) NOT NULL,
    agency_type_name VARCHAR(50),
    county VARCHAR(100),
    state_abbr VARCHAR(2) NOT NULL,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    is_nibrs BOOLEAN,
    nibrs_start_date DATE
);

CREATE TABLE IF NOT EXISTS gold_offense_facts (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    state_abbr VARCHAR(2) NOT NULL REFERENCES gold_dim_state(state_abbr),
    offense_code VARCHAR(10) NOT NULL REFERENCES gold_dim_offense(offense_code),
    year INT NOT NULL,
    month INT NOT NULL,
    actual_count INT,
    clearance_count INT,
    clearance_rate DECIMAL(6,4),
    rate_per_100k DECIMAL(10,4),
    population INT,
    CONSTRAINT uq_gold_state_offense_month
        UNIQUE (state_abbr, offense_code, year, month)
);