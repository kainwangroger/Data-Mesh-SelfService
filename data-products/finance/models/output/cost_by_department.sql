SELECT
    department,
    DATE_TRUNC('month', entry_date)::date AS report_month,
    SUM(debit) AS total_cost,
    CASE
        WHEN department = 'Sales' THEN 25
        WHEN department = 'Marketing' THEN 15
        WHEN department = 'R&D' THEN 30
        WHEN department = 'IT' THEN 12
        WHEN department = 'HR' THEN 8
        WHEN department = 'Finance' THEN 10
        ELSE 5
    END AS headcount,
    ROUND(SUM(debit) / NULLIF(
        CASE
            WHEN department = 'Sales' THEN 25
            WHEN department = 'Marketing' THEN 15
            WHEN department = 'R&D' THEN 30
            WHEN department = 'IT' THEN 12
            WHEN department = 'HR' THEN 8
            WHEN department = 'Finance' THEN 10
            ELSE 5
        END, 0), 2) AS cost_per_head,
    '1.0' AS data_product_version,
    NOW() AS updated_at
FROM {{ ref('stg_general_ledger') }}
WHERE debit > 0
GROUP BY department, DATE_TRUNC('month', entry_date)
