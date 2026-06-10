import streamlit as st
import pandas as pd
import plotly.express as px
from worldcup_intelligence_suite import apply_theme, TEAMS, style_bar

apply_theme()
st.title("Team Rankings")
st.caption("Compare attack, defense, and form profile across the teams in the sample.")

df = pd.DataFrame([
    {"Team": t, "Goals For": v["gf"], "Goals Against": v["ga"], "Form": v["form_points"], "Elo": v["elo"]}
    for t, v in TEAMS.items()
])

tab1, tab2 = st.tabs(["Attack", "Defense"])
with tab1:
    fig_attack = px.bar(df.sort_values("Goals For", ascending=False), x="Team", y="Goals For", text="Goals For", color_discrete_sequence=["#d7b67b"])
    fig_attack.update_traces(textposition='outside', cliponaxis=False)
    fig_attack = style_bar(fig_attack, "Attack output")
    st.plotly_chart(fig_attack, use_container_width=True)
with tab2:
    fig_def = px.bar(df.sort_values("Goals Against", ascending=True), x="Team", y="Goals Against", text="Goals Against", color_discrete_sequence=["#7c8ea8"])
    fig_def.update_traces(textposition='outside', cliponaxis=False)
    fig_def = style_bar(fig_def, "Defensive record")
    st.plotly_chart(fig_def, use_container_width=True)

st.dataframe(df.sort_values("Elo", ascending=False), use_container_width=True, hide_index=True)
