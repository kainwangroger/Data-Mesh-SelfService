import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from api import api_get, api_post

st.header("Contrats de données")

with st.expander("➕ Nouveau contrat"):
    with st.form("new_contract"):
        col1, col2 = st.columns(2)
        with col1:
            c_name = st.text_input("Nom", placeholder="ventes_vers_marketing_v1")
            c_provider = st.selectbox("Domaine fournisseur", ["sales", "marketing", "finance"])
            c_consumer = st.selectbox("Domaine consommateur", ["sales", "marketing", "finance"])
        with col2:
            c_product = st.text_input("Produit cible", placeholder="customer_360")
            c_sla_uptime = st.slider("SLA disponibilité (%)", 90, 100, 99)
            c_sla_latence = st.selectbox("SLA latence max", ["1h", "6h", "24h"])
        if st.form_submit_button("Créer"):
            result = api_post("/data-contracts", {
                "name": c_name,
                "provider_domain": c_provider,
                "consumer_domain": c_consumer,
                "data_product_name": c_product,
                "sla": {"uptime": c_sla_uptime, "max_latency": c_sla_latence},
                "terms": {"purpose": "analytics"},
            })
            if result:
                st.success("Contrat créé !")
                st.rerun()

contrats = api_get("/data-contracts")
if contrats:
    df = pd.DataFrame(contrats)
    st.dataframe(
        df[["name", "provider_domain", "consumer_domain", "data_product_name", "status"]].rename(columns={
            "name": "Nom", "provider_domain": "Fournisseur", "consumer_domain": "Consommateur",
            "data_product_name": "Produit", "status": "Statut",
        }),
        height=400, use_container_width=False, hide_index=True,
        column_config={
            "Nom": st.column_config.TextColumn(width=250),
            "Fournisseur": st.column_config.TextColumn(width=200),
            "Consommateur": st.column_config.TextColumn(width=200),
            "Produit": st.column_config.TextColumn(width=250),
            "Statut": st.column_config.TextColumn(width=150),
        },
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Flux entre domaines")
        flow = df.groupby(["provider_domain", "consumer_domain"]).size().reset_index(name="count")
        labels = list(set(flow["provider_domain"].tolist() + flow["consumer_domain"].tolist()))
        idx = {l: i for i, l in enumerate(labels)}
        fig = go.Figure(data=[go.Sankey(
            node=dict(label=labels, color=["#636EFA", "#EF553B", "#00CC96"]),
            link=dict(
                source=[idx[r["provider_domain"]] for _, r in flow.iterrows()],
                target=[idx[r["consumer_domain"]] for _, r in flow.iterrows()],
                value=flow["count"].tolist(),
            )
        )])
        fig.update_layout(title="Contrats par domaine", height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### SLA des contrats")
        sla_data = []
        for _, c in df.iterrows():
            sla = c.get("sla", {})
            if isinstance(sla, dict):
                sla_data.append({"contrat": c["name"], "uptime": sla.get("uptime", 0)})
        if sla_data:
            sla_df = pd.DataFrame(sla_data)
            fig = px.bar(sla_df, x="contrat", y="uptime", title="Disponibilité SLA",
                         color="uptime", color_continuous_scale="RdYlGn")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Statistiques")
    col3, col4 = st.columns(2)
    with col3:
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        fig = px.pie(status_counts, values="count", names="status",
                     title="Contrats par statut", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        prov_counts = df["provider_domain"].value_counts().reset_index()
        prov_counts.columns = ["domaine", "count"]
        fig = px.bar(prov_counts, x="domaine", y="count",
                     title="Contrats fournis par domaine", color="domaine")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aucun contrat.")
