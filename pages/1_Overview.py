import streamlit as st
import pandas as pd
import plotly.express as px
from worldcup_intelligence_suite import apply_theme, TEAMS, style_bar

apply_theme()
st.title("Overview")
st.caption("High-level benchmark view across all teams in the model.")

df = pd.DataFrame([
    {"Team": t, "Elo": v["elo"], "Goals For": v["gf"], "Goals Against": v["ga"], "Form": v["form_points"]}
    for t, v in TEAMS.items()
]).sort_values("Elo", ascending=False)

c1, c2 = st.columns(2)
with c1:
    fig_elo = px.bar(df, x="Team", y="Elo", text="Elo", color_discrete_sequence=["#d7b67b"])
    fig_elo.update_traces(textposition='outside', cliponaxis=False)
    fig_elo = style_bar(fig_elo, "Team Elo rankings")
    st.plotly_chart(fig_elo, use_container_width=True)
with c2:
    fig_form = px.bar(df.sort_values("Form", ascending=False), x="Team", y="Form", text="Form", color_discrete_sequence=["#7c8ea8"])
    fig_form.update_traces(textposition='outside', cliponaxis=False)
    fig_form = style_bar(fig_form, "Recent form rankings")
    st.plotly_chart(fig_form, use_container_width=True)

st.dataframe(df, use_container_width=True, hide_index=True)
