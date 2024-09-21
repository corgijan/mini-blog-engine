from flask import Flask, redirect, make_response, request, session, g, url_for
import jinja2, uuid, os, sqlite3, json

app = Flask(__name__)
app.secret_key = os.urandom(64)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

DB_DRIVER = "SQLITE"  # JSON or SQLITE
DATAFILE = "data.db"
PASSPHRASE = os.environ.get("RECIPE_PASSPHRASE") or "ichessegernekuchen"

header = """
                <!DOCTYPE html>
                <html>
                <head>
                <title>Corgijans Rezepte</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link rel="stylesheet" href="/static/style.css">
                </head>
                <body>
                <style>
                * { font-size: 20px; color: #E9C46A; font-family: "Helvetica", sans-serif; }
                body{ background: #264653;margin:0; }
                .add { color: #E9C46A !important; }
                img { width: 100%; height: auto; }
                a { color: #E9C46A; }
                a:visited, .home { color: #F4A261; }
                textarea, input {
                    background: #2A9D8F;
                    border: 3px solid #264653;
                }
                main { padding: 40px; max-width: 600px; margin:auto; }
                img {max-width:300px;max-height:300px;}
                details{
                    padding:40px 0 40px 0;
                    background: #2A9D8F;
                    width: 500px;
                    border-radius: 15px;
                }
                .pre{ white-space: pre-wrap; }
                .norm{ background: #264653; border: 0px; text-decoration: underline; }
                .nav-link{ font-size:1rem; }
                
                </style>
 <!--               
<header class="header-section has-img">

<div class="big-img intro-header" style="background-image: url(&quot;https://images.unsplash.com/photo-1712741042337-124ff2469441?q=80&amp;w=1974&amp;auto=format&amp;fit=crop&amp;ixlib=rb-4.0.3&amp;ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&quot;);">
  <div class="container-md">
    <div class="row">
      <div class="col-xl-8 offset-xl-2 col-lg-10 offset-lg-1">
        <div class="page-heading">
          <h1>Projects</h1>
          
            
              <hr class="small">
              <span class="page-subheading">Why you'd want to go on a date with me</span>
            
          

          
        </div>
      </div>
    </div>
  </div>
  <span class="img-desc" style="display: none;"></span>
</div>

<div class="intro-header no-img">
  <div class="container-md">
    <div class="row">
      <div class="col-xl-8 offset-xl-2 col-lg-10 offset-lg-1">
        <div class="page-heading">
          <h1>Projects</h1>
          
            
              <hr class="small">
              <span class="page-subheading">Why you'd want to go on a date with me</span>
        </div>
      </div>
    </div>
  </div>
</div>
</header>
-->
                <main style="margin-top:100px">
                <nav style="font-size: 1rem" class="navbar navbar-expand-xl fixed-top navbar-custom top-nav-regular navbar-dark"><a class="navbar-brand" href="/">🦊 corgijans Rezepte</a><button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#main-navbar" aria-controls="main-navbar" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>

  <div class="collapse navbar-collapse" id="main-navbar">
    <ul class="navbar-nav ml-auto">
          <li class="nav-item">
            <a class="nav-link" href="/">home</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/e/new">hinzufügen</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="http://blog.corgijan.dev">blog</a>
          </li>
          </ul>
  </div>
    <div class="avatar-container">
      <div class="avatar-img-border">
        <a href="/">
          <img alt="Navigation bar avatar" class="avatar-img" src="http://blog.corgijan.dev/assets/images/ava.jpg">
        </a>
      </div>
    </div>
  
</nav>


                """
footer = """
                <script src="/static/script.js"></script>
                </main>
                </body>
                </html>
               """
main_page = """
                <script>
                function filterRecipes() {
                    let filter = document.getElementById('recipesFilter').value.toUpperCase();
                    for (let li of document.getElementById('recipesList').getElementsByTagName('li')) {
                        let a = li.getElementsByTagName('a')[0];
                        let txtValue = a.textContent || a.innerText;
                        li.style.display = (txtValue.toUpperCase().indexOf(filter) > -1) ? "" : "none"
                    }
                }
                function sortRecipes() {
                    let list = document.getElementById('recipesList')
                    Array.from(list.getElementsByTagName('li'))
                        .sort((a, b) => (sortSelector.value === 'asc' ? 1 : -1) * (a.innerText).localeCompare(b.innerText))
                        .forEach(item => list.appendChild(item));
                }
                </script>
                <p>Wilkommen bei Corgijans Rezepten<br> Dies ist ein "Code-Golf" Projekt mit ~250 Zeilen Code</p>
                REZEPTE: <br>
                <input type="text" id="recipesFilter" onkeyup="filterRecipes()" placeholder="Suche nach Rezepten,Tags..">
                {% if recipes_count >= 50 %}
                <select id="sortSelector" onchange="sortRecipes()"><option value="asc">aufsteigend</option><option value="desc">absteigend</option></select>
                {% endif %}
                <ul id="recipesList">
                    {% for r in recipes%}
                    <li><h2><a href="/r/{{r.id|e}}">{{ r.title|e}}<span style="display:none">{{r.tags|e}}</span></a></h2></li>
                    {% endfor %}
                </ul>
                """
