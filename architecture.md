# Architecture — Data Mesh Self-Service Platform

```mermaid
graph TB
    subgraph "Self-Service Portal"
        SP[Streamlit<br/>5 pages]
    end

    subgraph "Governance Layer"
        GA[Governance API<br/>FastAPI]
        PE[Policy Engine<br/>Rule-based]
        MR[(Metadata Registry<br/>SQLite)]
        AD[Airflow DAG<br/>Gouvernance quotidienne]
    end

    subgraph "Data Domains"
        subgraph "Sales"
            S_IN[(input<br/>raw_transactions<br/>customer_events)]
            S_OUT[(output<br/>sales_transactions<br/>customer_360<br/>inventory_forecast)]
        end
        subgraph "Marketing"
            M_IN[(input<br/>campaigns<br/>campaign_results)]
            M_OUT[(output<br/>campaign_performance<br/>audience_insights)]
        end
        subgraph "Finance"
            F_IN[(input<br/>general_ledger<br/>invoices)]
            F_OUT[(output<br/>profit_loss<br/>cost_by_department)]
        end
    end

    subgraph "Data Transformation"
        DBT_S[dbt Sales]
        DBT_M[dbt Marketing]
        DBT_F[dbt Finance]
    end

    subgraph "Storage"
        PG[(PostgreSQL<br/>3 bases isolées)]
        MINIO[MinIO<br/>Data Lake]
    end

    SP -->|API REST| GA
    GA --> PE
    GA --> MR
    
    AD -->|Healthcheck| PG
    AD -->|Schema drift| PG
    AD -->|Cost report| PG

    S_IN --> DBT_S --> S_OUT
    M_IN --> DBT_M --> M_OUT
    F_IN --> DBT_F --> F_OUT

    S_OUT --> PG
    M_OUT --> PG
    F_OUT --> PG
    S_IN --> PG
    M_IN --> PG
    F_IN --> PG

    GA -->|Metadata| PG

    style SP fill:#00BCD4,color:#fff
    style GA fill:#673AB7,color:#fff
    style PE fill:#FF9800,color:#fff
    style AD fill:#2196F3,color:#fff
    style PG fill:#9C27B0,color:#fff
    style MINIO fill:#4CAF50,color:#fff
```

## Flux des données

1. **Streamlit Portal** — Interface self-service pour découvrir, créer et demander des data products
2. **Governance API** — Enregistre les métadonnées, évalue les policies d'accès, trace les audits
3. **3 Domaines isolés** (Sales / Marketing / Finance) avec leur propre base PostgreSQL
4. **dbt** — Transforme les tables `input` → `output` (data products)
5. **Airflow** — Orchestre la gouvernance quotidienne (healthcheck, schema drift, coûts)
6. **Policy Engine** — Rule-based : deny by default, exceptions pour certains rôles/domaines

## Ports

| Service | Port |
|---------|------|
| PostgreSQL | 5432 |
| MinIO API | 9002 |
| MinIO Console | 9003 |
| Airflow | 8080 |
| Governance API | 8100 |
| Streamlit Portal | 8501 |
