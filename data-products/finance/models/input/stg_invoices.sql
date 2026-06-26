SELECT
    invoice_id,
    vendor_id,
    amount,
    due_date,
    paid,
    category,
    ingested_at
FROM {{ source('finance_input', 'invoices') }}
