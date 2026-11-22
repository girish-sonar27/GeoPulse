--------------------------------------------------------
-- GeoPulse Snowflake Database Setup Script
-- Assignment: ITS/DA/1951, Group 45
-- Member 1: Data Engineering & Spatial Processing
-- Project: Hyper-Local Retail Mobility Analytics
-- Date: 18 November 2026
--------------------------------------------------------

-- ============================================================
-- 1. CREATE DATABASE AND SCHEMAS
-- ============================================================

-- Create the main database for GeoPulse project
CREATE DATABASE IF NOT EXISTS GEOPULSE_DB;

-- Use the created database
USE DATABASE GEOPULSE_DB;

-- Create RAW schema for unprocessed/landing data
CREATE SCHEMA IF NOT EXISTS RAW;

-- Create ANALYTICS schema for processed/mart data
CREATE SCHEMA IF NOT EXISTS ANALYTICS;

-- ============================================================
-- 2. CREATE TABLES IN RAW SCHEMA
-- ============================================================

-- DEVICE_PINGS table: Stores cleaned GPS pings data
-- Source: geolife_gps_cleaned.csv (24,730,077 records)
CREATE OR REPLACE TABLE RAW.DEVICE_PINGS (
    DEVICE_ID VARCHAR(50) NOT NULL,
    LATITUDE FLOAT NOT NULL,
    LONGITUDE FLOAT NOT NULL,
    ALTITUDE_FEET FLOAT,
    EXCEL_DAYS FLOAT,
    DATE DATE NOT NULL,
    TIME TIME NOT NULL,
    TIMESTAMP DATETIME NOT NULL,
    SOURCE_FILE VARCHAR(255),
    RECORD_DATE_LOADED DATETIME DEFAULT CURRENT_TIMESTAMP()
);

-- COMMENT: Raw GPS pings from GeoLife trajectory conversion
-- Total records expected: ~24.7M after cleaning
-- Geography column will be computed spatially

-- STORES table: Contains fictional store locations
CREATE OR REPLACE TABLE RAW.STORES (
    STORE_ID VARCHAR(20) PRIMARY KEY,
    STORE_NAME VARCHAR(100) NOT NULL,
    LATITUDE FLOAT NOT NULL,
    LONGITUDE FLOAT NOT NULL,
    CATCHMENT_RADIUS_METERS NUMBER DEFAULT 500,
    STORE_AREA_ZIP VARCHAR(10),
    OPEN_DATE DATE,
    CLOSE_DATE DATE,
    IS_ACTIVE BOOLEAN DEFAULT TRUE
);

-- COMMENT: Three fictional store locations for analysis
-- Store data used for 500m catchment area calculations
-- STORE_001, STORE_002, STORE_003 with synthetic coordinates

-- ============================================================
-- 3. CREATE TABLES IN ANALYTICS SCHEMA
-- ============================================================

-- DAILY_FOOTFALL: Aggregated hourly footfall per store
CREATE OR REPLACE TABLE ANALYTICS.DAILY_FOOTFALL (
    STORE_ID VARCHAR(20) NOT NULL,
    DATE DATE NOT NULL,
    HOUR NUMBER NOT NULL,
    UNIQUE_VISITORS NUMBER,
    TOTAL_FOOTFALL NUMBER,
    PRIMARY KEY (STORE_ID, DATE, HOUR)
);

-- WEEKLY_VISITOR_OVERLAP: Visitor overlap between stores
CREATE OR REPLACE TABLE ANALYTICS.WEEKLY_VISITOR_OVERLAP (
    WEEK_START_DATE DATE NOT NULL,
    STORE_1_ID VARCHAR(20) NOT NULL,
    STORE_2_ID VARCHAR(20) NOT NULL,
    OVERLAPPING_VISITORS NUMBER,
    TOTAL_VISITORS_STORE_1 NUMBER,
    TOTAL_VISITORS_STORE_2 NUMBER,
    OVERLAP_PERCENTAGE FLOAT,
    PRIMARY KEY (WEEK_START_DATE, STORE_1_ID, STORE_2_ID)
);

