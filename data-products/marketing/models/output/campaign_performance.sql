SELECT
    c.campaign_id,
    c.campaign_name,
    c.channel,
    SUM(r.impressions) AS total_impressions,
    SUM(r.clicks) AS total_clicks,
    SUM(r.conversions) AS total_conversions,
    SUM(r.spend) AS total_spend,
    CASE WHEN SUM(r.impressions) > 0
        THEN ROUND(SUM(r.clicks)::DECIMAL / SUM(r.impressions), 4)
        ELSE 0
    END AS ctr,
    CASE WHEN SUM(r.spend) > 0
        THEN ROUND((SUM(r.conversions) * 50.0) / SUM(r.spend), 4)
        ELSE 0
    END AS roas,
    '1.0' AS data_product_version,
    NOW() AS updated_at
FROM {{ ref('stg_campaigns') }} c
JOIN {{ ref('stg_campaign_results') }} r ON c.campaign_id = r.campaign_id
GROUP BY c.campaign_id, c.campaign_name, c.channel
