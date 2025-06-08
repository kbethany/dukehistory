import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.set_page_config(page_title="Duke History Alumni Outcomes", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("grads.csv")  # adjust path if needed

    df = df.rename(columns={
        "Completion Year (Academic)": "gradyr",
        "Where Are They Now":        "job",
        "Role":                      "role",
        "Employer":                  "employer",
        "Profession":                "profession",
        "Industry":                  "industry"
    })

    if "id" not in df.columns:
        df["id"] = range(1, len(df) + 1)

    df["status_known"] = df["role"].notna()

    for col in ["industry", "profession", "employer"]:
        df[col] = df[col].fillna("Unknown")

    return df

df = load_data()
df_known = df[df["status_known"]]

# Build sidebar
st.sidebar.header("Filter by Graduation Year")
years = sorted(df["gradyr"].dropna().unique())
selected_years = st.sidebar.multiselect(
    "Select graduation year(s)",
    options=years,
    default=years
)

# Apply  filter
filtered = df[df["gradyr"].isin(selected_years)]

# Title and context
st.title("Where Do Our History Graduates Go?")
st.caption("This dashboard shows a snapshot of current employment outcomes for History majors graduating between 2016 and 2023, based on publicly available information from LinkedIn.")

st.markdown("---")

# Section 1: Total counts
col1, col2 = st.columns(2)
col1.metric("Total Graduates", len(df))
col2.metric("With Known Outcomes", len(df_known))

# Section 2: Graduates by year
st.subheader("Graduates by Year")
df_filtered = df_known[df_known["profession" != "Unknown"]]
grads_per_year = df_known.groupby("gradyr").size().reset_index(name="count")
mean_val = grads_per_year["count"].mean()

bar = alt.Chart(grads_per_year).mark_bar().encode(
    x=alt.X("gradyr:O", title="Graduation Year"),
    y=alt.Y("count:Q", title="Number of Graduates"),
    tooltip=["gradyr", "count"]
)

mean_rule = alt.Chart(pd.DataFrame({'mean': [mean_val]})).mark_rule(color="red", strokeDash=[4, 4]).encode(
    y="mean:Q"
)

st.altair_chart(bar + mean_rule, use_container_width=True)

# Section 3: Top industries
st.subheader("Top Industries")
df_industry_known = df_known[df_known["profession" != "Unknown"]]
filtered_df = df_industry_known[df_industry_known["gradyr"].isin(selected_years)]
industry_counts = df_industry_known["industry"].value_counts().head(10).reset_index()
industry_counts.columns = ["industry", "count"]

chart = alt.Chart(industry_counts).mark_bar().encode(
    x=alt.X("count:Q", title="Number of Graduates"),
    y=alt.Y("industry:N", sort="-x", title="Industry"),
    tooltip=["industry", "count"]
)
st.altair_chart(chart, use_container_width=True)

## Tree Map of Industries
years = sorted(df["gradyr"].dropna().unique())
filtered_df = df[df["gradyr"].isin(selected_years)]
profession_counts = (
    filtered_df["industry"]
    .value_counts()
    .reset_index()
)


fig = px.treemap(
    profession_counts,
    path=["industry"],
    values="count",
    title="Industry by Graduation Year",
    height=700  # 👈 Increase height here (e.g., 700 or more)
)
st.plotly_chart(fig, use_container_width=True)



# Section 4: Top Professions
st.subheader("Top Professions")

df_profession_known = df_known[df_known["profession" != "Unknown"].isin(selected_years)]
filtered_df = df_industry_known[df_industry_known["gradyr"].isin(selected_years)]
profession_counts = df_profession_known["profession"].value_counts().head(10).reset_index()
profession_counts.columns = ["profession", "count"]

chart = alt.Chart(profession_counts).mark_bar().encode(
    x=alt.X("count:Q", title="Number of Graduates"),
    y=alt.Y("profession:N", sort="-x", title="Profession"),
    tooltip=["profession", "count"]
)
st.altair_chart(chart, use_container_width=True)


## Tree Map of Professions
years = sorted(df["gradyr"].dropna().unique())
filtered_df = df[df["gradyr"].isin(selected_years)]
profession_counts = (
    filtered_df["profession"]
    .value_counts()
    .reset_index()
)
import plotly.express as px

fig = px.treemap(
    profession_counts,
    path=["profession"],
    values="count",
    title="Professions by Graduation Year",
    height=700  # 👈 Increase height here (e.g., 700 or more)
)
st.plotly_chart(fig, use_container_width=True)


"""
# Generate text from known employers
df_employer_known = df_known[df_known["employer"] != "Unknown"].isin(selected_years)]
text = " ".join(df_employer_known["employer"])

# Create word cloud
wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)

# Display in Streamlit
st.subheader("Top Employers")
fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)


# Optional: raw data table
with st.expander("View raw data"):
    st.table(df_known.head(50))  # or full df if it's not too big
"""
st.subheader("List of Employers")
st.dataframe(df_known[["employer"]].drop_duplicates().sort_values(by="employer").reset_index(drop=True))

employer_counts = (
    df_known["employer"]
    .value_counts()
    .reset_index()
    .rename(columns={"index": "Employer", "employer": "Count"})
)
st.dataframe(employer_counts)
