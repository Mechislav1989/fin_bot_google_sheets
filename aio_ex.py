import os 
from dotenv import load_dotenv
import aiohttp
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import logging
from aiogram.contrib.fsm_storage.files import JSONStorage
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup)
from middleware import AccessMiddleware
import ngrok

import wwmess
import exceptions
from categories import Categories

load_dotenv()

api_key = os.getenv('api_token')
client = ngrok.Client(api_key)
ports = 0
for t in client.tunnels.list():
    ports = t.public_url

api_bot = os.getenv('bot')

WEBHOOK_PATH = ''
WEBAPP_HOST = os.getenv('webapp_host')
WEBAPP_PORT = os.getenv('webapp_port')
host = f"{WEBAPP_HOST}:{WEBAPP_PORT}"
WEBHOOK_HOST = ports
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
ACCESS_ID = os.getenv('access_id')
storage: MemoryStorage = MemoryStorage()

bot: Bot = Bot(token=api_bot)
dp: Dispatcher = Dispatcher(bot, storage=storage)
dp.middleware.setup(AccessMiddleware(ACCESS_ID))
dp.middleware.setup(LoggingMiddleware())

logger = logging.getLogger(__name__)


class OrderTime(StatesGroup):
    choosing_date = State()


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    

async def on_shutdown(dp):
    logging.warning('Shutting down..')
    await bot.delete_webhook()
    
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('GoodBye!')
    

@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await message.answer(
        "This is expense management bot \n\n"
        "If you want ta add expense - do like this: 100 fruits \n\n"
        "Todays expenses: /today\n"
        "Expenses for this month: /month\n"
        "Expanses for this year: /year\n"
        "All Expanses: /all\n"
        "Last aded expenses: /last\n"
        "Categories of expenses: /categories"
    )    
   

@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
    try:
        row_id  = int(message.text[4:])
        wwmess.delete(row_id)
        answer = "Delete"
    except:
        answer = "You haven't any entires for deleting"    
    await message.answer(answer)    


@dp.message_handler(commands=['last'])
async def last_expenses(message: types.Message):
    last_expenses = wwmess.last_expense()
    if not last_expenses:
        await message.answer('There is no adds')
        return
    last_expenses_r = [
        f"{last_expenses.amount} griven on {last_expenses.name} - push on "
        f"/del{last_expenses.id} for deleting" 
    ]    
    answer = "Last save expenses: \n\n *" + "\n\n*".join(last_expenses_r)
    await message.answer(answer)


@dp.message_handler(commands=['categories'])
async def category_expenses(message: types.Message):
    categories = Categories()._load_name()
    answer = f"Categories of expenses: \n\n•" + ("\n• ".join([f" {category} ({', '.join(name)})" 
              for category, name  in categories.items()]))
    await message.answer(answer)    


@dp.message_handler(commands=['today'])
async def today_expenses(message: types.Message, state: FSMContext):
    answer = wwmess.get_today()
    markup = InlineKeyboardMarkup()
    today_button = InlineKeyboardButton(text='Do you want to get plot for a day expenses?', callback_data='today')
    markup.add(today_button)
    call_data = 'day'
    
    async with state.proxy() as data:
        data['choosing_date'] = call_data
        
    await message.answer(answer, reply_markup=markup)
    await state.set_state(OrderTime.choosing_date)
       

@dp.message_handler(commands=['month'])
async def today_expenses(message: types.Message, state: FSMContext):
    answer = wwmess.get_month()
    markup = InlineKeyboardMarkup()
    today_button = InlineKeyboardButton(text='Do you want to get plot for a moth expenses?', callback_data='month')
    markup.add(today_button)
    call_data = 'month'
    
    async with state.proxy() as data:
        data['choosing_date'] = call_data
        
    await message.answer(answer, reply_markup=markup)
    await OrderTime.choosing_date.set() 


@dp.message_handler(commands=['year'])
async def today_expenses(message: types.Message, state: FSMContext):
    answer = wwmess.get_year()
    markup = InlineKeyboardMarkup()
    today_button = InlineKeyboardButton(text='Do you want to get plot for an year expenses?', callback_data='year')
    markup.add(today_button)
    call_data = 'year'
    
    async with state.proxy() as data:
        data['choosing_date'] = call_data
        
    await message.answer(answer, reply_markup=markup)
    await OrderTime.choosing_date.set() 


@dp.message_handler(commands=['all'])
async def today_expenses(message: types.Message, state: FSMContext):
    answer = wwmess.get_all()
    markup = InlineKeyboardMarkup()
    today_button = InlineKeyboardButton(text='Do you want to get plot for all the time?', callback_data='all')
    markup.add(today_button)
    call_data = 'all'
    
    async with state.proxy() as data:
        data['choosing_date'] = call_data
    
    await message.answer(answer, reply_markup=markup)
    await OrderTime.choosing_date.set() 

                            
@dp.callback_query_handler(state=OrderTime.choosing_date)
async def process_plot(callback: CallbackQuery, state: FSMContext,):
    await bot.answer_callback_query(callback.id)
    
    async with state.proxy() as date:
        call_data = date['choosing_date']
      
    wwmess.get_image(call_data)
        
    try:
        with open(f'img/stat.png', 'rb') as photo: 
            await bot.send_photo(chat_id=callback.from_user.id, photo=photo) 
            await state.reset_state()   
    except exceptions.BadFoto as e:
        await bot.send_message(callback.from_user.id, str(e))            


@dp.message_handler()
async def add_expense(message: types.Message):
    try:
        expense = wwmess.add_expense(message.text)
    except exceptions.NotCorrectName as e:
        await message.answer(str(e))
        return
    
    answer = f"{expense.amount} griven on {expense.name} - push on {expense.category}."   
    await message.answer(answer)


async def main():
    logging.basicConfig(level=logging.INFO, 
                        format=u'%(filename)s:%(lineno)d #%(levelname)-8s '
               u'[%(asctime)s] - %(name)s - %(message)s')
    logging.info('Starting bot')
    

if __name__ == '__main__':
    executor.start_webhook(
        dp, webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=False,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT
        )    
    