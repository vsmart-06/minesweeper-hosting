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
        )''')
except db.errors.ProgrammingError:
    pass

c.execute("INSERT INTO user_data VALUES (706855396828250153, 16, 33, 46, 79, 42, 1900, 57, 'public')")