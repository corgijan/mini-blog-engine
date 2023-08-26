from typing import List
from flask import Flask, redirect, make_response, request, session
import json, jinja2, uuid, os, sqlite3, re

app = Flask(__name__)
app.secret_key = os.urandom(32)
sqlite3.connect('data.db').execute("CREATE TABLE IF NOT EXISTS recipes (id text PRIMARY KEY, title text NOT NULL, ingredients text, prep text, tags text, cvss real)").close()
header = """
                <!DOCTYPE html>
                <html>
                <head>
                <title>Bäcker One</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                </head>
                <body>
                <style>
                *{
                    font-size: 20px;
                    color: #E9C46A;
                    font-family: "Georgia"
                }
                body{ background: #264653; }
                .add { color: #E9C46A !important; }
                a { color: #E9C46A; }
                a:visited, .home { color: #F4A261; }
                textarea,input {
                    background: #2A9D8F;
                    border: 3px solid #264653;
                }
                main{
                    padding: 40px;
                    max-width: 800px;
                }
                details{
                    padding:40px 0 40px 0;
                    background: #2A9D8F;
                    width: 500px;
                    border-radius: 15px;
                }
                .pre{ white-space: pre-wrap; }
                .norm{ background: #264653;border:0px;text-decoration: underline; }
                </style>
                <main>
                <div><a class="home" href="/">HOME</a> <a class="add" href="/e/new">HINZUFÜGEN</a> <button class="add norm" onclick="alert('Jan.vaorin(at)gmail(punkt)de All Cookies are functional ones')">IMPRESSUM</button></div>
                """
footer = """
                </main>
                </body>
                </html>
               """
main_page = """
                <script>
                function filterRecepies() {
                    let filter = document.getElementById('recepiesFilter').value.toUpperCase();
                    for (let li of document.getElementById('recepiesList').getElementsByTagName('li')) {
                        let a = li.getElementsByTagName('a')[0];
                        let txtValue = a.textContent || a.innerText;
                        li.style.display = (txtValue.toUpperCase().indexOf(filter) > -1) ? "" : "none"
                    }
                }
                function sortRecepies() {
                    let list = document.getElementById('recepiesList')
                    Array.from(list.getElementsByTagName('li'))
                        .sort((a, b) => (sortSelector.value === 'asc' ? 1 : -1) * (a.innerText).localeCompare(b.innerText))
                        .forEach(item => list.appendChild(item));
                }
                </script>
                <p>Hello at Bäckerone,<br> your responsible disclosure service for recepies!</p>
                REZEPTE: <br>
                <input type="text" id="recepiesFilter" onkeyup="filterRecepies()" placeholder="Suche nach Rezepten,Tags..">
                <select id="sortSelector" onchange="sortRecepies()"><option value="asc">aufsteigend</option><option value="desc">absteigend</option></select>
                <ul id="recepiesList">
                    {% for r in recepies%}
                    <li><h2><a href="/r/{{r.id|e}}">{{ r.title|e}}<span style="display:none">{{r.tags|e}}</span></a></h2></li>
                    {% endfor %}
                </ul>
                <script>sortRecepies()</script>
                """

edit_page = """
                <form method="post" action="/">
                Titel:<br> <input name="title" value="{{r.title|e}}"></input><br>
                Tags (Kommaseparierte Liste):<br> <input name="tags" value="{{r.tags|e}}"/><br>
                Zutaten:<br> <textarea name="ingredients" rows="5" cols="33">{{r.ingredients|e}}</textarea><br>
                Zubereitung:<br> <textarea name="prep" rows="5" cols="33">{{r.prep|e}}</textarea><br>
                <br>
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
                <br>
"""

