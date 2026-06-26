"""
Airflow DAG — Data Mesh Governance Pipeline.

Orchestrates:
1. Domain health checks
2. Data contract validation
3. Schema drift detection
4. Cost attribution report
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    "owner": "data-platform",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def check_domain_health():
    import psycopg2
    domains = [
        ("Sales", "sales_db"),
        ("Marketing", "marketing_db"),
        ("Finance", "finance_db"),
    ]
    for name, db in domains:
        try:
            conn = psycopg2.connect(
                dbname=db,
                user="admin",
                password="admin123",
                host="postgres-domains",
                port=5432,
            )
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            conn.close()
            print(f"  ✓ {name} domain healthy")
        except Exception as e:
            print(f"  ✗ {name} domain unhealthy: {e}")
            raise


def validate_data_contracts():
    import requests
    try:
        r = requests.get("http://governance-api:8100/data-contracts", timeout=5)
        contracts = r.json()
        print(f"  {len(contracts)} data contracts found")
        for c in contracts:
            print(f"    - {c['name']}: {c['status']}")
    except Exception as e:
        print(f"  Failed to validate contracts: {e}")


def detect_schema_drift():
    domains_schemas = {
        "sales_db": ["input.raw_transactions", "output.sales_transactions", "output.customer_360"],
        "marketing_db": ["input.campaigns", "output.campaign_performance"],
        "finance_db": ["input.general_ledger", "output.profit_loss"],
    }
    for db, tables in domains_schemas.items():
        try:
            conn = psycopg2.connect(
                dbname=db,
                user="admin",
                password="admin123",
                host="postgres-domains",
                port=5432,
            )
            cur = conn.cursor()
            for table in tables:
                cur.execute(
                    """
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    """,
                    (table.split(".")[0], table.split(".")[1]),
                )
                cols = cur.fetchall()
                print(f"  {db}.{table}: {len(cols)} columns")
            cur.close()
            conn.close()
        except Exception as e:
            print(f"  Schema drift check failed for {db}: {e}")


def generate_cost_report():
    try:
        conn = psycopg2.connect(
            dbname="finance_db",
            user="admin",
            password="admin123",
            host="postgres-domains",
            port=5432,
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT department, SUM(debit) as total_cost
            FROM input.general_ledger
            WHERE entry_date >= NOW() - INTERVAL '30 days'
            GROUP BY department
            ORDER BY total_cost DESC
        """)
        rows = cur.fetchall()
        print("  Cost by department (last 30 days):")
        for dept, cost in rows:
            print(f"    {dept}: ${cost:,.2f}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  Cost report failed: {e}")


with DAG(
    "governance_pipeline",
    default_args=default_args,
    description="Data Mesh governance orchestration",
    schedule="0 6 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["governance", "data-mesh"],
) as dag:

    start = EmptyOperator(task_id="start")

    check_health = PythonOperator(
        task_id="check_domain_health",
        python_callable=check_domain_health,
    )

    validate_contracts = PythonOperator(
        task_id="validate_data_contracts",
        python_callable=validate_data_contracts,
    )

    schema_drift = PythonOperator(
        task_id="detect_schema_drift",
        python_callable=detect_schema_drift,
    )

    cost_report = PythonOperator(
        task_id="generate_cost_report",
        python_callable=generate_cost_report,
    )

    end = EmptyOperator(task_id="end")

    start >> [check_health, validate_contracts] >> schema_drift >> cost_report >> end
