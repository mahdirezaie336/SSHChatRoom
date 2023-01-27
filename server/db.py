import sqlite3
import datetime


class Database:
    def __init__(self):
        self.connection = sqlite3.connect("msgs.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS messages(date TEXT PRIMARY KEY, receiver TEXT, sender TEXT, msg TEXT, status TEXT)")
        self.connection.commit()
    
    def insert(self, sender: str, receiver: str, msg: str, status: bool):
        self.cursor.execute(f"INSERT INTO messages VALUES('{datetime.datetime.now()}', '{sender}', '{receiver}', '{msg}', '{str(status)}')")
        self.connection.commit()