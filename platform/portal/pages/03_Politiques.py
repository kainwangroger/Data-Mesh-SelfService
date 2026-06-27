import streamlit as st
import pandas as pd
import plotly.express as px
from api import api_get, api_post

st.header("Politiques d'accès")

with st.expander("➕ Nouvelle politique"):
    with st.form("new_policy"):
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input("Nom", placeholder="marketing_lecture_gold")
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
                st.success("Politique créée !")
                st.rerun()

policies = api_get("/policies")
if policies:
    df = pd.DataFrame(policies)
    st.dataframe(
        df[["name", "policy_type", "effect", "priority", "enabled"]].rename(columns={
            "name": "Nom", "policy_type": "Type", "effect": "Effet",
            "priority": "Priorité", "enabled": "Activée",
        }),
        height=250, use_container_width=False, hide_index=True,
        column_config={c: st.column_config.TextColumn(width=300) for c in ["Nom", "Type", "Effet", "Priorité", "Activée"]},
    )

    col1, col2 = st.columns(2)
    with col1:
        eff = df["effect"].value_counts().reset_index()
        eff.columns = ["effect", "count"]
        fig = px.pie(eff, values="count", names="effect",
                     title="Allow vs Deny", hole=0.3,
                     color_discrete_map={"allow": "#00CC96", "deny": "#EF553B"})
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        typ = df["policy_type"].value_counts().reset_index()
        typ.columns = ["type", "count"]
        fig = px.bar(typ, x="type", y="count",
                     title="Par type", color="type")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        enabled = df["enabled"].value_counts().reset_index()
        enabled.columns = ["enabled", "count"]
        enabled["enabled"] = enabled["enabled"].map({True: "Activée", False: "Désactivée"})
        fig = px.pie(enabled, values="count", names="enabled",
                     title="Politiques activées", hole=0.3,
                     color_discrete_map={"Activée": "#00CC96", "Désactivée": "#AB63FA"})
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        fig = px.bar(df.sort_values("priority"), x="name", y="priority",
                     title="Priorités", color="effect",
                     color_discrete_map={"allow": "#00CC96", "deny": "#EF553B"})
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Aucune politique.")
