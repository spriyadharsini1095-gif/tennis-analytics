import os
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text, URL
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=True)
st.set_page_config(page_title="Tennis Analytics", layout="wide")
import base64

def set_bg1(path):
    with open(path, "rb") as f:
        img = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(0,0,0,0.45), rgba(0,0,0,0.45)),
                    url("data:image/jpg;base64,{img}");
        background-size: cover;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)

set_bg1("bg1.jpg")

st.markdown("""
<style>
header, .stAppHeader, [data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: rgba(0, 0, 0, 0.35); }
[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(198, 244, 50, 0.4);
    border-radius: 12px;
    padding: 12px;
}
h1, h2, h3 { color: #C6F432; }
</style>
""", unsafe_allow_html=True)
# ---------------- Database connection ----------------
def get_secret(key, default=None):
    """Read from Streamlit Secrets (cloud) or .env (local)."""
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

@st.cache_resource
def get_engine():
    url = URL.create(
        "postgresql+psycopg2",
        username=get_secret("DB_USER"),
        password=get_secret("DB_PASSWORD"),
        host=get_secret("DB_HOST"),
        port=int(get_secret("DB_PORT", 5432)),
        database=get_secret("DB_NAME"),
        query={"sslmode": get_secret("DB_SSLMODE", "prefer")},
    )
    return create_engine(url, pool_pre_ping=True)

@st.cache_data(ttl=600)
def run(sql, params=None):
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)

# ---------------- Base data ----------------
rankings = run("""
    SELECT c.competitor_id, c.name, c.country, c.country_code,
           r.rank, r.movement, r.points, r.competitions_played
    FROM competitor_rankings r
    JOIN competitors c ON r.competitor_id = c.competitor_id
""")
rankings["points"] = rankings["points"].fillna(0).astype(int)
rankings["movement"] = rankings["movement"].fillna(0).astype(int)

# ---------------- Sidebar navigation ----------------
st.sidebar.title("Tennis Analytics")
page = st.sidebar.radio("Go to", [
    "Overview", "Competitors", "Country Analysis",
    "Leaderboards", "Competitions", "Venues"])

# ================= 1. OVERVIEW =================
if page == "Overview":
    st.title("Game Analytics: Tennis Data Dashboard")
    st.caption("Data source: Sportradar Tennis API v3")

    total_comp = run("SELECT COUNT(*) AS n FROM competitions")["n"][0]
    total_venues = run("SELECT COUNT(*) AS n FROM venues")["n"][0]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Ranked Competitors", rankings["competitor_id"].nunique())
    c2.metric("Countries", rankings["country"].nunique())
    c3.metric("Highest Points", f"{rankings['points'].max():,}")
    c4.metric("Competitions", f"{total_comp:,}")
    c5.metric("Venues", f"{total_venues:,}")

    st.subheader("Top 10 by Points")
    st.dataframe(
        rankings.sort_values("points", ascending=False)
                .head(10)[["name", "country", "rank", "points"]],
        hide_index=True, use_container_width=True)

# ================= 2. COMPETITORS (search + filter + details) =================
elif page == "Competitors":
    st.title("Search & Filter Competitors")

    col1, col2 = st.columns(2)
    selected_names = col1.multiselect(
    "Search by competitor name",options=sorted(rankings["name"].dropna().unique()),
    placeholder="Choose competitors (type to search)",
    )
    countries = col2.multiselect("Country", sorted(rankings["country"].dropna().unique()))

    col3, col4 = st.columns(2)
    rmin, rmax = int(rankings["rank"].min()), int(rankings["rank"].max())
    rank_range = col3.slider("Rank range", rmin, rmax, (rmin, rmax))
    min_points = col4.number_input("Minimum points", 0, int(rankings["points"].max()), 0, step=100)

    df = rankings.copy()
    if selected_names:
        df = df[df["name"].isin(selected_names)]
    if countries:
        df = df[df["country"].isin(countries)]
    df = df[df["rank"].between(*rank_range) & (df["points"] >= min_points)]

    st.write(f"**{len(df)} competitors found**")
    st.dataframe(df.drop(columns=["competitor_id"]).sort_values("rank"),
                 hide_index=True, use_container_width=True)

    st.divider()
    st.subheader("Competitor Details")
    if not df.empty:
        choice = st.selectbox("Select a competitor", df.sort_values("name")["name"].unique())
        p = df[df["name"] == choice].iloc[0]
        d1, d2, d3, d4, d5 = st.columns(5)
        d1.metric("Rank", int(p["rank"]))
        d2.metric("Movement", int(p["movement"]), delta=int(p["movement"]))
        d3.metric("Points", f"{int(p['points']):,}")
        d4.metric("Competitions Played", int(p["competitions_played"] or 0))
        d5.metric("Country", p["country"] or "N/A")