-- CANNIBILIZATION_ANALYSIS: Store cannibalization metrics
CREATE OR REPLACE TABLE ANALYTICS.CANNIBILIZATION_ANALYSIS (
    STORE_ID VARCHAR(20) NOT NULL,
    TOTAL_UNIQUE_VISITORS NUMBER,
    VISITORS_MULTIPLE_STORES NUMBER,
    CANNIBALIZATION_PERCENTAGE FLOAT,
    PRIMARY KEY (STORE_ID)
);

-- ============================================================
-- 4. CREATE GEOGRAPHY-ENRICHED VIEWS
-- ============================================================

-- View: DEVICE_PINGS_WITH_GEO (RAW schema)
CREATE OR REPLACE VIEW RAW.DEVICE_PINGS_WITH_GEO AS
SELECT
    DEVICE_ID,
    LATITUDE,
    LONGITUDE,
    ALTITUDE_FEET,
    EXCEL_DAYS,
    DATE,
    TIME,
    TIMESTAMP,
    SOURCE_FILE,
    -- Create GEOGRAPHY point from latitude/longitude
    GEOGRAPHY(PARSE_GEOGRAPHY('POINT(' || TO_LONG(LONGITUDE) || ' ' || TO_LONG(LATITUDE) || ')')) AS GEO_POINT
FROM RAW.DEVICE_PINGS;

-- View: STORES_WITH_CATCHMENT (RAW schema)
CREATE OR REPLACE VIEW RAW.STORES_WITH_CATCHMENT AS
SELECT
    STORE_ID,
    STORE_NAME,
    LATITUDE,
    LONGITUDE,
    CATCHMENT_RADIUS_METERS,
    -- Create GEOGRAPHY point for store location
    GEOGRAPHY(PARSE_GEOGRAPHY('POINT(' || TO_LONG(LONGITUDE) || ' ' || TO_LONG(LATITUDE) || ')')) AS GEO_POINT,
    -- Create 500m buffer catchment area
    GEOGRAPHY_BUFFER(GEOGRAPHY(PARSE_GEOGRAPHY('POINT(' || TO_LONG(LONGITUDE) || ' ' || TO_LONG(LATITUDE) || ')')),
                     CATCHMENT_RADIUS_METERS) AS CATCHMENT_POLYGON
FROM RAW.STORES;

-- ============================================================
-- 5. INSERT SAMPLE DATA
-- ============================================================

-- Insert 3 fictional store locations (Member 1 responsibility)
INSERT INTO RAW.STORES (STORE_ID, STORE_NAME, LATITUDE, LONGITUDE, CATCHMENT_RADIUS_METERS) VALUES
('STORE_001', 'Downtown Retail Center', 28.6139, 77.2090, 500),
('STORE_002', 'Suburban Shopping Plaza', 28.7041, 77.3516, 500),
('STORE_003', 'Urban Convenience Store', 28.5355, 77.1733, 500);

-- ============================================================
-- 6. SAMPLE SYNTHETIC GPS RECORDS FOR TESTING
-- ============================================================

-- Insert sample GPS records to verify pipeline functionality
INSERT INTO RAW.DEVICE_PINGS (DEVICE_ID, LATITUDE, LONGITUDE, ALTITUDE_FEET, EXCEL_DAYS, DATE, TIME, TIMESTAMP, SOURCE_FILE) VALUES
-- Records near STORE_001 (Downtown)
('DEVICE_001', 28.6145, 77.2095, 120.5, 45235.1234, CURRENT_DATE(), CURRENT_TIME(), CURRENT_TIMESTAMP(), 'test_sample'),
('DEVICE_002', 28.6152, 77.2101, 135.2, 45235.1235, CURRENT_DATE(), CURRENT_TIME(), CURRENT_TIMESTAMP(), 'test_sample'),
-- Records near STORE_002 (Suburban)
('DEVICE_003', 28.7048, 77.3522, 98.7, 45235.5678, CURRENT_DATE(), CURRENT_TIME(), CURRENT_TIMESTAMP(), 'test_sample'),
('DEVICE_004', 28.7055, 77.3530, 112.3, 45235.5679, CURRENT_DATE(), CURRENT_TIME(), CURRENT_TIMESTAMP(), 'test_sample'),
-- Records near STORE_003 (Urban)
('DEVICE_005', 28.5362, 77.1739, 145.8, 45235.8912, CURRENT_DATE(), CURRENT_TIME(), CURRENT_TIMESTAMP(), 'test_sample'),
('DEVICE_006', 28.5358, 77.1728, 118.4, 45235.8913, CURRENT_DATE(), CURRENT_TIME(), CURRENT_TIMESTAMP(), 'test_sample');