edit_page = """
                <form method="post" enctype="multipart/form-data" action="/">
                Bild:<br>{% if has_image %}<img src="{{ img_url }}"><br>{% endif %}<input type="file" name="image" accept="image/webp, image/jpeg, image/png" /><br>
                Titel:<br> <input name="title" value="{{r.title|e}}" /><br>
                Tags (Kommaseparierte Liste):<br> <input name="tags" value="{{r.tags|e}}"/><br>
                Zutaten:<br> <textarea name="ingredients" rows="5" cols="33">{{r.ingredients|e}}</textarea><br>
                Zubereitung:<br> <textarea name="prep" rows="5" cols="33">{{r.prep|e}}</textarea><br><br>
                {% if authenticated %}
                    <input name="pass" value="" type="hidden"/><br>
                {% else %}
                    Passphrase:<br> <input name="pass"/><br>
                {%endif%}
                <input type="hidden" name="id" value="{{r.id|e}}"/><br>
                <div class="del" style="display:none">Zum Löschen, Rezepttitel eingeben:<br><input id="del-title" name="del-title" value="" onkeyup="document.getElementById('del-submit').innerHTML = document.getElementById('del-title').value!='' ? 'Löschen' : 'Abschicken'"/></div><br>
                <div style="display:flex; gap:10px;">
                    <button  id="del-submit" type="submit">Abschicken</button>
                    <button class="del" type="button" onclick="for (let e of document.getElementsByClassName('del')) {e.style.display = e.style.display=='none' ? 'block' : 'none'}">Löschen</button>
                </div>
                </form>
                *all recipes are released in the public domain and can be used freely 
                <br>
                """
recipe_page = """
                <h1>{{r.title|e}}</h1>
                {% if has_image %}<img src="{{ img_url }}"><br>{% endif %}
                <h3>Tags: {{r.tags|e}}</h3>
                <h3 style="text-decoration: underline;"> Zutaten: </h3>
                <h4><p class="pre">{{r.ingredients|e}}</p></h4>
                <h3 style="text-decoration: underline;"> Zubereitung: </h3>
                <h4><p class="pre">{{r.prep|e}}</p></h4>
                <a href="/e/{{r.id}}">Editieren</a>
                """


def page(name):
    return header + name + footer


def get_sqlite_db():
    if 'db' not in g:
        g.db = sqlite3.connect('data.db')
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
                    if os.path.isfile(os.path.join('static', id)): os.remove(os.path.join('static', id))
                else:
                    conn.cursor().execute("INSERT OR REPLACE INTO recipes VALUES (?, ?, ?, ?, ?, ?)", (
                    id, request.form["title"][0:3000], request.form["ingredients"][0:3000],
                    request.form["prep"][0:3000], request.form["tags"][0:3000], request.form.get('cvss', 0.0)))
                conn.commit()
            template = jinja2.Environment().from_string(page(edit_page))
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
    template = jinja2.Environment().from_string(page(main_page))
    return template.render(recipes=recipes, recipes_count=len(recipes))


@app.route("/e/<id>")
def rezepte_edit(id):
    if id != "new":
        recipe = get_rezept(id)
        if recipe is None: return page("Rezept nicht gefunden :(")
    else:
        recipe = dict(title="", tags="", prep="", ingredients="", id="")
    template = jinja2.Environment().from_string(page(edit_page))
    return make_response(template.render(r=recipe, authenticated=('authenticated' in session),
                                         img_url=url_for('static', filename=recipe['id']),
                                         has_image=os.path.isfile(os.path.join('static', recipe['id']))))


@app.route("/r/<id>")
def rezepte_show(id):
    recipe = get_rezept(id)
    if recipe is None: return page("Rezept nicht gefunden :(")
    template = jinja2.Environment().from_string(page(recipe_page))
    return template.render(r=recipe, img_url=url_for('static', filename=recipe['id']),
                           has_image=os.path.isfile(os.path.join('static', recipe['id'])))


def get_rezept(id):
    if DB_DRIVER == "JSON":
        recipe_row = list(filter(lambda r: r["id"] == id, get_json_db()))
        recipe_row = recipe_row[0] if recipe_row else None
    elif DB_DRIVER == "SQLITE":
        recipe_row = get_sqlite_db().cursor().execute(
            "SELECT title, ingredients, prep, tags, id, cvss FROM recipes WHERE id = ?", (id,)).fetchone()
    return dict(recipe_row) if recipe_row is not None else None
