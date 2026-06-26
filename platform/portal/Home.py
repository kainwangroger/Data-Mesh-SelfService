"""
Data Mesh Self-Service Portal
Page d'accueil — catalogue des data products + demandes d'accès
"""

import os
import json
from urllib.request import urlopen, Request

import streamlit as st
import pandas as pd
import plotly.express as px

GOVERNANCE_API = os.getenv("GOVERNANCE_API_URL", "http://localhost:8100")

st.set_page_config(
    page_title="Data Mesh Portal",
    page_icon="🔀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🔀 Data Mesh Self-Service Portal")
st.markdown("---")


# ── Sidebar ──────────────────────────────

st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Aller à",
    ["🏠 Accueil", "📦 Data Products", "📋 Data Contracts", "🔐 Policies", "📊 Monitoring"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Domaine courant**")
domain_filter = st.sidebar.selectbox(
    "Filtrer par domaine",
    ["Tous", "sales", "marketing", "finance"],
)


# ── API helpers ──────────────────────────

def api_get(path):
    try:
        req = Request(f"{GOVERNANCE_API}{path}")
        with urlopen(req, timeout=3) as resp:
            return json.loads(resp.read())
    except Exception as e:
        st.error(f"API error: {e}")
        return []


def api_post(path, data):
    try:
        req = Request(
            f"{GOVERNANCE_API}{path}",
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=3) as resp:
            return json.loads(resp.read())
    except Exception as e:
        st.error(f"API error: {e}")
        return None


# ── Pages ─────────────────────────────────

if page == "🏠 Accueil":
    col1, col2, col3, col4 = st.columns(4)

    data_products = api_get("/data-products")
    contracts = api_get("/data-contracts")
    policies = api_get("/policies")
    domains = api_get("/domains")

    col1.metric("Data Products", len(data_products))
    col2.metric("Data Contracts", len(contracts))
    col3.metric("Policies", len(policies))
    col4.metric("Domains", len(domains))

    st.markdown("### Data Products récents")
    if data_products:
        df = pd.DataFrame(data_products)
        if domain_filter != "Tous":
            df = df[df["domain"] == domain_filter]
        st.dataframe(
            df[["name", "domain", "owner", "sla_tier", "status"]],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Aucun data product enregistré. Va dans la section Data Products pour en créer.")

    st.markdown("### Data Products par domaine")
    if data_products:
        df_counts = pd.DataFrame(data_products).groupby("domain").size().reset_index(name="count")
        fig = px.pie(df_counts, values="count", names="domain", title="Répartition par domaine")
        st.plotly_chart(fig, use_container_width=True)


elif page == "📦 Data Products":
    st.header("Data Products")

    # Create new
    with st.expander("➕ Nouveau Data Product"):
        with st.form("new_dp"):
            col1, col2 = st.columns(2)
            with col1:
                dp_name = st.text_input("Nom", placeholder="sales_transactions_v2")
                dp_domain = st.selectbox("Domaine", ["sales", "marketing", "finance"])
                dp_owner = st.text_input("Owner", placeholder="equipe-sales")
            with col2:
                dp_desc = st.text_area("Description", placeholder="Description du data product")
                dp_sla = st.selectbox("SLA Tier", ["gold", "silver", "bronze"])
                dp_tags = st.text_input("Tags (virgules)", placeholder="transactions, ventes, temps-reel")
            submitted = st.form_submit_button("Créer")
            if submitted:
                tags = [t.strip() for t in dp_tags.split(",") if t.strip()]
                result = api_post("/data-products", {
                    "name": dp_name,
                    "domain": dp_domain,
                    "description": dp_desc,
                    "owner": dp_owner,
                    "sla_tier": dp_sla,
                    "tags": tags,
                })
                if result:
                    st.success(f"Data product '{dp_name}' créé !")
                    st.rerun()

    # List
    st.markdown("### Catalogue")
    dps = api_get("/data-products")
    if dps:
        if domain_filter != "Tous":
            dps = [dp for dp in dps if dp["domain"] == domain_filter]
        for dp in dps:
            with st.container(border=True):
                cols = st.columns([3, 1, 1, 1])
                cols[0].markdown(f"**{dp['name']}**  \n*{dp['description'] or ''}*")
                cols[1].markdown(f"Domaine: `{dp['domain']}`")
                cols[2].markdown(f"SLA: `{dp['sla_tier']}`")
                cols[3].markdown(f"Status: `{dp['status']}`")
    else:
        st.info("Aucun data product — créez-en un avec le formulaire ci-dessus.")


elif page == "📋 Data Contracts":
    st.header("Data Contracts")

    with st.expander("➕ Nouveau contrat"):
        with st.form("new_contract"):
            col1, col2 = st.columns(2)
            with col1:
                c_name = st.text_input("Nom du contrat", placeholder="sales_to_marketing_v1")
                c_provider = st.selectbox("Domaine fournisseur", ["sales", "marketing", "finance"])
                c_consumer = st.selectbox("Domaine consommateur", ["sales", "marketing", "finance"])
            with col2:
                c_product = st.text_input("Data product", placeholder="customer_360")
                c_sla_uptime = st.slider("SLA uptime (%)", 90, 100, 99)
                c_sla_latency = st.selectbox("SLA latence max", ["1h", "6h", "24h"])
            submitted = st.form_submit_button("Créer")
            if submitted:
                result = api_post("/data-contracts", {
                    "name": c_name,
                    "provider_domain": c_provider,
                    "consumer_domain": c_consumer,
                    "data_product_name": c_product,
                    "sla": {"uptime": c_sla_uptime, "max_latency": c_sla_latency},
                    "terms": {"purpose": "analytics"},
                })
                if result:
                    st.success("Contrat créé !")
                    st.rerun()

    contracts = api_get("/data-contracts")
    if contracts:
        df = pd.DataFrame(contracts)
        st.dataframe(
            df[["name", "provider_domain", "consumer_domain", "data_product_name", "status"]],
            use_container_width=True,
            hide_index=True,
        )


elif page == "🔐 Policies":
    st.header("Access Policies")

    with st.expander("➕ Nouvelle policy"):
        with st.form("new_policy"):
            col1, col2 = st.columns(2)
            with col1:
                p_name = st.text_input("Nom", placeholder="marketing_read_gold")
                p_type = st.selectbox("Type", ["access_control", "data_quality", "cost_control"])
                p_effect = st.selectbox("Effet", ["allow", "deny"])
            with col2:
                p_desc = st.text_area("Description")
                p_priority = st.number_input("Priorité", 0, 1000, 100)
                p_actors = st.text_input("Acteurs (regex)", placeholder="marketing_.*")
            submitted = st.form_submit_button("Créer")
            if submitted:
                result = api_post("/policies", {
                    "name": p_name,
                    "description": p_desc,
                    "policy_type": p_type,
                    "effect": p_effect,
                    "priority": p_priority,
                    "rule": {
                        "actors": [p_actors] if p_actors else [],
                        "actions": ["read"],
                        "resources": {},
                    },
                })
                if result:
                    st.success("Policy créée !")
                    st.rerun()

    policies = api_get("/policies")
    if policies:
        df = pd.DataFrame(policies)
        st.dataframe(
            df[["name", "policy_type", "effect", "priority", "enabled"]],
            use_container_width=True,
            hide_index=True,
        )


elif page == "📊 Monitoring":
    st.header("Monitoring & Audit")

    st.subheader("Healthcheck")
    health = api_get("/health")
    if health:
        st.json(health)

    st.subheader("Audit Logs")
    logs = api_get("/audit-logs")
    if logs:
        df = pd.DataFrame(logs)
        st.dataframe(
            df[["created_at", "action", "actor", "resource_type", "resource_id"]],
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("Policy Evaluation")
    col1, col2 = st.columns(2)
    with col1:
        eval_actor = st.text_input("Acteur", "marketing_analyst")
        eval_action = st.selectbox("Action", ["read", "write", "query", "admin"])
    with col2:
        eval_domain = st.text_input("Domaine cible", "sales")
        eval_product = st.text_input("Data product cible", "customer_360")

    if st.button("Évaluer l'accès"):
        result = api_post("/evaluate", {
            "actor": eval_actor,
            "action": eval_action,
            "resource": {"domain": eval_domain, "name": eval_product},
        })
        if result:
            if result["allowed"]:
                st.success(f"✅ {result['reason']}")
            else:
                st.error(f"❌ {result['reason']}")
