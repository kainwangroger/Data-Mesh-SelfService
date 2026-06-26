SELECT
    campaign_id,
    campaign_name,
    channel,
    budget,
    start_date,
    end_date,
    target_segment,
    ingested_at
FROM {{ source('marketing_input', 'campaigns') }}
