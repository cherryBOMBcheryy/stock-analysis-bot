# analytics.py
import io
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text

plt.switch_backend('Agg') 

def create_db_engine(database_url):
    return create_engine(database_url, future=True)

def query_prices(engine, ticker=None, start_date=None, end_date=None):
    q = "SELECT * FROM stock_data WHERE 1=1"
    params={}
    if ticker:
        q += " AND upper(\"Ticker\") = :ticker"
        params['ticker'] = ticker.upper()
    if start_date:
        q += f" AND \"Date\" >= TO_DATE('{start_date}', 'YYYY-MM-DD')"
        params['start_date'] = start_date
    if end_date:
        q += f" AND \"Date\" <= TO_DATE('{end_date}', 'YYYY-MM-DD')"
        params['end_date'] = end_date
    df = pd.read_sql(text(q), engine, params=params)
    df['Date'] = pd.to_datetime(df['Date'])
    return df.sort_values(by = 'Date').reset_index(drop=True)

def compute_stats(df):
    if df.empty:
        return None
    s={}
    s['ticker'] = list(df.Ticker.unique())[0]
    s['mean_close']=float(df['Close'].mean())
    s['min_close']=float(df['Close'].min())
    s['max_close']=float(df['Close'].max())
    s['start_price']=float(df.iloc[0]['Close'])
    s['end_price']=float(df.iloc[-1]['Close'])
    s['change_abs']=s['end_price']-s['start_price']
    s['change_pct']=(s['change_abs']/s['start_price'])*100 if s['start_price']!=0 else None
    s['volatility']=float(df['Close'].pct_change().dropna().std())
    return s

def plot_price_chart(df):
    if df is None or df.empty:
        raise ValueError("Нет данных")
    plt.figure(figsize=(10,4))
    plt.plot(df['Date'], df['Close'])
    plt.title(f"Динамика цены акций компании {list(df.Brand_Name.unique())[0]}")
    plt.xlabel("Дата")
    plt.ylabel("Цена закрытия")
    plt.grid(True)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf


def format_stats(stats):
    if not stats:
        return "Нет данных для анализа."
    
    formatted_stats = (
        f"Аналитика по тикеру {stats['ticker']} за указанный период:\n\n"
        f"Средняя цена закрытия:  {stats['mean_close']:.2f}\n"
        f"Минимальная цена закрытия:  {stats['min_close']:.2f}\n"
        f"Максимальная цена закрытия:  {stats['max_close']:.2f}\n"
        f"Цена на начало периода:  {stats['start_price']:.2f}\n"
        f"Цена на конец периода:  {stats['end_price']:.2f}\n"
        f"Изменение цены:  {stats['change_abs']:.2f} ({stats['change_pct']:.2f}%)\n"
        f"Волатильность:  {stats['volatility']:.4f}\n"
    )
    
    if stats['change_abs'] > 0:
        formatted_stats += "\nЦены росли."
    elif stats['change_abs'] < 0:
        formatted_stats += "\nЦены упали."
    else:
        formatted_stats += "\nЦены остались без изменения."
    
    return formatted_stats