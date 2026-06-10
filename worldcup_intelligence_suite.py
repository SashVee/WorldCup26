import streamlit as st
from math import exp, factorial
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="World Cup 2026 Intelligence Suite", page_icon="⚽", layout="wide")

import pandas as pd

teams_df = pd.read_csv("teams.csv")

TEAMS = {
    row["Team"]: {
        "group": row["group"],
        "elo": float(row["elo"]),
        "gf": float(row["gf"]),
        "ga": float(row["ga"]),
        "form_points": int(row["form_points"]),
    }
    for _, row in teams_df.iterrows()
}

VENUES = {
    "New York New Jersey": {"country": "USA", "host_boost": 0.00},
    "Mexico City": {"country": "Mexico", "host_boost": 0.08},
    "Toronto": {"country": "Canada", "host_boost": 0.05},
    "Los Angeles": {"country": "USA", "host_boost": 0.00},
    "Dallas": {"country": "USA", "host_boost": 0.00},
    "Miami": {"country": "USA", "host_boost": 0.00},
}

BASE_GOALS = 1.35
MAX_GOALS = 6


def apply_theme():
    st.markdown("""
    <style>
    :root {
        --bg: #0b1220;
        --panel: #111827;
        --line: rgba(148, 163, 184, 0.16);
        --text: #e5e7eb;
        --muted: #94a3b8;
        --accent: #c7a86b;
        --accent-2: #e7d3ad;
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(199,168,107,0.08), transparent 24%),
            linear-gradient(180deg, #08101c 0%, #0b1220 100%);
        color: var(--text);
    }
    .block-container {
        max-width: 1280px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    .hero-wrap {
        background: linear-gradient(135deg, rgba(17,24,39,0.96), rgba(15,23,42,0.96));
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 1.5rem 1.6rem;
        box-shadow: 0 16px 40px rgba(0,0,0,0.28);
        margin-bottom: 1rem;
    }
    .eyebrow {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        background: rgba(199,168,107,0.12);
        color: var(--accent-2);
        border: 1px solid rgba(199,168,107,0.22);
        font-size: 0.82rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .hero-title {
        font-size: 2.05rem;
        font-weight: 700;
        margin: 0.8rem 0 0.45rem 0;
        color: #f8fafc;
    }
    .hero-subtitle, .muted {
        color: var(--muted);
    }
    .panel {
        background: linear-gradient(180deg, rgba(17,24,39,0.95), rgba(15,23,42,0.95));
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1.1rem;
        box-shadow: 0 10px 26px rgba(0,0,0,0.22);
    }
    .panel-title {
        color: #f8fafc;
        font-weight: 600;
        font-size: 1.03rem;
        margin-bottom: 0.2rem;
    }
    .panel-note {
        color: var(--muted);
        font-size: 0.92rem;
        margin-bottom: 0.9rem;
    }
    .stat-chip {
        background: rgba(255,255,255,0.02);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 0.95rem 1rem;
        height: 100%;
    }
    .stat-label {
        color: var(--muted);
        font-size: 0.82rem;
        margin-bottom: 0.2rem;
    }
    .stat-value {
        color: #f8fafc;
        font-size: 1.05rem;
        font-weight: 600;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.015));
        border: 1px solid var(--line);
        padding: 1rem;
        border-radius: 18px;
    }
    div[data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
    }
    div[data-baseweb="select"] > div {
        background-color: rgba(15,23,42,0.92);
        border-color: rgba(148,163,184,0.22);
        border-radius: 14px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #d7b67b, #b69057);
        color: #111827;
        border: none;
        border-radius: 14px;
        font-weight: 700;
        padding: 0.72rem 1rem;
    }
    .footer {
        text-align: center;
        color: var(--muted);
        font-size: 0.88rem;
        margin-top: 1.2rem;
    }
    </style>
    """, unsafe_allow_html=True)


def poisson_pmf(lmbda, k):
    return exp(-lmbda) * (lmbda ** k) / factorial(k)


def normalize_form(points_last5):
    return points_last5 / 15.0


