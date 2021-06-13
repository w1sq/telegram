import pathlib
from types import ModuleType
from aiogram.types import user
import telebot
from aiogram import Bot, Dispatcher, executor, types
from key import API_KEY
import schedule
import threading
import time
import requests
import sqlite3
from datetime import datetime
import logging
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.input_media import MediaGroup
from aiogram.types.input_media import InputMedia
from aiogram.types import InputFile
import asyncio
from io import BytesIO


logging.basicConfig(level=logging.INFO, filename='logs.log')
storage = MemoryStorage()
bot = Bot(token=API_KEY)
dp = Dispatcher(bot, storage=storage)
con = sqlite3.connect("users.db",check_same_thread=False)
cur = con.cursor()
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
print('Bot started')


class FormSub(StatesGroup):
    answer = State()


class FormChng1(StatesGroup):
    answer = State()

class FormChng2(StatesGroup):
    answer = State()

class FormDay(StatesGroup):
    answer = State()


@dp.message_handler(commands = ['start'])
async def start_command(message):
    await message.answer('Привет, это бот для рассылки магазина фортнайт в телеграмм \n'
                                     'Ежедневно в 3 ночи присылает обновления магазина \n'
                                     '/info - для информации по всем командам')


@dp.message_handler(commands=['info','help'])
async def info(message):
    await message.answer('/subscribe - для подписки на ежедневную рассылку \n'
                                    '/unsubscribe - для отписки от рассылки \n'
                                    '/change_pve - для смены информации о себе(интересен ли вам контент режима пве) \n'
                                    '/get_today - присылает сегодняшний материал рассылки \n'
                                    '/get_day - получить материал расслки опеределенного дня')


@dp.message_handler(commands=['subscribe'])
async def subscribe(message):
    print(f'Подписка юзера {str(message.chat.id)}')
    user_id = (int(message.chat.id),)
    users = cur.execute('''
    SELECT id FROM info
    ''').fetchall()
    if user_id not in users:
        await message.answer('Хотите ли вы получать обновления алертов пве? да/нет')
        await FormSub.answer.set()
    else:
        await message.answer('Вы уже подписаны на рассылку')


@dp.message_handler(state=FormSub.answer)
async def confirm(message,state):
    if message.text.lower() == 'да':
        cur.execute('''
        INSERT INTO info VALUES(?,1)
        ''',(message.chat.id,))
        con.commit()
        await message.answer('Вы успешно подписались :)')
        await state.finish()
    elif message.text.lower() == 'нет':
        cur.execute('''
        INSERT INTO info VALUES(?,0)
        ''',(message.chat.id,))
        con.commit()
        await message.answer('Вы успешно подписались :)')
        await state.finish()
    else:
        await message.answer('Принимается только ответы да/нет')


@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message):
    user_id = message.chat.id
    user = cur.execute('''
    SELECT id FROM info
    WHERE id == ?
    ''',(user_id,)).fetchone()
    if user:
        print(f'Отписка юзера {user_id}')
        cur.execute('''
        DELETE from info
        where id == ?
        ''',((user_id,)))
        con.commit()
        await bot.send_message(user_id,'Вы успешно отписались :)')
    else:
        await bot.send_message(user_id,'Вы еще не подписаны на рассылку')


@dp.message_handler(commands=['change_pve'])
async def change_pve(message):
    pve = cur.execute('''
    SELECT pve FROM info
    WHERE id == ?
    ''',(message.chat.id,)).fetchall()
    if pve:
        if pve[0][0]==1:
            await message.answer('Сейчас каждый день вы получаете и магазин и алерты. \n'
                                'Вы хотите получать только магазин? да/нет')
            await FormChng1.answer.set()
        elif pve[0][0] == 0:
            await message.answer('Сейчас каждый день вы получаете только магазин. \n'
                                'Хотите также получать алерты? да/нет' )
            await FormChng2.answer.set()
    else:
        await message.answer('Вы еще не подписаны на рассылку \n'
                            '/subscribe чтобы подписаться')


@dp.message_handler(state=FormChng1.answer)
async def change(message,state):
    if message.text.lower() == 'да':
        cur.execute('''
        UPDATE info
        SET pve = 0 
        WHERE id = ?''',(message.chat.id,))
        con.commit()
        await message.answer('Теперь вы будете получать только магазин:)')
        await state.finish()
    elif message.text.lower() == 'нет':
        await message.answer('Все остается так же')
        await state.finish()
    else:
        await message.answer('Принимается только ответы да/нет')


@dp.message_handler(state=FormChng2.answer)
async def change(message,state):
    if message.text.lower() == 'да':
        cur.execute('''
        UPDATE info
        SET pve = 1 
        WHERE id = ?''',(message.chat.id,))
        con.commit()
        await message.answer('Теперь вы будете получать и магазин и алерты:)')
        await state.finish()
    elif message.text.lower() == 'нет':
        await message.answer('Все остается так же')
        await state.finish()
    else:
        await message.answer('Принимается только ответы да/нет')


