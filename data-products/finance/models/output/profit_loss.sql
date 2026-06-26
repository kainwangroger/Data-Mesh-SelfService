SELECT
    entry_date AS report_date,
    SUM(CASE WHEN account_code LIKE '7%' THEN credit ELSE 0 END) AS revenue,
    SUM(CASE WHEN account_code = '6000' THEN debit ELSE 0 END) AS cogs,
    SUM(CASE WHEN account_code LIKE '7%' THEN credit ELSE 0 END)
        - SUM(CASE WHEN account_code = '6000' THEN debit ELSE 0 END) AS gross_profit,
    SUM(CASE WHEN account_code LIKE '60%' AND account_code != '6000' THEN debit
             WHEN account_code LIKE '6%' THEN debit ELSE 0 END) AS operating_expenses,
    (SUM(CASE WHEN account_code LIKE '7%' THEN credit ELSE 0 END)
        - SUM(CASE WHEN account_code LIKE '6%' THEN debit ELSE 0 END)
        + SUM(CASE WHEN account_code LIKE '8%' THEN credit ELSE 0 END)
        - SUM(CASE WHEN account_code LIKE '9%' THEN debit ELSE 0 END)) AS net_profit,
    '1.0' AS data_product_version,
    NOW() AS updated_at
FROM {{ ref('stg_general_ledger') }}
GROUP BY entry_date
ORDER BY entry_date DESC
