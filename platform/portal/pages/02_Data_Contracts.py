import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from api import api_get, api_post

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
        if st.form_submit_button("Créer"):
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

    if len(contracts) > 1:
        st.markdown("### Flux de données entre domaines")
        flow_df = df.groupby(["provider_domain", "consumer_domain"]).size().reset_index(name="contrats")

        labels = list(set(flow_df["provider_domain"].tolist() + flow_df["consumer_domain"].tolist()))
        label_index = {l: i for i, l in enumerate(labels)}
        fig = go.Figure(data=[go.Sankey(
            node=dict(label=labels),
            link=dict(
                source=[label_index[r["provider_domain"]] for _, r in flow_df.iterrows()],
                target=[label_index[r["consumer_domain"]] for _, r in flow_df.iterrows()],
                value=flow_df["contrats"].tolist(),
            ))])
        fig.update_layout(title="Flux de contrats entre domaines")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aucun contrat.")
