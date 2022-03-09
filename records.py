import mysql.connector as db
import os

db_url = os.getenv("JAWSDB_URL")
db_url_temp = db_url.replace("mysql://", "")
db_url_temp = db_url_temp.replace("@", ":")
db_url_temp = db_url_temp.replace("3306/", "")
u, p, h, d = map(str, db_url_temp.split(":"))

conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
)

c = conn.cursor()

try:
    c.execute('''CREATE TABLE user_data (
        user_id BIGINT NOT NULL PRIMARY KEY,
        best_time INT,
        games_won INT NOT NULL,
        games_lost INT NOT NULL,
        total_games INT NOT NULL,
        win_percent DECIMAL NOT NULL,
        tot_time INT,
        avg_time INT,
        privacy VARCHAR,
        initial_supporter VARCHAR,
        win_streak INT,
        max_streak INT
        )''')
except db.errors.ProgrammingError:
    pass

def stats_update(id, win):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )

    c = conn.cursor()
    c.execute("SELECT * FROM user_data")
    all_recs = c.fetchall()
    length = len(all_recs)
    try:
        if win == 1:
            c.execute('''INSERT INTO user_data 
            (user_id, games_won, games_lost, total_games, win_percent, win_streak, max_streak) 
            VALUES ('''+str(id)+", 1, 0, 1, 100, 1, 1)")
            if length > 100:
                c.execute("UPDATE user_data SET initial_supporter = 'no' WHERE user_id = "+str(id))
        else:
            c.execute('''INSERT INTO user_data 
            (user_id, games_won, games_lost, total_games, win_percent, win_streak, max_streak) 
            VALUES ('''+str(id)+", 0, 1, 1, 0, 0, 0)")
            if length > 100:
                c.execute("UPDATE user_data SET initial_supporter = 'no' WHERE user_id = "+str(id))
        conn.commit()
    except db.errors.IntegrityError:
        c.execute("SELECT * FROM user_data WHERE user_id = "+str(id))
        record = c.fetchone()
        if win == 1:
            new_wins = record[2]+1
            new_total = record[4]+1
            new_streak = record[10]+1
            new_percent = (new_wins/new_total)*100
            c.execute("UPDATE user_data SET games_won = "+str(new_wins)+", total_games = "+str(new_total)+", win_percent = "+str(new_percent)+", win_streak = "+str(new_streak)+" WHERE user_id = "+str(id))
            if new_streak > record[11]:
                c.execute("UPDATE user_data SET max_streak = "+str(new_streak)+" WHERE user_id = "+str(id))
        else:
            new_lost = record[3]+1
            new_total = record[4]+1
            new_percent = (record[2]/new_total)*100
            c.execute("UPDATE user_data SET games_lost = "+str(new_lost)+", total_games = "+str(new_total)+", win_percent = "+str(new_percent)+", win_streak = 0 WHERE user_id = "+str(id))
        conn.commit()
    c.close()
    conn.close()

def score_check(id, time):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )

    c = conn.cursor()
    c.execute("SELECT * FROM user_data WHERE user_id = "+str(id))
    record = c.fetchone()
    if record[1] == None:
        c.execute("UPDATE user_data SET best_time = "+str(time)+", tot_time = "+str(time)+", avg_time = "+str(time)+" WHERE user_id = "+str(id))
        conn.commit()
        c.close()
        conn.close()
        return "new high"
    else:
        old_tot_time = record[6]
        new_tot_time = old_tot_time+time
        new_avg_time = int(new_tot_time/record[2])
        c.execute("UPDATE user_data SET tot_time = "+str(new_tot_time)+", avg_time = "+str(new_avg_time)+" WHERE user_id = "+str(id))
        if time < record[1]:
            c.execute("UPDATE user_data SET best_time = "+str(time)+" WHERE user_id = "+str(id))
            conn.commit()
            c.close()
            conn.close()
            return "new record"
    conn.commit()
    c.close()
    conn.close()
    return "no change"
    
    
def global_leaderboard(stat):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )

    c = conn.cursor()
    c.execute(f'''SELECT user_id, {stat} FROM user_data ORDER BY {stat}''')
    leaders = c.fetchall()
    leaders_new = list(leaders)
    for record in leaders:
        if record[1] == 0 or None:
            leaders_new.remove(record)
    c.close()
    conn.close()
    if stat == "max_streak":
        leaders_new.sort(reverse = True)
    return leaders_new[0:10]

def server_leaderboard(members, stat):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )

    c = conn.cursor()
    server_leaders = []
    for x in members:
        try:
            c.execute(f"SELECT user_id, {stat} FROM user_data WHERE user_id = "+str(x))
            server_leaders.append(c.fetchone())
        except db.errors.OperationalError:
            pass
    while True:
        try:
            server_leaders.remove(None)
        except ValueError:
            break
    server_leaders_new = list(server_leaders)
    for y in server_leaders:
        if y[1] == 0 or None:
            server_leaders_new.remove(y)
    server_leaders_new.sort(key = lambda a: a[1])
    c.close()
    conn.close()
    if stat == "max_streak":
        server_leaders_new.sort(reverse = True)
    return server_leaders_new[0:10]

def profile(id):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )

    c = conn.cursor()
    try:
        c.execute("SELECT * FROM user_data WHERE user_id = "+str(id))
        return c.fetchone()
    except db.errors.OperationalError:
        pass
    c.close()
    conn.close()

def privacy_change(id, priv):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )

    c = conn.cursor()
    try:
        c.execute("UPDATE user_data SET privacy = '"+str(priv)+"' WHERE user_id = "+str(id))
        conn.commit()
    except db.errors.OperationalError:
        pass
    c.close()
    conn.close()

def delete_record(id):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()
    try:
        c.execute("DELETE FROM user_data WHERE user_id = "+str(id))
        conn.commit()
    except db.errors.OperationalError:
        pass
    c.close()
    conn.close()

c.close()
conn.close()