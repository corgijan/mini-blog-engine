from typing import List
from flask import Flask, redirect
from flask import request
import json
import jinja2
import uuid

app = Flask(__name__)

main_page = """
                <p>Hello at Bäckerone, your responsible disclosure service for recepies!</p>
                REZEPTE: 
                    <ul>
                {% for r in recepies%}
                    <li><h2><a href="/r/{{r.hash}}">{{ r.title }}</a></h2></li>
                {% endfor %}
                </ul>
                <details>
                <summary>Rezept hinzufügen</summary>
                <form method="post">
                Titel:<br> <input name="title" /><br>
                Zutaten:<br> <textarea name="ingredients" rows="5" cols="33"></textarea><br>
                Rezept:<br> <textarea name="prep" rows="5" cols="33"></textarea><br>
                <br>
                Passphrase:<br> <input name="pass" /><br>
                <button type="submit">SEND</button>
                </form>
                </details>
                """

recepie_page = """
                <p>Hello at Bäckerone, your responsible disclosure service for recepies!</p>
                    <h1>{{r.title}}</h1><br>
                    <h3> Zutaten: </h3>
                    <h4>{{r.ingredients}}</h4><br>
                    <h3> Zubereitung: </h3>
                    <h4>{{r.prep}}<h4>
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
            if request.form["pass"]=="ichessegernekuchen":
                rezept = dict(title=request.form["title"][0:3000],ingredients=request.form["ingredients"][0:3000],prep=request.form["prep"][0:3000], hash=uuid.uuid4().__str__())
                rezepte.append(rezept)
                with open("data.txt","w") as data:
                    data.write(json.dumps(rezepte,indent=2))
                return redirect("/r/"+rezept["hash"])
            else:
                return "FALSCHE PASSPHRASE"
        environment = jinja2.Environment()
        template = environment.from_string(main_page)
        return template.render(recepies=rezepte)
           


@app.route("/r/<id>")
def rezepte(id):
    rezepte = []
    with open("data.txt","r") as data:
        try: 
            rezepte: List[dict] = json.loads(data.read())
        except:
            rezepte = []
        rezept = list(filter(lambda x: x["hash"] == id,rezepte))
        if rezept!=[]:
            rezept = rezept[0]
            environment = jinja2.Environment()
            template = environment.from_string(recepie_page)
            return template.render(r=rezept)
        else:
            return "Rezept nicht gefunden :("
