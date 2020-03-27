import pandas as pd
import numpy as np
import datetime as dt
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

@st.cache
def read_file(date, path="data/oxcgrt.csv", remove_unnamed=True):

    raw_df = pd.read_csv(path, parse_dates=["Date"])

    if remove_unnamed:
        raw_df = raw_df.loc[:, ~raw_df.columns.str.contains('^Unnamed')]

    return raw_df

@st.cache(hash_funcs={pd.DataFrame: lambda _: None})
def get_countries(raw_df):

    country_lst = list(set(raw_df["CountryName"].values))

    return country_lst[:]

@st.cache(hash_funcs={pd.DataFrame: lambda _: None})
def get_data_df(raw_df):

    primary_index_lst=["CountryName", "CountryCode", "Date"]
    data_df = raw_df[primary_index_lst + ["StringencyIndex", "ConfirmedCases", "ConfirmedDeaths"]]    
    #data_df = data_df.fillna(0)

    return data_df

@st.cache
def get_country_df(country, data_df):

    grouped = data_df.groupby("CountryName")

    return grouped.get_group(selected_country)

st.title("Country Covid-19 Tracker")

raw_df = read_file(str(dt.date.today()))
data_df = get_data_df(raw_df)
country_lst = get_countries(data_df)

selected_country = st.selectbox("Select Country", 
    country_lst, country_lst.index("Malaysia"))

target_df = get_country_df(selected_country, data_df)

fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Scatter(
        x=target_df["Date"],
        y=target_df["ConfirmedCases"],
        name="ConfirmedCases"
    )
)

fig.add_trace(
    go.Scatter(
        x=target_df["Date"],
        y=target_df["ConfirmedDeaths"],
        name="ConfirmedDeaths"
    )
)


fig.add_trace(
    go.Scatter(
        x=target_df["Date"],
        y=target_df["StringencyIndex"],
        name="StringencyIndex"
    ),
    secondary_y=True
)

st.write(fig)
st.write(target_df[["Date", "StringencyIndex", "ConfirmedCases", "ConfirmedDeaths"]].set_index("Date"))

st.subheader("Disclaimer:")
st.text(" Please note that the  Stringency Index is for comparative purposes only, and should not\
\nnecessarily be interpreted as rating of the appropriateness or effectiveness of a \
\ncountry's response.")

st.subheader("Citation:")
st.text("Hale, Thomas and Samuel Webster (2020). Oxford COVID-19 Government Response Tracker")

st.subheader("Resources:")
st.markdown("https://www.bsg.ox.ac.uk/research/research-projects/oxford-covid-19-government-response-tracker")