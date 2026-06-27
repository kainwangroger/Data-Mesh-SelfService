"""
Unit tests for PolicyEngine.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "platform" / "governance"))

import pytest
from policy import PolicyEngine, DEFAULT_POLICIES


@pytest.fixture
def engine():
    return PolicyEngine()


@pytest.fixture
def default_policies():
    return DEFAULT_POLICIES


class TestPolicyEngineInit:
    def test_engine_creation(self, engine):
        assert isinstance(engine, PolicyEngine)

    def test_default_policies_count(self, default_policies):
        assert len(default_policies) == 4


class TestDefaultPolicyEvaluation:
    def test_admin_full_access(self, engine, default_policies):
        result = engine.evaluate(
            actor="admin",
            action="write",
            resource={"domain": "finance", "name": "profit_loss"},
            policies=default_policies,
        )
        assert result["allowed"] is True
        assert result["matched_policy"] == "admin_full_access"

    def test_admin_any_action(self, engine, default_policies):
        result = engine.evaluate(
            actor="admin",
            action="delete",
            resource={"domain": "sales", "name": "anything"},
            policies=default_policies,
        )
        assert result["allowed"] is True

    def test_marketing_read_all(self, engine, default_policies):
        result = engine.evaluate(
            actor="marketing_analyst",
            action="read",
            resource={"domain": "sales", "name": "sales_transactions"},
            policies=default_policies,
        )
        assert result["allowed"] is True
        assert result["matched_policy"] == "marketing_read_all"

    def test_marketing_cannot_write(self, engine, default_policies):
        result = engine.evaluate(
            actor="marketing_analyst",
            action="write",
            resource={"domain": "sales", "name": "sales_transactions"},
            policies=default_policies,
        )
        assert result["allowed"] is False

    def test_finance_read_gold_sales(self, engine, default_policies):
        result = engine.evaluate(
            actor="finance_analyst",
            action="read",
            resource={"domain": "sales", "name": "customer_360", "sla_tier": "gold"},
            policies=default_policies,
        )
        assert result["allowed"] is True

    def test_finance_read_bronze_sales_denied(self, engine, default_policies):
        result = engine.evaluate(
            actor="finance_analyst",
            action="read",
            resource={"domain": "sales", "name": "raw_data", "sla_tier": "bronze"},
            policies=default_policies,
        )
        assert result["allowed"] is False

    def test_cross_domain_default_deny(self, engine, default_policies):
        result = engine.evaluate(
            actor="unknown_user",
            action="read",
            resource={"domain": "finance", "name": "profit_loss"},
            policies=default_policies,
        )
        assert result["allowed"] is False
        assert result["matched_policy"] == "default"

    def test_disabled_policy_ignored(self, engine, default_policies):
        policies = [
            {
                "name": "should_not_match",
                "policy_type": "access_control",
                "priority": 1000,
                "effect": "allow",
                "enabled": False,
                "rule": {"actors": [r".*"], "actions": ["*"]},
            },
            *default_policies,
        ]
        result = engine.evaluate(
            actor="unknown_user",
            action="read",
            resource={"domain": "sales"},
            policies=policies,
        )
        assert result["allowed"] is False


class TestCustomPolicies:
    def test_custom_allow(self, engine):
        policies = [
            {
                "name": "custom_read",
                "policy_type": "access_control",
                "priority": 500,
                "effect": "allow",
                "enabled": True,
                "rule": {
                    "actors": [r"custom_.*"],
                    "actions": ["read"],
                    "resources": {"domain": "analytics"},
                },
            },
        ]
        result = engine.evaluate(
            actor="custom_user",
            action="read",
            resource={"domain": "analytics", "name": "dashboard"},
            policies=policies,
        )
        assert result["allowed"] is True

    def test_custom_deny_wins_over_lower_priority(self, engine):
        policies = [
            {
                "name": "high_priority_deny",
                "priority": 100,
                "effect": "deny",
                "enabled": True,
                "rule": {"actors": [r".*"], "actions": ["delete"]},
            },
            {
                "name": "low_priority_allow",
                "priority": 10,
                "effect": "allow",
                "enabled": True,
                "rule": {"actors": [r".*"], "actions": ["delete"]},
            },
        ]
        result = engine.evaluate(
            actor="anyone",
            action="delete",
            resource={"domain": "test"},
            policies=policies,
        )
        assert result["allowed"] is False
        assert result["matched_policy"] == "high_priority_deny"

    def test_resource_attribute_match(self, engine):
        policies = [
            {
                "name": "pii_restricted",
                "priority": 100,
                "effect": "deny",
                "enabled": True,
                "rule": {
                    "actors": [r".*"],
                    "actions": ["read"],
                    "resources": {"contains_pii": "true"},
                },
            },
            {
                "name": "allow_others",
                "priority": 10,
                "effect": "allow",
                "enabled": True,
                "rule": {"actors": [r".*"], "actions": ["read"]},
            },
        ]
        pii_result = engine.evaluate(
            actor="user",
            action="read",
            resource={"name": "customers", "contains_pii": "true"},
            policies=policies,
        )
        assert pii_result["allowed"] is False

        non_pii_result = engine.evaluate(
            actor="user",
            action="read",
            resource={"name": "aggregates", "contains_pii": "false"},
            policies=policies,
        )
        assert non_pii_result["allowed"] is True

    def test_cost_condition(self, engine):
        policies = [
            {
                "name": "cost_limit",
                "priority": 100,
                "effect": "deny",
                "enabled": True,
                "rule": {
                    "actors": [r".*"],
                    "actions": ["query"],
                    "conditions": {"max_cost_per_query": 100},
                },
            },
            {
                "name": "allow_all_queries",
                "priority": 10,
                "effect": "allow",
                "enabled": True,
                "rule": {
                    "actors": [r".*"],
                    "actions": ["query"],
                },
            },
        ]
        cheap = engine.evaluate(
            actor="user",
            action="query",
            resource={"name": "small_data", "estimated_cost": 50},
            policies=policies,
        )
        assert cheap["allowed"] is True
        assert cheap["matched_policy"] == "allow_all_queries"

        expensive = engine.evaluate(
            actor="user",
            action="query",
            resource={"name": "big_data", "estimated_cost": 200},
            policies=policies,
        )
        assert expensive["allowed"] is False
        assert expensive["matched_policy"] == "cost_limit"
