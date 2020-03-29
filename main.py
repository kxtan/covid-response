import pandas as pd
import datetime as dt
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

@st.cache
def read_file(date, path="data/oxcgrt.csv", remove_unnamed=True):

    raw_df = pd.read_csv(path, parse_dates=["Date"])
    raw_df['Date'] = pd.to_datetime(raw_df['Date']).dt.date

    if remove_unnamed:
        raw_df = raw_df.loc[:, ~raw_df.columns.str.contains('^Unnamed')]

    return raw_df

@st.cache(hash_funcs={pd.DataFrame: lambda _: None})
def get_countries(raw_df):

    country_lst = list(set(raw_df["CountryName"].values))
    country_lst.sort()

    return country_lst[:]

@st.cache(hash_funcs={pd.DataFrame: lambda _: None})
def get_data_df(raw_df):

    primary_index_lst=["CountryName", "CountryCode", "Date"]
    data_df = raw_df[primary_index_lst + 
    ["StringencyIndex", "ConfirmedCases", "ConfirmedDeaths", "S1_School closing"]]    
    #data_df = data_df.fillna(0)

    return data_df

@st.cache
def get_country_df(country, data_df, drop_countries=True):

    grouped = data_df.groupby("CountryName")
    df = grouped.get_group(selected_country)

    if drop_countries:
        df = df.drop(columns=["CountryName", "CountryCode"])

    return df
@st.cache
def get_school_closed_df(country, data_df):
    
    school_closed_df = data_df[data_df.CountryName == country]
    school_closed_df = school_closed_df[['CountryName', 'Date', 'S1_School closing']]
    # The point in time where schools are closed
    school_closed_df = school_closed_df[data_df['S1_School closing'] > 0]

    school_closed_df = school_closed_df['Date'].min()
    return school_closed_df


st.title("Country Covid-19 Tracker")
raw_df = read_file(str(dt.date.today()))

data_df = get_data_df(raw_df)
country_lst = get_countries(data_df)

selected_country = st.sidebar.selectbox("Select Country", 
    country_lst, country_lst.index("United Kingdom"))

target_df = get_country_df(selected_country, data_df)

remove_zero = st.sidebar.checkbox("Remove zero cases", value=True)

# school_closed = st.sidebar.checkbox("School closed", value=False)

if remove_zero:
    target_df = target_df[(target_df[["StringencyIndex", "ConfirmedCases", "ConfirmedDeaths"]].T != 0).any()]

###Get daily delta in df form
delta_df = target_df[["ConfirmedCases", "ConfirmedDeaths"]].diff()
delta_df.insert(0, 'Date', target_df["Date"])

cumu_fig = make_subplots(specs=[[{"secondary_y": True}]])

cumu_fig.add_trace(
    go.Scatter(
        x=target_df["Date"],
        y=target_df["ConfirmedCases"],
        name="ConfirmedCases"
    )
)

cumu_fig.add_trace(
    go.Scatter(
        x=target_df["Date"],
        y=target_df["ConfirmedDeaths"],
        name="ConfirmedDeaths"
    )
)

cumu_fig.add_trace(
    go.Scatter(
        x=target_df["Date"],
        y=target_df["StringencyIndex"],
        name="StringencyIndex"
    ),
    secondary_y=True
)

# if school_closed:
#     school_closed_date = get_school_closed_df(selected_country, data_df)

#     cumu_fig.add_trace(
#         go.Scatter(
#             x=target_df[target_df.Date == school_closed_date]['Date'],
#             y=daily_change_df[daily_change_df.Date == school_closed_date]['DailyChangeInConfirmedCases'],
#             name="School closed"
#         )
#     )

cumu_fig.update_shapes(dict(xref='x', yref='y'))
cumu_fig.update_layout(
    title="Cumulative chart on Stringency, Cases & Deaths"
)
cumu_fig.update_xaxes(title_text="Date")
cumu_fig.update_yaxes(title_text="Cases/Deaths", secondary_y=False)
cumu_fig.update_yaxes(title_text="StringencyIndex", secondary_y=True)

st.subheader("Cumulative cases in {}".format(selected_country))
st.write(cumu_fig)


display_columns = ["Date", "ConfirmedCases", 
    "ConfirmedDeaths", "StringencyIndex"]
st.write(target_df[display_columns].set_index("Date").sort_index(ascending=False))

delta_fig = make_subplots(specs=[[{"secondary_y": True}]])

delta_fig.add_trace(
    go.Scatter(
        x=delta_df["Date"],
        y=delta_df["ConfirmedCases"],
        name="ConfirmedCases"
    )
)

delta_fig.add_trace(
    go.Scatter(
        x=delta_df["Date"],
        y=delta_df["ConfirmedDeaths"],
        name="ConfirmedDeaths"
    )
)

delta_fig.add_trace(
    go.Scatter(
        x=target_df["Date"],
        y=target_df["StringencyIndex"],
        name="StringencyIndex"
    ),
    secondary_y=True
)

delta_fig.update_layout(
    title="Daily Change in Cases & Deaths"
)
delta_fig.update_xaxes(title_text="Date")
delta_fig.update_yaxes(title_text="Cases/Deaths", secondary_y=False)
delta_fig.update_yaxes(title_text="StringencyIndex", secondary_y=True)

st.subheader("Daily Changes in {}".format(selected_country))
st.write(delta_fig)


display_columns = ["Date", "ConfirmedCases", 
    "ConfirmedDeaths"]
display_delta_df = delta_df.rename(columns={"ConfirmedCases": "NewCases", "ConfirmedDeaths": "NewDeaths"})
display_delta_df = display_delta_df.set_index("Date").sort_index(ascending=False)
st.write(display_delta_df)

st.subheader("Disclaimer:")
st.text(" Please note that the  Stringency Index is for comparative purposes only, and should not\
\nnecessarily be interpreted as rating of the appropriateness or effectiveness of a \
\ncountry's response.")

st.subheader("Citation:")
st.text("Hale, Thomas and Samuel Webster (2020). Oxford COVID-19 Government Response Tracker")

st.subheader("Resources:")
st.markdown("https://www.bsg.ox.ac.uk/research/research-projects/oxford-covid-19-government-response-tracker")