"""
Football Player Performance Analytics Dashboard
================================================
⚠️  SYNTHETIC DATA NOTICE: All player names, clubs, and statistics in this
    dashboard are entirely synthetic and generated for demonstration purposes.
    They do not represent real-world football players or results.
"""

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS — dark football theme ────────────────────────────────────────
THEME_CSS = """
<style>
/* Global background */
.stApp { background-color: #0d1117; color: #e6edf3; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] * { color: #e6edf3 !important; }

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 16px 20px;
}
[data-testid="stMetricValue"] { color: #00ff87 !important; font-size: 2rem !important; }
[data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 0.85rem !important; }

/* Headers */
h1, h2, h3 { color: #00ff87 !important; }
h4, h5, h6 { color: #e6edf3 !important; }

/* Dividers */
hr { border-color: #21262d; }

/* Selectbox / multiselect labels */
.stSelectbox label, .stMultiSelect label, .stTextInput label,
.stRadio label { color: #8b949e !important; }

/* Buttons */
.stButton > button {
    background-color: #238636;
    color: #ffffff;
    border: none;
    border-radius: 6px;
}
.stButton > button:hover { background-color: #2ea043; }

/* Download button */
.stDownloadButton > button {
    background-color: #1f6feb;
    color: #ffffff;
    border: none;
    border-radius: 6px;
}
.stDownloadButton > button:hover { background-color: #388bfd; }

/* DataFrames */
.stDataFrame { border: 1px solid #21262d; border-radius: 8px; }

/* Warning / info boxes */
.stAlert { border-radius: 8px; }

/* Caption text */
.stCaption { color: #8b949e !important; }
</style>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)

# ── Plotly dark layout defaults ──────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#161b22",
    plot_bgcolor="#0d1117",
    font=dict(color="#e6edf3", family="Segoe UI, system-ui, sans-serif"),
    title_font=dict(color="#00ff87"),
    legend=dict(bgcolor="#161b22", bordercolor="#21262d", borderwidth=1),
    xaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
    yaxis=dict(gridcolor="#21262d", zerolinecolor="#21262d"),
    margin=dict(t=50, b=40, l=40, r=20),
)

GREEN   = "#00ff87"
ACCENT  = "#1f6feb"
PALETTE = px.colors.qualitative.Plotly


def apply_layout(fig):
    """Apply the shared dark theme to any Plotly figure."""
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


# ── Data loading ─────────────────────────────────────────────────────────────
CSV_PATH = os.path.join(os.path.dirname(__file__), "football_players.csv")


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load football_players.csv and return a clean DataFrame."""
    if not os.path.exists(CSV_PATH):
        st.error(
            f"Dataset not found at `{CSV_PATH}`. "
            "Please run `py generate_data.py` first to create the dataset."
        )
        st.stop()

    df = pd.read_csv(CSV_PATH)

    # Basic integrity checks
    required_cols = {
        "player_id", "player_name", "team", "position", "season",
        "goals", "assists", "minutes_played", "rating",
    }
    missing = required_cols - set(df.columns)
    if missing:
        st.error(f"Dataset is missing expected columns: {missing}")
        st.stop()

    # Coerce numeric columns; fill NaN with 0
    numeric_cols = [
        "goals", "assists", "shots", "shots_on_target", "passes",
        "pass_accuracy", "dribbles", "tackles", "yellow_cards",
        "red_cards", "rating", "matches_played", "minutes_played", "age",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Ensure position order
    pos_order = ["GK", "DEF", "MID", "FWD"]
    df["position"] = pd.Categorical(df["position"], categories=pos_order, ordered=True)

    return df


# ── Sidebar filters ───────────────────────────────────────────────────────────
def render_sidebar(df: pd.DataFrame):
    """Render sidebar filters and return the active page + filter values."""
    with st.sidebar:
        st.markdown("## ⚽ Football Analytics")
        st.markdown("---")

        # Page selector
        page = st.radio(
            "Navigate",
            ["Overview", "Player Analysis", "Team Analysis", "Position Analysis", "Data Table"],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("### 🔍 Filters")

        # Season filter
        seasons_all = sorted(df["season"].unique().tolist())
        seasons = st.multiselect("Season", seasons_all, default=seasons_all)

        # Team filter
        teams_all = sorted(df["team"].unique().tolist())
        teams = st.multiselect("Team", teams_all, default=teams_all)

        # Position filter
        pos_all = ["GK", "DEF", "MID", "FWD"]
        positions = st.multiselect("Position", pos_all, default=pos_all)

        # Player filter (dynamically scoped to above filters)
        pre_df = df[
            df["season"].isin(seasons) &
            df["team"].isin(teams) &
            df["position"].isin(positions)
        ] if seasons and teams and positions else df.iloc[0:0]

        players_all = sorted(pre_df["player_name"].unique().tolist())
        players = st.multiselect("Player (optional)", players_all, default=[])

        st.markdown("---")
        st.caption("⚠️ All data is **synthetic** and for demonstration only.")

    return page, seasons, teams, positions, players


# ── Apply filters ─────────────────────────────────────────────────────────────
def apply_filters(df, seasons, teams, positions, players):
    """Filter the DataFrame based on sidebar selections."""
    # Guard: if any filter group is empty, return empty df (handled downstream)
    if not seasons or not teams or not positions:
        return df.iloc[0:0]

    mask = (
        df["season"].isin(seasons) &
        df["team"].isin(teams) &
        df["position"].isin(positions)
    )
    filtered = df[mask]

    if players:
        filtered = filtered[filtered["player_name"].isin(players)]

    return filtered


def guard_empty(df: pd.DataFrame):
    """Show a warning and stop if the filtered DataFrame is empty."""
    if df.empty:
        st.warning(
            "⚠️ No data matches the current filter selection. "
            "Please adjust the filters in the sidebar."
        )
        st.stop()


# ── Overview Page ─────────────────────────────────────────────────────────────
def render_overview(df: pd.DataFrame):
    st.title("📊 Overview")
    st.caption("High-level KPIs and league-wide summary for the selected filters.")
    st.markdown("---")

    # ── KPI row ──
    total_players  = df["player_id"].nunique()
    total_goals    = int(df["goals"].sum())
    total_assists  = int(df["assists"].sum())
    total_minutes  = int(df["minutes_played"].sum())
    avg_rating     = round(df["rating"].mean(), 2)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🧑‍🤝‍🧑 Total Players",    f"{total_players:,}")
    c2.metric("⚽ Total Goals",          f"{total_goals:,}")
    c3.metric("🅰️ Total Assists",        f"{total_assists:,}")
    c4.metric("⏱️ Total Minutes",        f"{total_minutes:,}")
    c5.metric("⭐ Avg Player Rating",    f"{avg_rating}")

    st.markdown("---")

    col_l, col_r = st.columns(2)

    # Goals by team
    with col_l:
        team_goals = (
            df.groupby("team")["goals"]
            .sum()
            .reset_index()
            .sort_values("goals", ascending=True)
        )
        fig = px.bar(
            team_goals, x="goals", y="team", orientation="h",
            title="Goals by Team",
            labels={"goals": "Total Goals", "team": "Club"},
            color_discrete_sequence=[GREEN],
        )
        apply_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    # Top 10 players by rating
    with col_r:
        top10 = (
            df.nlargest(10, "rating")[["player_name", "team", "rating"]]
            .sort_values("rating", ascending=True)
        )
        fig2 = px.bar(
            top10, x="rating", y="player_name", orientation="h",
            title="Top 10 Players by Rating",
            labels={"rating": "Rating", "player_name": "Player"},
            color="rating",
            color_continuous_scale=[[0, "#21262d"], [1, GREEN]],
            hover_data=["team"],
        )
        fig2.update_coloraxes(showscale=False)
        apply_layout(fig2)
        st.plotly_chart(fig2, use_container_width=True)


# ── Player Analysis Page ──────────────────────────────────────────────────────
def render_player(df: pd.DataFrame):
    st.title("🔎 Player Analysis")
    st.caption("Compare players and explore scoring & shooting patterns.")
    st.markdown("---")

    player_list = sorted(df["player_name"].unique().tolist())

    if len(player_list) == 0:
        st.info("No players available for the current filter selection.")
        return

    # Default: top 5 by rating from the filtered set
    default_players = (
        df.nlargest(5, "rating")["player_name"].tolist()
        if len(player_list) >= 5
        else player_list[:min(5, len(player_list))]
    )

    selected = st.multiselect(
        "Select players to compare (from filtered list)",
        options=player_list,
        default=default_players,
    )

    # ── Comparison bar chart ──
    if not selected:
        st.info("ℹ️ Select at least one player above to see the comparison chart.")
    else:
        comp_df = df[df["player_name"].isin(selected)]
        # Aggregate across seasons if multiple rows per player
        comp_agg = (
            comp_df.groupby("player_name")
            .agg(
                goals=("goals", "sum"),
                assists=("assists", "sum"),
                shots=("shots", "sum"),
                tackles=("tackles", "sum"),
                passes=("passes", "sum"),
            )
            .reset_index()
        )
        comp_melted = comp_agg.melt(
            id_vars="player_name", var_name="Stat", value_name="Value"
        )
        fig_comp = px.bar(
            comp_melted, x="Stat", y="Value", color="player_name",
            barmode="group",
            title="Player Comparison — Key Stats",
            labels={"Value": "Total", "player_name": "Player"},
            color_discrete_sequence=PALETTE,
        )
        apply_layout(fig_comp)
        st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("---")

    col_l, col_r = st.columns(2)

    # Goals vs Assists scatter
    with col_l:
        fig_ga = px.scatter(
            df, x="assists", y="goals",
            color="position",
            size="minutes_played",
            hover_name="player_name",
            hover_data={"team": True, "rating": True, "minutes_played": False},
            title="Goals vs Assists",
            labels={"assists": "Assists", "goals": "Goals", "position": "Position"},
            color_discrete_sequence=PALETTE,
            size_max=20,
        )
        apply_layout(fig_ga)
        st.plotly_chart(fig_ga, use_container_width=True)

    # Shots vs Goals scatter
    with col_r:
        fig_sg = px.scatter(
            df, x="shots", y="goals",
            color="team",
            size="minutes_played",
            hover_name="player_name",
            hover_data={"position": True, "shots_on_target": True, "minutes_played": False},
            title="Shots vs Goals",
            labels={"shots": "Shots", "goals": "Goals", "team": "Club"},
            color_discrete_sequence=PALETTE,
            size_max=20,
        )
        apply_layout(fig_sg)
        st.plotly_chart(fig_sg, use_container_width=True)


# ── Team Analysis Page ────────────────────────────────────────────────────────
def render_team(df: pd.DataFrame):
    st.title("🏟️ Team Analysis")
    st.caption("Club-level aggregations and comparisons.")
    st.markdown("---")

    team_agg = (
        df.groupby("team")
        .agg(
            goals=("goals", "sum"),
            assists=("assists", "sum"),
            player_count=("player_id", "nunique"),
            avg_rating=("rating", "mean"),
        )
        .reset_index()
        .sort_values("goals", ascending=False)
    )
    team_agg["avg_rating"] = team_agg["avg_rating"].round(2)

    col1, col2 = st.columns(2)

    # Goals per team
    with col1:
        fig1 = px.bar(
            team_agg.sort_values("goals", ascending=True),
            x="goals", y="team", orientation="h",
            title="Total Goals by Club",
            labels={"goals": "Goals", "team": "Club"},
            color_discrete_sequence=[GREEN],
        )
        apply_layout(fig1)
        st.plotly_chart(fig1, use_container_width=True)

    # Assists per team
    with col2:
        fig2 = px.bar(
            team_agg.sort_values("assists", ascending=True),
            x="assists", y="team", orientation="h",
            title="Total Assists by Club",
            labels={"assists": "Assists", "team": "Club"},
            color_discrete_sequence=[ACCENT],
        )
        apply_layout(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    # Squad size pie
    with col3:
        fig3 = px.pie(
            team_agg, names="team", values="player_count",
            title="Squad Size by Club",
            color_discrete_sequence=PALETTE,
            hole=0.35,
        )
        apply_layout(fig3)
        fig3.update_traces(textinfo="label+percent", textfont_color="#e6edf3")
        st.plotly_chart(fig3, use_container_width=True)

    # Average rating per team
    with col4:
        fig4 = px.bar(
            team_agg.sort_values("avg_rating", ascending=True),
            x="avg_rating", y="team", orientation="h",
            title="Average Player Rating by Club",
            labels={"avg_rating": "Avg Rating", "team": "Club"},
            color="avg_rating",
            color_continuous_scale=[[0, "#21262d"], [1, GREEN]],
        )
        fig4.update_coloraxes(showscale=False)
        apply_layout(fig4)
        st.plotly_chart(fig4, use_container_width=True)


# ── Position Analysis Page ────────────────────────────────────────────────────
def render_position(df: pd.DataFrame):
    st.title("📐 Position Analysis")
    st.caption("Breakdown of performance metrics by playing position.")
    st.markdown("---")

    pos_order = ["GK", "DEF", "MID", "FWD"]
    pos_agg = (
        df.groupby("position", observed=True)
        .agg(
            goals=("goals", "sum"),
            assists=("assists", "sum"),
            player_count=("player_id", "nunique"),
            avg_rating=("rating", "mean"),
        )
        .reset_index()
    )
    pos_agg["position"] = pd.Categorical(pos_agg["position"], categories=pos_order, ordered=True)
    pos_agg = pos_agg.sort_values("position")
    pos_agg["avg_rating"] = pos_agg["avg_rating"].round(2)

    col1, col2 = st.columns(2)

    # Goals by position
    with col1:
        fig1 = px.bar(
            pos_agg, x="position", y="goals",
            title="Total Goals by Position",
            labels={"position": "Position", "goals": "Goals"},
            color="position",
            color_discrete_sequence=PALETTE,
        )
        apply_layout(fig1)
        st.plotly_chart(fig1, use_container_width=True)

    # Assists by position
    with col2:
        fig2 = px.bar(
            pos_agg, x="position", y="assists",
            title="Total Assists by Position",
            labels={"position": "Position", "assists": "Assists"},
            color="position",
            color_discrete_sequence=PALETTE,
        )
        apply_layout(fig2)
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    # Rating distribution box plot (needs raw df, not aggregated)
    with col3:
        df_sorted = df.copy()
        df_sorted["position"] = pd.Categorical(df_sorted["position"], categories=pos_order, ordered=True)
        fig3 = px.box(
            df_sorted.sort_values("position"), x="position", y="rating",
            color="position",
            title="Rating Distribution by Position",
            labels={"position": "Position", "rating": "Rating"},
            color_discrete_sequence=PALETTE,
        )
        apply_layout(fig3)
        st.plotly_chart(fig3, use_container_width=True)

    # Position distribution pie
    with col4:
        fig4 = px.pie(
            pos_agg, names="position", values="player_count",
            title="Player Distribution by Position",
            color_discrete_sequence=PALETTE,
            hole=0.35,
        )
        apply_layout(fig4)
        fig4.update_traces(textinfo="label+percent", textfont_color="#e6edf3")
        st.plotly_chart(fig4, use_container_width=True)


# ── Data Table Page ───────────────────────────────────────────────────────────
def render_table(df: pd.DataFrame):
    st.title("📋 Data Table")
    st.caption("Search, sort, and download filtered player statistics.")
    st.markdown("---")

    # Name search
    query = st.text_input("🔍 Search by player name", placeholder="e.g. Carlos Silva")
    if query:
        df = df[df["player_name"].str.contains(query, case=False, na=False)]

    # Column ordering
    preferred_cols = [
        "player_name", "team", "position", "season", "age", "nationality",
        "matches_played", "minutes_played", "goals", "assists",
        "shots", "shots_on_target", "passes", "pass_accuracy",
        "dribbles", "tackles", "yellow_cards", "red_cards", "rating",
    ]
    display_cols = [c for c in preferred_cols if c in df.columns]
    df_display = df[display_cols].sort_values("rating", ascending=False)

    st.caption(f"Showing **{len(df_display):,}** records")

    st.dataframe(df_display, use_container_width=True, height=500)

    st.markdown("---")

    # CSV download
    csv_bytes = df_display.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="football_stats_filtered.csv",
        mime="text/csv",
    )


# ── Main router ───────────────────────────────────────────────────────────────
def main():
    df_raw = load_data()

    page, seasons, teams, positions, players = render_sidebar(df_raw)

    df = apply_filters(df_raw, seasons, teams, positions, players)
    guard_empty(df)

    if page == "Overview":
        render_overview(df)
    elif page == "Player Analysis":
        render_player(df)
    elif page == "Team Analysis":
        render_team(df)
    elif page == "Position Analysis":
        render_position(df)
    elif page == "Data Table":
        render_table(df)


if __name__ == "__main__":
    main()
