import streamlit as st
import pandas as pd
import plotly.express as px
from api import api_get, api_post

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
        if st.form_submit_button("Créer"):
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

    st.markdown("### Vue d'ensemble")
    col1, col2 = st.columns(2)
    with col1:
        effect_counts = df["effect"].value_counts().reset_index()
        effect_counts.columns = ["effect", "count"]
        fig = px.pie(effect_counts, values="count", names="effect",
                      title="Policies: Allow vs Deny", hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        type_counts = df["policy_type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]
        fig2 = px.bar(type_counts, x="type", y="count",
                       title="Policies par type", color="type")
        st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Aucune policy.")
