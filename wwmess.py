import datetime
import re 
from typing import List, NamedTuple, Optional

import exceptions
from categories import Categories as cg
import g_sheets as gsh
from decorators import get_statistic, get_plot


class Message(NamedTuple):
    amount: int
    name: str
    

class Expense(NamedTuple):
    id: Optional[int]
    category: str
    name: str
    amount: int
    

def add_expense(raw_message: str) -> Expense:
    parsed_message = _parse_message(raw_message)
    amount = parsed_message.amount
    date = _get_now_formatted()
    name = parsed_message.name
    category = cg().get_category(name)
    inserted_row_id = gsh.GoogleSh().add(amount, date, name, category, raw_message)
    return Expense(id=gsh._num_column, category=category, name=name, amount=amount)
    

def last_expense() -> Expense:
    rows = gsh._get()[-1]
    last_expense = Expense(id=rows[0], category=rows[1], name=rows[2], amount=rows[3])
    return last_expense


def _parse_message(raw_message: str) -> Message:
    reg_result = re.match(r"([\d ]+) (.*)", str(raw_message))
    
    if not reg_result or not reg_result.group(0) or not reg_result.group(1) \
        or not reg_result.group(2):
            raise exceptions.NotCorrectName("Don't understand you.") 
    
    amount = reg_result.group(1).replace("", "")
    name = reg_result.group(2).strip().lower()
    return Message(amount=amount, name=name)                   


@get_statistic
def get_today() -> str:

    return 'day' 

                
@get_statistic
def get_month() -> str:
    
    return 'month' 


@get_statistic
def get_year() -> str:
    
    return 'year' 


@get_statistic
def get_all() -> str:
    
    return True   


def _day_month_year() -> str:
    date = _get_now_formatted()
    today = date.split(' ')[0].split('-')[2]
    this_month = date.split(' ')[0].split('-')[1]
    this_year = date.split(' ')[0].split('-')[0]
    return str(today), str(this_month), str(this_year)        
 
   
def _get_now_formatted() -> str:
    return _get_time().strftime("%Y-%m-%d %H:%M:%S")


def _get_time() -> datetime.datetime:
    now = datetime.datetime.now()
    return now
  
  
def delete(row_id):
    return gsh.GoogleSh().dlt(row_id)


def get_image(call_data):
    return get_plot(call_data)

