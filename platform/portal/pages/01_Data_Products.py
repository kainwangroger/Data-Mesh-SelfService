import streamlit as st
import pandas as pd
import plotly.express as px
from api import api_get, api_post

st.header("Data Products")

with st.expander("➕ Nouveau Data Product"):
    with st.form("new_dp"):
        col1, col2 = st.columns(2)
        with col1:
            dp_name = st.text_input("Nom", placeholder="sales_transactions_v2")
            dp_domain = st.selectbox("Domaine", ["sales", "marketing", "finance"])
            dp_owner = st.text_input("Owner", placeholder="equipe-sales")
        with col2:
            dp_desc = st.text_area("Description")
            dp_sla = st.selectbox("SLA Tier", ["gold", "silver", "bronze"])
            dp_tags = st.text_input("Tags (virgules)", placeholder="transactions, ventes")
        if st.form_submit_button("Créer"):
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

domain_filter = st.selectbox("Filtrer par domaine", ["Tous", "sales", "marketing", "finance"])

dps = api_get("/data-products")
if dps:
    df = pd.DataFrame(dps)
    if domain_filter != "Tous":
        df = df[df["domain"] == domain_filter]

    st.markdown(f"**{len(df)} data products**")
    for _, dp in df.iterrows():
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            c1.markdown(f"**{dp['name']}**  \n*{dp.get('description', '') or ''}*")
            c2.metric("Domaine", dp['domain'])
            c3.metric("SLA", dp['sla_tier'])
            c4.metric("Status", dp['status'])

    st.markdown("### Statistiques")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(df, names="domain", title="Répartition par domaine", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig2 = px.bar(df, x="domain", color="sla_tier", title="SLA par domaine", barmode="group")
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Aucun data product — créez-en un avec le formulaire ci-dessus.")
