from typing import List
from flask import Flask, redirect, make_response
from flask import request, session
import json
import jinja2
import uuid
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)
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
                </style>
                <main>
                <div><a class="home" href="/">HOME</a> <a class="add" href="/e/new">HINZUFÜGEN</a></div>
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
                </script>
                <p>Hello at Bäckerone,<br> your responsible disclosure service for recepies!</p>
                REZEPTE: <br>
                <input type="text" id="recepiesFilter" onkeyup="filterRecepies()" placeholder="Suche nach Rezepten,Tags..">
                <ul id="recepiesList">
                    {% for r in recepies%}
                    <li><h2><a href="/r/{{r.id|e}}">{{ r.title|e}}<span style="display:none">{{r.tags|e}}</span></a></h2></li>
                    {% endfor %}
                </ul>
                """

edit_page= """
                <form method="post" action="/">
                Titel :<br> <input name="title" value="{{r.title|e}}"></input><br>
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
                <div class="del" style="display:none">
                Zum Löschen, Rezepttitel eingeben :<br> 
                <input id="del-title" name="del-title" value="" onkeyup="document.getElementById('del-submit').innerHTML = document.getElementById('del-title').value!='' ? 'Löschen' : 'Abschicken'"/></div><br>
                <div style="display:flex; gap:10px;">
                <button class="del" type="submit">Abschicken</button>
                <button class="del" type="button" onclick="for (let e of document.getElementsByClassName('del')) {e.style.display = e.style.display=='none' ? 'block' : 'none'}">Löschen</button>
                <button class="del" id="del-submit" type="submit" style="display:none">Abschicken</button>
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
    rezepte = []
    with open("data.txt","r") as data:
        try:
            rezepte = json.loads(data.read())
        except:
            rezepte = []
        if request.method == "POST":
            if request.form["pass"]==(os.environ.get("RECEPIE_PASSPHRASE") or "ichessegernekuchen") or 'authenticated' in session:
                session['authenticated'] = True
                if request.form["title"]=="":
                    return page("Please enter at least a title")
                rezept = dict(title=request.form["title"][0:3000],ingredients=request.form["ingredients"][0:3000],prep=request.form["prep"][0:3000],tags=request.form["tags"][0:3000] ,id=uuid.uuid4().__str__())
                if request.form.get("id")!=None:
                    rezepte = list(filter(lambda x: x["id"] != request.form["id"],rezepte))
                if request.form["del-title"]!=request.form["title"]:
                    if request.form["del-title"]!="":
                        return page("TITEL NICHT KORREKT, Rezept wird nicht gelöscht")
                    rezepte.append(rezept)
                with open("data.txt","w") as data:
                    data.write(json.dumps(rezepte,indent=2))
                environment = jinja2.Environment()
                template = environment.from_string(page(edit_page))
                if request.form["del-title"]==request.form["title"]:
                    return make_response(redirect("/"))
                return make_response(redirect("/r/"+rezept["id"]))
            else:
                return page("FALSCHE PASSPHRASE, Rezept nicht angelegt / editiert / gelöscht")
        environment = jinja2.Environment()
        template = environment.from_string(page(main_page))
        return template.render(recepies=rezepte)
           

@app.route("/e/<id>")
def rezepte_edit(id):
    rezepte = []
    with open("data.txt","r") as data:
        try: 
            rezepte: List[dict] = json.loads(data.read())
        except:
            rezepte = []
        if id!="new":
            rezept = list(filter(lambda x: x["id"] == id,rezepte))
            if rezept==[]: 
                return page("Rezept nicht gefunden :(")
            rezept = rezept[0]
        else:
            rezept = dict(title="",tags="",prep="",ingredients="",id="")
        environment = jinja2.Environment()
        template = environment.from_string(page(edit_page))
        authenticated = 'authenticated' in session
        res = make_response( template.render(r=rezept, authenticated=authenticated))
        return res

@app.route("/r/<id>")
def rezepte_show(id):
    rezepte = []
    with open("data.txt","r") as data:
        try: 
            rezepte: List[dict] = json.loads(data.read())
        except:
            rezepte = []
        rezept = list(filter(lambda x: x["id"] == id,rezepte))
        if rezept!=[]:
            rezept = rezept[0]
            environment = jinja2.Environment()
            template = environment.from_string(page(recepie_page))
            return template.render(r=rezept)
        else:
            return page("Rezept nicht gefunden :(")


def page(name):
    return header + name + footer