# ================= 3. COUNTRY ANALYSIS =================
elif page == "Country Analysis":
    st.title("Country-wise Analysis")

    country_df = (rankings.groupby("country", dropna=True)
                  .agg(competitors=("competitor_id", "count"),
                       avg_points=("points", "mean"),
                       total_points=("points", "sum"))
                  .reset_index()
                  .sort_values("competitors", ascending=False))
    country_df["avg_points"] = country_df["avg_points"].round(0).astype(int)

    st.subheader("Top 15 Countries by Number of Competitors")
    st.bar_chart(country_df.head(15).set_index("country")["competitors"])

    st.subheader("Top 15 Countries by Average Points")
    st.bar_chart(country_df.sort_values("avg_points", ascending=False)
                 .head(15).set_index("country")["avg_points"])

    st.subheader("Full Country Table")
    st.dataframe(country_df, hide_index=True, use_container_width=True)

# ================= 4. LEADERBOARDS =================
elif page == "Leaderboards":
    st.title("Leaderboards")
    n = st.slider("Show top", 5, 50, 10)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Highest Points")
        st.dataframe(rankings.sort_values("points", ascending=False).head(n)
                     [["name", "country", "points"]], hide_index=True, use_container_width=True)
    with col2:
        st.subheader("Most Competitions Played")
        st.dataframe(rankings.sort_values("competitions_played", ascending=False).head(n)
                     [["name", "country", "competitions_played"]], hide_index=True, use_container_width=True)

    st.subheader("Biggest Climbers This Week")
    st.dataframe(rankings.sort_values("movement", ascending=False).head(n)
                 [["name", "country", "rank", "movement"]], hide_index=True, use_container_width=True)

    st.subheader("Stable Rank (No Movement)")
    st.dataframe(rankings[rankings["movement"] == 0].sort_values("rank")
                 [["name", "country", "rank", "points"]], hide_index=True, use_container_width=True)

# ================= 5. COMPETITIONS =================
elif page == "Competitions":
    st.title("Competitions & Categories")

    by_cat = run("""
        SELECT cat.category_name, COUNT(comp.competition_id) AS total_competitions
        FROM categories cat
        LEFT JOIN competitions comp ON comp.category_id = cat.category_id
        GROUP BY cat.category_name
        ORDER BY total_competitions DESC
    """)
    st.subheader("Competitions per Category")
    st.bar_chart(by_cat.set_index("category_name"))

    st.subheader("Competition Types by Category")
    dist = run("""
        SELECT cat.category_name, comp.type, COUNT(*) AS total
        FROM competitions comp
        JOIN categories cat ON comp.category_id = cat.category_id
        GROUP BY cat.category_name, comp.type
    """)
    pivot = dist.pivot_table(index="category_name", columns="type",
                             values="total", fill_value=0)
    st.dataframe(pivot, use_container_width=True)

    st.subheader("Browse Competitions")
    cat = st.selectbox("Category", by_cat["category_name"])
    top_only = st.checkbox("Top-level competitions only (no parent)")
    sql = """
        SELECT comp.competition_name, comp.type, comp.gender, comp.level
        FROM competitions comp
        JOIN categories cat ON comp.category_id = cat.category_id
        WHERE cat.category_name = :cat
    """
    if top_only:
        sql += " AND comp.parent_id IS NULL"
    st.dataframe(run(sql + " ORDER BY comp.competition_name", {"cat": cat}),
                 hide_index=True, use_container_width=True)

# ================= 6. VENUES =================
elif page == "Venues":
    st.title("Venues & Complexes")

    by_country = run("""
        SELECT country_name, COUNT(*) AS total_venues
        FROM venues
        WHERE country_name IS NOT NULL
        GROUP BY country_name
        ORDER BY total_venues DESC
        LIMIT 15
    """)
    st.subheader("Top 15 Countries by Number of Venues")
    st.bar_chart(by_country.set_index("country_name"))

    st.subheader("Complexes with More Than One Venue")
    st.dataframe(run("""
        SELECT cx.complex_name, COUNT(v.venue_id) AS total_venues
        FROM complexes cx
        JOIN venues v ON cx.complex_id = v.complex_id
        GROUP BY cx.complex_name
        HAVING COUNT(v.venue_id) > 1
        ORDER BY total_venues DESC
    """), hide_index=True, use_container_width=True)

    st.subheader("Find Venues by Country")
    all_c = run("SELECT DISTINCT country_name FROM venues WHERE country_name IS NOT NULL ORDER BY 1")
    sel = st.selectbox("Country", all_c["country_name"])
    st.dataframe(run("""
        SELECT v.venue_name, v.city_name, v.timezone, cx.complex_name
        FROM venues v
        JOIN complexes cx ON v.complex_id = cx.complex_id
        WHERE v.country_name = :c
        ORDER BY v.venue_name
    """, {"c": sel}), hide_index=True, use_container_width=True)