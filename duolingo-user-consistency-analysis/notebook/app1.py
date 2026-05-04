import streamlit as st
import pandas as pd
import math
from pathlib import Path
import plotly.express as px
# run on the terminal: pip install plotly
# run on the terminal: pip install gdown
# run on the terminal: streamlit run streamlit_app.py
# the following bash commands are if the csv file is being loaded from github directly (the csv file is too big for that) 
# git rm --cached data.csv
# echo "data.csv" >> .gitignore
# git add .
# git commit -m "remove data.csv from repo"
# git push



# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Duolingo Reviews Analysis",
    layout="wide"
)

st.title("📊 Duolingo Reviews Analysis")
st.caption("Explore trends and patterns in user reviews")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    import gdown
    file_id = "128cct_W07kKWWszjmfdV0rOeJbkSpVDu"
    gdown.download(f"https://drive.google.com/uc?id={file_id}", "data.csv", quiet=True)
    df = pd.read_csv("data.csv", low_memory=False)
    df["at"] = pd.to_datetime(df["at"])
    df["year"] = df["at"].dt.year
    df["month"] = df["at"].dt.month
    return df


df = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

selected_score = st.sidebar.multiselect(
    "Select Scores",
    options=sorted(df["score"].unique()),
    default=sorted(df["score"].unique())
)

filtered_df = df[df["score"].isin(selected_score)]

# -----------------------------
# Helper Functions
# -----------------------------
def get_reviews_per_month(df):
    data = df.groupby(["year", "month"]).size().reset_index(name="count")
    data["date"] = pd.to_datetime(
        data["year"].astype(str) + "-" + data["month"].astype(str)
    )
    return data

def get_avg_score(df):
    data = (
        df.groupby(["year", "month"])["score"]
        .mean()
        .reset_index(name="average_score")
    )
    data["date"] = pd.to_datetime(
        data["year"].astype(str) + "-" + data["month"].astype(str)
    )
    return data

def get_score_distribution(df):
    return df["score"].value_counts().sort_index().reset_index()

def get_score_trends(df):
    data = (
        df.groupby(["year", "month", "score"])
        .size()
        .reset_index(name="count")
    )
    data["date"] = pd.to_datetime(
        data[["year", "month"]].assign(day=1)
    )
    return data

def add_covid_line(fig, label="COVID-19 (Mar 2020)"):
    """Add a vertical dashed red line at March 2020 using shapes (works in all Plotly versions)."""
    fig.add_shape(
        type="line",
        x0="2020-03-01", x1="2020-03-01",
        y0=0, y1=1,
        yref="paper",
        line=dict(color="red", dash="dash", width=1.5)
    )
    fig.add_annotation(
        x="2020-03-01",
        y=0.97,
        yref="paper",
        text=label,
        showarrow=False,
        xanchor="left",
        font=dict(color="red", size=11),
        bgcolor="rgba(255,255,255,0.7)"
    )
    return fig

# -----------------------------
# Tabs Layout
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Trends",
    "Distribution",
    "💡 Insights & Analysis"
])

# -----------------------------
# TAB 1: Overview
# -----------------------------
with tab1:
    st.subheader("Key Metrics")

    col1, col2 = st.columns(2)
    col1.metric("Total Reviews", len(filtered_df))
    col2.metric("Average Score", round(filtered_df["score"].mean(), 2))

    st.subheader("Reviews Over Time")

    reviews_data = get_reviews_per_month(filtered_df)

    fig_reviews = px.line(
        reviews_data,
        x="date",
        y="count",
        title="Number of Reviews Per Month"
    )

    st.plotly_chart(fig_reviews, use_container_width=True)

# -----------------------------
# TAB 2: Trends
# -----------------------------
with tab2:
    st.subheader("Average Score Over Time")

    avg_score_data = get_avg_score(filtered_df)

    fig_avg = px.line(
        avg_score_data,
        x="date",
        y="average_score",
        title="Average Score Over Time"
    )

    st.plotly_chart(fig_avg, use_container_width=True)

    st.subheader("Score Trends Over Time")

    trend_data = get_score_trends(filtered_df)

    fig_trends = px.line(
        trend_data,
        x="date",
        y="count",
        color="score",
        title="Review Scores Over Time"
    )

    st.plotly_chart(fig_trends, use_container_width=True)

# -----------------------------
# TAB 3: Distribution
# -----------------------------
with tab3:
    st.subheader("Score Distribution")

    dist_data = get_score_distribution(filtered_df)
    dist_data.columns = ["score", "count"]

    fig_dist = px.bar(
        dist_data,
        x="score",
        y="count",
        title="Number of Reviews by Score"
    )

    st.plotly_chart(fig_dist, use_container_width=True)

