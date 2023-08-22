from typing import List
from flask import Flask, redirect, make_response
from flask import request
import json
import jinja2
import uuid

app = Flask(__name__)
header = """
                <!DOCTYPE html>
                <html>
                <head>
                <title>Bäcker One</title>
                </head>
                <body>
                <style>
                *{
                    font-size: 20px;
                    color: #E9C46A;
                    font-family: "Georgia"
                }
                body{
                    background: #264653;
                }
                a {
                    color: #E9C46A;
                }
                a:visited {
                      color: #F4A261;
                }
                textarea,input {
                    background: #2A9D8F;
                    border: 3px solid #264653;
                }
                main{
                        padding: 40px;
                }
                details{
                    padding:40px 0 40px 0;
                    background: #2A9D8F;
                    width: 500px;
                    border-radius: 15px;
                }
                </style>
                <main>
                <div><a href="/">HOME</a> <a href="/e/new">HINZUFÜGEN</a></div>
                """
footer = """
                </main>
                </body>
                </html>
                """
main_page = """
                <p>Hello at Bäckerone, your responsible disclosure service for recepies!</p>
                REZEPTE: 
                    <ul>
                {% for r in recepies%}
                    <li><h2><a href="/r/{{r.id}}">{{ r.title }}</a></h2></li>
                {% endfor %}
                </ul>
                """

edit_page= """
                <form method="post" action="/">
                Titel :<br> <input name="title" value="{{r.title}}"></input><br>
                Tags (Kommaseparierte Liste):<br> <input name="tags" value="{{r.tags}}"/><br>
                Zutaten:<br> <textarea name="ingredients" rows="5" cols="33">{{r.ingredients}}</textarea><br>
                Zubereitung:<br> <textarea name="prep" rows="5" cols="33">{{r.prep}}</textarea><br>
                <br>
                {% if not passphrase %}
                Passphrase:<br> <input name="pass"/><br>
                {% else %}
                <input name="pass" value="ichessegernekuchen" type="hidden"/><br>
                {%endif%}
                <input type="hidden" name="id" value="{{r.id}}"/>
                <button type="submit">Abschicken</button>
                </form>

"""

recepie_page = """
                    <p>Hello at Bäckerone, your responsible disclosure service for recepies!</p>
                    <h1>{{r.title}}</h1>
                    <h3 style="text-decoration: underline;"> Zutaten: </h3>
                    <h4><pre>{{r.ingredients}}</pre></h4>
                    <h3 style="text-decoration: underline;"> Zubereitung: </h3>
                    <h4><pre>{{r.prep}}</pre></h4>
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
            if request.form["pass"]=="ichessegernekuchen" or "pass" in request.cookies:
                rezept = dict(title=request.form["title"][0:3000],ingredients=request.form["ingredients"][0:3000],prep=request.form["prep"][0:3000],tags=request.form["tags"][0:3000] ,id=uuid.uuid4().__str__())
                print(request.form["title"])
                if request.form.get("id")!=None:
                    rezepte = list(filter(lambda x: x["id"] != request.form["id"],rezepte))
                rezepte.append(rezept)
                print(rezept)
                with open("data.txt","w") as data:
                    data.write(json.dumps(rezepte,indent=2))
                return redirect("/r/"+rezept["id"])
            else:
                return page("FALSCHE PASSPHRASE, Rezept nicht angelegt / editiert")
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
        passphrase= request.cookies.get("pass")
        res = make_response( template.render(r=rezept, passphrase=passphrase))
        res.set_cookie( "pass", "ok")
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
