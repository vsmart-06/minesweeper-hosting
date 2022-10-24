import mysql.connector as db
import os

h = os.getenv("PLANETSCALE_HOST")
u = os.getenv("PLANETSCALE_USERNAME")
p = os.getenv("PLANETSCALE_PASSWORD")
d = os.getenv("PLANETSCALE_DATABASE")

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
        max_streak INT,
        min_moves INT,
        tot_moves INT,
        avg_moves INT,
        theme VARCHAR
        )''')

    c.execute('''CREATE TABLE bot_stats (
        id INT NOT NULL PRIMARY KEY, 
        minesweeper INT NOT NULL, 
        minesweeper_custom INT NOT NULL, 
        tournament INT NOT NULL, 
        leaderboard INT NOT NULL, 
        server_leaderboard INT NOT NULL, 
        user_profile INT NOT NULL, 
        profile_settings INT NOT NULL, 
        delete_stats INT NOT NULL, 
        theme INT NOT NULL,
        connect_four INT NOT NULL,
        othello INT NOT NULL,
        mastermind INT NOT NULL,
        yahtzee INT NOT NULL,
        battleship INT NOT NULL,
        live INT NOT NULL,
        hangman INT NOT NULL,
        uno INT NOT NULL,
        wordle INT NOT NULL,
        tzfe INT NOT NULL,
        trivia INT NOT NULL,
        flags INT NOT NULL,
        other INT NOT NULL,
        invite INT NOT NULL,
        support INT NOT NULL,
        vote INT NOT NULL,
        website INT NOT NULL,
        help INT NOT NULL
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
    c.execute("SELECT COUNT(*) FROM user_data")
    length = c.fetchone()[0]
    try:
        if win == 1:
            c.execute(f'''INSERT INTO user_data 
            (user_id, games_won, games_lost, total_games, win_percent, win_streak, max_streak, theme) 
            VALUES ({id}, 1, 0, 1, 100, 1, 1, 'dark')''')
            if length > 100:
                c.execute(f"UPDATE user_data SET initial_supporter = 'no' WHERE user_id = {id}")
        else:
            c.execute(f'''INSERT INTO user_data 
            (user_id, games_won, games_lost, total_games, win_percent, win_streak, max_streak, theme) 
            VALUES ({id}, 0, 1, 1, 0, 0, 0, 'dark')''')
            if length > 100:
                c.execute(f"UPDATE user_data SET initial_supporter = 'no' WHERE user_id = {id}")
        conn.commit()
    except db.errors.IntegrityError:
        c.execute(f"SELECT * FROM user_data WHERE user_id = {id}")
        record = c.fetchone()
        if win == 1:
            new_wins = record[2]+1
            new_total = record[4]+1
            new_streak = record[10]+1
            new_percent = (new_wins/new_total)*100
            c.execute(f"UPDATE user_data SET games_won = {new_wins}, total_games = {new_total}, win_percent = {new_percent}, win_streak = {new_streak} WHERE user_id = {id}")
            if new_streak > record[11]:
                c.execute(f"UPDATE user_data SET max_streak = {new_streak} WHERE user_id = {id}")
        else:
            new_lost = record[3]+1
            new_total = record[4]+1
            new_percent = (record[2]/new_total)*100
            c.execute(f"UPDATE user_data SET games_lost = {new_lost}, total_games = {new_total}, win_percent = {new_percent}, win_streak = 0 WHERE user_id = {id}")
        conn.commit()
    c.close()
    conn.close()

def score_check(id, time, moves):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )

    c = conn.cursor()
    c.execute(f"SELECT * FROM user_data WHERE user_id = {id}")
    record = c.fetchone()
    if record[1] == None:
        c.execute(f"UPDATE user_data SET best_time = {time}, tot_time = {time}, avg_time = {time}, min_moves = {moves}, tot_moves = {moves}, avg_moves = {moves} WHERE user_id = {id}")
        conn.commit()
        c.close()
        conn.close()
        return "new high"
    else:
        old_tot_time = record[6]
        old_tot_moves = record[13]
        new_tot_time = old_tot_time+time
        new_avg_time = int(new_tot_time/record[2])
        new_tot_moves = old_tot_moves+moves
        new_avg_moves = int(new_tot_moves/record[2])
        c.execute(f"UPDATE user_data SET tot_time = {new_tot_time}, avg_time = {new_avg_time}, tot_moves = {new_tot_moves}, avg_moves = {new_avg_moves} WHERE user_id = {id}")
        if time < record[1]:
            c.execute(f"UPDATE user_data SET best_time = {time} WHERE user_id = {id}")
            conn.commit()
            c.close()
            conn.close()
            return "new record"
        if moves < record[12] or record[12] == 0:
            c.execute(f"UPDATE user_data SET min_moves = {moves} WHERE user_id = {id}")
            conn.commit()
            c.close()
            conn.close()
            return "lesser moves"
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
        if stat == "max_streak":
            if record[1] == 0:
                leaders_new.remove(record)
        else:
            if record[1] == None:
                leaders_new.remove(record)
    c.close()
    conn.close()
    if stat == "max_streak":
        leaders_new.sort(key = lambda a: a[1], reverse = True)
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
            c.execute(f"SELECT user_id, {stat} FROM user_data WHERE user_id = {x}")
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
        if stat == "max_streak":
            if y[1] == 0:
                server_leaders_new.remove(y)
        else:
            if y[1] == None:
                server_leaders_new.remove(y)
    server_leaders_new.sort(key = lambda a: a[1])
    c.close()
    conn.close()
    if stat == "max_streak":
        server_leaders_new.sort(key = lambda a: a[1], reverse = True)
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
        c.execute(f"SELECT * FROM user_data WHERE user_id = {id}")
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
        c.execute(f"UPDATE user_data SET privacy = '{priv}' WHERE user_id = {id}")
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
        c.execute(f"DELETE FROM user_data WHERE user_id = {id}")
        conn.commit()
    except db.errors.OperationalError:
        pass
    c.close()
    conn.close()

