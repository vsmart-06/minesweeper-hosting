import psycopg as db
import os
db_url = os.getenv("DATABASE_URL")
conn = db.connect(db_url)
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
        privacy VARCHAR
        );''')
except db.errors.ProgrammingError:
    pass

c.execute("INSERT INTO user_data VALUES (706855396828250153, 16, 33, 46, 79, 42, 1900, 57, 'public');")
c.execute("INSERT INTO user_data VALUES (182729649703485440, NULL, 0, 1, 1, 0, NULL, NULL, 'public');")
c.execute("INSERT INTO user_data VALUES (223150756335845377, NULL, 0, 2, 2, 0, NULL, NULL, 'public');")
c.execute("INSERT INTO user_data VALUES (536955497300099073, NULL, 0, 1, 1, 0, NULL, NULL, 'public');")
c.execute("INSERT INTO user_data VALUES (603169885069115412, NULL, 0, 1, 1, 0, NULL, NULL, 'public');")
c.execute("INSERT INTO user_data VALUES (765081950317838376, 92, 3, 5, 8, 38, 411, 137, 'private');")
c.execute("INSERT INTO user_data VALUES (780779734140715048, NULL, 0, 1, 1, 0, NULL, NULL, 'public');")
c.execute("INSERT INTO user_data VALUES (835048216780734485, NULL, 0, 1, 1, 0, NULL, NULL, 'public');")
c.execute("INSERT INTO user_data VALUES (835838741011628033, 259, 3, 4, 7, 43, 1064, 354, 'public');")
c.execute("INSERT INTO user_data VALUES (836563003105214515, 68, 5, 20, 25, 20, 674, 134, 'public');")
c.execute("INSERT INTO user_data VALUES (842009008986652703, 173, 2, 4, 6, 33, 406, 203, 'public');")
c.execute("INSERT INTO user_data VALUES (846409513295937607, NULL, 0, 1, 1, 0, NULL, NULL, 'public');")
conn.commit()

def stats_update(id, win):
    try:
        if win == 1:
            c.execute('''INSERT INTO user_data 
            (user_id, games_won, games_lost, total_games, win_percent) 
            VALUES ('''+str(id)+", 1, 0, 1, 100);")
        else:
            c.execute('''INSERT INTO user_data 
            (user_id, games_won, games_lost, total_games, win_percent) 
            VALUES ('''+str(id)+", 0, 1, 1, 0);")
        conn.commit()
    except db.errors.IntegrityError:
        c.execute("SELECT * FROM user_data WHERE user_id = "+str(id)+";")
        record = c.fetchone()
        if win == 1:
            new_wins = record[2]+1
            new_total = record[4]+1
            new_percent = (new_wins/new_total)*100
            c.execute("UPDATE user_data SET games_won = "+str(new_wins)+", total_games = "+str(new_total)+", win_percent = "+str(new_percent)+" WHERE user_id = "+str(id)+";")
        else:
            new_lost = record[3]+1
            new_total = record[4]+1
            new_percent = (record[2]/new_total)*100
            c.execute("UPDATE user_data SET games_lost = "+str(new_lost)+", total_games = "+str(new_total)+", win_percent = "+str(new_percent)+" WHERE user_id = "+str(id)+";")
        conn.commit()

def score_check(id, time):
    c.execute("SELECT * FROM user_data WHERE user_id = "+str(id)+";")
    record = c.fetchone()
    if record[1] == None:
        c.execute("UPDATE user_data SET best_time = "+str(time)+", tot_time = "+str(time)+", avg_time = "+str(time)+" WHERE user_id = "+str(id)+";")
        conn.commit()
        return "new high"
    else:
        old_tot_time = record[6]
        new_tot_time = old_tot_time+time
        new_avg_time = int(new_tot_time/record[2])
        c.execute("UPDATE user_data SET tot_time = "+str(new_tot_time)+", avg_time = "+str(new_avg_time)+" WHERE user_id = "+str(id)+";")
        if time < record[1]:
            c.execute("UPDATE user_data SET best_time = "+str(time)+" WHERE user_id = "+str(id)+";")
            conn.commit()
            return "new record"
    conn.commit()
    return "no change"
    
    
def global_leaderboard():
    c.execute('''
                SELECT user_id, best_time
                FROM user_data
                ORDER BY best_time;''')
    leaders = c.fetchmany(10)
    return leaders

def server_leaderboard(members):
    server_leaders = []
    for x in members:
        try:
            c.execute("SELECT user_id, best_time FROM user_data WHERE user_id = "+str(x)+";")
            server_leaders.append(c.fetchone())
        except db.errors.OperationalError:
            pass
    while True:
        try:
            server_leaders.remove(None)
        except ValueError:
            break
    server_leaders.sort(key = lambda a: a[1])
    return server_leaders[0:10]

def profile(id):
    try:
        c.execute("SELECT * FROM user_data WHERE user_id = "+str(id)+";")
        return c.fetchone()
    except db.errors.OperationalError:
        pass

def privacy_change(id, p):
    try:
        c.execute("UPDATE user_data SET privacy = '"+str(p)+"' WHERE user_id = "+str(id)+";")
        conn.commit()
    except db.errors.OperationalError:
        pass