"""
Integration tests for Governance API endpoints.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "platform" / "governance"))

import pytest


class TestHealth:
    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "governance-api"


class TestDataProducts:
    def test_create_data_product(self, client):
        resp = client.post("/data-products", json={
            "name": "test_product",
            "domain": "sales",
            "description": "Test data product",
            "owner": "test_owner",
            "sla_tier": "gold",
            "tags": ["test", "sales"],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "test_product"
        assert data["domain"] == "sales"
        assert data["owner"] == "test_owner"
        assert data["sla_tier"] == "gold"
        assert data["status"] == "active"
        assert "id" in data

    def test_create_duplicate_data_product(self, client):
        client.post("/data-products", json={
            "name": "duplicate",
            "domain": "sales",
            "owner": "owner1",
        })
        resp = client.post("/data-products", json={
            "name": "duplicate",
            "domain": "marketing",
            "owner": "owner2",
        })
        assert resp.status_code == 409

    def test_list_data_products(self, client):
        client.post("/data-products", json={
            "name": "dp1", "domain": "sales", "owner": "owner1",
        })
        client.post("/data-products", json={
            "name": "dp2", "domain": "marketing", "owner": "owner2",
        })
        resp = client.get("/data-products")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2

    def test_list_data_products_filtered_by_domain(self, client):
        client.post("/data-products", json={
            "name": "dp_sales", "domain": "sales", "owner": "owner1",
        })
        client.post("/data-products", json={
            "name": "dp_mkt", "domain": "marketing", "owner": "owner2",
        })
        resp = client.get("/data-products?domain=sales")
        data = resp.json()
        assert len(data) == 1
        assert data[0]["domain"] == "sales"

    def test_get_data_product_by_id(self, client):
        create_resp = client.post("/data-products", json={
            "name": "get_test", "domain": "finance", "owner": "owner",
        })
        dp_id = create_resp.json()["id"]
        resp = client.get(f"/data-products/{dp_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "get_test"

    def test_get_data_product_not_found(self, client):
        resp = client.get("/data-products/9999")
        assert resp.status_code == 404


class TestDataContracts:
    def test_create_data_contract(self, client):
        resp = client.post("/data-contracts", json={
            "name": "contract1",
            "provider_domain": "sales",
            "consumer_domain": "marketing",
            "data_product_name": "customer_360",
            "sla": {"uptime": 99.5, "max_latency": "1h"},
            "terms": {"purpose": "analytics"},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "contract1"
        assert data["provider_domain"] == "sales"
        assert data["status"] == "draft"

    def test_list_data_contracts(self, client):
        client.post("/data-contracts", json={
            "name": "c1", "provider_domain": "sales",
            "consumer_domain": "marketing", "data_product_name": "dp1",
        })
        client.post("/data-contracts", json={
            "name": "c2", "provider_domain": "finance",
            "consumer_domain": "sales", "data_product_name": "dp2",
        })
        resp = client.get("/data-contracts")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_data_contract_by_id(self, client):
        create_resp = client.post("/data-contracts", json={
            "name": "contract_get", "provider_domain": "sales",
            "consumer_domain": "marketing", "data_product_name": "dp",
        })
        c_id = create_resp.json()["id"]
        resp = client.get(f"/data-contracts/{c_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "contract_get"

    def test_get_data_contract_not_found(self, client):
        resp = client.get("/data-contracts/9999")
        assert resp.status_code == 404


class TestPolicies:
    def test_create_policy(self, client):
        resp = client.post("/policies", json={
            "name": "policy1",
            "policy_type": "access_control",
            "effect": "allow",
            "priority": 100,
            "rule": {"actors": [r"test_.*"], "actions": ["read"], "resources": {}},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "policy1"
        assert data["enabled"] is True

    def test_list_policies(self, client):
        resp = client.get("/policies")
        assert resp.status_code == 200
        assert len(resp.json()) >= 4  # 4 default policies

    def test_list_policies_filtered_by_enabled(self, client):
        client.post("/policies", json={
            "name": "disabled_policy", "policy_type": "access_control",
            "effect": "deny", "priority": 0,
            "rule": {},
        })
        resp = client.get("/policies?enabled=true")
        for p in resp.json():
            assert p["enabled"] is True


class TestDomains:
    def test_create_domain(self, client):
        resp = client.post("/domains", json={
            "name": "analytics",
            "description": "Analytics domain",
            "owner": "analytics-team",
            "storage_quota_gb": 50.0,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "analytics"
        assert data["status"] == "active"

    def test_list_domains(self, client):
        client.post("/domains", json={
            "name": "test_domain", "owner": "admin",
        })
        resp = client.get("/domains")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1


class TestPolicyEvaluation:
    def test_evaluate_admin_access(self, client):
        resp = client.post("/evaluate?actor=admin&action=write", json={
            "domain": "sales",
            "name": "any_product",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["allowed"] is True

    def test_evaluate_default_deny(self, client):
        resp = client.post("/evaluate?actor=stranger&action=read", json={
            "domain": "finance",
            "name": "profit_loss",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["allowed"] is False

    def test_evaluate_marketing_read_all(self, client):
        resp = client.post("/evaluate?actor=marketing_user&action=read", json={
            "domain": "sales",
            "name": "some_product",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["allowed"] is True

    def test_evaluate_finance_gold_sales(self, client):
        resp = client.post("/evaluate?actor=finance_team&action=read", json={
            "domain": "sales",
            "name": "gold_product",
            "sla_tier": "gold",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["allowed"] is True


class TestAuditLogs:
    def test_audit_logs_after_operations(self, client):
        client.post("/data-products", json={
            "name": "audit_dp", "domain": "sales", "owner": "admin",
        })
        client.post("/data-contracts", json={
            "name": "audit_contract", "provider_domain": "sales",
            "consumer_domain": "marketing", "data_product_name": "audit_dp",
        })
        resp = client.get("/audit-logs")
        assert resp.status_code == 200
        logs = resp.json()
        assert len(logs) >= 2

    def test_audit_log_limit(self, client):
        for i in range(5):
            client.post("/domains", json={
                "name": f"domain_{i}", "owner": "admin",
            })
        resp = client.get("/audit-logs?limit=3")
        assert len(resp.json()) == 3