-- ============================================================
-- 7. VERIFICATION QUERIES
-- ============================================================

-- Verify database creation
SELECT 'GEOPULSE_DB' AS OBJECT_NAME, GET_DATABASE_NAME() AS CURRENT_DATABASE;

-- Verify tables exist
SELECT TABLE_NAME, TABLE_TYPE FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA IN ('RAW', 'ANALYTICS')
ORDER BY TABLE_SCHEMA, TABLE_NAME;

-- Verify store locations
SELECT STORE_ID, STORE_NAME, LATITUDE, LONGITUDE, CATCHMENT_RADIUS_METERS FROM RAW.STORES;

-- Verify GPS records count
SELECT COUNT(*) AS TOTAL_RECORDS FROM RAW.DEVICE_PINGS;

-- Verify geography points are computed
SELECT DEVICE_ID, LATITUDE, LONGITUDE, GEO_POINT FROM RAW.DEVICE_PINGS_WITH_GEO LIMIT 5;

-- ============================================================
-- 8. END OF SETUP SCRIPT
-- ============================================================

-- Grant necessary permissions (adjust based on Snowflake role hierarchy)
-- GRANT USAGE ON DATABASE GEOPULSE_DB TO ROLE ANALYST_ROLE;
-- GRANT USAGE ON SCHEMA GEOPULSE_DB.RAW TO ROLE ANALYST_ROLE;
-- GRANT USAGE ON SCHEMA GEOPULSE_DB.ANALYTICS TO ROLE ANALYST_ROLE;
-- GRANT SELECT ON ALL TABLES IN SCHEMA GEOPULSE_DB.RAW TO ROLE ANALYST_ROLE;
-- GRANT SELECT ON ALL TABLES IN SCHEMA GEOPULSE_DB.ANALYTICS TO ROLE ANALYST_ROLE;

-- Note: Actual permission assignment depends on organizational Snowflake setup.
-- This script establishes the database structure for Member 1 (Data Engineering) to load
-- GPS data and begin spatial processing with PySpark + Apache Sedona.

-- ============================================================
-- DOCUMENTATION NOTES
-- ============================================================
--
-- Project: GeoPulse - Hyper-Local Retail Mobility Analytics
-- Assignment ID: ITS/DA/1951, Group 45
-- Team Lead: Kanishka Gupta
-- Member 1 Role: Data Engineering & Spatial Processing
--
-- TABLE DESIGNS:
--   - RAW.DEVICE_PINGS: Cleaned GPS pings from GeoLife conversion (24.7M records)
--   - RAW.STORES: 3 fictional store locations with 500m catchment radii
--   - ANALYTICS.DAILY_FOOTFALL: Hourly footfall per store (aggregated)
--   - ANALYTICS.WEEKLY_VISITOR_OVERLAP: Visitor overlap between store pairs
--   - ANALYTICS.CANNIBALIZATION_ANALYSIS: Store cannibalization metrics
--
-- SPATIAL PROCESSING PIPELINE (Member 1 responsibility):
--   1. Configure PySpark + Apache Sedona
--   2. Generate 500m catchment polygons from STORES table
--   3. Spatial join: GPS pings (RAW.DEVICE_PINGS) ↔ store catchments
--   4. Visitor-to-store mapping and counting
--   5. H3 hexagonal temporal aggregation
--   6. Airflow pipeline automation
--
-- MEMBER 2 RESPONSIBILITIES (separate):
--   - dbt transformations for metrics
--   - Cannibalization analysis
--   - Kepler.gl dashboard development
--
-- IMPORTANT:
--   - GeoLife data approval must be confirmed with Team Lead
--   - Large dataset (24.7M records) should be loaded incrementally
--   - All spatial processing must validate row counts at each stage
--   - Never commit large CSV files to GitHub
--===========================================================

SELECT COUNT(*) AS STORE_COUNT FROM GEOPULSE_DB.RAW.STORES;
SELECT COUNT(*) AS GPS_PING_COUNT FROM GEOPULSE_DB.RAW.DEVICE_PINGS;