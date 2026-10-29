from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# -------------------- Page setup --------------------
st.set_page_config(
    page_title="COVID-19 Data Analysis Dashboard",
    page_icon="🦠",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {font-size: 2.25rem; font-weight: 800; margin-bottom: 0.1rem;}
    .subtitle {color: #9CA3AF; font-size: 1rem; margin-bottom: 1.2rem;}
    div[data-testid="stMetric"] {
        background: rgba(120, 120, 120, 0.10);
        border: 1px solid rgba(150, 150, 150, 0.20);
        padding: 14px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">🦠 COVID-19 Data Analysis Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Explore reported cases, deaths, and vaccination trends by country and date.</div>',
    unsafe_allow_html=True,
)

# -------------------- Load data --------------------
DATA_FILE = Path(__file__).parent / "owid-covid-data.csv"

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    needed = ["location", "date"]
    missing = [col for col in needed if col not in df.columns]
    if missing:
        raise ValueError(
            "The CSV is missing required columns: "
            + ", ".join(missing)
            + ". Please use a COVID dataset with 'location' and 'date' columns."
        )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    numeric_columns = [
        "total_cases", "new_cases", "total_deaths",
        "new_deaths", "people_vaccinated"
    ]
    for col in numeric_columns:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df.dropna(subset=["date", "location"])
    df["location"] = df["location"].astype(str)
    return df.sort_values("date")

if not DATA_FILE.exists():
    st.error("Dataset file not found.")
    st.write("Please put **owid-covid-data.csv** in the same folder as **app.py**.")
    st.stop()

try:
    data = load_data(str(DATA_FILE))
except Exception as exc:
    st.error(f"Could not read the dataset: {exc}")
    st.stop()

if data.empty:
    st.error("The dataset has no usable rows.")
    st.stop()

# -------------------- Sidebar filters --------------------
st.sidebar.header("🔎 Dashboard Filters")
countries = sorted(data["location"].dropna().unique().tolist())
default_country = "India" if "India" in countries else countries[0]
selected_country = st.sidebar.selectbox(
    "Choose a country or location",
    countries,
    index=countries.index(default_country),
)

min_date = data["date"].min().date()
max_date = data["date"].max().date()
date_range = st.sidebar.date_input(
    "Choose date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

if start_date > end_date:
    st.sidebar.warning("Start date must be before end date.")
    st.stop()

filtered = data[
    (data["date"].dt.date >= start_date)
    & (data["date"].dt.date <= end_date)
].copy()
country_data = filtered[filtered["location"] == selected_country].copy()

if country_data.empty:
    st.warning("No data is available for this country in the selected date range.")
    st.stop()

# Keep the last available record for summary totals.
latest = country_data.sort_values("date").iloc[-1]
total_cases = int(latest["total_cases"])
total_deaths = int(latest["total_deaths"])
vaccinated = int(latest["people_vaccinated"])
death_rate = (total_deaths / total_cases * 100) if total_cases else 0

# -------------------- Summary cards --------------------
st.subheader(f"📍 Overview: {selected_country}")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Reported total cases", f"{total_cases:,}")
m2.metric("Reported total deaths", f"{total_deaths:,}")
m3.metric("People vaccinated", f"{vaccinated:,}")
m4.metric("Deaths / cases", f"{death_rate:.2f}%")

st.caption(
    f"Showing {selected_country} from {start_date:%d %b %Y} to {end_date:%d %b %Y}. "
    "Figures can be incomplete. If using sample data, label it clearly in your presentation."
)

# -------------------- Trend charts --------------------
st.subheader("📈 Case and death trends")
left, right = st.columns(2)

with left:
    fig_cases = px.line(
        country_data, x="date", y="total_cases",
        title=f"Total reported cases in {selected_country}",
        markers=True,
        labels={"date": "Date", "total_cases": "Total cases"},
    )
    fig_cases.update_layout(margin=dict(l=10, r=10, t=55, b=10), height=380)
    st.plotly_chart(fig_cases, use_container_width=True)

with right:
    fig_deaths = px.line(
        country_data, x="date", y="total_deaths",
        title=f"Total reported deaths in {selected_country}",
        markers=True,
        labels={"date": "Date", "total_deaths": "Total deaths"},
    )
    fig_deaths.update_layout(margin=dict(l=10, r=10, t=55, b=10), height=380)
    st.plotly_chart(fig_deaths, use_container_width=True)

left2, right2 = st.columns(2)
with left2:
    fig_daily = px.bar(
        country_data, x="date", y="new_cases",
        title=f"New cases by date in {selected_country}",
        labels={"date": "Date", "new_cases": "New cases"},
    )
    fig_daily.update_layout(margin=dict(l=10, r=10, t=55, b=10), height=350)
    st.plotly_chart(fig_daily, use_container_width=True)

with right2:
    fig_vax = px.line(
        country_data, x="date", y="people_vaccinated",
        title=f"People vaccinated in {selected_country}",
        markers=True,
        labels={"date": "Date", "people_vaccinated": "People vaccinated"},
    )
    fig_vax.update_layout(margin=dict(l=10, r=10, t=55, b=10), height=350)
    st.plotly_chart(fig_vax, use_container_width=True)

# -------------------- Country comparison --------------------
st.subheader("🌍 Compare countries")
compare_countries = st.multiselect(
    "Select countries to compare",
    countries,
    default=[c for c in ["India", "United States", "Brazil", "Japan"] if c in countries],
)
compare_data = filtered[filtered["location"].isin(compare_countries)].copy()

if not compare_data.empty:
    metric_choice = st.selectbox(
        "Choose a statistic",
        ["total_cases", "total_deaths", "new_cases", "people_vaccinated"],
        format_func=lambda x: {
            "total_cases": "Total cases",
            "total_deaths": "Total deaths",
            "new_cases": "New cases",
            "people_vaccinated": "People vaccinated",
        }[x],
    )
    fig_compare = px.line(
        compare_data,
        x="date",
        y=metric_choice,
        color="location",
        title="Country comparison over time",
        labels={"date": "Date", metric_choice: metric_choice.replace("_", " ").title(), "location": "Country"},
    )
    fig_compare.update_layout(margin=dict(l=10, r=10, t=55, b=10), height=420)
    st.plotly_chart(fig_compare, use_container_width=True)
else:
    st.info("Select one or more countries to show a comparison chart.")

# -------------------- Data table and download --------------------
st.subheader("📋 View and download data")
show_data = st.checkbox("Show data table", value=True)
display_columns = [
    col for col in [
        "location", "date", "total_cases", "new_cases",
        "total_deaths", "new_deaths", "people_vaccinated"
    ] if col in filtered.columns
]
if show_data:
    st.dataframe(
        filtered[display_columns].sort_values(["location", "date"]),
        use_container_width=True,
        hide_index=True,
    )

csv_bytes = filtered[display_columns].to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download filtered data as CSV",
    data=csv_bytes,
    file_name="covid_dashboard_filtered_data.csv",
    mime="text/csv",
)

st.divider()
st.caption(
    "Project note: The sample CSV supplied for testing contains illustrative data, not official statistics. "
    "Replace it with a verified dataset before drawing real-world conclusions."
)
