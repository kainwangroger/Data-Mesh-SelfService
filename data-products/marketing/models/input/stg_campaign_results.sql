SELECT
    result_id,
    campaign_id,
    impressions,
    clicks,
    conversions,
    spend,
    result_date,
    ingested_at
FROM {{ source('marketing_input', 'campaign_results') }}