@dp.message_handler(commands=['get_day'])
async def get_day(message):
    await message.answer('Пришли мне дату выхода желаемого магазина в формате 15.9.2019')
    await FormDay.answer.set()

@dp.message_handler(state=FormDay.answer)
async def change(message,state):
    user_id = message.chat.id
    pve = cur.execute('''
    SELECT pve FROM info
    WHERE id == ?
    ''',(user_id,)).fetchall()[0][0]
    if message.text.lower() != 'отмена':
        try:    
            if date := validate_date(message.text.lower()):
                url1 = f'https://seebot.dev/images/archive/missions/{date.day}_{months[date.month-1]}_{date.year}.png'
                url2 = f'https://seebot.dev/images/archive/missions/{date.day}_{months[date.month-1]}_{date.year}_1.png'
                url3 = f'https://bot.fnbr.co/shop-image/fnbr-shop-{date.day}-{date.month}-{date.year}.png'
                if pve == 1:
                    mediagroup = create_webmediagroup([url1,url2,url3])
                    await bot.send_media_group(user_id,mediagroup)
                    await state.finish()
                elif pve[0][0] == 0:
                    await bot.send_photo(BytesIO(requests.get(url3).content))
                    await state.finish()
            else:
                await message.answer('Неправильный формат. Либо вводи правильно либо пиши отмена')
        except Exception:
            await message.answer('Извини, слишком глухая дата')
            await state.finish()

    else:
        await state.finish()


def validate_date(date):
    date_format = '%d.%m.%Y'
    try:
        return datetime.strptime(date,date_format)
    except ValueError:
        return False

def create_webmediagroup(images):
    mediagroup = MediaGroup()
    for image in images:
        data = requests.get(image)
        mediagroup.attach_photo(BytesIO(data.content))
    return mediagroup


def create_mediagroup():
    mediagroup = MediaGroup()
    mediagroup.attach_photo(InputFile(open('pics\missions1.png','rb')))
    mediagroup.attach_photo(InputFile(open('pics\missions2.png','rb')))
    mediagroup.attach_photo(InputFile(open('pics\shop.png','rb')))
    return mediagroup


@dp.message_handler(commands=['get_today'])
async def get_today(message):
    user_id = message.chat.id
    pve = cur.execute('''
    SELECT pve FROM info
    WHERE id == ?
    ''',(user_id,)).fetchall()
    if pve:
        if pve[0][0] == 1:
            await message.answer('Сегодняшний магазин + алерты')
            mediagroup = create_mediagroup()
            await bot.send_media_group(user_id,mediagroup)
        else:
            with open('pics\shop.png','rb') as shop:
                await message.answer('Сегодняшний магазин')
                await bot.send_photo(user_id,shop)
    else:
        await message.answer('Вы не подписаны на рассылку')


async def photo_sender(bot):
    print(f'Начинаем цикл {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
    load_pics() #скачивает картинки
    users = cur.execute('''
    SELECT * FROM info
    ''').fetchall()
    for user in users:
        user_id = user[0]
        pve = user[1]
        try:
            if pve == 1:
                await bot.send_message(user_id,f'Магазин + алерты на {datetime.now().strftime("%d/%m/%Y")}')
                mediagroup = create_mediagroup()
                await bot.send_media_group(user_id,mediagroup)
            else:
                with open('pics\shop.png','rb') as shop:
                    await bot.send_message(user_id,f'Магазин на {datetime.now().strftime("%d/%m/%Y")}')
                    await bot.send_photo(user_id,shop)
        except Exception as e:
            print(f'Удаление юзера {user_id}, причина - блокировка бота')
            cur.execute('''
                DELETE from info
                where id == ?
                ''',(user_id,))
            con.commit()


def timer_sending(bot,loop):
    asyncio.run_coroutine_threadsafe(photo_sender(bot),loop)
    time.sleep(10)


schedule.every().day.at('03:10').do(lambda: timer_sending(bot,loop))
def schedule_cycle():
    while True:
        schedule.run_pending()
        time.sleep(1)


def load_pics():
    url1 = f'https://seebot.dev/images/archive/missions/{datetime.now().day}_{months[int(datetime.now().month)-1]}_{datetime.now().year}.png'
    url2 = f'https://seebot.dev/images/archive/missions/{datetime.now().day}_{months[int(datetime.now().month)-1]}_{datetime.now().year}_1.png'
    url3 = f'https://bot.fnbr.co/shop-image/fnbr-shop-{datetime.now().day}-{str(datetime.now().month)}-{datetime.now().year}.png'
    query = requests.get(url1)
    with open('pics\missions1.png', 'wb') as file:
        file.write(query.content)
    query = requests.get(url2)
    with open('pics\missions2.png', 'wb') as file:
        file.write(query.content)
    query = requests.get(url3)
    with open('pics\shop.png','wb') as file:
        file.write(query.content)


daemon = threading.Thread(target=schedule_cycle, daemon=True)
daemon.start()
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, skip_updates=True)