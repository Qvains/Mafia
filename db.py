import sqlite3
from random import shuffle,choice
def insert_player(id,username):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO players (player_id,username) VALUES {id,username}")
    con.commit()
    con.close()
def mafia_players() -> list:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT username FROM players WHERE role = 'mafia'")
    data = cur.fetchall()
    con.close()
    return data
def citizen_players() -> list:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT username FROM players WHERE role != 'mafia'")
    data = [i[0] for i in cur.fetchall()]
    con.close()
    return data
def players_roles() -> list:
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    cur.execute("SELECT username,role FROM players")
    data = cur.fetchall()
    con.close()
    return data
def players_amount() -> list:
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    cur.execute("SELECT username FROM players")
    data = cur.fetchall()
    con.close()
    return data
def set_roles(count_players : int):
    game_roles = ['citizen'] * count_players
    mafia_count = int(count_players * 0.3)
    for i in range(mafia_count):
        game_roles[i] = "mafia"
    game_roles[-1] = 'sherrif'
    game_roles[-2] = "doctor"
    game_roles = shuffle(game_roles)
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    cur.execute("SELECT player_id FROM players")
    ids = cur.fetchall()
    for role,id in zip(game_roles,ids):
        cur.execute(f"UPDATE players SET role = '{role}' WHERE id = {id[0]}")
    con.commit()
    con.close()
def get_players_roles():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT player_id,role FROM players")
    data = cur.fetchall()
    con.close()
    return data
def get_mafia_players():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT username FROM players WHERE role = 'mafia'")
    data = [i[0] for i in cur.fetchall()]
    con.close()
    return data
def kill_citizen() -> tuple:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT MAX(citizen_vote) FROM players WHERE dead = 0")
    max_votes = cur.fetchone()[0]
    cur.execute(f"SELECT player_id,usernames FROM players WHERE citizen_vote = {max_votes} AND dead = 0")
    killed = cur.fetchall()
    usernames_killed = (i[1] for i in killed)
    for i in killed:
        cur.execute(f"UPDATE players SET dead = 1 WHERE player_id = {i[0]}")
    con.commit()
    con.close()
    return usernames_killed
def kill_mafia() -> str:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT MAX(mafia_vote) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute(f"SELECT player_id,username FROM players WHERE dead = 0 AND mafia_vote = {max_votes}")
    usernames_killed = choice(cur.fetchall())
    username_choice = usernames_killed[1]
    cur.execute(f"UPDATE players SET dead = 1 WHERE player_id = {usernames_killed[0]}")
    con.commit()
    con.close()
    return username_choice
def vote(type,username,player_id):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(f"SELECT voted FROM players WHERE player_id = {player_id},dead = 0,voted = 0")
    if cur.fetchone():
        cur.execute(f"UPDATE players SET voted = 1 WHERE player_id = {player_id}")
        cur.execute(f"UPDATE players SET {type} = {type} + 1 WHERE username = {username}")
        con.commit()
        con.close()
        return True
    con.close()
    return False
def clear():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("UPDATE players SET mafia_vote = 0 citizen_vote = 0 voted = 0 dead = 0")
    con.commit()
    con.close()
def get_all_allive() -> list:
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute("SELECT username FROM players WHERE dead = 0")
    data = [i[0] for i in cur.fetchall]
    con.close()
    return data