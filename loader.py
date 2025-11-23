import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import TIMESTAMP, FLOAT, VARCHAR
from config.config import DATABASE_URL

df = pd.read_csv('World-Stock-Prices-Dataset.csv')
filter_df = df[(df['Date'].str.split('-').str[0] == '2024') & (df['Industry_Tag'] == 'technology')]

engine_url = DATABASE_URL
engine = create_engine(engine_url)
  

# Загружаем DataFrame в PostgreSQL
filter_df.to_sql(
    name='stock_data' ,
    con=engine,
    if_exists='replace',
    index=False,
    dtype={
        'Date': TIMESTAMP,
        'Open': FLOAT,
        'High': FLOAT,
        'Low': FLOAT,
        'Close': FLOAT,
        'Volume': FLOAT,
        'Brand_Name': VARCHAR(255),
        'Ticker': VARCHAR(50),
        'Industry_Tag': VARCHAR(255),
        'Country': VARCHAR(100),
        'Dividends': FLOAT,
        'Stock Splits': FLOAT,
        'Capital Gains': FLOAT
    }
)




