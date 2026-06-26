SELECT
    event_id,
    customer_id,
    event_type,
    event_data,
    event_timestamp,
    ingested_at
FROM {{ source('sales_input', 'customer_events') }}
