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


def api_get(path):
    try:
        req = Request(f"{GOVERNANCE_API}{path}")
        with urlopen(req, timeout=3) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return []


col1, col2, col3, col4 = st.columns(4)

data_products = api_get("/data-products")
contracts = api_get("/data-contracts")
policies = api_get("/policies")
domains = api_get("/domains")

col1.metric("Data Products", len(data_products))
col2.metric("Data Contracts", len(contracts))
col3.metric("Policies", len(policies))
col4.metric("Domains", len(domains))

st.markdown("### Data Products")
if data_products:
    df = pd.DataFrame(data_products)
    st.dataframe(
        df[["name", "domain", "owner", "sla_tier", "status", "tags"]].rename(columns={
            "name": "Nom", "domain": "Domaine", "owner": "Propriétaire",
            "sla_tier": "SLA", "status": "Statut", "tags": "Tags",
        }),
        height=250, use_container_width=True, hide_index=True,
    )

    cols = st.columns(2)
    with cols[0]:
        df_counts = df.groupby("domain").size().reset_index(name="count")
        fig = px.pie(df_counts, values="count", names="domain",
                      title="Data Products par domaine", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    with cols[1]:
        df_sla = df.groupby("sla_tier").size().reset_index(name="count")
        fig2 = px.bar(df_sla, x="sla_tier", y="count",
                       title="Data Products par SLA", color="sla_tier")
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Aucun data product enregistré.")

st.markdown("### Derniers accès évalués")
logs = api_get("/audit-logs?limit=10")
if logs:
    df_logs = pd.DataFrame(logs)
    display_cols = [c for c in ["created_at", "action", "actor", "resource_type", "resource_id"] if c in df_logs.columns]
    st.dataframe(
        df_logs[display_cols].rename(columns={
            "created_at": "Date", "action": "Action", "actor": "Acteur",
            "resource_type": "Type", "resource_id": "Cible",
        }),
        height=250, use_container_width=True, hide_index=True,
    )
