import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Beer Dashboard", layout="wide")

# ---------- LOAD DATA ----------
file_path = Path("Beer Consumed Guest For Dashboard.xlsx")

if not file_path.exists():
    st.error("❌ Excel file not found. Upload it to GitHub repository.")
    st.stop()

@st.cache_data
def load_data(path):
    return pd.read_excel(path)

df = load_data(file_path)

# ---------- DATA PREPROCESS ----------
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Customer Mobile No'] = df['Customer Mobile No'].astype(str)
df['Day'] = df['Date'].dt.day_name()

df['Hour'] = pd.to_datetime(
    df['Time'].astype(str), errors='coerce'
).dt.hour

# ---------- TITLE ----------
st.title("🍺 Beer Consumption Guest Segmentation Dashboard")

# ---------- SIDEBAR ----------
st.sidebar.header("Filters")

centre = st.sidebar.multiselect(
    "Business Unit",
    df['POSDescription'].dropna().unique(),
    default=df['POSDescription'].dropna().unique()
)

month = st.sidebar.multiselect(
    "Reporting Period",
    df['Bill Month'].dropna().unique(),
    default=df['Bill Month'].dropna().unique()
)

df = df[(df['POSDescription'].isin(centre)) &
        (df['Bill Month'].isin(month))]

# ---------- KPI ----------
total_revenue = df['Gross Amount'].sum()
unique_guests = df['Customer Mobile No'].nunique()

repeat_guests = df['Customer Mobile No'].value_counts()
repeat_pct = (
    repeat_guests[repeat_guests > 1].count() / unique_guests * 100
    if unique_guests else 0
)

c1, c2, c3 = st.columns(3)
c1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
c2.metric("Unique Guests", unique_guests)
c3.metric("Repeat Guest %", f"{repeat_pct:.1f}%")

st.divider()

# ---------- SEGMENTATION ----------
st.subheader("Guest Segementation")

guest_metrics = df.groupby('Customer Mobile No').agg(
    visits=('Bill No', 'nunique'),
    spend=('Gross Amount', 'sum')
).reset_index()

def segment(row):
    if row['spend'] > 10000 or row['visits'] >= 6:
        return 'VIP'
    elif row['visits'] >= 3:
        return 'Regular'
    return 'Occasional'

guest_metrics['Segment'] = guest_metrics.apply(segment, axis=1)

st.bar_chart(guest_metrics['Segment'].value_counts())

st.write("### Revenue by Segment")
seg_rev = guest_metrics.merge(
    df[['Customer Mobile No','Gross Amount']],
    on='Customer Mobile No'
).groupby('Segment')['Gross Amount'].sum()

st.bar_chart(seg_rev)

st.divider()

# ---------- CENTRE PREFERENCE ----------
st.subheader("Centre-wise Beer Preference")

heatmap = pd.pivot_table(
    df,
    index='POSDescription',
    columns='MenuGroupDescription',
    values='Customer Mobile No',
    aggfunc='nunique',
    fill_value=0
)

st.dataframe(heatmap)

st.divider()

# ---------- VISIT FREQUENCY ----------
st.subheader("Visit Frequency")

visit_dist = (
    df.groupby('Customer Mobile No')['Bill No']
    .nunique()
    .value_counts()
    .sort_index()
)

st.bar_chart(visit_dist)

st.divider()

# ---------- PEAK TIME ----------
st.subheader("Peak Consumption")

c1, c2 = st.columns(2)

with c1:
    st.write("Revenue by Day")
    st.bar_chart(df.groupby('Day')['NetAmount'].sum())

with c2:
    st.write("Revenue by Hour")
    st.bar_chart(df.groupby('Hour')['NetAmount'].sum())

st.divider()

# ---------- CLV ----------
st.subheader("Customer Lifetime Value")

clv = df.groupby('Customer Mobile No').agg(
    visits=('Bill No','nunique'),
    total_spend=('NetAmount','sum')
)

st.metric("Average CLV", f"₹{clv['total_spend'].mean():,.0f}")

st.write("Top Customers")
st.dataframe(clv.sort_values('total_spend', ascending=False).head(10))

st.divider()

# ---------- RETENTION ----------
st.subheader("Retention Insights")

last_visit = df.groupby('Customer Mobile No')['Date'].max()

inactive = last_visit[last_visit < df['Date'].max() - pd.Timedelta(days=30)]
recent = last_visit[last_visit >= df['Date'].max() - pd.Timedelta(days=7)]

st.write("Inactive Guests (30+ days)")
st.dataframe(inactive)

st.write("Likely to Return")
st.dataframe(recent)

st.divider()

# ---------- BRAND INSIGHTS ----------
st.subheader("Beer Brand Insights")

brand_summary = df.groupby('MenuGroupDescription').agg(
    Unique_Guests=('Customer Mobile No','nunique'),
    Quantity=('Quantity','sum'),
    Revenue=('Gross Amount','sum')
).sort_values('Revenue', ascending=False)

st.dataframe(brand_summary)

st.write("Revenue by Brand")
st.bar_chart(brand_summary['Revenue'])

top_brand = brand_summary.index[0]
low_brand = brand_summary.index[-1]

st.success(f"🏆 Most Preferred: {top_brand}")
st.warning(f"Low Performing: {low_brand}")
