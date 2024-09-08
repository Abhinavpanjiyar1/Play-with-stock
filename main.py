import pandas
import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd
import numpy as np
from fmp_python.fmp import FMP
import requests
import pandas_ta as ta


# Define a function to fetch fundamental data from FMP
def get_fundamental_data_fmp(ticker, api_key):
    try:
        # URLs for Balance Sheet, Income Statement, and Cash Flow data
        balance_sheet_url = f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?apikey={api_key}'
        income_statement_url = f'https://financialmodelingprep.com/api/v3/income-statement/{ticker}?apikey={api_key}'
        cash_flow_url = f'https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?apikey={api_key}'

        # Fetching the data from FMP API
        balance_sheet = requests.get(balance_sheet_url).json()
        income_statement = requests.get(income_statement_url).json()
        cash_flow = requests.get(cash_flow_url).json()

        return balance_sheet, income_statement, cash_flow

    except Exception as e:
        raise Exception(f"Error fetching data from FMP API: {str(e)}")

st.title("ABHINAV STOCK DATA")
ticker = st.sidebar.text_input("Ticker")
start_date= st.sidebar.date_input("Start_date")
end_date = st.sidebar.date_input("End_date")

data = yf.download(ticker, start = start_date, end = end_date)
#fig = px.line(data, x = data.index, y =data['Adj Close'], title = ticker)
fig = px.line(data, x=data.index, y='Adj Close', title=ticker)
#st.plotly_chart(fig)

pricing_data, fundamental_data, news, technical_analysis, data_cleaner = st.tabs(["Pricing data", "Fundamental data", "News", "Technical  Indicator", "Data Cleaner"])
#st.plotly_chart(fig)

with pricing_data:
    st.header('price movements')
    data2 = data.copy()
    data2["% change"] = data["Adj Close"] /data["Adj Close"].shift(1)-1
    data2.dropna(inplace = True)
    st.write(data)
    annual_return = data2['% change'].mean()*252*100
    st.write("Annual Return is:", annual_return,'%')
    stdev = np.std(data2['% change'])*np.sqrt(252)
    st.write('Standard Deviation is :', stdev, '%')
    st.write('Risk adj. Return is:', annual_return / (stdev*100))
    st.plotly_chart(fig)

with fundamental_data:
    api_key = 'otOO95CIYAkAARE3mA7BaXVeuNeodqjI'  # Your Financial Modeling Prep API key
    if ticker:
        try:
            # Fetch fundamental data from FMP using the function
            balance_sheet, income_statement, cash_flow = get_fundamental_data_fmp(ticker, api_key)

            st.subheader('Balance Sheet')
            st.write(pd.DataFrame(balance_sheet))

            st.subheader('Income Statement')
            st.write(pd.DataFrame(income_statement))

            st.subheader('Cash Flow')
            st.write(pd.DataFrame(cash_flow))
        except Exception as e:
            st.error(f"Error fetching fundamental data: {e}")

    #st.write("fundamental")


from stocknews import StockNews
with news:
    st.header(f'News of {ticker}')
    sn = StockNews(ticker, save_news = False)
    df_news = sn.read_rss()

    for i in range(10):
        st.subheader(f'News {i+1}')
        st.write(df_news['published'][i]) #Date of news
        st.write(df_news['title'][i]) #Title of news
        st.write(df_news['summary'][i]) #summary of news

        #sentiment analysis for title and summary
        title_sentiment = df_news['sentiment_title'][i]
        st.write(f'Title Sentiment{title_sentiment}')

        news_sentiment = df_news['sentiment_summary'][i]
        st.write(f'News Sentiment {news_sentiment}')
    #st.write("news")

with technical_analysis:
    st.subheader('Technical Analysis Dashboard')
    df = pandas.DataFrame()
    ind_list = df.ta.indicators(as_list = True)
    #st.write(ind_list)
    technical_analysis = st.selectbox('Technical Indicator', options = ind_list)
    method = technical_analysis
    indicator = pd.DataFrame(getattr(ta, method)(low= data['Low'],close = data['Close'],
                                                 high = data['High'], open = data['Open']))
    indicator['Close'] = data['Close']
    st.write(indicator)
    fig_ind = px.line(indicator)
    st.plotly_chart(fig_ind)


# Data Cleaner Tab
with data_cleaner:
    st.subheader("Data Cleaner")

    # Select dataset to clean
    dataset_option = st.selectbox("Which dataset would you like to clean?", ["Fundamental Data", "Technical Indicator"])

    if dataset_option == "Fundamental Data":
        # Show the fundamental data to clean
        st.write("Cleaning Fundamental Data")

        # Display existing fundamental data
        fundamental_datasets = {"Balance Sheet": pd.DataFrame(balance_sheet),
                                "Income Statement": pd.DataFrame(income_statement),
                                "Cash Flow": pd.DataFrame(cash_flow)}
        dataset_to_clean = st.selectbox("Select which fundamental data to clean", list(fundamental_datasets.keys()))

        # Get the selected dataset and allow cleaning
        data_to_clean = fundamental_datasets[dataset_to_clean]
        st.write(f"Original {dataset_to_clean}:")
        st.write(data_to_clean)

    elif dataset_option == "Technical Indicator":
        # Show the technical indicator data to clean
        st.write("Cleaning Technical Indicator Data")
        st.write(indicator)

        data_to_clean = indicator

    # Option to remove columns
    columns_to_remove = st.multiselect("Select columns to remove", data_to_clean.columns)
    if columns_to_remove:
        data_to_clean.drop(columns=columns_to_remove, inplace=True)
        st.write("Data after removing selected columns:")
        st.write(data_to_clean)

    # Option to handle NaN values
    nan_handling = st.selectbox("How would you like to handle NaN values?", ["Drop NaNs", "Fill NaNs with mean", "Fill NaNs with zero"])

    if nan_handling == "Drop NaNs":
        data_to_clean.dropna(inplace=True)
    elif nan_handling == "Fill NaNs with mean":
        data_to_clean.fillna(data_to_clean.mean(), inplace=True)
    elif nan_handling == "Fill NaNs with zero":
        data_to_clean.fillna(0, inplace=True)

    st.write("Cleaned Data")
    st.write(data_to_clean)








