from tinydb import TinyDB, Query
import os
import config

class DatabaseClient:
    _instance = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseClient, cls).__new__(cls)
            # Use path from config
            cls._db = TinyDB(config.DB_PATH)
        return cls._instance

    @property
    def db(self):
        return self._db

    def get_table(self, table_name: str):
        return self._db.table(table_name)

    def close(self):
        if self._db:
            self._db.close()
