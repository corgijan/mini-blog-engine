import json
import sqlite3

from config import DATAFILE
from flask import  g


def get_sqlite_db():
    if 'db' not in g and "entities" in g :
        g.db = sqlite3.connect(DATAFILE)
        g.db.row_factory = sqlite3.Row
        for table in Entities:
            g.db.execute(
                table.sql_create_table_string()
            )
    return g.db


def get_json_db():
    try:
        with open(DATAFILE) as db_file:
            db_recipes = json.load(db_file)
    except Exception:
        db_recipes = {}
    return [{"id": id, **recipe} for id, recipe in db_recipes.items()]

