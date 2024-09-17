from config import *
from dbstuff import get_sqlite_db, get_json_db


class EntityDefinition():
    def __init__(self ):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError
    def from_dict(dict):
        raise NotImplementedError
    @staticmethod
    def sql_create_table_string():
        raise NotImplementedError
    @staticmethod
    def all():
        raise NotImplementedError
    def save(self):
        raise NotImplementedError
    def delete(self):
        raise NotImplementedError

class Grape(EntityDefinition):
    def __init__(self, id, title, grape_info, taste_info, tags, cvss):
        self.id = id
        self.title = title
        self.grape_info = grape_info
        self.taste_info = taste_info
        self.tags = tags
        self.cvss = cvss

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "grape_info": self.grape_info,
            "taste_info": self.taste_info,
            "tags": self.tags,
            "cvss": self.cvss
        }

    @staticmethod
    def from_dict(dict):
        return Entity(dict["id"], dict["title"], dict["grape_info"], dict["taste_info"], dict["tags"], dict["cvss"])

    def save(self):
        if DB_DRIVER == "JSON":
            with open(DATAFILE, 'r+') as db_file:
                try:
                    recipes = json.load(db_file)
                except Exception:
                    recipes = {}
                recipes[self.id] = self.to_dict()
                db_file.seek(0)
                db_file.truncate()
                json.dump(recipes, db_file, indent=4)
        elif DB_DRIVER == "SQLITE":
            conn = get_sqlite_db()
            conn.cursor().execute("INSERT OR REPLACE INTO grapes VALUES (?, ?, ?, ?, ?, ?)",
                                  (self.id, self.title, self.grape_info, self
                                   .taste_info, self.tags, self.cvss))
            conn.commit()
        else:
            raise Error("Unknown DB_DRIVER")

    def delete(self):
        if DB_DRIVER == "JSON":
            with open(DATAFILE, 'r+') as db_file:
                try:
                    recipes = json.load(db_file)
                except Exception:
                    recipes = {}
                if self.id in recipes:
                    del recipes[self.id]
                    db_file.seek(0)
                    db_file.truncate()
                    json.dump(recipes, db_file, indent=4)
        elif DB_DRIVER == "SQLITE":
            conn = get_sqlite_db()
            conn.cursor().execute("DELETE FROM grapes WHERE id = ?", (self.id,))
            conn.commit()
        else:
            raise Error("Unknown DB_DRIVER")


    @staticmethod
    def all():
        if DB_DRIVER == "JSON":
            return get_json_db()
        elif DB_DRIVER == "SQLITE":
            conn = get_sqlite_db()
            return conn.cursor().execute("SELECT * FROM grapes").fetchall()
        else:
            raise Error("Unknown DB_DRIVER")

    @staticmethod
    def sql_create_table_string():
        return "CREATE TABLE IF NOT EXISTS grapes (id text PRIMARY KEY, title text NOT NULL, grape_info text, taste_info text, tags text, cvss real)"

    @staticmethod
    def find(id):
        if DB_DRIVER == "JSON":
            recipes = get_json_db()
            for recipe in recipes:
                if recipe["id"] == id:
                    return recipe
            return None
        elif DB_DRIVER == "SQLITE":
            conn = get_sqlite_db()
            return conn.cursor().execute("SELECT * FROM grapes WHERE id = ?", (id,)).fetchone()
        else:
            raise Error("Unknown DB_DRIVER")

