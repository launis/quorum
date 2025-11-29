from tinydb import TinyDB, Query
from tinydb.storages import Storage
import json
import os
import config

class UTF8JSONStorage(Storage):
    def __init__(self, path):
        self.path = path

    def read(self):
        if not os.path.exists(self.path):
            return None
        with open(self.path, 'r', encoding='utf-8') as handle:
            try:
                return json.load(handle)
            except json.JSONDecodeError:
                return None

    def write(self, data):
        with open(self.path, 'w', encoding='utf-8') as handle:
            json.dump(data, handle, indent=4, ensure_ascii=False)

    def close(self):
        pass

class DatabaseClient:
    _instance = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseClient, cls).__new__(cls)
            # Use path from config
            cls._db = TinyDB(config.DB_PATH, storage=UTF8JSONStorage)
        return cls._instance

    @property
    def db(self):
        return self._db

    def get_table(self, table_name: str):
        return self._db.table(table_name)

    def close(self):
        if self._db:
            self._db.close()
