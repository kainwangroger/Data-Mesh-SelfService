SELECT
    transaction_id,
    customer_id,
    product_id,
    amount,
    quantity,
    transaction_date::date AS transaction_date,
    store_id,
    channel,
    ingested_at
FROM {{ source('sales_input', 'raw_transactions') }}
WHERE amount > 0
