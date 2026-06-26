SELECT
    customer_id,
    SUM(amount) AS total_spent,
    AVG(amount) AS avg_ticket,
    COUNT(*) AS visit_count,
    MODE() WITHIN GROUP (ORDER BY channel) AS preferred_channel,
    MAX(transaction_date) AS last_purchase_date,
    CASE
        WHEN SUM(amount) > 10000 THEN 'premium'
        WHEN SUM(amount) > 3000 THEN 'regular'
        ELSE 'occasional'
    END AS segment,
    '1.0' AS data_product_version,
    NOW() AS updated_at
FROM {{ ref('stg_raw_transactions') }}
GROUP BY customer_id
