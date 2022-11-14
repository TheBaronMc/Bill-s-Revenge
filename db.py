import sqlite3

class Connector:
    def __init__(self) -> None:
        self.con = sqlite3.connect('game.db')
        print('> Connected to database successfully')

        try:
            self.con.execute('SELECT * FROM stats')
        except:
            print('> Ceating table to store scores')
            self.con.execute('CREATE TABLE stats ( date TEXT, score TEXT, nb_ennmies TEXT, gameover TEXT, aggressive TEXT, time TEXT )')
            self.con.commit()

    def add(self, date: str, score: int, nb_ennmies: int, gameover: bool, aggressive: bool, time: float):
        query = f"INSERT INTO stats VALUES ( \"{date}\", {score}, {nb_ennmies}, {gameover}, {aggressive}, {time} )"
        self.con.execute(query)
        self.con.commit()

    def get_stats(self):
        return self.con.execute('SELECT * FROM stats').fetchall()
            

    