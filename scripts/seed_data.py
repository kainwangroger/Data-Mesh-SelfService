"""
Seed data generator for Data Mesh domains.
Generates realistic sample data for sales, marketing, and finance.
"""

import os
import random
from datetime import datetime, timedelta, date

import psycopg2
from psycopg2.extras import execute_values

random.seed(42)

SALES_PRODUCTS = [
    ("PROD-001", "Électronique"), ("PROD-002", "Électronique"),
    ("PROD-003", "Vêtements"), ("PROD-004", "Vêtements"),
    ("PROD-005", "Alimentation"), ("PROD-006", "Alimentation"),
    ("PROD-007", "Maison"), ("PROD-008", "Maison"),
    ("PROD-009", "Sport"), ("PROD-010", "Sport"),
    ("PROD-011", "Livres"), ("PROD-012", "Musique"),
    ("PROD-013", "Jouets"), ("PROD-014", "Jardin"),
]

MARKETING_CAMPAIGNS = [
    ("CAMP-001", "Promo Été", "email"), ("CAMP-002", "Soldes Hiver", "social"),
    ("CAMP-003", "Lancement Produit", "display"), ("CAMP-004", "Newsletter Q1", "email"),
    ("CAMP-005", "Affiliation Blog", "affiliate"), ("CAMP-006", "Pub TV", "tv"),
]

FINANCE_ACCOUNTS = [
    ("6000", "Achats matières"), ("6010", "Services externes"),
    ("6020", "Frais personnel"), ("6030", "Loyer"),
    ("6040", "Marketing"), ("6050", "Informatique"),
    ("7000", "Ventes produits"), ("7010", "Ventes services"),
    ("8000", "Produits financiers"), ("9000", "Charges exceptionnelles"),
]

DOMAINS = {
    "sales_db": {
        "host": os.getenv("SALES_DB_HOST", "localhost"),
        "port": int(os.getenv("SALES_DB_PORT", "5432")),
    },
    "marketing_db": {
        "host": os.getenv("MK_DB_HOST", "localhost"),
        "port": int(os.getenv("MK_DB_PORT", "5432")),
    },
    "finance_db": {
        "host": os.getenv("FIN_DB_HOST", "localhost"),
        "port": int(os.getenv("FIN_DB_PORT", "5432")),
    },
}


def seed_sales(conn):
    cur = conn.cursor()
    today = date.today()

    # Raw transactions (last 90 days)
    tx_rows = []
    for i in range(500):
        tx_id = f"TX-{today.strftime('%Y%m')}-{i:04d}"
        cust_id = f"CUST-{random.randint(1, 100):04d}"
        prod_id, cat = random.choice(SALES_PRODUCTS)
        amount = round(random.uniform(5, 500), 2)
        qty = random.randint(1, 5)
        tx_date = today - timedelta(days=random.randint(0, 89), hours=random.randint(0, 23))
        store = f"STORE-{random.randint(1, 20):02d}"
        channel = random.choice(["web", "mobile", "store", "api"])
        tx_rows.append((tx_id, cust_id, prod_id, amount, qty, tx_date, store, channel))

    execute_values(
        cur,
        """
        INSERT INTO input.raw_transactions
            (transaction_id, customer_id, product_id, amount, quantity, transaction_date, store_id, channel)
        VALUES %s
        ON CONFLICT (transaction_id) DO NOTHING
        """,
        tx_rows,
    )
    print(f"  + {len(tx_rows)} raw_transactions inserted")

    # Sales transactions output (aggregated daily)
    out_rows = []
    for day_offset in range(90):
        day = today - timedelta(days=day_offset)
        daily_rev = round(random.uniform(1000, 15000), 2)
        cat = random.choice(["Électronique", "Vêtements", "Alimentation", "Maison", "Sport", "Livres"])
        store = f"STORE-{random.randint(1, 20):02d}"
        channel = random.choice(["web", "store"])
        out_rows.append((
            f"DP-SALES-{day.strftime('%Y%m%d')}",
            f"CUST-SUM-{random.randint(1, 50):04d}",
            cat, daily_rev, day, store, channel,
        ))

    execute_values(
        cur,
        """
        INSERT INTO output.sales_transactions
            (transaction_id, customer_id, product_category, amount, transaction_date, store_id, channel)
        VALUES %s
        ON CONFLICT (transaction_id) DO NOTHING
        """,
        out_rows,
    )
    print(f"  + {len(out_rows)} sales_transactions inserted")
    conn.commit()


