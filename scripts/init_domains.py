"""
Initialisation des domaines Data Mesh.
Crée les tables Input/Output pour chaque domaine.
"""

import os
import sys

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

DOMAINS = [
    {
        "name": "sales",
        "db": "sales_db",
        "tables": {
            "input": {
                "raw_transactions": """
                    CREATE TABLE IF NOT EXISTS input.raw_transactions (
                        id SERIAL PRIMARY KEY,
                        transaction_id VARCHAR(64) UNIQUE NOT NULL,
                        customer_id VARCHAR(32) NOT NULL,
                        product_id VARCHAR(32) NOT NULL,
                        amount DECIMAL(12,2) NOT NULL,
                        quantity INT NOT NULL,
                        transaction_date TIMESTAMP NOT NULL,
                        store_id VARCHAR(16) NOT NULL,
                        channel VARCHAR(16) NOT NULL,
                        ingested_at TIMESTAMP DEFAULT NOW()
                    )
                """,
                "customer_events": """
                    CREATE TABLE IF NOT EXISTS input.customer_events (
                        id SERIAL PRIMARY KEY,
                        event_id VARCHAR(64) UNIQUE NOT NULL,
                        customer_id VARCHAR(32) NOT NULL,
                        event_type VARCHAR(32) NOT NULL,
                        event_data JSONB,
                        event_timestamp TIMESTAMP NOT NULL,
                        ingested_at TIMESTAMP DEFAULT NOW()
                    )
                """,
            },
            "output": {
                "sales_transactions": """
                    CREATE TABLE IF NOT EXISTS output.sales_transactions (
                        id SERIAL PRIMARY KEY,
                        transaction_id VARCHAR(64) UNIQUE NOT NULL,
                        customer_id VARCHAR(32) NOT NULL,
                        product_category VARCHAR(64) NOT NULL,
                        amount DECIMAL(12,2) NOT NULL,
                        transaction_date DATE NOT NULL,
                        store_id VARCHAR(16) NOT NULL,
                        channel VARCHAR(16) NOT NULL,
                        data_product_version VARCHAR(8) DEFAULT '1.0',
                        sla_tier VARCHAR(8) DEFAULT 'silver',
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """,
                "customer_360": """
                    CREATE TABLE IF NOT EXISTS output.customer_360 (
                        id SERIAL PRIMARY KEY,
                        customer_id VARCHAR(32) UNIQUE NOT NULL,
                        total_spent DECIMAL(14,2) DEFAULT 0,
                        avg_ticket DECIMAL(10,2) DEFAULT 0,
                        visit_count INT DEFAULT 0,
                        preferred_channel VARCHAR(16),
                        last_purchase_date DATE,
                        segment VARCHAR(16),
                        data_product_version VARCHAR(8) DEFAULT '1.0',
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """,
                "inventory_forecast": """
                    CREATE TABLE IF NOT EXISTS output.inventory_forecast (
                        id SERIAL PRIMARY KEY,
                        product_id VARCHAR(32) NOT NULL,
                        forecast_date DATE NOT NULL,
                        predicted_demand DECIMAL(10,2),
                        confidence_lower DECIMAL(10,2),
                        confidence_upper DECIMAL(10,2),
                        data_product_version VARCHAR(8) DEFAULT '1.0',
                        model_name VARCHAR(32),
                        updated_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(product_id, forecast_date)
                    )
                """,
            },
        },
    },
    {
        "name": "marketing",
        "db": "marketing_db",
        "tables": {
            "input": {
                "campaigns": """
                    CREATE TABLE IF NOT EXISTS input.campaigns (
                        id SERIAL PRIMARY KEY,
                        campaign_id VARCHAR(64) UNIQUE NOT NULL,
                        campaign_name VARCHAR(128) NOT NULL,
                        channel VARCHAR(32) NOT NULL,
                        budget DECIMAL(12,2) NOT NULL,
                        start_date DATE NOT NULL,
                        end_date DATE NOT NULL,
                        target_segment VARCHAR(32),
                        ingested_at TIMESTAMP DEFAULT NOW()
                    )
                """,
                "campaign_results": """
                    CREATE TABLE IF NOT EXISTS input.campaign_results (
                        id SERIAL PRIMARY KEY,
                        result_id VARCHAR(64) UNIQUE NOT NULL,
                        campaign_id VARCHAR(64) NOT NULL,
                        impressions INT DEFAULT 0,
                        clicks INT DEFAULT 0,
                        conversions INT DEFAULT 0,
                        spend DECIMAL(12,2) DEFAULT 0,
                        result_date DATE NOT NULL,
                        ingested_at TIMESTAMP DEFAULT NOW()
                    )
                """,
            },
            "output": {
                "campaign_performance": """
                    CREATE TABLE IF NOT EXISTS output.campaign_performance (
                        id SERIAL PRIMARY KEY,
                        campaign_id VARCHAR(64) NOT NULL,
                        campaign_name VARCHAR(128),
                        channel VARCHAR(32),
                        total_impressions INT DEFAULT 0,
                        total_clicks INT DEFAULT 0,
                        total_conversions INT DEFAULT 0,
                        total_spend DECIMAL(14,2) DEFAULT 0,
                        ctr DECIMAL(6,4),
                        roas DECIMAL(10,4),
                        data_product_version VARCHAR(8) DEFAULT '1.0',
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """,
                "audience_insights": """
                    CREATE TABLE IF NOT EXISTS output.audience_insights (
                        id SERIAL PRIMARY KEY,
                        segment VARCHAR(32) NOT NULL,
                        customer_count INT DEFAULT 0,
                        avg_ltv DECIMAL(10,2) DEFAULT 0,
                        top_channel VARCHAR(32),
                        engagement_rate DECIMAL(6,4),
                        data_product_version VARCHAR(8) DEFAULT '1.0',
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """,
            },
        },
    },
    {
        "name": "finance",
        "db": "finance_db",
        "tables": {
            "input": {
                "general_ledger": """
                    CREATE TABLE IF NOT EXISTS input.general_ledger (
                        id SERIAL PRIMARY KEY,
                        entry_id VARCHAR(64) UNIQUE NOT NULL,
                        account_code VARCHAR(16) NOT NULL,
                        debit DECIMAL(14,2) DEFAULT 0,
                        credit DECIMAL(14,2) DEFAULT 0,
                        entry_date DATE NOT NULL,
                        description TEXT,
                        department VARCHAR(32),
                        ingested_at TIMESTAMP DEFAULT NOW()
                    )
                """,
                "invoices": """
                    CREATE TABLE IF NOT EXISTS input.invoices (
                        id SERIAL PRIMARY KEY,
                        invoice_id VARCHAR(64) UNIQUE NOT NULL,
                        vendor_id VARCHAR(32) NOT NULL,
                        amount DECIMAL(12,2) NOT NULL,
                        due_date DATE NOT NULL,
                        paid BOOLEAN DEFAULT FALSE,
                        category VARCHAR(32),
                        ingested_at TIMESTAMP DEFAULT NOW()
                    )
                """,
            },
            "output": {
                "profit_loss": """
                    CREATE TABLE IF NOT EXISTS output.profit_loss (
                        id SERIAL PRIMARY KEY,
                        report_date DATE NOT NULL,
                        revenue DECIMAL(14,2) DEFAULT 0,
                        cogs DECIMAL(14,2) DEFAULT 0,
                        gross_profit DECIMAL(14,2) DEFAULT 0,
                        operating_expenses DECIMAL(14,2) DEFAULT 0,
                        net_profit DECIMAL(14,2) DEFAULT 0,
                        data_product_version VARCHAR(8) DEFAULT '1.0',
                        updated_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(report_date)
                    )
                """,
                "cost_by_department": """
                    CREATE TABLE IF NOT EXISTS output.cost_by_department (
                        id SERIAL PRIMARY KEY,
                        department VARCHAR(32) NOT NULL,
                        report_month DATE NOT NULL,
                        total_cost DECIMAL(14,2) DEFAULT 0,
                        headcount INT DEFAULT 0,
                        cost_per_head DECIMAL(10,2) DEFAULT 0,
                        data_product_version VARCHAR(8) DEFAULT '1.0',
                        updated_at TIMESTAMP DEFAULT NOW(),
                        UNIQUE(department, report_month)
                    )
                """,
            },
        },
    },
]


