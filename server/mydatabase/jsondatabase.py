import json
import hashlib
from threading import Lock


def synchronized(func):
    def wrapper(self, *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)
    return wrapper


class JsonDatabase:
    def __init__(self, database_name):
        self.database_name = database_name
        self.db = json.load(open(database_name))
        self.lock = Lock()

    def authenticate(self, username, password):
        # Check if user exists
        return username in self.db and self.db[username] == password

    def register(self, username, password):
        # Check if user exists
        if username in self.db:
            return False

        # Hash Password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Insert user into database
        self.db[username] = hashed_password
        self.dump()
        return True

    @synchronized
    def dump(self):
        with open(self.database_name, "w") as f:
            json.dump(self.db, f)

    def close(self):
        """
        This method is not needed for json database
        :return: nothing
        """
        return self.database_name
