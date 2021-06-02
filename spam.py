from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
import shutil
from time import sleep
months = {'1':'Jan','2':'Feb','3':'Mar','4':'Apr','5':'May','6':'Jun','7':'Jul','8':'Aug','9':'Sep','10':'Oct','11':'Nov','12':'Dec'}

def shop():
    url = f'https://seebot.dev/images/archive/missions/{datetime.now().day}_{months[str(datetime.now().month)]}_{datetime.now().year}.png'
    url1 = f'https://seebot.dev/images/archive/missions/{datetime.now().day}_{months[str(datetime.now().month)]}_{datetime.now().year}_1.png'
    sleep(5)
    html = requests.get(url, stream=True)
    with open('img.png','wb') as out_file:
        shutil.copyfileobj(html.raw,out_file)
    del html
    html = requests.get(url1, stream=True)
    with open('img1.png','wb') as out_file:
        shutil.copyfileobj(html.raw,out_file)
    del html
shop()
