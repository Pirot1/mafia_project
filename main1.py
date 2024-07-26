from telebot import TeleBot, types
from random import randint, choice
from time import sleep
#import json
#import data_base
import db
#from time import time
#import requests
#import wikipedia

#import pickle
TOKEN = '...'
bot = TeleBot(TOKEN)

#points = 0
#index = 0
#sum_check = 0
game = False
night = False






#Mafia


@bot.message_handler(func=lambda m: m.text.lower() == 'готов играть' and m.chat.type == 'private')
def send_text(message):
    bot.send_message(message.chat.id, f'{message.from_user.first_name} играет')
    bot.send_message(message.from_user.id, 'Вы добавлены в игру')
    db.insert_player(message.from_user.id, username=message.from_user.first_name)



@bot.message_handler(commands=['play'])
def game_on(message):
    if not game:
        bot.send_message(message.chat.id, 'Если хотите играть напишите "готов играть" в ЛС')



@bot.message_handler(commands=['game'])
def start(message):
    global game
    players = db.players_amount()
    if players >= 1 and not game: #для теста >=1; >=5
        db.set_roles(players)
        players_roles = db.get_players_roles()
        mafia_uersname = db.get_mafia_usernames()
        for player_id, role in players_roles:
            bot.send_message(message.chat.id,text = role)
            if role == 'mafia':
                bot.send_message(message.chat.id,text = f'Все члены мафии: \n{mafia_uersname}')
        game = True
        bot.send_message(message.chat.id, text = 'Игра началась')
        game_loop(message)
        return
    bot.send_message(message.chat.id, text = 'Недостаточно игроков')


@bot.message_handler(commands=["kill"])
def kill(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_alive()
    mafia_usernames = db.get_mafia_usernames()
    if night and message.from_user.first_name in mafia_usernames:
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого имени нет')
            return
        voted = db.vote("mafia_vote", username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учитан')
            return
        bot.send_message(
            message.chat.id, 'У вас больше нет права голосовавать')
    bot.send_message(message.chat.id, 'Сейчас нельзя убивать')


@bot.message_handler(commands=["kick"])
def kick(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_alive()  
    if not night:
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого имени нет')
            return
        voted = db.vote("citizen_vote", username, message.from_user.id)
        if voted:
            bot.send_message(message.chat.id, 'Ваш голос учитан')
            return
        bot.send_message(
            message.chat.id, 'У вас больше нет права голосовавать')
        return
    bot.send_message(
        message.chat.id, 'Сейчас ночь вы не можете никого убить')
    
@bot.message_handler(commands=['arrest'])
def arrest(message):
    username = ' '.join(message.text.split(' ')[1:])
    usernames = db.get_all_alive()
    sherifs = db.get_sherif_username()
    if not night and message.from_user.first_name in sherifs:
        if not username in usernames:
            bot.send_message(message.chat.id, 'Такого имени нет')
            return
        arrested = db.sherif_vote(username)
        bot.send_message(message.chat.id, arrested)
    bot.send_message(message.chat.id, 'Сейчас ночь')
        





def autoplay_citizen(message):
    players_roles = db.get_players_roles()
    for player_id, _ in players_roles:
        usernames = db.get_all_alive()
        name = f'robot{player_id}'
        if player_id < 5 and name in usernames:
            usernames.remove(name)
            vote_username = choice(usernames)
            db.vote('citizen_vote', vote_username, player_id)
            bot.send_message(
                message.chat.id, f'{name} проголосовал против {vote_username}')
            sleep(0.5)


def autoplay_mafia():
    players_roles = db.get_players_roles()
    for player_id, role in players_roles:
        usernames = db.get_all_alive()
        name = f'robot{player_id}'
        if player_id < 5 and name in usernames and role == 'mafia':
            usernames.remove(name)
            vote_username = choice(usernames)
            db.vote('mafia_vote', vote_username, player_id)
            
def get_killed(night):
    if not night:
        username_killed = db.citizens_vote()
        return f'Горожане выгнали: {username_killed}'
    username_killed = db.mafia_kill()
    return f'Мафия убила: {username_killed}'

def game_loop(message):
    global night, game
    bot.send_message(
        message.chat.id, "Добро пожаловать в игру! Вам дается 10 секунд, чтобы познакомиться")
    sleep(1)#10 сек
    while True:
        msg = get_killed(night)
        bot.send_message(message.chat.id, msg)
        if not night:
            bot.send_message(
                message.chat.id, "Город засыпает, просыпается мафия. Наступила ночь")
        else:
            bot.send_message(
                message.chat.id, "Город просыпается. Наступил день")
        winner = db.check_winner()
        if winner == 'Мафия' or winner == 'Горожане':
            game = False
            bot.send_message(
                message.chat.id, text=f'Игра окончена победили: {winner}')
            return
        db.clear(dead=True)
        night = not night
        alive = db.get_all_alive()
        alive = '\n'.join(alive)
        bot.send_message(message.chat.id, text=f'В игре:\n{alive}')
        sleep(10)
        autoplay_mafia() if night else autoplay_citizen(message)



if __name__ == "__main__":
    bot.infinity_polling()