# -----------------------------
# TAB 4: Insights & Analysis
# -----------------------------
with tab4:
    st.subheader("💡 Key Insights & Analysis")

    # ---- Insight 1: Long-term growth ----
    st.markdown("### 📈 Long-Term Growth in App Reviews")
    st.markdown("""
    The overall volume of Duolingo reviews has grown significantly over time.
    This mirrors the broader rise of mobile language learning — as smartphones became
    ubiquitous and self-improvement culture expanded, apps like Duolingo saw a surge
    in both downloads and engaged users leaving feedback.

    The upward trend in review count is not just a Duolingo story: it reflects a
    structural shift in how people learn languages, moving away from textbooks and
    classroom settings toward on-demand, gamified mobile experiences.
    """)

    reviews_data_all = get_reviews_per_month(df)
    fig_growth = px.line(
        reviews_data_all,
        x="date",
        y="count",
        title="Total Reviews Per Month (All Scores)",
        labels={"count": "Number of Reviews", "date": "Date"}
    )
    fig_growth = add_covid_line(fig_growth, "COVID-19 Declared (Mar 2020)")
    st.plotly_chart(fig_growth, use_container_width=True)

    # ---- Insight 2: COVID-19 impact ----
    st.markdown("### 🦠 The COVID-19 Effect")
    st.markdown("""
    A notable spike in reviews coincides with the onset of the COVID-19 pandemic
    in early 2020. With schools closed, offices shut, and people stuck at home,
    millions turned to self-improvement apps to fill their time — and Duolingo
    was one of the biggest beneficiaries.

    This pandemic-driven surge wasn't just a blip. It introduced a large cohort of
    new users to the app during a period when learning a new language felt both
    meaningful and achievable. Many of these users became long-term engagers, which
    helps explain why review volumes remained elevated even after lockdowns ended.
    """)

    # ---- Insight 3: High scores post-COVID ----
    st.markdown("### ⭐ High Ratings Remained Elevated Post-Pandemic")

    trend_data_all = get_score_trends(df)
    high_scores = trend_data_all[trend_data_all["score"].isin([4, 5])]

    fig_high = px.line(
        high_scores,
        x="date",
        y="count",
        color="score",
        title="4 & 5-Star Reviews Over Time",
        labels={"count": "Number of Reviews", "date": "Date", "score": "Score"}
    )
    fig_high = add_covid_line(fig_high, "COVID-19 Pandemic Begins")
    st.plotly_chart(fig_high, use_container_width=True)

    st.markdown("""
    Even as the pandemic subsided, 4- and 5-star reviews stayed well above pre-2020
    levels. This suggests that the wave of pandemic users who stuck with Duolingo
    were largely satisfied with the product — a sign of genuine retention rather
    than just a temporary spike in usage.

    This could be partly attributed to Duolingo's continued product improvements
    during this period, including better gamification features, personalized learning
    paths, and expanded language offerings that kept users engaged long after the
    initial lockdown novelty wore off.
    """)

    # ---- Insight 4: Score composition ----
    st.markdown("### 🔍 Review Polarization: Love It or Hate It")

    dist_data_all = get_score_distribution(df)
    dist_data_all.columns = ["score", "count"]

    fig_polar = px.bar(
        dist_data_all,
        x="score",
        y="count",
        title="Overall Score Distribution",
        color="score",
        color_continuous_scale="RdYlGn",
        labels={"count": "Number of Reviews", "score": "Score"}
    )
    st.plotly_chart(fig_polar, use_container_width=True)

    st.markdown("""
    The score distribution reveals a strongly **bimodal** pattern — reviews are
    concentrated at the extremes (1-star and 5-star), with relatively few neutral
    3-star reviews in between. This is common with consumer apps: users who feel
    strongly — either delighted or frustrated — are far more likely to leave a review
    than those with a lukewarm experience.

    The dominance of 5-star ratings suggests that Duolingo's core user base is highly
    satisfied, while the significant volume of 1-star reviews likely captures users
    who hit paywalls, experienced bugs, or felt misled by the free tier's limitations.
    """)

    # ---- Insight 5: Summary callout ----
    st.markdown("### 📝 Summary")
    st.info("""
    **Key Takeaways:**

    - 📱 Review volume has grown steadily, reflecting the global rise of mobile language learning.
    - 🦠 The COVID-19 pandemic caused a sharp and sustained increase in user engagement.
    - ⭐ High scores (4 & 5 stars) remained elevated post-pandemic, pointing to genuine user satisfaction.
    - 📊 The review distribution is bimodal — most users either love or strongly dislike the app.
    - 🔄 Duolingo's product improvements likely helped retain the pandemic cohort of new users.
    """)

# -----------------------------
# Raw Data
# -----------------------------
with st.expander("Show Raw Data"):
    st.dataframe(filtered_df.head(100))
