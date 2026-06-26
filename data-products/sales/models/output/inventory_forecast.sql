WITH daily_sales AS (
    SELECT
        product_id,
        transaction_date,
        SUM(quantity) AS units_sold
    FROM {{ ref('stg_raw_transactions') }}
    GROUP BY product_id, transaction_date
),
product_avg AS (
    SELECT
        product_id,
        AVG(units_sold) AS daily_avg
    FROM daily_sales
    GROUP BY product_id
)
SELECT
    p.product_id,
    CURRENT_DATE + INTERVAL '1 day' * s.i AS forecast_date,
    ROUND(p.daily_avg * (1 + (RANDOM() * 0.2 - 0.1)), 2) AS predicted_demand,
    ROUND(p.daily_avg * 0.8, 2) AS confidence_lower,
    ROUND(p.daily_avg * 1.2, 2) AS confidence_upper,
    '1.0' AS data_product_version,
    'moving_avg_v1' AS model_name,
    NOW() AS updated_at
FROM product_avg p
CROSS JOIN generate_series(0, 13) AS s(i)
