-- 01_create_tables.sql
-- SQLite schema for the cleaned UCI credit card portfolio.
-- Amounts are in New Taiwan dollars (NT$). PAY_1 = September 2005 ... PAY_6 = April 2005.
-- Repayment status: -2 no consumption, -1 paid in full, 0 revolving, 1..9 months in arrears.

DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    ID                  INTEGER PRIMARY KEY,
    LIMIT_BAL           REAL    NOT NULL,
    SEX                 INTEGER NOT NULL,   -- 1 male, 2 female
    EDUCATION           INTEGER NOT NULL,   -- 1 graduate school, 2 university, 3 high school, 4 other
    MARRIAGE            INTEGER NOT NULL,   -- 1 married, 2 single, 3 other
    AGE                 INTEGER NOT NULL,
    PAY_1 INTEGER, PAY_2 INTEGER, PAY_3 INTEGER, PAY_4 INTEGER, PAY_5 INTEGER, PAY_6 INTEGER,
    BILL_AMT1 REAL, BILL_AMT2 REAL, BILL_AMT3 REAL, BILL_AMT4 REAL, BILL_AMT5 REAL, BILL_AMT6 REAL,
    PAY_AMT1 REAL,  PAY_AMT2 REAL,  PAY_AMT3 REAL,  PAY_AMT4 REAL,  PAY_AMT5 REAL,  PAY_AMT6 REAL,
    DEFAULT_NEXT_MONTH  INTEGER NOT NULL,   -- 1 = defaulted in October 2005
    UTILISATION         REAL,               -- BILL_AMT1 / LIMIT_BAL, floored at 0
    MONTHS_LATE_6M      INTEGER,            -- months with status >= 1 in the last six
    MAX_DELINQUENCY_6M  INTEGER,            -- worst arrears status in the last six months
    PAYMENT_RATIO_6M    REAL                -- payments / bills over six months, capped at 1
);

-- Filled by notebooks/03_risk_segmentation.ipynb
DROP TABLE IF EXISTS risk_tiers;

CREATE TABLE risk_tiers (
    ID           INTEGER PRIMARY KEY REFERENCES customers (ID),
    RISK_TIER    TEXT NOT NULL,
    PD_SCORE     REAL NOT NULL               -- out-of-fold XGBoost probability of default
);
