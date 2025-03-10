from flask import Flask, redirect, make_response, request, session, g, url_for, render_template, send_from_directory
import jinja2, uuid, os, sqlite3, json
import os

app = Flask(__name__)
app.secret_key = os.urandom(64)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

DB_DRIVER = os.environ.get("DRIVER") or "JSON"  # JSON or SQLITE
DATAFILE = os.environ.get("DATA_PATH") or "data/data.json"
PASSPHRASE = os.environ.get("RECIPE_PASSPHRASE") or "ichessegernekuchen"


def page(name):
    return header + name + footer


def get_sqlite_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATAFILE)
        g.db.row_factory = sqlite3.Row
        g.db.execute(
            "CREATE TABLE IF NOT EXISTS recipes (id text PRIMARY KEY, title text NOT NULL, ingredients text, prep text, tags text, cvss real)")
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
    if request.method == "POST":
        if request.form["pass"] == PASSPHRASE or 'authenticated' in session:
            session['authenticated'] = True
            if request.form["title"] == "": return page("Bitte wenigstens einen Titel eingeben")
            if request.form["del-title"] != "" and request.form["del-title"] != request.form["title"]: return page(
                "TITEL NICHT KORREKT, Rezept wird nicht gelöscht")
            id = request.form["id"] if request.form.get("id", "") != "" else uuid.uuid4().__str__()
            if 'image' in request.files and request.files['image'].mimetype in {'image/webp', 'image/jpeg',
                                                                                'image/png'}:
                if not os.path.exists('static/img'): os.makedirs('static/img')
                request.files['image'].save(os.path.join('static/img', id))
            if DB_DRIVER == "JSON":
                mode = 'a' if os.path.exists(DATAFILE) else 'w'
                with open(DATAFILE, mode) as db_file:
                    try:
                        recipes = json.load(db_file)
                    except Exception:
                        recipes = {}
                    if request.form["del-title"] != "":
                        if id in recipes: del recipes[id]
                        if os.path.isfile(os.path.join('static/img', id)): os.remove(os.path.join('static/img', id))
                    else:
                        recipes[id] = dict(title=request.form["title"][0:3000],
                                           ingredients=request.form["ingredients"][0:3000],
                                           prep=request.form["prep"][0:3000], tags=request.form["tags"][0:3000],
                                           cvss=0.0)
                    db_file.seek(0)
                    db_file.truncate()
                    json.dump(recipes, db_file, indent=4)
            elif DB_DRIVER == "SQLITE":
                conn = get_sqlite_db()
                if request.form["del-title"] != "":
                    conn.cursor().execute("DELETE FROM recipes WHERE id = ?", (id,))
                    if os.path.isfile(os.path.join('static/img', id)): os.remove(os.path.join('static/img', id))
                else:
                    conn.cursor().execute("INSERT OR REPLACE INTO recipes VALUES (?, ?, ?, ?, ?, ?)", (
                    id, request.form["title"][0:3000], request.form["ingredients"][0:3000],
                    request.form["prep"][0:3000], request.form["tags"][0:3000], request.form.get('cvss', 0.0)))
                conn.commit()
            if request.form["del-title"] == request.form["title"]: return make_response(redirect("/"))
            return make_response(redirect("/r/" + id))
        else:
            return page("FALSCHE PASSPHRASE, Rezept nicht angelegt / editiert / gelöscht")
    if DB_DRIVER == "JSON":
        recipes = get_json_db()
    elif DB_DRIVER == "SQLITE":
        recipe_rows = get_sqlite_db().cursor().execute(
            "SELECT title, ingredients, prep, tags, id, cvss FROM recipes ORDER BY title ASC").fetchall()
        recipes = [dict(row) for row in recipe_rows]
    return render_template('index.html',recipes=recipes, recipes_count=len(recipes))


@app.route("/e/<id>")
def rezepte_edit(id):
    if id != "new":
        recipe = get_rezept(id)
        if recipe is None: return page("Rezept nicht gefunden :(")
    else:
        recipe = dict(title="", tags="", prep="", ingredients="", id="")
    return render_template("edit_recipe.html",r=recipe, authenticated=('authenticated' in session),
                                         img_url='/static/img/'+recipe['id'],
                                         has_image=os.path.isfile(os.path.join('static/img', recipe['id'])))

@app.route("/r/<id>")
def rezepte_show(id):
    recipe = get_rezept(id)
    if recipe is None: return page("Rezept nicht gefunden :(")
    return render_template("recipe.html",r=recipe, img_url='/static/img/'+recipe['id'],
                           has_image=os.path.isfile(os.path.join('static/img', recipe['id'])))


def get_rezept(id):
    if DB_DRIVER == "JSON":
        recipe_row = list(filter(lambda r: r["id"] == id, get_json_db()))
        recipe_row = recipe_row[0] if recipe_row else None
    elif DB_DRIVER == "SQLITE":
        recipe_row = get_sqlite_db().cursor().execute(
            "SELECT title, ingredients, prep, tags, id, cvss FROM recipes WHERE id = ?", (id,)).fetchone()
    return dict(recipe_row) if recipe_row is not None else None


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/x-icon')
@app.route('/favicon.png')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.png', mimetype='image/x-icon')