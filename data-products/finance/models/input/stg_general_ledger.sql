SELECT
    entry_id,
    account_code,
    debit,
    credit,
    entry_date,
    description,
    department,
    ingested_at
FROM {{ source('finance_input', 'general_ledger') }}
