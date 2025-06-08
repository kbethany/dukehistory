import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Duke History Alumni Outcomes", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("grads.csv")


    # Rename columns
    df = df.rename(columns={
        "Completion Year (Academic)": "gradyr",
        "Where Are They Now": "job",
        "Role": "role",
        "Employer": "employer",
        "Profession": "profession",
        "Industry": "industry"})

    # Add ID if not present
    if "id" not in df.columns:
        df["id"] = range(1, len(df) + 1)

    # Add known/unknown status
    df["status_known"] = df["role"].notna()

    # Clean up blanks
    for col in ["industry", "profession", "employer"]:
        df[col] = df[col].fillna("Unknown")

    return df

df = load_data()
df_known = df[df["status_known"]]


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

industry_counts = df_known["industry"].value_counts().head(10).reset_index()
industry_counts.columns = ["industry", "count"]

chart = alt.Chart(industry_counts).mark_bar().encode(
    x=alt.X("count:Q", title="Number of Graduates"),
    y=alt.Y("industry:N", sort="-x", title="Industry"),
    tooltip=["industry", "count"]
)
st.altair_chart(chart, use_container_width=True)

# Section 4: Top Professions
st.subheader("Top Professions")

df_profession_known = df_known[df_known["profession"] != "Unknown"]
profession_counts = df_profession_known["profession"].value_counts().head(10).reset_index()
profession_counts.columns = ["profession", "count"]

chart = alt.Chart(profession_counts).mark_bar().encode(
    x=alt.X("count:Q", title="Number of Graduates"),
    y=alt.Y("profession:N", sort="-x", title="Profession"),
    tooltip=["profession", "count"]
)
st.altair_chart(chart, use_container_width=True)

# Section 5: Top Employers
st.subheader("Top Employers")

df_employer_known = df_known[df_known["employer"] != "Unknown"]
employer_counts = df_employer_known["employer"].value_counts().head(10).reset_index()
employer_counts.columns = ["employer", "count"]

chart = alt.Chart(employer_counts).mark_bar().encode(
    x=alt.X("count:Q", title="Number of Graduates"),
    y=alt.Y("employer:N", sort="-x", title="Employer"),
    tooltip=["employer", "count"]
)
st.altair_chart(chart, use_container_width=True)


import altair as alt

df_filtered = df[df["profession"] != "Unknown"]

industry_by_year = alt.Chart(df_known).mark_bar().encode(
    x=alt.X("gradyr:O", title="Graduation Year", sort=alt.EncodingSortField(field="grad_year", order="ascending")),
    y=alt.Y("count():Q", title="Number of Graduates"),
    color=alt.Color("profession:N", title="Industry"),
    tooltip=["gradyr:O", "profession:N", "count():Q"]
).properties(
    title="Industry Breakdown by Graduation Year",
)

st.altair_chart(industry_by_year, use_container_width=True)

##another way to show this
years = sorted(df["gradyr"].dropna().unique())
selected_years = st.multiselect("Select graduation year(s)", years, default=years)
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
)
st.plotly_chart(fig, use_container_width=True)


# Optional: raw data table
with st.expander("View raw data"):
    st.table(df_known.head(50))  # or full df if it's not too big


import streamlit as st
import pandas as pd
import plotly.express as px

# Load data (cached for performance)
@st.cache_data
def load_data():
    return pd.read_csv("data/grads.csv")

df = load_data()

# --- Filter: Graduation Year ---
st.sidebar.header("Filter")
years = sorted(df["gradyr"].dropna().unique())
selected_years = st.sidebar.multiselect(
    "Select graduation year(s)",
    options=years,
    default=years
)

# Apply filter
filtered_df = df[df["gradyr"].isin(selected_years)]

# --- Clean profession field ---
filtered_df = filtered_df[filtered_df["profession"].notna()]
filtered_df = filtered_df[filtered_df["profession"].str.lower() != "unknown"]

# --- Count professions ---
profession_counts = (
    filtered_df["profession"]
    .value_counts()
    .reset_index()
)

# --- Plot tree map ---
fig = px.treemap(
    profession_counts,
    path=["profession"],
    values="count",
    title="Top Professions by Graduation Year Selection"
)
st.plotly_chart(fig, use_container_width=True)