def get_connection(host, port, user, password, dbname):
    conn = psycopg2.connect(
        host=host, port=port, user=user, password=password, dbname=dbname
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def init_domains(host="localhost", port=5432, user="admin", password="admin123"):
    # First connect to default db to ensure domain databases exist
    conn = get_connection(host, port, user, password, "datamesh")
    cur = conn.cursor()

    for domain in DOMAINS:
        db_name = domain["db"]
        cur.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (db_name,)
        )
        if not cur.fetchone():
            cur.execute(f'CREATE DATABASE {db_name}')
            print(f"  + Database {db_name} created")
        else:
            print(f"  ~ Database {db_name} already exists")

    cur.close()
    conn.close()

    # Now create tables in each domain database
    for domain in DOMAINS:
        db_name = domain["db"]
        conn = get_connection(host, port, user, password, db_name)
        cur = conn.cursor()

        # Create schemas
        for schema in ("input", "output"):
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            print(f"  + Schema {db_name}.{schema} ready")

        # Create tables
        for schema_name, tables in domain["tables"].items():
            for table_name, ddl in tables.items():
                cur.execute(ddl)
                print(f"  + Table {db_name}.{schema_name}.{table_name} ready")

        cur.close()
        conn.close()

    print("\n✓ All domains initialized successfully")


if __name__ == "__main__":
    init_domains(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "admin123"),
    )
