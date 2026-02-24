#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np 
import pandas as pd 
import streamlit as st 
import openpyxl 

# In[2]:


df = pd.read_excel("Beer Consumed Guest For Dashboard.xlsx" , engine="openpyxl")


# In[3]:


df['Date'] = pd.to_datetime(df['Date'])
df['Customer Mobile No'] = df['Customer Mobile No'].astype(str)
df['Day'] = df['Date'].dt.day_name()
df['Hour'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour


# In[4]:


st.title("Beer Consumption Guest Segmentation Dashboard")


# In[ ]:





# ### Sidebar Filter

# In[5]:


st.sidebar.title("Analysis Parameters")


# In[6]:


centre = st.sidebar.multiselect(
    "Select Business Unit",
    df['POSDescription'].unique(),
    default=df['POSDescription'].unique())


# In[7]:


month = st.sidebar.multiselect(
    "Reporting Period",
    df['Bill Month'].unique(),
    default=df['Bill Month'].unique()
)


# In[ ]:





# In[ ]:





# In[ ]:





# In[8]:


df = df[(df['POSDescription'].isin(centre)) &
        (df['Bill Month'].isin(month))]


# ### KPI For Dashboard

# In[9]:


total_revenue = df['Gross Amount'].sum()
unique_guests = df['Customer Mobile No'].nunique()
repeat_guests = df['Customer Mobile No'].value_counts()
repeat_pct = (repeat_guests[repeat_guests > 1].count() / unique_guests) * 100


# In[10]:


col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"₹{total_revenue:,.0f}")
col2.metric("Unique Guests", unique_guests)
col3.metric("Repeat Guest %", f"{repeat_pct:.1f}%")

st.markdown("---_")


# ### CUSTOMER SEGMENTATION

# In[11]:


st.subheader("Beer Consumed Guest Segmentation")


# In[12]:


guest_metrics = df.groupby('Customer Mobile No').agg(
    visits=('Bill No', 'nunique'),
    spend=('Gross Amount', 'sum')
).reset_index()


# In[13]:


def segment(row):
    if row['spend'] > 10000 or row['visits'] >= 6:
        return 'VIP'
    elif row['visits'] >= 3:
        return 'Regular'
    else:
        return 'Occasional'


# In[14]:


guest_metrics['Segment'] = guest_metrics.apply(segment, axis=1)


# In[15]:


seg_counts = guest_metrics['Segment'].value_counts()


# In[16]:


st.bar_chart(seg_counts)


# In[17]:


st.write("### Revenue Contribution by Segment")
seg_rev = guest_metrics.merge(df[['Customer Mobile No','Gross Amount']],
                              on='Customer Mobile No') \
                       .groupby('Segment')['Gross Amount'].sum()
st.bar_chart(seg_rev)


# In[18]:


st.markdown("--")


# ### CENTRE-WISE BEER PREFERENCE HEATMAP

# In[19]:


st.subheader("Centre-wise Beer Preference")


# In[20]:


heatmap_data = pd.pivot_table(
    df,
    index='POSDescription',
    columns='MenuGroupDescription',
    values='Customer Mobile No',
    aggfunc=pd.Series.nunique,
    fill_value=0
)

st.dataframe(heatmap_data)

st.markdown("--")


# ### VISIT FREQUENCY ANALYSIS

# In[21]:


st.subheader("Visit Frequency Distribution")

visit_freq = df.groupby('Customer Mobile No')['Bill No'].nunique()
visit_dist = visit_freq.value_counts().sort_index()

st.bar_chart(visit_dist)

st.markdown("--")


# ### PEAK DAY & TIME ANALYSIS

# In[22]:


st.subheader("Peak Consumption Insights")

col1, col2 = st.columns(2)

with col1:
    day_sales = df.groupby('Day')['NetAmount'].sum()
    st.write("Revenue by Day")
    st.bar_chart(day_sales)

with col2:
    hour_sales = df.groupby('Hour')['NetAmount'].sum()
    st.write("Revenue by Hour")
    st.bar_chart(hour_sales)

st.markdown("--")


# ### CUSTOMER LIFETIME VALUE (CLV)

# In[23]:


st.subheader("Customer Lifetime Value")

clv = df.groupby('Customer Mobile No').agg(
    visits=('Bill No', 'nunique'),
    total_spend=('NetAmount', 'sum')
)

st.metric("Average CLV", f"₹{clv['total_spend'].mean():,.0f}")

st.write("Top 10 Customers by CLV")
st.dataframe(clv.sort_values(by='total_spend', ascending=False).head(10))

st.markdown("--")


# ### NEXT VISIT / RETENTION INSIGHTS

# In[24]:


st.subheader("Retention & Next Visit Insights")

last_visit = df.groupby('Customer Mobile No')['Date'].max().reset_index()
inactive = last_visit[last_visit['Date'] < df['Date'].max() - pd.Timedelta(days=30)]

st.write("Inactive Guests (30+ days)")
st.dataframe(inactive)

st.write("Guests Likely to Return Soon")
recent = last_visit[last_visit['Date'] >= df['Date'].max() - pd.Timedelta(days=7)]
st.dataframe(recent)


# ### Beer Brand Consumption Insights

# In[25]:


st.subheader("Beer Brand Consumption Insights")

brand_summary = df.groupby('MenuGroupDescription').agg(
    Unique_Guests=('Customer Mobile No', 'nunique'),
    Quantity_Sold=('Quantity', 'sum'),
    Revenue=('Gross Amount', 'sum')
).reset_index().sort_values(by='Revenue', ascending=False)

st.dataframe(brand_summary)


# In[26]:


st.write("### Revenue Contribution by Beer Brand")
st.bar_chart(brand_summary.set_index('MenuGroupDescription')['Revenue'])


# In[27]:


st.write("### Unique Guests by Beer Brand")
st.bar_chart(brand_summary.set_index('MenuGroupDescription')['Unique_Guests'])


# In[28]:


top_brand = brand_summary.iloc[0]['MenuGroupDescription']
st.success(f"🏆 Most Preferred Beer Category :- {top_brand}")


# In[29]:


low_brand = brand_summary.iloc[-1]['MenuGroupDescription']
st.warning(f"⚠ Low Performing Category :- {low_brand}")


# In[30]:


st.subheader("Guest Beer Brand Preference")

guest_pref = df.groupby(
    ['Customer Mobile No','MenuGroupDescription']
).size().reset_index(name='Orders')

st.dataframe(guest_pref.sort_values(by='Orders', ascending=False).head(20))


# 

# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




