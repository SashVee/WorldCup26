import streamlit as st
import pandas as pd
import plotly.express as px
from worldcup_intelligence_suite import apply_theme, TEAMS, VENUES, match_probabilities, explain, style_bar

apply_theme()
st.title("Match Analysis")
st.caption("Professional pre-match report with probability and scoreline visuals.")

team_names = list(TEAMS.keys())
venue_names = list(VENUES.keys())
left, right = st.columns([1, 1.55], gap="large")

with left:
    team_a = st.selectbox("Team A", team_names, index=0)
    team_b = st.selectbox("Team B", team_names, index=4)
    venue = st.selectbox("Venue", venue_names, index=0)
    predict = st.button("Generate Match Report", use_container_width=True)

with right:
    if team_a == team_b:
        st.warning("Please choose two different teams.")
    elif predict:
        result = match_probabilities(team_a, team_b, venue)
        m1, m2, m3 = st.columns(3)
        m1.metric(f"{team_a} Win", f"{result['win_a']}%")
        m2.metric("Draw", f"{result['draw']}%")
        m3.metric(f"{team_b} Win", f"{result['win_b']}%")

        prob_df = pd.DataFrame({
            "Outcome": [team_a, "Draw", team_b],
            "Probability": [result["win_a"], result["draw"], result["win_b"]]
        })
        fig_prob = px.bar(prob_df, x="Outcome", y="Probability", text="Probability", color="Outcome",
                          color_discrete_sequence=["#d7b67b", "#64748b", "#7c8ea8"])
        fig_prob.update_traces(texttemplate='%{text:.2f}%', textposition='outside', cliponaxis=False)
        fig_prob = style_bar(fig_prob, "Outcome probabilities")
        st.plotly_chart(fig_prob, use_container_width=True)

        score_df = pd.DataFrame(result["top_scorelines"])
        fig_score = px.bar(score_df, x="score", y="probability", text="probability", color_discrete_sequence=["#d7b67b"])
        fig_score.update_traces(texttemplate='%{text:.2f}%', textposition='outside', cliponaxis=False)
        fig_score = style_bar(fig_score, "Top scorelines")
        st.plotly_chart(fig_score, use_container_width=True)

        st.info(explain(team_a, team_b))
    else:
        st.info("Select teams and a venue, then generate the report.")
