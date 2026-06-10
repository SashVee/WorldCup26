import streamlit as st
import pandas as pd
import plotly.express as px
from worldcup_intelligence_suite import apply_theme, VENUES, style_bar

apply_theme()
st.title("Venues")
st.caption("Host-country context and boost assumptions used in the model.")

df = pd.DataFrame([
    {"Venue": k, "Country": v["country"], "Host Boost": v["host_boost"]}
    for k, v in VENUES.items()
])

fig = px.bar(df, x="Venue", y="Host Boost", text="Host Boost", color="Country")
fig.update_traces(texttemplate='%{text:.2f}', textposition='outside', cliponaxis=False)
fig = style_bar(fig, "Venue host influence")
st.plotly_chart(fig, use_container_width=True)

st.dataframe(df, use_container_width=True, hide_index=True)
