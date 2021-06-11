import telebot
from telebot.types import Message
from constants import API_KEY,months
import schedule
import threading
import time
import requests
import sqlite3
from datetime import datetime
from PIL import Image
from io import StringIO

bot = telebot.TeleBot(API_KEY)
con = sqlite3.connect("users.db",check_same_thread=False)
cur = con.cursor()
print('Bot started')

@bot.message_handler(commands = ['start'])
def start_command(message):
    bot.send_message(message.chat.id,'Привет, это бот для рассылки магазина фортнайт в телеграмм \n'
                                     'Ежедневно в 3 ночи присылает обновления магазина \n'
                                     '/info - для информации по всем командам')


@bot.message_handler(commands=['info','help'])
def info(message):
    bot.send_message(message.chat.id,'/subscribe - для подписки на ежедневную рассылку \n'
                                    '/unsubscribe - для отписки от рассылки \n'
                                    '/change_pve - для смены информации о себе(интересен ли вам контент режима пве) \n'
                                    '/get_today - присылает сегодняшний материал рассылки \n'
                                    '/get_day - получить материал расслки опеределенного дня')



@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    print(f'Подписка юзера {str(message.chat.id)}')
    user_id = (int(message.chat.id),)
    users = cur.execute('''
    SELECT id FROM info
    ''').fetchall()
    pve = 1
    if user_id not in users:
        cur.execute('''
        INSERT INTO info VALUES(?,?)
        ''',(message.chat.id,pve,))
        con.commit()
        bot.send_message(message.chat.id,'Вы успешно подписались :)')
    else:
        bot.send_message(message.chat.id,'Вы уже подписаны на рассылку')



@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
    users = cur.execute('''
    SELECT id FROM info
    ''').fetchall()
    user_id = (int(message.chat.id),)
    if user_id in users:
        print(f'Отписка юзера {str(message.chat.id)}')
        cur.execute('''
        DELETE from info
        where id == ?
        ''',(message.chat.id,))
        con.commit()
        bot.send_message(message.chat.id,'Вы успешно отписались :)')
    else:
        bot.send_message(message.chat.id,'Вы еще не подписаны на рассылку')


@bot.message_handler(commands=['change_pve'])
def change_pve(message):
    pve = cur.execute('''
    SELECT pve FROM info
    WHERE id == ?
    ''',(message.chat.id,)).fetchall()[0][0]
    if pve==1:
        bot.send_message(message.chat.id,'Сейчас каждый день вы получаете алерты')
    else:
        bot.send_message(message.chat.id,'Сейчас каждый день вы получаете только магазин')



@bot.message_handler(commands=['get_day'])
def get_day(message):
    pve = cur.execute('''
    SELECT pve FROM info
    WHERE id == ?
    ''',(message.chat.id,)).fetchall()[0][0]
    with open('pics\missions1.png','rb') as pve1, open('pics\missions2.png','rb') as pve2, open('pics\shop.png','rb') as shop:
        if pve == 1:
            bot.send_media_group(message.chat.id,[telebot.types.InputMediaPhoto(pve1),telebot.types.InputMediaPhoto(pve2),telebot.types.InputMediaPhoto(shop)])
        else:
            bot.send_photo(message.chat.id,shop)

@bot.message_handler(commands=['get_today'])
def get_today(message):
    pve = cur.execute('''
    SELECT pve FROM info
    WHERE id == ?
    ''',(message.chat.id,)).fetchall()[0][0]
    with open('pics\missions1.png','rb') as pve1, open('pics\missions2.png','rb') as pve2, open('pics\shop.png','rb') as shop:
        if pve == 1:
            bot.send_message(message.chat.id,'Сегодняшний магазин + алерты')
            bot.send_media_group(message.chat.id,[telebot.types.InputMediaPhoto(pve1),telebot.types.InputMediaPhoto(pve2),telebot.types.InputMediaPhoto(shop)])
        else:
            bot.send_message(message.chat.id,'Сегодняшний магазин')
            bot.send_photo(message.chat.id,shop)

def photo_sender(bot):
    print(f'Начинаем цикл {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
    load_pics() #скачивает картинки
    users = cur.execute('''
    SELECT * FROM info
    ''').fetchall()
    for user in users:
        user_id = user[0]
        pve = user[1]
        with open('pics\missions1.png','rb') as pve1, open('pics\missions2.png','rb') as pve2, open('pics\shop.png','rb') as shop:
            try:
                if pve == 1:
                    bot.send_message(user_id,f'Магазин + алерты на {datetime.now().strftime("%d/%m/%Y")}')
                    bot.send_media_group(user_id,[telebot.types.InputMediaPhoto(pve1),telebot.types.InputMediaPhoto(pve2),telebot.types.InputMediaPhoto(shop)])
                else:
                    bot.send_message(user_id,f'Магазин на {datetime.now().strftime("%d/%m/%Y")}')
                    bot.send_photo(user_id,shop)
            except Exception:
                print(f'Удаление юзера {user_id}, причина - блокировка бота')
                cur.execute('''
                    DELETE from info
                    where id == ?
                    ''',(user_id,))
                con.commit()


schedule.every().day.at('03:10').do(lambda: photo_sender(bot))
#schedule.every().second.do(lambda: photo_sender(bot))
def schedule_cycle():
    while True:
        schedule.run_pending()
        time.sleep(1)


def load_pics():
    url1 = f'https://seebot.dev/images/archive/missions/{datetime.now().day}_{months[str(datetime.now().month)]}_{datetime.now().year}.png'
    url2 = f'https://seebot.dev/images/archive/missions/{datetime.now().day}_{months[str(datetime.now().month)]}_{datetime.now().year}_1.png'
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
bot.polling()