from wave import Error

from flask import Flask, redirect, make_response, request, session, g, url_for
import jinja2, uuid, os, sqlite3, json
from templates import *

app = Flask(__name__)
app.secret_key = os.urandom(64)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

DB_DRIVER = "SQLITE"  # JSON or SQLITE
DATAFILE = "grapes.db"
PASSPHRASE = os.environ.get("RECIPE_PASSPHRASE") or "ichtrinkegernewein"

PASS_ERROR = "Wrong Passphrase!  Please enter the correct one !"

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

class Regions(EntityDefinition):
    def __init__(self, id, title, region_info, taste_info, tags, cvss):
        self.id = id
        self.title = title
        self.region_info = region_info
        self.taste_info = taste_info
        self.tags = tags
        self.cvss = cvss

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "region_info": self.region_info,
            "taste_info": self.taste_info,
            "tags": self.tags,
            "cvss": self.cvss
        }

    @staticmethod
    def from_dict(dict):
        return Entity(dict["id"], dict["title"], dict["region_info"], dict["taste_info"], dict["tags"], dict["cvss"])

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
            conn.cursor().execute("INSERT OR REPLACE INTO regions VALUES (?, ?, ?, ?, ?, ?)",
                                  (self.id, self.title, self.region_info, self
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
            conn.cursor().execute("DELETE FROM regions WHERE id = ?", (self.id,))
            conn.commit()
        else:
            raise Error("Unknown DB_DRIVER")

    def all():
        if DB_DRIVER == "JSON":
            return get_json_db()
        elif DB_DRIVER == "SQLITE":
            conn = get_sqlite_db()
            return conn.cursor().execute("SELECT * FROM regions").fetchall()
        else:
            raise Error("Unknown DB_DRIVER")

    def sql_create_table_string():
        return "CREATE TABLE IF NOT EXISTS regions (id text PRIMARY KEY, title text NOT NULL, region_info text, taste_info text, tags text, cvss real)"

    def find(id):
        if DB_DRIVER == "JSON":
            recipes = get_json_db()
            for recipe in recipes:
                if recipe["id"] == id:
                    return recipe
            return None
        elif DB_DRIVER == "SQLITE":
            conn = get_sqlite_db()
            return conn.cursor().execute("SELECT * FROM regions WHERE id = ?", (id,)).fetchone()
        else:
            raise Error("Unknown DB_DRIVER")



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

class Wine(EntityDefinition):
    def __init__(self, id, title, wine_info, taste_info, tags, cvss):
        self.id = id
        self.title = title
        self.wine_info = wine_info
        self.taste_info = taste_info
        self.tags = tags
        self.cvss = cvss

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "wine_info": self.wine_info,
            "taste_info": self.taste_info,
            "tags": self.tags,
            "cvss": self.cvss
        }

    @staticmethod
    def from_dict(dict):
        return Entity(dict["id"], dict["title"], dict["wine_info"], dict["taste_info"], dict["tags"], dict["cvss"])

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
            conn.cursor().execute("INSERT OR REPLACE INTO wines VALUES (?, ?, ?, ?, ?, ?)",
                                  (self.id, self.title, self.wine_info, self
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
            conn.cursor().execute("DELETE FROM wines WHERE id = ?", (self.id,))
            conn.commit()
        else:
            raise Error("Unknown DB_DRIVER")

    @staticmethod
    def all():
        if DB_DRIVER == "JSON":
            return get_json_db()
        elif DB_DRIVER == "SQLITE":
            conn = get_sqlite_db()
            return conn.cursor().execute("SELECT * FROM wines").fetchall()

    @staticmethod
    def sql_create_table_string():
        return "CREATE TABLE IF NOT EXISTS wines (id text PRIMARY KEY, title text NOT NULL, wine_info text, taste_info text, tags text, cvss real)"



Entities = [
    Grape,
    Regions,
    Wine

]

def page(name):
    return header + name + footer


def get_sqlite_db():
    if 'db' not in g:
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


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None: db.close()


@app.route("/", methods=["GET", "POST"])
def main():
    return page("Hello at Rebenberg,<br> your grape variety index!")


@app.route("/edit_grapes/<id>")
def rezepte_edit(id):
    if id != "new":
        recipe = Grape.find(id)
        if recipe is None: return page("nicht gefunden :(")
    else:
        recipe = dict(title="", tags="", taste_info="", grape_info="", id="")
    template = jinja2.Environment().from_string(page(edit_page))
    return make_response(template.render(r=recipe, authenticated=('authenticated' in session),
                                         img_url=url_for('static', filename=recipe['id']),
                                         has_image=os.path.isfile(os.path.join('static', recipe['id']))))

@app.route("/grapes", methods=["GET", "POST"])
def add_grape():
    if request.method == "POST":
        if request.form["pass"] == PASSPHRASE or 'authenticated' in session:
            session['authenticated'] = True
            if request.form["title"] == "": return page("Bitte wenigstens einen Titel eingeben")
            if request.form["del-title"] != "" and request.form["del-title"] != request.form["title"]: return page(
                "Title not correct, deleting")
            id = request.form["id"] if request.form.get("id", "") != "" else uuid.uuid4().__str__()
            if 'image' in request.files and request.files['image'].mimetype in {'image/webp', 'image/jpeg',
                                                                                'image/png'}:
                if not os.path.exists('static'): os.makedirs('static')
                request.files['image'].save(os.path.join('static', id))
            if DB_DRIVER == "JSON":
                with open(DATAFILE, 'r+') as db_file:
                    try:
                        recipes = json.load(db_file)
                    except Exception:
                        recipes = {}
                    if request.form["del-title"] != "":
                        if id in recipes: del recipes[id]
                        if os.path.isfile(os.path.join('static', id)): os.remove(os.path.join('static', id))
                    else:
                        recipes[id] = dict(title=request.form["title"][0:3000],
                                           grape_info=request.form["grape_info"][0:3000],
                                           taste_info=request.form["taste_info"][0:3000], tags=request.form["tags"][0:3000],
                                           cvss=0.0)
                    db_file.seek(0)
                    db_file.truncate()
                    json.dump(recipes, db_file, indent=4)
            elif DB_DRIVER == "SQLITE":
                conn = get_sqlite_db()
                if request.form["del-title"] != "":
                    name_table = "grapes"
                    conn.cursor().execute(f"DELETE FROM {name_table} WHERE id = ?", (id,))
                    if os.path.isfile(os.path.join('static', id)): os.remove(os.path.join('static', id))
                else:
                    name_table = "grapes"
                    conn.cursor().execute(f"INSERT OR REPLACE INTO {name_table} VALUES (?, ?, ?, ?, ?, ?)", (
                        id, request.form["title"][0:3000], request.form["grape_info"][0:3000],
                        request.form["taste_info"][0:3000], request.form["tags"][0:3000], request.form.get('cvss', 0.0)))
                conn.commit()
            template = jinja2.Environment().from_string(page(edit_page))
            if request.form["del-title"] == request.form["title"]: return make_response(redirect("/"))
            return make_response(redirect("/grapes/" + id))
        else:
            return page(PASS_ERROR)
    if DB_DRIVER == "JSON":
        recipes = get_json_db()
    elif DB_DRIVER == "SQLITE":
        recipe_rows = Grape.all()
        recipes = [dict(row) for row in recipe_rows]
    template = jinja2.Environment().from_string(page(main_page))
    return template.render(recipes=recipes, recipes_count=len(recipes), title="Grapes")


@app.route("/grapes/<id>")
def rezepte_show(id):
        recipe = Grape.find(id)
        if recipe is None: return page("nicht gefunden :(")
        template = jinja2.Environment().from_string(page(recipe_page))
        return template.render(r=recipe, img_url=url_for('static', filename=recipe['id']),
                               has_image=os.path.isfile(os.path.join('static', recipe['id'])),title="Grapes")

@app.route("/regions", methods=["GET", "POST"])
def regions():
    if request.method == "POST":
        if request.form["pass"] == PASSPHRASE or 'authenticated' in session:
            session['authenticated'] = True
            if request.form["title"] == "": return page("Bitte wenigstens einen Titel eingeben")
            if request.form["del-title"] != "" and request.form["del-title"] != request.form["title"]: return page(
                "Title not correct, deleting")
            id = request.form["id"] if request.form.get("id", "") != "" else uuid.uuid4().__str__()
            if 'image' in request.files and request.files['image'].mimetype in {'image/webp', 'image/jpeg',
                                                                                'image/png'}:
                if not os.path.exists('static'): os.makedirs('static')
                request.files['image'].save(os.path.join('static', id))
            if DB_DRIVER == "JSON":
                with open(DATAFILE, 'r+') as db_file:
                    try:
                        recipes = json.load(db_file)
                    except Exception:
                        recipes = {}
                    if request.form["del-title"] != "":
                        if id in recipes: del recipes[id]
                        if os.path.isfile(os.path.join('static', id)): os.remove(os.path.join('static', id))
                    else:
                        recipes[id] = dict(title=request.form["title"][0:3000],
                                           region_info=request.form["region_info"][0:3000],
                                           taste_info=request.form["taste_info"][0:3000], tags=request.form["tags"][0:3000],
                                           cvss=0.0)
                    db_file.seek(0)
                    db_file.truncate()
                    json.dump(recipes, db_file, indent=4)
            elif DB_DRIVER == "SQLITE":
                conn = get_sqlite_db()
                if request.form["del-title"] != "":
                    name_table = "regions"
                    conn.cursor().execute(f"DELETE FROM {name_table} WHERE id = ?", (id,))
                    if os.path.isfile(os.path.join('static', id)): os.remove(os.path.join('static', id))
                else:
                    name_table = "regions"
                    conn.cursor().execute(f"INSERT OR REPLACE INTO {name_table} VALUES (?, ?, ?, ?, ?, ?)", (
                        id, request.form["title"][0:3000], request.form["region_info"][0:3000],
                        request.form["taste_info"][0:3000], request.form["tags"][0:3000], request.form.get('cvss', 0.0)))
                conn.commit()
            template = jinja2.Environment().from_string(page(edit_page))
            if request.form["del-title"] == request.form["title"]: return make_response(redirect("/"))
            return make_response(redirect("/regions/" + id))
        else:
            return page(PASS_ERROR)
    if DB_DRIVER == "JSON":
        recipes = get_json_db()
    elif DB_DRIVER == "SQLITE":
        recipe_rows = Regions.all()
        recipes = [dict(row) for row in recipe_rows]
    template = jinja2.Environment().from_string(page(main_page))
    return template.render(recipes=recipes, recipes_count=len(recipes), title="Regions")

@app.route("/regions/<id>")
def regions_show(id):
    recipe = Regions.find(id)
    if recipe is None: return page("nicht gefunden :(")
    template = jinja2.Environment().from_string(page(recipe_page))
    return template.render(r=recipe, img_url=url_for('static', filename=recipe['id']),
                           has_image=os.path.isfile(os.path.join('static', recipe['id'])),title="Regions")
@app.route("/edit_regions/<id>")
def regions_edit(id):
    if id != "new":
        recipe = Regions.find(id)
        if recipe is None: return page("Nicht gefunden :(")
    else:
        recipe = dict(title="", tags="", taste_info="", region_info="", id="")
    template = jinja2.Environment().from_string(page(edit_page_region))
    return make_response(template.render(r=recipe, authenticated=('authenticated' in session),
                                         img_url=url_for('static', filename=recipe['id']),
                                         has_image=os.path.isfile(os.path.join('static', recipe['id']))
                                         ,title="Regions"))


@app.route("/wines")
def wines():
    if DB_DRIVER == "JSON":
        recipes = get_json_db()
    elif DB_DRIVER == "SQLITE":
        recipe_rows = Wine.all()
        recipes = [dict(row) for row in recipe_rows]
    template = jinja2.Environment().from_string(page(main_page))
    return template.render(recipes=recipes, recipes_count=len(recipes),title="Wines")
