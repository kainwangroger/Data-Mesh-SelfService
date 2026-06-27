import streamlit as st
import pandas as pd
import plotly.express as px
from api import api_get, api_post

st.header("Produits de données")

with st.expander("➕ Nouveau produit"):
    with st.form("new_dp"):
        col1, col2 = st.columns(2)
        with col1:
            dp_name = st.text_input("Nom", placeholder="ventes_consolidees")
            dp_domain = st.selectbox("Domaine", ["sales", "marketing", "finance"])
            dp_owner = st.text_input("Propriétaire", placeholder="equipe-ventes")
        with col2:
            dp_desc = st.text_area("Description")
            dp_sla = st.selectbox("Niveau SLA", ["gold", "silver", "bronze"])
            dp_tags = st.text_input("Tags (virgules)", placeholder="ventes, temps-reel")
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
                st.success(f"Produit '{dp_name}' créé !")
                st.rerun()

filtre = st.selectbox("Filtrer par domaine", ["Tous", "sales", "marketing", "finance"])

dps = api_get("/data-products")
if dps:
    df = pd.DataFrame(dps)
    if filtre != "Tous":
        df = df[df["domain"] == filtre]

    st.markdown(f"**{len(df)} produits**")
    for _, dp in df.iterrows():
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            c1.markdown(f"**{dp['name']}**  \n*{dp.get('description', '') or ''}*")
            c2.metric("Domaine", dp["domain"])
            c3.metric("SLA", dp["sla_tier"])
            c4.metric("Statut", dp["status"])

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(df, names="domain", title="Répartition par domaine", hole=0.3,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(df, x="domain", color="sla_tier", title="SLA par domaine",
                     barmode="group", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        owner_counts = df["owner"].value_counts().reset_index()
        owner_counts.columns = ["owner", "count"]
        fig = px.bar(owner_counts, x="owner", y="count",
                     title="Produits par propriétaire", color="owner")
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        tags = []
        for t in df["tags"]:
            if isinstance(t, list):
                tags.extend(t)
        if tags:
            tag_counts = pd.Series(tags).value_counts().reset_index()
            tag_counts.columns = ["tag", "count"]
            fig = px.bar(tag_counts.head(10), x="tag", y="count",
                         title="Top tags", color="tag")
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aucun produit — créez-en un avec le formulaire ci-dessus.")
