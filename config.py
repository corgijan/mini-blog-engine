import os

DB_DRIVER = "SQLITE"  # JSON or SQLITE
DATAFILE = "grapes.db"
PASSPHRASE = os.environ.get("RECIPE_PASSPHRASE") or "ichtrinkegernewein"
