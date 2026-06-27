"""
Seed script — crée des data products, domaines, contrats et policies
dans la Governance API pour alimenter le portail Streamlit.
Usage: python3 scripts/seed_governance.py
"""

import sys
import os
import json
from urllib.request import urlopen, Request

API = os.getenv("GOVERNANCE_API_URL", "http://localhost:8100")


from urllib.request import urlopen, Request
from urllib.error import HTTPError


def api_post(path, data):
    url = f"{API}{path}"
    req = Request(url, data=json.dumps(data).encode(),
                  headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        raise Exception(f"{e.code}: {e.read().decode()}")


def api_get(path):
    url = f"{API}{path}"
    with urlopen(url, timeout=5) as resp:
        return json.loads(resp.read())

DATA_PRODUCTS = [
    # Sales
    {"name": "sales_transactions", "domain": "sales", "owner": "equipe-sales", "sla_tier": "gold",
     "description": "Transactions de ventes en temps réel", "tags": ["ventes", "temps-reel"]},
    {"name": "customer_360", "domain": "sales", "owner": "equipe-sales", "sla_tier": "gold",
     "description": "Vue unifiée clients (CRM + ventes)", "tags": ["clients", "crm"]},
    {"name": "inventory_forecast", "domain": "sales", "owner": "equipe-logistique", "sla_tier": "silver",
     "description": "Prévisions de stock par entrepôt", "tags": ["stock", "prevision"]},
    {"name": "product_catalog", "domain": "sales", "owner": "equipe-produit", "sla_tier": "bronze",
     "description": "Catalogue produits mis à jour hebdomadaire", "tags": ["catalogue", "produits"]},
    # Marketing
    {"name": "campaign_performance", "domain": "marketing", "owner": "equipe-marketing", "sla_tier": "gold",
     "description": "ROI des campagnes publicitaires", "tags": ["campagnes", "roi"]},
    {"name": "audience_insights", "domain": "marketing", "owner": "equipe-marketing", "sla_tier": "silver",
     "description": "Segmentation et insights audiences", "tags": ["audience", "segmentation"]},
    {"name": "social_media_metrics", "domain": "marketing", "owner": "equipe-reseaux", "sla_tier": "bronze",
     "description": "Métriques réseaux sociaux agrégées", "tags": ["reseaux-sociaux", "metrics"]},
    # Finance
    {"name": "profit_loss", "domain": "finance", "owner": "equipe-finance", "sla_tier": "gold",
     "description": "Compte de résultat mensuel", "tags": ["finance", "pnl"]},
    {"name": "cost_by_department", "domain": "finance", "owner": "equipe-finance", "sla_tier": "silver",
     "description": "Suivi des coûts par département", "tags": ["couts", "departements"]},
    {"name": "budget_forecast", "domain": "finance", "owner": "equipe-finance", "sla_tier": "silver",
     "description": "Prévisions budgétaires trimestrielles", "tags": ["budget", "prevision"]},
    {"name": "invoice_aging", "domain": "finance", "owner": "equipe-comptabilite", "sla_tier": "bronze",
     "description": "Suivi des factures impayées", "tags": ["factures", "recouvrement"]},
]

DOMAINS = [
    {"name": "sales", "description": "Domaine commercial et ventes", "owner": "equipe-sales", "database": "sales_db", "storage_quota_gb": 100},
    {"name": "marketing", "description": "Domaine marketing et campagnes", "owner": "equipe-marketing", "database": "marketing_db", "storage_quota_gb": 50},
    {"name": "finance", "description": "Domaine financier et comptable", "owner": "equipe-finance", "database": "finance_db", "storage_quota_gb": 75},
]

CONTRACTS = [
    {"name": "sales_to_marketing_customers", "provider_domain": "sales", "consumer_domain": "marketing",
     "data_product_name": "customer_360", "sla": {"uptime": 99.5, "max_latency": "1h"},
     "terms": {"purpose": "campaign_targeting", "pii_restricted": True}},
    {"name": "sales_to_finance_revenue", "provider_domain": "sales", "consumer_domain": "finance",
     "data_product_name": "sales_transactions", "sla": {"uptime": 99.9, "max_latency": "30min"},
     "terms": {"purpose": "financial_reporting"}},
    {"name": "marketing_to_sales_campaigns", "provider_domain": "marketing", "consumer_domain": "sales",
     "data_product_name": "campaign_performance", "sla": {"uptime": 99, "max_latency": "6h"},
     "terms": {"purpose": "sales_attribution"}},
    {"name": "finance_to_marketing_budget", "provider_domain": "finance", "consumer_domain": "marketing",
     "data_product_name": "budget_forecast", "sla": {"uptime": 99, "max_latency": "24h"},
     "terms": {"purpose": "budget_planning"}},
]


def seed():
    print(f"Seeding Governance API at {API}...")

    try:
        health = api_get("/health")
        print(f"  API health: {health['status']}")
    except Exception as e:
        print(f"  API unreachable: {e}")
        return

    for d in DOMAINS:
        try:
            api_post("/domains", d)
            print(f"  + Domain '{d['name']}' created")
        except Exception as e:
            if "already exists" in str(e) or "409" in str(e):
                print(f"  ~ Domain '{d['name']}' already exists")
            else:
                print(f"  ! Domain '{d['name']}' error: {e}")

    for dp in DATA_PRODUCTS:
        try:
            api_post("/data-products", dp)
            print(f"  + Data product '{dp['name']}' created")
        except Exception as e:
            if "already exists" in str(e) or "409" in str(e):
                print(f"  ~ Data product '{dp['name']}' already exists")
            else:
                print(f"  ! Data product '{dp['name']}' error: {e}")

    for c in CONTRACTS:
        try:
            api_post("/data-contracts", c)
            print(f"  + Contract '{c['name']}' created")
        except Exception as e:
            print(f"  ! Contract '{c['name']}' error: {e}")

    print("\nSeed complete!")
    print(f"  Data products: {len(DATA_PRODUCTS)}")
    print(f"  Domains: {len(DOMAINS)}")
    print(f"  Contracts: {len(CONTRACTS)}")


if __name__ == "__main__":
    seed()