def theme_change(id, theme):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()
    try:
        c.execute(f"UPDATE user_data SET theme = '{theme}' WHERE user_id = {id}")
        conn.commit()
    except db.errors.OperationalError:
        pass
    c.close()
    conn.close()

def get_theme(id):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()
    try:
        c.execute(f"SELECT theme FROM user_data WHERE user_id = {id}")
        theme = c.fetchone()[0]
    except TypeError:
        theme = "dark"
    c.close()
    conn.close()
    return theme

def member_count():
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM user_data")
    count = c.fetchone()[0]
    c.close()
    conn.close()
    return count

def change_stats(column):
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()
    c.execute("SELECT * FROM bot_stats WHERE id = 1")
    stats = c.fetchone()
    columns = ["id", "minesweeper", "minesweeper_custom", "tournament", "leaderboard", "server_leaderboard", "user_profile", "profile_settings", "delete_stats", "theme", "connect_four","othello", "mastermind", "yahtzee", "battleship", "live", "hangman", "uno" ,"wordle", "tzfe", "trivia", "flags", "other", "invite", "support", "vote", "website", "help"]
    ind = columns.index(column)
    new_value = stats[ind] + 1
    c.execute(f"UPDATE bot_stats SET {column} = {new_value} WHERE id = 1")
    conn.commit()
    c.close()
    conn.close()

def get_stats():
    conn = db.connect(
    host = h,
    user = u,
    password = p,
    database = d
    )
    c = conn.cursor()
    c.execute("SELECT * FROM bot_stats WHERE id = 1")
    stats = c.fetchone()
    columns = ["id", "minesweeper", "minesweeper_custom", "tournament", "leaderboard", "server_leaderboard", "user_profile", "profile_settings", "delete_stats", "theme", "connect_four","othello", "mastermind", "yahtzee", "battleship", "live", "hangman", "uno" ,"wordle", "tzfe", "trivia", "flags", "other", "invite", "support", "vote", "website", "help"]
    data = {}
    for x in range(1, len(columns)):
        data[columns[x]] = stats[x]
    return data

c.close()
conn.close()