def expected_goals(team_a, team_b, venue=None):
    a = TEAMS[team_a]
    b = TEAMS[team_b]
    elo_gap = (a["elo"] - b["elo"]) / 400.0
    form_a = normalize_form(a["form_points"])
    form_b = normalize_form(b["form_points"])
    attack_a = a["gf"] / BASE_GOALS
    defense_weak_b = b["ga"] / BASE_GOALS
    attack_b = b["gf"] / BASE_GOALS
    defense_weak_a = a["ga"] / BASE_GOALS
    venue_adj_a = 0.0
    venue_adj_b = 0.0
    if venue and venue in VENUES:
        host_country = VENUES[venue]["country"]
        boost = VENUES[venue]["host_boost"]
        if host_country == team_a:
            venue_adj_a += boost
        elif host_country == team_b:
            venue_adj_b += boost
    lambda_a = BASE_GOALS * (0.50 * attack_a + 0.20 * defense_weak_b + 0.20 * (1 + elo_gap) + 0.10 * (1 + (form_a - form_b))) + venue_adj_a
    lambda_b = BASE_GOALS * (0.50 * attack_b + 0.20 * defense_weak_a + 0.20 * (1 - elo_gap) + 0.10 * (1 + (form_b - form_a))) + venue_adj_b
    return max(0.2, round(lambda_a, 3)), max(0.2, round(lambda_b, 3))


def match_probabilities(team_a, team_b, venue=None):
    lambda_a, lambda_b = expected_goals(team_a, team_b, venue)
    probs_a = [poisson_pmf(lambda_a, k) for k in range(MAX_GOALS + 1)]
    probs_b = [poisson_pmf(lambda_b, k) for k in range(MAX_GOALS + 1)]
    win_a = draw = win_b = 0.0
    scorelines = []
    for i, pa in enumerate(probs_a):
        for j, pb in enumerate(probs_b):
            p = pa * pb
            scorelines.append(((i, j), p))
            if i > j:
                win_a += p
            elif i == j:
                draw += p
            else:
                win_b += p
    total = win_a + draw + win_b
    win_a /= total
    draw /= total
    win_b /= total
    top_scores = sorted(scorelines, key=lambda x: x[1], reverse=True)[:5]
    return {
        "expected_goals_a": round(lambda_a, 3),
        "expected_goals_b": round(lambda_b, 3),
        "win_a": round(win_a * 100, 2),
        "draw": round(draw * 100, 2),
        "win_b": round(win_b * 100, 2),
        "top_scorelines": [{"score": f"{s[0]}-{s[1]}", "probability": round(p * 100, 2)} for s, p in top_scores],
    }


def explain(team_a, team_b):
    a = TEAMS[team_a]
    b = TEAMS[team_b]
    reasons = []
    if a["elo"] > b["elo"]:
        reasons.append(f'higher Elo ({a["elo"]} vs {b["elo"]})')
    if a["gf"] > b["gf"]:
        reasons.append("stronger recent attack")
    if a["ga"] < b["ga"]:
        reasons.append("better recent defense")
    if a["form_points"] > b["form_points"]:
        reasons.append("better recent form")
    if not reasons:
        reasons.append("a balanced profile")
    return f"{team_a} is favored mainly because of " + ", ".join(reasons[:3]) + "."


def style_bar(fig, title):
    fig.update_layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb"),
        title_font=dict(size=20, color="#f8fafc"),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(148,163,184,0.12)", zeroline=False),
        margin=dict(l=10, r=10, t=50, b=10),
        showlegend=False,
    )
    return fig


apply_theme()

st.markdown("""
<div class='hero-wrap'>
    <div class='eyebrow'>World Cup Intelligence Suite</div>
    <div class='hero-title'>Executive Match Analysis Dashboard</div>
    <div class='hero-subtitle'>A multi-page professional app for match probability, venue context, and team-level benchmarking.</div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("<div class='stat-chip'><div class='stat-label'>Teams in model</div><div class='stat-value'>9</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='stat-chip'><div class='stat-label'>Venues tracked</div><div class='stat-value'>6</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='stat-chip'><div class='stat-label'>Core engine</div><div class='stat-value'>Elo + Poisson</div></div>", unsafe_allow_html=True)

st.markdown("<div class='panel' style='margin-top:1rem;'>", unsafe_allow_html=True)
st.markdown("<div class='panel-title'>Home</div>", unsafe_allow_html=True)
st.markdown("<div class='panel-note'>Use the sidebar pages to move across Overview, Match Analysis, Venues, and Team Rankings. Streamlit supports multipage navigation using either a pages directory or the newer page/navigation APIs.</div>", unsafe_allow_html=True)

rank_df = pd.DataFrame([
    {"Team": t, "Elo": v["elo"], "Goals For": v["gf"], "Goals Against": v["ga"], "Form": v["form_points"]}
    for t, v in TEAMS.items()
]).sort_values("Elo", ascending=False)

fig = px.bar(rank_df, x="Team", y="Elo", text="Elo", color_discrete_sequence=["#d7b67b"])
fig.update_traces(textposition='outside', cliponaxis=False)
fig = style_bar(fig, "Elo ranking overview")
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='footer'>Multipage Streamlit app with professional navigation-ready structure.</div>", unsafe_allow_html=True)