import streamlit as st
import pandas as pd
import anthropic
import json
import plotly.express as px

# run on the terminal: pip install plotly gdown anthropic
# then run: streamlit run streamlit_app.py


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
# Sidebar
# -----------------------------
st.sidebar.header("Filters")

selected_score = st.sidebar.multiselect(
    "Select Scores",
    options=sorted(df["score"].unique()),
    default=sorted(df["score"].unique())
)

st.sidebar.divider()

st.sidebar.markdown("**🤖 AI Complaint Analyzer**")
api_key = st.sidebar.text_input(
    "Anthropic API key",
    type="password",
    help="Required for the AI section below. Get one at console.anthropic.com."
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


# ================================
# Section 1: Key Metrics
# ================================
st.header("Key Metrics")

col1, col2 = st.columns(2)
col1.metric("Total Reviews", len(filtered_df))
col2.metric("Average Score", round(filtered_df["score"].mean(), 2))

st.divider()


# ================================
# Section 2: Reviews Over Time
# ================================
st.header("Reviews Over Time")

reviews_data = get_reviews_per_month(filtered_df)

fig_reviews = px.line(
    reviews_data,
    x="date",
    y="count",
    title="Number of Reviews Per Month"
)
st.plotly_chart(fig_reviews, width="stretch")

st.divider()


# ================================
# Section 3: Trends
# ================================
st.header("Trends")

avg_score_data = get_avg_score(filtered_df)

fig_avg = px.line(
    avg_score_data,
    x="date",
    y="average_score",
    title="Average Score Over Time"
)
st.plotly_chart(fig_avg, width="stretch")

trend_data = get_score_trends(filtered_df)

fig_trends = px.line(
    trend_data,
    x="date",
    y="count",
    color="score",
    title="Review Scores Over Time"
)
st.plotly_chart(fig_trends, width="stretch")

st.divider()


# ================================
# Section 4: Distribution
# ================================
st.header("Score Distribution")

dist_data = get_score_distribution(filtered_df)
dist_data.columns = ["score", "count"]

fig_dist = px.bar(
    dist_data,
    x="score",
    y="count",
    title="Number of Reviews by Score"
)
st.plotly_chart(fig_dist, width="stretch")

st.divider()


# ================================
# Section 5: Insights & Analysis
# ================================
st.header("💡 Key Insights & Analysis")

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
st.plotly_chart(fig_growth, width="stretch")

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
st.plotly_chart(fig_high, width="stretch")

st.markdown("""
Even as the pandemic subsided, 4- and 5-star reviews stayed well above pre-2020
levels. This suggests that the wave of pandemic users who stuck with Duolingo
were largely satisfied with the product — a sign of genuine retention rather
than just a temporary spike in usage.
""")

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
st.plotly_chart(fig_polar, width="stretch")

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

st.markdown("### 📝 Summary")
st.info("""
**Key Takeaways:**
- 📱 Review volume has grown steadily, reflecting the global rise of mobile language learning.
- 🦠 The COVID-19 pandemic caused a sharp and sustained increase in user engagement.
- ⭐ High scores (4 & 5 stars) remained elevated post-pandemic, pointing to genuine user satisfaction.
- 📊 The review distribution is bimodal — most users either love or strongly dislike the app.
- 🔄 Duolingo's product improvements likely helped retain the pandemic cohort of new users.
""")

st.divider()


# ================================
# Section 6: AI Complaint Analyzer
# ================================
st.header("🤖 AI Complaint Analyzer")
st.caption("Uses Claude to categorize the most common complaints from 1-star reviews. Add your Anthropic API key in the sidebar to use this section.")

col_a, col_b = st.columns([2, 1])

with col_a:
    sample_size = st.slider(
        "Number of 1-star reviews to analyze",
        min_value=20,
        max_value=200,
        value=75,
        step=5
    )

with col_b:
    year_options = ["All time"] + sorted(df["year"].dropna().unique().astype(int).tolist(), reverse=True)
    selected_year = st.selectbox("Filter by year", options=year_options)

one_star_df = df[df["score"] == 1].copy()

if selected_year != "All time":
    one_star_df = one_star_df[one_star_df["year"] == int(selected_year)]

one_star_df = one_star_df.dropna(subset=["content"])

st.markdown(
    f"**{len(one_star_df):,}** 1-star reviews available"
    + (f" in {selected_year}" if selected_year != "All time" else "")
    + f". Will sample **{min(sample_size, len(one_star_df))}** for analysis."
)

if st.button("Analyze complaints", type="primary"):
    if not api_key:
        st.warning("Please enter your Anthropic API key in the sidebar to use this feature.")
    elif len(one_star_df) == 0:
        st.warning("No 1-star reviews found for the selected filter.")
    else:
        sample = one_star_df["content"].sample(
            min(sample_size, len(one_star_df)),
            random_state=42
        ).tolist()

        reviews_text = "\n".join([f"{i+1}. {r}" for i, r in enumerate(sample)])

        prompt = f"""You are analyzing 1-star app store reviews for Duolingo. Extract and categorize the main complaints.
Reviews:
{reviews_text}
Respond ONLY with a valid JSON object — no markdown, no backticks, no explanation. Use this exact structure:
{{
  "complaint_categories": [
    {{
      "label": "Short category name (3-5 words)",
      "count": <number of reviews mentioning this>,
      "severity": "high" | "medium" | "low",
      "example_quote": "a short representative quote from the reviews (under 15 words)",
      "description": "One sentence describing this complaint pattern."
    }}
  ],
  "dominant_tone": "2-3 word description of overall emotional tone",
  "summary": "2-3 sentence summary of what 1-star reviewers are most upset about and what Duolingo could do."
}}
Sort complaint_categories by count descending. Include 5-7 categories."""

        with st.spinner("Claude is reading the complaints..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                message = client.messages.create(
                    model="claude-opus-4-5",
                    max_tokens=1500,
                    messages=[{"role": "user", "content": prompt}]
                )

                raw = message.content[0].text.strip()
                raw = raw.replace("```json", "").replace("```", "").strip()
                result = json.loads(raw)

                categories = result.get("complaint_categories", [])
                dominant_tone = result.get("dominant_tone", "N/A")
                summary = result.get("summary", "")

                m1, m2, m3 = st.columns(3)
                m1.metric("Reviews analyzed", len(sample))
                m2.metric("Complaint categories", len(categories))
                m3.metric("Overall tone", dominant_tone)

                chart_df = pd.DataFrame([
                    {"Complaint": c["label"], "Mentions": c["count"]}
                    for c in categories
                ]).sort_values("Mentions", ascending=True)

                fig_complaints = px.bar(
                    chart_df,
                    x="Mentions",
                    y="Complaint",
                    orientation="h",
                    title="Complaint frequency",
                    color="Mentions",
                    color_continuous_scale="Reds"
                )
                fig_complaints.update_layout(showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig_complaints, width="stretch")

                st.markdown("#### Breakdown")

                severity_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}

                for cat in categories:
                    icon = severity_icons.get(cat.get("severity", "medium"), "🟡")
                    with st.expander(f"{icon} **{cat['label']}** — {cat['count']} mentions"):
                        st.markdown(f"**Severity:** {cat.get('severity', 'N/A').capitalize()}")
                        st.markdown(f"**Pattern:** {cat.get('description', '')}")
                        if cat.get("example_quote"):
                            st.markdown(f"> _{cat['example_quote']}_")

                st.markdown("#### AI summary")
                st.info(summary)

            except json.JSONDecodeError:
                st.error("Claude returned an unexpected format. Try again.")
                st.code(raw)
            except Exception as e:
                st.error(f"Something went wrong: {e}")

with st.expander("Preview raw 1-star reviews"):
    st.dataframe(
        one_star_df[["at", "content", "score"]].head(20),
        width="stretch"
    )

st.divider()


# ================================
# Raw Data
# ================================
with st.expander("Show Raw Data"):
    st.dataframe(filtered_df.head(100))
