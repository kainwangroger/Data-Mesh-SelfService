import streamlit as st
import pandas as pd
import plotly.express as px
from api import api_get, api_post

st.header("Surveillance & Audit")

st.subheader("État des services")
health = api_get("/health")
if health:
    st.json(health)

st.subheader("Journal d'audit")
limite = st.slider("Nombre d'entrées", 5, 100, 20)
logs = api_get(f"/audit-logs?limit={limite}")
if logs:
    df = pd.DataFrame(logs)
    cfg = {c: st.column_config.TextColumn(width=300) for c in df.columns}
    st.dataframe(df, height=400, use_container_width=False, hide_index=True, column_config=cfg)

    st.markdown("### Activité dans le temps")
    df["date"] = pd.to_datetime(df["created_at"]).dt.date
    timeline = df.groupby("date").size().reset_index(name="actions")
    fig = px.line(timeline, x="date", y="actions", title="Actions par jour",
                  markers=True)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        acteurs = df["actor"].value_counts().reset_index()
        acteurs.columns = ["acteur", "count"]
        fig = px.bar(acteurs.head(10), x="acteur", y="count",
                     title="Top acteurs", color="acteur")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        actions = df["action"].value_counts().reset_index()
        actions.columns = ["action", "count"]
        fig = px.pie(actions, values="count", names="action",
                     title="Types d'actions", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Simulateur d'accès")
st.markdown("Testez qui peut accéder à quoi selon les politiques actives.")

col1, col2 = st.columns(2)
with col1:
    eval_acteur = st.text_input("Acteur", "marketing_analyst")
    eval_action = st.selectbox("Action", ["read", "write", "query", "admin"])
with col2:
    eval_domaine = st.text_input("Domaine cible", "sales")
    eval_produit = st.text_input("Produit cible", "customer_360")
    eval_sla = st.selectbox("SLA requis", ["gold", "silver", "bronze", "aucun"])

if st.button("🔍 Évaluer l'accès", type="primary"):
    resource = {"domain": eval_domaine, "name": eval_produit}
    if eval_sla != "aucun":
        resource["sla_tier"] = eval_sla
    result = api_post(
        "/evaluate",
        data=resource,
        params={"actor": eval_acteur, "action": eval_action},
    )
    if result:
        if result["allowed"]:
            st.success(f"✅ **ACCÈS AUTORISÉ**  \n{result['reason']}")
        else:
            st.error(f"❌ **ACCÈS REFUSÉ**  \n{result['reason']}")
        with st.expander("Détail de la décision"):
            st.json(result)
