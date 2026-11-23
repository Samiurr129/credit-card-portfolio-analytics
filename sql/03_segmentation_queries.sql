-- 03_segmentation_queries.sql
-- Risk-tier reporting (SQLite). Needs the risk_tiers table written by
-- notebooks/03_risk_segmentation.ipynb.

-- name: tier_summary
SELECT t.RISK_TIER                                          AS risk_tier,
       COUNT(*)                                             AS customers,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1)   AS portfolio_share_pct,
       ROUND(AVG(c.DEFAULT_NEXT_MONTH) * 100, 1)            AS default_rate_pct,
       ROUND(AVG(t.PD_SCORE) * 100, 1)                      AS avg_model_pd_pct,
       ROUND(AVG(c.UTILISATION) * 100, 1)                   AS avg_utilisation_pct
FROM risk_tiers t
JOIN customers  c ON c.ID = t.ID
GROUP BY t.RISK_TIER
ORDER BY t.RISK_TIER;

-- name: exposure_at_default_by_tier
-- Balance (Sept bill, floored at 0) of customers who defaulted, and each tier's share.
SELECT t.RISK_TIER                                              AS risk_tier,
       ROUND(SUM(MAX(c.BILL_AMT1, 0)) / 1e6, 1)                 AS balance_ntd_m,
       ROUND(SUM(CASE WHEN c.DEFAULT_NEXT_MONTH = 1 THEN MAX(c.BILL_AMT1, 0) ELSE 0 END) / 1e6, 1)
                                                                AS defaulted_balance_ntd_m,
       ROUND(SUM(CASE WHEN c.DEFAULT_NEXT_MONTH = 1 THEN MAX(c.BILL_AMT1, 0) ELSE 0 END) * 100.0
             / SUM(SUM(CASE WHEN c.DEFAULT_NEXT_MONTH = 1 THEN MAX(c.BILL_AMT1, 0) ELSE 0 END)) OVER (), 1)
                                                                AS share_of_defaulted_balance_pct
FROM risk_tiers t
JOIN customers  c ON c.ID = t.ID
GROUP BY t.RISK_TIER
ORDER BY t.RISK_TIER;

-- name: tier_ranking_within_age_band
-- Highest-risk tier by default rate inside each age band (window function).
WITH tier_age AS (
    SELECT CASE WHEN c.AGE < 30 THEN '21-29' WHEN c.AGE < 40 THEN '30-39'
                WHEN c.AGE < 50 THEN '40-49' ELSE '50+' END AS age_band,
           t.RISK_TIER,
           COUNT(*)                                 AS customers,
           AVG(c.DEFAULT_NEXT_MONTH)                AS default_rate
    FROM risk_tiers t JOIN customers c ON c.ID = t.ID
    GROUP BY age_band, t.RISK_TIER
)
SELECT age_band, RISK_TIER AS risk_tier, customers,
       ROUND(default_rate * 100, 1) AS default_rate_pct,
       RANK() OVER (PARTITION BY age_band ORDER BY default_rate DESC) AS risk_rank
FROM tier_age
ORDER BY age_band, risk_rank;