recepie_page = """
                <p>Hello at Bäckerone, your responsible disclosure service for recepies!</p>
                <h1>{{r.title|e}}</h1>
                <h3>Tags: {{r.tags|e}}</h3>
                <h3 style="text-decoration: underline;"> Zutaten: </h3>
                <h4><p class="pre">{{r.ingredients|e}}</p></h4>
                <h3 style="text-decoration: underline;"> Zubereitung: </h3>
                <h4><p class="pre">{{r.prep|e}}</p></h4>
                <a href="/e/{{r.id}}">Editieren</a>
                """


@app.route("/", methods=["GET","POST"])
def main():
    if request.method == "POST":
        if request.form["pass"] == (os.environ.get("RECEPIE_PASSPHRASE") or "ichessegernekuchen") or 'authenticated' in session:
            session['authenticated'] = True
            if request.form["title"] == "": return page("Bitte wenigstens einen Titel eingeben")
            if request.form["del-title"] != "" and request.form["del-title"] != request.form["title"]: return page("TITEL NICHT KORREKT, Rezept wird nicht gelöscht")
            id = request.form["id"] if request.form.get("id", "") != "" else uuid.uuid4().__str__()
            conn = get_db_connection()
            if request.form["del-title"] != "":
                conn.cursor().execute("DELETE FROM recipes WHERE id = ?", (id if is_uuid(id) else "0",))
            else:
                if request.form.get("id", "") != "":
                    conn.cursor().execute("UPDATE recipes SET title=?, ingredients=?, prep=?, tags=?, cvss=? WHERE id = ?", (request.form["title"][0:3000], request.form["ingredients"][0:3000], request.form["prep"][0:3000], request.form["tags"][0:3000], request.form.get('cvss', 0.0), id if is_uuid(id) else "0"))
                else:
                    conn.cursor().execute("INSERT INTO recipes VALUES (?, ?, ?, ?, ?, ?)", (id, request.form["title"][0:3000], request.form["ingredients"][0:3000], request.form["prep"][0:3000], request.form["tags"][0:3000], request.form.get('cvss', 0.0)))
            conn.commit()
            conn.close()
            template = jinja2.Environment().from_string(page(edit_page))
            if request.form["del-title"]==request.form["title"]: return make_response(redirect("/"))
            return make_response(redirect("/r/"+id))
        else:
            return page("FALSCHE PASSPHRASE, Rezept nicht angelegt / editiert / gelöscht")
    conn = get_db_connection()
    recepie_rows = conn.cursor().execute("SELECT title, ingredients, prep, tags, id, cvss FROM recipes ORDER BY title ASC").fetchall()
    conn.close()
    recepies = [dict(row) for row in recepie_rows]
    template = jinja2.Environment().from_string(page(main_page))
    return template.render(recepies=recepies)
           

@app.route("/e/<id>")
def rezepte_edit(id):
    if id!="new":
        conn = get_db_connection()
        print(id)
        recepie_row = conn.cursor().execute("SELECT title, ingredients, prep, tags, id, cvss FROM recipes WHERE id = ?", (id,)).fetchone()
        conn.close()
        if recepie_row is None: return page("Rezept nicht gefunden :(")
        recepie = dict(recepie_row)
    else:
        recepie = dict(title="",tags="",prep="",ingredients="",id="")
    template = jinja2.Environment().from_string(page(edit_page))
    authenticated = 'authenticated' in session
    return make_response( template.render(r=recepie, authenticated=authenticated))

@app.route("/r/<id>")
def rezepte_show(id):
    conn = get_db_connection()
    recepie_row = conn.cursor().execute("SELECT title, ingredients, prep, tags, id, cvss FROM recipes WHERE id = ?", (id,)).fetchone()
    conn.close()
    if recepie_row is None: return page("Rezept nicht gefunden :(")
    recepie = dict(recepie_row)
    template = jinja2.Environment().from_string(page(recepie_page))
    return template.render(r=recepie)
            

def page(name):
    return header + name + footer

def is_uuid(uuid: str):
    return re.match("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", uuid.lower())

def get_db_connection():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn