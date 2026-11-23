-- 02_portfolio_kpis.sql
-- Portfolio KPI queries (SQLite). Each query is separated by a "-- name:" line
-- so notebooks/01_EDA.ipynb can run them one by one.

-- name: portfolio_overview
SELECT
    COUNT(*)                                        AS customers,
    ROUND(AVG(DEFAULT_NEXT_MONTH) * 100, 2)         AS default_rate_pct,
    ROUND(SUM(LIMIT_BAL) / 1e6, 1)                  AS total_limit_ntd_m,
    ROUND(SUM(MAX(BILL_AMT1, 0)) / 1e6, 1)          AS total_balance_ntd_m,
    ROUND(SUM(MAX(BILL_AMT1, 0)) * 100.0 / SUM(LIMIT_BAL), 1) AS portfolio_utilisation_pct
FROM customers;

-- name: default_rate_by_utilisation_band
WITH banded AS (
    SELECT DEFAULT_NEXT_MONTH,
           CASE WHEN UTILISATION < 0.3 THEN '1: <30%'
                WHEN UTILISATION < 0.5 THEN '2: 30-50%'
                WHEN UTILISATION < 0.8 THEN '3: 50-80%'
                WHEN UTILISATION < 1.0 THEN '4: 80-100%'
                ELSE                        '5: 100%+' END AS utilisation_band
    FROM customers
)
SELECT utilisation_band,
       COUNT(*)                                AS customers,
       ROUND(AVG(DEFAULT_NEXT_MONTH) * 100, 1) AS default_rate_pct
FROM banded
GROUP BY utilisation_band
ORDER BY utilisation_band;

-- name: default_rate_by_current_status
SELECT CASE WHEN PAY_1 <= -1 THEN 'Paid in full / no use'
            WHEN PAY_1 = 0   THEN 'Revolving, up to date'
            WHEN PAY_1 = 1   THEN '1 month late'
            WHEN PAY_1 = 2   THEN '2 months late'
            ELSE                  '3+ months late' END   AS september_status,
       COUNT(*)                                          AS customers,
       ROUND(AVG(DEFAULT_NEXT_MONTH) * 100, 1)           AS default_rate_pct
FROM customers
GROUP BY september_status
ORDER BY MIN(PAY_1);

-- name: delinquency_roll_rates
-- Share of customers in each August arrears bucket who moved to each September bucket.
WITH buckets AS (
    SELECT CASE WHEN PAY_2 <= 0 THEN '0 current' WHEN PAY_2 = 1 THEN '1 month'
                WHEN PAY_2 = 2 THEN '2 months' ELSE '3+ months' END AS aug_bucket,
           CASE WHEN PAY_1 <= 0 THEN '0 current' WHEN PAY_1 = 1 THEN '1 month'
                WHEN PAY_1 = 2 THEN '2 months' ELSE '3+ months' END AS sep_bucket
    FROM customers
)
SELECT aug_bucket,
       sep_bucket,
       COUNT(*) AS customers,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY aug_bucket), 1) AS pct_of_aug_bucket
FROM buckets
GROUP BY aug_bucket, sep_bucket
ORDER BY aug_bucket, sep_bucket;

-- name: default_rate_by_age_band
SELECT CASE WHEN AGE < 30 THEN '21-29' WHEN AGE < 40 THEN '30-39'
            WHEN AGE < 50 THEN '40-49' ELSE '50+' END AS age_band,
       COUNT(*)                                       AS customers,
       ROUND(AVG(DEFAULT_NEXT_MONTH) * 100, 1)        AS default_rate_pct,
       ROUND(AVG(LIMIT_BAL))                          AS avg_limit_ntd
FROM customers
GROUP BY age_band
ORDER BY age_band;

-- name: limit_band_exposure_share
-- Cumulative share of outstanding balance by credit-limit band (window function).
WITH bands AS (
    SELECT CASE WHEN LIMIT_BAL < 50000  THEN '1: <50k'
                WHEN LIMIT_BAL < 150000 THEN '2: 50k-150k'
                WHEN LIMIT_BAL < 300000 THEN '3: 150k-300k'
                ELSE                         '4: 300k+' END AS limit_band,
           MAX(BILL_AMT1, 0) AS balance,
           DEFAULT_NEXT_MONTH
    FROM customers
)
SELECT limit_band,
       COUNT(*)                                             AS customers,
       ROUND(AVG(DEFAULT_NEXT_MONTH) * 100, 1)              AS default_rate_pct,
       ROUND(SUM(balance) * 100.0 / SUM(SUM(balance)) OVER (), 1) AS balance_share_pct,
       ROUND(SUM(SUM(balance)) OVER (ORDER BY limit_band) * 100.0
             / SUM(SUM(balance)) OVER (), 1)                AS cumulative_balance_share_pct
FROM bands
GROUP BY limit_band
ORDER BY limit_band;
