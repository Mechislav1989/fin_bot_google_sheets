from functools import wraps
import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import List
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

from categories import Categories as cg
import g_sheets as gsh


load_dotenv()

def get_statistic(funcs):
    @wraps(funcs)
    def wrap():
        range = funcs()
        
        df = _config_datafraim()
        categories = cg()._load_categories()
        date = _get_date(range)
        
        answers_by_date = _funcs_date(df, categories, date, range)   
        return answers_by_date   
    return wrap


def get_plot(call_data):
    df = _config_datafraim()
    range = str(call_data)
    date = _get_date(range)
    range_date = _range_date(df, range)
    fig = df.loc[range_date==date]
    
    plot = fig.groupby(['category']).sum().plot(kind='pie', y='amount', autopct='%1.0f%%', subplots=True, figsize=(10, 8))
    plt.title("Expense Class Pie Chart", fontsize=32, fontweight="bold")
    plt.ylabel("")
    plt.legend(title="Expense Class", loc="lower left", bbox_to_anchor=(-0.3, -0.135))
    plt.savefig('img/stat.png')


def _config_datafraim():
    results = gsh._get()[1:]
    
    df = pd.DataFrame(results, columns=['num', 'category', 'name', 'amount', 'date', 'raw_text'])
    df['amount'] = df['amount'].astype(int)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
    return df


def _funcs_date(df, categories: List, date: str, range: str) -> str:
    range_date = _range_date(df, range)
    
    result = df.loc[(range_date == date), 'amount'].sum()
    results_by_category = dict()
    
    for category in categories:
        result_by_category = df.loc[(df['category'] == category)&(range_date == date), 'amount'].sum()
        results_by_category[category] = result_by_category
    return _formate_out(result, results_by_category)


def _get_date(range):
    ranges_our_date = {
        'day': pd.to_datetime('today').day,
        'month': pd.to_datetime('today').month,
        'year': pd.to_datetime('today').year,
        'all': True
    }
    
    for key, value in ranges_our_date.items():
        if key == range:
            date = value       
    return date
        

def _range_date(df, range: str):
    ranges_date = {
        'day': df['date'].dt.day,
        'month': df['date'].dt.month,
        'year': df['date'].dt.year,
        'all': df['date']
    }
    
    for key, value in ranges_date.items():
        if key == range:
            range_date = value        
    return range_date        


def _formate_out(result, results_by_category) -> str:
    usd = float(usd_uah())
    return f"Expenses for today:\n All - {result} griven or {round(result/usd, 2)} usd. \n Expenses by categories: \n\n•" + \
                ("\n• ".join([f" {category} - {amount} griven or {round(amount/usd, 2)} usd" 
                for category, amount in results_by_category.items()]))
                

def usd_uah() -> float:
    url = os.getenv('url_usd')
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.114 YaBrowser/22.9.1.1095 Yowser/2.5 Safari/537.36'
    }
    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    allnews = soup.findAll('span', class_='mfm-posr')[0].contents[0]
    
    return allnews
          