def seed_marketing(conn):
    cur = conn.cursor()
    today = date.today()

    # Campaigns
    camp_rows = []
    for i, (cid, name, ch) in enumerate(MARKETING_CAMPAIGNS):
        start = today - timedelta(days=random.randint(30, 120))
        end = start + timedelta(days=random.randint(14, 45))
        budget = round(random.uniform(5000, 50000), 2)
        segment = random.choice(["premium", "standard", "new", "all"])
        camp_rows.append((cid, name, ch, budget, start, end, segment))

    execute_values(
        cur,
        """
        INSERT INTO input.campaigns
            (campaign_id, campaign_name, channel, budget, start_date, end_date, target_segment)
        VALUES %s
        ON CONFLICT (campaign_id) DO NOTHING
        """,
        camp_rows,
    )
    print(f"  + {len(camp_rows)} campaigns inserted")

    # Campaign results (daily)
    res_rows = []
    for cid, _, _ in MARKETING_CAMPAIGNS:
        for day_offset in range(30):
            day = today - timedelta(days=day_offset)
            res_id = f"RES-{cid}-{day.strftime('%Y%m%d')}"
            impressions = random.randint(1000, 50000)
            clicks = int(impressions * random.uniform(0.01, 0.08))
            conv = int(clicks * random.uniform(0.02, 0.12))
            spend = round(random.uniform(50, 500), 2)
            res_rows.append((res_id, cid, impressions, clicks, conv, spend, day))

    execute_values(
        cur,
        """
        INSERT INTO input.campaign_results
            (result_id, campaign_id, impressions, clicks, conversions, spend, result_date)
        VALUES %s
        ON CONFLICT (result_id) DO NOTHING
        """,
        res_rows,
    )
    print(f"  + {len(res_rows)} campaign_results inserted")
    conn.commit()


def seed_finance(conn):
    cur = conn.cursor()
    today = date.today()

    # General ledger entries
    gl_rows = []
    for i in range(200):
        eid = f"GL-{i:04d}"
        acct_code, acct_name = random.choice(FINANCE_ACCOUNTS)
        debit = round(random.uniform(100, 10000), 2) if acct_code.startswith(("6", "9")) else 0
        credit = round(random.uniform(100, 10000), 2) if acct_code.startswith(("7", "8")) else 0
        entry_date = today - timedelta(days=random.randint(0, 89))
        dept = random.choice(["Sales", "Marketing", "R&D", "IT", "HR", "Finance"])
        gl_rows.append((eid, acct_code, debit, credit, entry_date, acct_name, dept))

    execute_values(
        cur,
        """
        INSERT INTO input.general_ledger
            (entry_id, account_code, debit, credit, entry_date, description, department)
        VALUES %s
        ON CONFLICT (entry_id) DO NOTHING
        """,
        gl_rows,
    )
    print(f"  + {len(gl_rows)} general_ledger entries inserted")

    # P&L output
    pl_rows = []
    for day_offset in range(12):
        month = today.replace(day=1) - timedelta(days=day_offset * 30)
        month_start = month.replace(day=1)
        revenue = round(random.uniform(50000, 200000), 2)
        cogs = round(revenue * random.uniform(0.4, 0.6), 2)
        gp = round(revenue - cogs, 2)
        opex = round(revenue * random.uniform(0.2, 0.35), 2)
        np = round(gp - opex, 2)
        pl_rows.append((month_start, revenue, cogs, gp, opex, np))

    execute_values(
        cur,
        """
        INSERT INTO output.profit_loss
            (report_date, revenue, cogs, gross_profit, operating_expenses, net_profit)
        VALUES %s
        ON CONFLICT (report_date) DO NOTHING
        """,
        pl_rows,
    )
    print(f"  + {len(pl_rows)} profit_loss rows inserted")
    conn.commit()


def main():
    user = os.getenv("POSTGRES_USER", "admin")
    password = os.getenv("POSTGRES_PASSWORD", "admin123")
    port = int(os.getenv("POSTGRES_PORT", "5432"))

    print("Seeding Sales domain...")
    conn = psycopg2.connect(dbname="sales_db", user=user, password=password, host="localhost", port=port)
    seed_sales(conn)
    conn.close()

    print("Seeding Marketing domain...")
    conn = psycopg2.connect(dbname="marketing_db", user=user, password=password, host="localhost", port=port)
    seed_marketing(conn)
    conn.close()

    print("Seeding Finance domain...")
    conn = psycopg2.connect(dbname="finance_db", user=user, password=password, host="localhost", port=port)
    seed_finance(conn)
    conn.close()

    print("\n✓ All domains seeded successfully")


if __name__ == "__main__":
    main()
