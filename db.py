import sqlite3
import random




def insert_player(player_id, username):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"INSERT INTO players (player_id, username) VALUES ('{player_id}', '{username}')"
    cur.execute(sql)
    con.commit()
    con.close()




def players_amount():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"SELECT * FROM players"
    cur.execute(sql)
    res = cur.fetchall()
    con.close()
    return len(res)

def get_sherif_username():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"SELECT username FROM PLAYERS where role = 'sherif' "
    cur.execute(sql)
    data = cur.fetchall()
    return data


def get_mafia_usernames():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"SELECT username FROM PLAYERS where role = 'mafia' "
    cur.execute(sql)
    data = cur.fetchall()
    names = ''
    for row in data:
        name = row[0]
        names += name + '\n'
    con.close()
    return names




def get_players_roles():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"SELECT player_id, role FROM players"
    cur.execute(sql)
    data = cur.fetchall()
    con.close()
    return data




def get_all_alive():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"SELECT username from players WHERE dead = 0"
    cur.execute(sql)
    data = cur.fetchall()
    data = [row[0] for row in data]
    con.close()
    return data




def set_roles(players):
    game_roles = ['citizen'] * players
    mafias = int(players * 0.3)
    sherif = int(players * 0.1)
    for i in range(mafias):
        game_roles[i] = 'mafia'
    for i in range(sherif):
        game_roles[i] = 'sherif'
    random.shuffle(game_roles)
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(f"SELECT player_id FROM PLAYERS")
    player_ids_rows = cur.fetchall()
    for role, row in zip(game_roles, player_ids_rows):
        sql = f"UPDATE players SET role = '{role}' WHERE player_id = {row[0]}"
        cur.execute(sql)
    con.commit()
    con.close()

def vote(type,username,player_id):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(f"SELECT username from players WHERE player_id = {player_id} and dead = 0 and voted = 0")
    can_vote = cur.fetchall()
    if can_vote:
        cur.execute(f'UPDATE players SET {type} = {type} + 1 WHERE username = "{username}"')
        cur.execute(f'UPDATE players SET voted = 1 WHERE player_id = "{player_id}"')
        con.commit()
        con.close()
        return True
    con.close()
    return False

def mafia_kill():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(f"SELECT MAX(mafia_vote) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM players WHERE dead = 0 and role = 'mafia'")
    mafia_alive = cur.fetchone()[0]
    username_killed = 'никого'
    if max_votes == mafia_alive:
        cur.execute(f"SELECT username FROM players WHERE mafia_vote = {max_votes}")
        username_killed = cur.fetchone()[0]
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}'")
        con.commit()
    con.close()
    return username_killed

def sherif_vote(username):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(f"SELECT username WHERE dead = 0 and role = sherif")
    voted = cur.fetchone()
    if voted:
        cur.execute(f"UPDATE players SET sherif_vote = 1 WHERE role = sherif")
        cur.execute(f"SELECT username, role FROM players WHERE username = {username}")
        show_username = cur.fetchone()
        con.commit()
    con.close()
    return show_username


def citizens_vote():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(f"SELECT MAX(citizen_vote) FROM players")
    max_votes = cur.fetchone()[0]
    cur.execute(f"SELECT COUNT(*) FROM players WHERE citizen_vote = {max_votes}")
    max_votes_count = cur.fetchone()[0]
    username_killed = 'никого'
    if max_votes_count == 1:
        cur.execute(f"SELECT username FROM players WHERE citizen_vote = {max_votes}")
        username_killed = cur.fetchone()[0]
        cur.execute(f"UPDATE players SET dead = 1 WHERE username = '{username_killed}'")
        con.commit()
    con.close()
    return username_killed

def check_winner():
    con = sqlite3.connect("db.db")
    cur = con.cursor()    
    all_alive = players_amount()
    sql = f"SELECT * FROM players WHERE role = 'mafia'"
    cur.execute(sql)
    res = cur.fetchall()
    data = len(res)
    
    mafia_won = 'Мафия'
    citizens_won = 'Горожане'
    if data >= all_alive:
        return mafia_won
    elif data == 0:
        return citizens_won
    con.commit()
    con.close() 


def clear(dead = False):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"UPDATE players SET citizen_vote = 0, mafia_vote = 0, voted = 0"
    if dead:
        sql += ', dead = 0'
    cur.execute(sql)
    con.commit()
    con.close()

def show_role(username):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    sql = f"SELECT role FROM players WHERE username = {username} "
    cur.execute(sql)
    data1 = cur.fetchall()
    con.close()
    return data1