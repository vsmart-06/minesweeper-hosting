import sqlite3

def stats_update(id, win):
    conn = sqlite3.connect("records.db")
    c = conn.cursor()

    try:
        c.execute('''
        CREATE TABLE high_scores (
            user_id integer NOT NULL PRIMARY KEY,
            best_time integer,
            games_won integer NOT NULL,
            games_lost integer NOT NULL,
            total_games integer NOT NULL,
            win_percent integer NOT NULL,
            tot_time integer,
            avg_time integer
        )''')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    try:
        if win == 1:
            c.execute("INSERT INTO high_scores VALUES ("+str(id)+", NULL, 1, 0, 1, 100, NULL, NULL)")
        else:
            c.execute("INSERT INTO high_scores VALUES ("+str(id)+", NULL, 0, 1, 1, 0, NULL, NULL)")
        conn.commit()
    except sqlite3.IntegrityError:
        c.execute("SELECT * FROM high_scores WHERE user_id = "+str(id))
        record = c.fetchone()
        if win == 1:
            new_wins = record[2]+1
            new_total = record[4]+1
            new_percent = (new_wins/new_total)*100
            c.execute("UPDATE high_scores SET games_won = "+str(new_wins)+", total_games = "+str(new_total)+", win_percent = "+str(new_percent)+" WHERE user_id = "+str(id))
        else:
            new_lost = record[3]+1
            new_total = record[4]+1
            new_percent = (record[2]/new_total)*100
            c.execute("UPDATE high_scores SET games_lost = "+str(new_lost)+", total_games = "+str(new_total)+", win_percent = "+str(new_percent)+" WHERE user_id = "+str(id))
        conn.commit()
    

def score_check(id, time):
    conn = sqlite3.connect("records.db")
    c = conn.cursor()

    try:
        c.execute('''
        CREATE TABLE high_scores (
            user_id integer NOT NULL PRIMARY KEY,
            best_time integer,
            games_won integer NOT NULL,
            games_lost integer NOT NULL,
            total_games integer NOT NULL,
            win_percent integer NOT NULL,
            tot_time integer,
            avg_time integer
        )''')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    c.execute("SELECT * FROM high_scores WHERE user_id = "+str(id))
    record = c.fetchone()
    if record[1] == None:
        c.execute("UPDATE high_scores SET best_time = "+str(time)+", tot_time = "+str(time)+", avg_time = "+str(time)+" WHERE user_id = "+str(id))
        conn.commit()
        
        return "new high"
    else:
        old_tot_time = record[6]
        new_tot_time = old_tot_time+time
        new_avg_time = int(new_tot_time/record[2])
        c.execute("UPDATE high_scores SET tot_time = "+str(new_tot_time)+", avg_time = "+str(new_avg_time)+" WHERE user_id = "+str(id))
        if time < record[1]:
            c.execute("UPDATE high_scores SET best_time = "+str(time)+" WHERE user_id = "+str(id))
            conn.commit()
            
            return "new record"
    conn.commit()
    
    return "no change"
    
    
def global_leaderboard():
    conn = sqlite3.connect("records.db")
    c = conn.cursor()

    try:
        c.execute('''
        CREATE TABLE high_scores (
            user_id integer NOT NULL PRIMARY KEY,
            best_time integer,
            games_won integer NOT NULL,
            games_lost integer NOT NULL,
            total_games integer NOT NULL,
            win_percent integer NOT NULL,
            tot_time integer,
            avg_time integer
        )''')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    c.execute('''
                SELECT user_id, best_time
                FROM high_scores
                ORDER BY best_time''')
    leaders = c.fetchmany(10)
    conn.commit()
    
    return leaders

def server_leaderboard(members):
    conn = sqlite3.connect("records.db")
    c = conn.cursor()

    try:
        c.execute('''
        CREATE TABLE high_scores (
            user_id integer NOT NULL PRIMARY KEY,
            best_time integer,
            games_won integer NOT NULL,
            games_lost integer NOT NULL,
            total_games integer NOT NULL,
            win_percent integer NOT NULL,
            tot_time integer,
            avg_time integer
        )''')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    server_leaders = []
    for x in members:
        try:
            c.execute("SELECT user_id, best_time FROM high_scores WHERE user_id = "+str(x))
            server_leaders.append(c.fetchone())
        except sqlite3.OperationalError:
            pass
    while True:
        try:
            server_leaders.remove(None)
        except ValueError:
            break
    server_leaders.sort(key = lambda a: a[1])
    conn.commit()
    
    return server_leaders[0:10]

def profile(id):
    conn = sqlite3.connect("records.db")
    c = conn.cursor()

    try:
        c.execute('''
        CREATE TABLE high_scores (
            user_id integer NOT NULL PRIMARY KEY,
            best_time integer,
            games_won integer NOT NULL,
            games_lost integer NOT NULL,
            total_games integer NOT NULL,
            win_percent integer NOT NULL,
            tot_time integer,
            avg_time integer
        )''')
        conn.commit()
    except sqlite3.OperationalError:
        pass
    try:
        c.execute("SELECT * FROM high_scores WHERE user_id = "+str(id))
        conn.commit()
        
        return c.fetchone()
    except sqlite3.OperationalError:
        pass