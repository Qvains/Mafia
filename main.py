from telebot import TeleBot
import db
from random import choice
from time import *
TOKEN = '6766627788:AAGBkSRNHBvYRdpRcE7hTp7N2mWkyFRK_NI'
bot = TeleBot(TOKEN)
game = False
night = False
@bot.message_handler(commands=['start'])
def start(message):
    print('111')
    global game
    if not game:
        bot.send_message(message.chat.id,"Если хотите начать игру напишите 'готов играть'")
@bot.message_handler(func=lambda m: m.text.lower() == "готов играть" and m.chat.type == 'private')
def ready(message):
    bot.send_message(message.chat.id,f"{message.from_user.first_name} вступил в игру")
    bot.send_message(message.from_user.id,"Вы добавлены в игру!")
    db.insert_player(message.from_user.id,message.from_user.username)
@bot.message_handler(commands=["game"])
def start_game(message):
    players_count = len(db.players_amount())
    global game
    if not game:
        if players_count < 5:
            bot.send_message(message.chat.id,"Игроков не хватает! Добавляю ботов!")
            for i in range(5 - players_count):
                db.insert_player(i+1,f"robot{i+1}")
        db.set_roles(players_count)
        players_roles = db.get_players_roles()
        mafia_players = db.get_mafia_players()
        for id,role in players_roles:
            bot.send_message(id,f"Ваша роль {role}")
            if role == 'mafia':
                bot.send_message(id,f"Список членов мафии {', '.join(mafia_players)}")
        game = True
        bot.send_message(message.chat.id,"Игра началась!")
        db.clear()
        start_game(message)
       
    bot.send_message(message.chat.id,"Игра уже начата!")
@bot.message_handler(commands=['play'])
def game_loop(msg):
    global night,game,voting
    winner = get_winner()
    while winner is None:
        bot.send_message(msg.chat.id,"У вас минута на обсуждение!")
        sleep(60)
        autoplay_citizen(msg)
        bot.send_message(msg.chat.id,"Начнем голосование!")
        sleep(20)
        bot.send_message(msg.chat.id,get_killed())
        sleep(7)
        bot.send_message(msg.chat.id,"Наступает ночь!")
        bot.send_message(msg.chat.id,"город засыпает!")
        bot.send_message(msg.chat.id,"Просыпается Мафия!")
        night = True
        autoplay_mafia()
        sleep(20)
        bot.send_message(msg.chat.id,"Наступает день!")
        bot.send_message(msg.chat.id,"город просыпается!")
        bot.send_message(msg.chat.id,get_killed())
        sleep(7)
        winner = get_winner()
    game = False
    bot.send(msg.chat.id,f"Победили {winner}")
@bot.message_handler(commands=['kick'])
def kick(msg):
    username = ''.join(msg.text.split()[1:])
    usernames = db.get_all_allive()
    if not night:
        if not username in usernames:
            bot.send_message(msg.chat.id,"Такого имени нет!")
            return
        if db.vote("citizen_vote",username,msg.from_user.id):
            bot.send_message(msg.chat.id,"Ваш голос учитан!")
            return
        bot.send_message(msg.chat.id,"У вас не прав голосовать!")
        return
    bot.send_message(msg.chat.id,"Сейчас ночь!")
@bot.message_handler(commands=['kill'])
def kill(msg):
    username = ''.join(msg.text.split()[1])
    usernames = db.get_all_allive()
    if night:
        if not username in usernames:
            bot.send_message(msg.chat.id,"Такого имени нет!")
            return
        if db.vote("mafia_vote",username,msg.from_user.id):
            bot.send_message(msg.chat.id,"Ваш голос учитан!")
            return
        bot.send_message(msg.chat.id,"У вас нет прав голосовать!")
    bot.send_message(msg.chat.id,"Сейчас день!")
def autoplay_citizen(message):
    players_roles = db.get_players_roles()
    for player_id, _ in players_roles:
        usernames = db.get_all_allive()
        name = f'robot{player_id}'
        if player_id < 5 and name in usernames:
            usernames.remove(name)
            vote_username = choice(usernames)
            db.vote('citizen_vote',vote_username,player_id)
            bot.send_message(message.chat.id,f'{name} проголосовал против {vote_username}')
def autoplay_mafia():
    players_roles = db.get_players_roles()
    for player_id, role in players_roles:
        usernames = db.get_all_allive()
        name = f'robot{player_id}'
        if player_id < 5 and name in usernames and role == 'mafia':
            usernames.remove(name)
            vote_username = choice(usernames)
            db.vote("mafia_vote",vote_username,player_id)
def get_killed():
    if not night:
        return f"Горожане выгнали {db.kill_citizen()}"
    return f'Мафия убила {db.kill_mafia()}'
def get_winner():
    return "Мафия" if len(db.citizen_players()) == len(db.mafia_players()) else "Горожане" if len(db.mafia_players()) == 0 else None
if __name__ == "__main__":
    bot.polling(non_stop=False)