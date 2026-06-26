SELECT
    t.transaction_id,
    t.customer_id,
    CASE
        WHEN t.product_id LIKE 'PROD-0%' AND t.product_id IN ('PROD-001','PROD-002') THEN 'Électronique'
        WHEN t.product_id IN ('PROD-003','PROD-004') THEN 'Vêtements'
        WHEN t.product_id IN ('PROD-005','PROD-006') THEN 'Alimentation'
        WHEN t.product_id IN ('PROD-007','PROD-008') THEN 'Maison'
        WHEN t.product_id IN ('PROD-009','PROD-010') THEN 'Sport'
        ELSE 'Autre'
    END AS product_category,
    t.amount,
    t.transaction_date,
    t.store_id,
    t.channel,
    '1.0' AS data_product_version,
    'silver' AS sla_tier,
    NOW() AS updated_at
FROM {{ ref('stg_raw_transactions') }} t
