"""
Policy-as-Code engine for Data Mesh governance.

Évalue les règles d'accès cross-domaine basées sur :
- Qui (role) peut accéder à quoi (data product)
- Sous quelles conditions (SLA, cost, PII)
"""

import re
from datetime import datetime, timezone
from typing import Any


class PolicyEngine:
    def __init__(self, db_session=None):
        self._db = db_session

    def evaluate(self, actor: str, action: str, resource: dict, policies: list[dict]) -> dict:
        """
        Évalue toutes les policies actives contre une requête d'accès.

        Returns:
            dict: {"allowed": bool, "matched_policy": str, "reason": str}
        """
        for policy in sorted(policies, key=lambda p: p.get("priority", 0), reverse=True):
            if not policy.get("enabled", True):
                continue

            rule = policy.get("rule", {})
            match = self._match_rule(rule, actor, action, resource)
            if match:
                effect = policy.get("effect", "deny")
                return {
                    "allowed": effect == "allow",
                    "matched_policy": policy.get("name", "unknown"),
                    "effect": effect,
                    "reason": f"Policy '{policy['name']}': {effect}",
                }

        return {
            "allowed": False,
            "matched_policy": "default",
            "effect": "deny",
            "reason": "No matching policy — denied by default",
        }

    def _match_rule(self, rule: dict, actor: str, action: str, resource: dict) -> bool:
        if not rule:
            return False

        # Match actor (role / user)
        if "actors" in rule:
            if not any(re.match(p, actor) for p in rule["actors"]):
                return False

        # Match action (supports "*" wildcard for all actions)
        if "actions" in rule:
            if "*" not in rule["actions"] and action not in rule["actions"]:
                return False

        # Match resource attributes
        if "resources" in rule:
            for key, pattern in rule["resources"].items():
                res_val = resource.get(key, "")
                if not re.match(str(pattern), str(res_val)):
                    return False

        # Match conditions (SLA, cost, etc.)
        if "conditions" in rule:
            for cond_key, cond_val in rule["conditions"].items():
                if cond_key == "sla_tier":
                    allowed_tiers = cond_val if isinstance(cond_val, list) else [cond_val]
                    if resource.get("sla_tier") not in allowed_tiers:
                        return False
                if cond_key == "max_cost_per_query":
                    if resource.get("estimated_cost", 0) <= cond_val:
                        return False

        return True


# ── Built-in policies ────────────────────────────────

DEFAULT_POLICIES = [
    {
        "name": "cross_domain_deny",
        "description": "Par défaut, les accès cross-domaine sont refusés",
        "policy_type": "access_control",
        "priority": 0,
        "effect": "deny",
        "enabled": True,
        "rule": {},
    },
    {
        "name": "sales_finance_read",
        "description": "Finance peut lire les data products Sales de niveau gold",
        "policy_type": "access_control",
        "priority": 100,
        "effect": "allow",
        "enabled": True,
        "rule": {
            "actors": [r"finance_.*", r"admin"],
            "actions": ["read", "query"],
            "resources": {"domain": "sales"},
            "conditions": {"sla_tier": ["gold", "silver"]},
        },
    },
    {
        "name": "marketing_read_all",
        "description": "Marketing peut lire tous les data products",
        "policy_type": "access_control",
        "priority": 50,
        "effect": "allow",
        "enabled": True,
        "rule": {
            "actors": [r"marketing_.*", r"admin"],
            "actions": ["read"],
            "resources": {},
        },
    },
    {
        "name": "admin_full_access",
        "description": "Les administrateurs ont un accès total",
        "policy_type": "access_control",
        "priority": 1000,
        "effect": "allow",
        "enabled": True,
        "rule": {
            "actors": [r"admin"],
            "actions": ["*"],
            "resources": {},
        },
    },
]
