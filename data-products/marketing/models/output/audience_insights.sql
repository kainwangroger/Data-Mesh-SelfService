SELECT
    'premium' AS segment,
    120 AS customer_count,
    8500.00 AS avg_ltv,
    'email' AS top_channel,
    0.1250 AS engagement_rate,
    '1.0' AS data_product_version,
    NOW() AS updated_at
UNION ALL
SELECT 'regular', 450, 3200.00, 'social', 0.0450, '1.0', NOW()
UNION ALL
SELECT 'occasional', 1200, 850.00, 'display', 0.0120, '1.0', NOW()
UNION ALL
SELECT 'new', 300, 150.00, 'affiliate', 0.0800, '1.0', NOW()
