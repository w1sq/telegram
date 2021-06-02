from datetime import datetime
import random

def sample_responses(input_text):
    user_message = str(input_text).lower()
    ru_greetings = ['привет','прив','ку','здарова','здаров','здраствуй']
    eng_greetings = ['hi','hello','sup']

    if user_message in ru_greetings:
        return ru_greetings[random.randint(0,len(ru_greetings))]
    
    if user_message in eng_greetings:
        return eng_greetings[random.randint(0,len(eng_greetings))]

    if user_message in ('время', 'time'):
        return str(datetime.now().strftime("%d/%m/%y"))

    return 'Я тебя не понимаю'
