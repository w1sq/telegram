import telebot
from constants import API_KEY,months
import responses as resp
import schedule
import threading
import time
import requests
from datetime import datetime

bot = telebot.TeleBot(API_KEY)
print('Bot started')

@bot.message_handler(commands = ['start'])
def start_command(message):
    bot.send_message(message.chat.id,'Привет, это бот для рассылки магазина фортнайт в телеграмм \n'
                                     'Ежедневно в 3 ночи присылает обновления магазина \n'
                                     '/info - для информации по всем командамrf')


@bot.message_handler(commands=['subscribe'])
def get_user_id(message):
    print(f'Подписка юзера {str(message.chat.id)}')
    with open('user.txt','r') as userstxt:
        users = userstxt.readlines()
        user_id = str(message.chat.id)
        if user_id not in users:
            with open('user.txt','a') as file:
                file.write(user_id)
            bot.send_message(message.chat.id,'Вы успешно подписались :)')
        else:
            bot.send_message(message.chat.id,'Вы уже подписаны на рассылку')


def photo_sender(bot):
    print(f'Начинаем цикл {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
    shop() #скачивает картинки
    time.sleep(10)
    with open('user.txt','r') as userstxt:
        users = userstxt.readlines()
    for user_id in users:
        for filename in ['pics\missions1.png','pics\missions2.png','pics\shop.png']:
            with open(filename,'rb') as file:
                bot.send_photo(user_id, file)

schedule.every().day.at('03:10').do(lambda: photo_sender(bot))
def schedule_cycle():
    while True:
        schedule.run_pending()
        time.sleep(1)


def shop():
    url1 = f'https://seebot.dev/images/archive/missions/{datetime.now().day}_{months[str(datetime.now().month)]}_{datetime.now().year}.png'
    url2 = f'https://seebot.dev/images/archive/missions/{datetime.now().day}_{months[str(datetime.now().month)]}_{datetime.now().year}_1.png'
    url3 = f'https://seebot.dev/images/archive/brshop/{datetime.now().day}_{months[str(datetime.now().month)]}_{datetime.now().year}.png'
    query = requests.get(url1)
    with open('pics/missions1.png', 'wb') as file:
        file.write(query.content)
    query = requests.get(url2)
    with open('pics/missions2.png', 'wb') as file:
        file.write(query.content)
    query = requests.get(url3)
    with open('pics/shop.png','wb') as file:
        file.write(query.content)
daemon = threading.Thread(target=schedule_cycle, daemon=True)
daemon.start()
bot.polling()