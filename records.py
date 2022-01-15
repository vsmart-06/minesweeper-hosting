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
try:
    c.execute("INSERT INTO user_data VALUES (706855396828250153, 16, 33, 46, 79, 42, 1900, 57, 'public')")
except db.errors.IntegrityError:
    pass
c.execute("INSERT INTO user_data VALUES (182729649703485440, NULL, 0, 1, 1, 0, NULL, NULL, 'public')")
c.execute("INSERT INTO user_data VALUES (223150756335845377, NULL, 0, 2, 2, 0, NULL, NULL, 'public')")
c.execute("INSERT INTO user_data VALUES (536955497300099073, NULL, 0, 1, 1, 0, NULL, NULL, 'public')")
c.execute("INSERT INTO user_data VALUES (603169885069115412, NULL, 0, 1, 1, 0, NULL, NULL, 'public')")
c.execute("INSERT INTO user_data VALUES (765081950317838376, 92, 3, 5, 8, 38, 411, 137, 'private')")
c.execute("INSERT INTO user_data VALUES (780779734140715048, NULL, 0, 1, 1, 0, NULL, NULL, 'public')")
c.execute("INSERT INTO user_data VALUES (835048216780734485, NULL, 0, 1, 1, 0, NULL, NULL, 'public')")
c.execute("INSERT INTO user_data VALUES (835838741011628033, 259, 3, 4, 7, 43, 1064, 354, 'public')")
c.execute("INSERT INTO user_data VALUES (836563003105214515, 68, 5, 20, 25, 20, 674, 134, 'public')")
c.execute("INSERT INTO user_data VALUES (842009008986652703, 173, 2, 4, 6, 33, 406, 203, 'public')")
c.execute("INSERT INTO user_data VALUES (846409513295937607, NULL, 0, 1, 1, 0, NULL, NULL, 'public')")