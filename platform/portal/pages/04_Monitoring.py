import streamlit as st
import pandas as pd
from api import api_get, api_post

st.header("Monitoring & Audit")

st.subheader("Santé des services")
health = api_get("/health")
if health:
    st.json(health)

st.subheader("Logs d'audit")
limit = st.slider("Nombre de logs", 5, 100, 20)
logs = api_get(f"/audit-logs?limit={limit}")
if logs:
    df = pd.DataFrame(logs)
    st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("Simulateur d'accès")
st.markdown("Testez qui peut accéder à quoi selon les politiques actives.")

col1, col2 = st.columns(2)
with col1:
    eval_actor = st.text_input("Acteur", "marketing_analyst")
    eval_action = st.selectbox("Action", ["read", "write", "query", "admin"])
with col2:
    eval_domain = st.text_input("Domaine cible", "sales")
    eval_product = st.text_input("Data product cible", "customer_360")
    eval_sla = st.selectbox("SLA requis", ["gold", "silver", "bronze", "none"])

if st.button("🔍 Évaluer l'accès", type="primary"):
    resource = {"domain": eval_domain, "name": eval_product}
    if eval_sla != "none":
        resource["sla_tier"] = eval_sla

    result = api_post(
        "/evaluate",
        data=resource,
        params={"actor": eval_actor, "action": eval_action},
    )
    if result:
        if result["allowed"]:
            st.success(f"✅ **ACCÈS AUTORISÉ**  \n{result['reason']}")
        else:
            st.error(f"❌ **ACCÈS REFUSÉ**  \n{result['reason']}")
        with st.expander("Détail de la décision"):
            st.json(result)
