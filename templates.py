header = """
                <!DOCTYPE html>
                <html>
                <head>
                <title>Rebenberg Corgijan</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                </head>
                <body>
                <style>
                * { font-size: 20px; color: whitesmoke;}
                body{ background: #660033;margin:0;min-height: 100vh; font-family: Tahoma, sans-serif;}
                .add { color: #E9C46A !important; }
                img { width: 100%; height: auto; }
                a { color: #E9C46A; }
                a:visited, .home { color: #F4A261; }
                textarea, input {
                    background: lightcoral;
                    border: 3px solid #660033;
                }
                main { padding: 40px; max-width: 600px; margin:auto; }
                img {max-width:300px;max-height:300px;}
                details{
                    padding:40px 0 40px 0;
                    background: lightcoral;
                    width: 500px;
                    border-radius: 15px;
                }
                .pre{ white-space: pre-wrap; }
                .norm{ background: #660033; border: 0px; text-decoration: underline; }
                button{ background: #660033; border: 0px; text-decoration: underline; }

                .ul {
                  list-style-type: none;
                  margin: 0;
                  padding: 0;
                  overflow: hidden;
                  background-color: #333;
                }

                .li {
                  float: left;
                }
                li-last{
                  float: right;
                }

                .li a {
                  display: block;
                  color: white;
                  text-align: center;
                  padding: 14px 16px;
                  text-decoration: none;
                }

                .li a:hover {
                  background-color: #111;
                }
                .navbar {
                  position: sticky;
                  top: 0;
                  overflow: hidden;
                  background-color: #333;
                }
                
                </style>

                <ul class="ul navbar" >
                  <li class="li"><a class="active" href="/"><b>REBENBERG</b></a></li>
                  <li class="li"><a href="/grapes">Grapes</a></li>
                  <li class="li"><a href="/regios">Regions</a></li>
                  <li class="li"><a href="/wines">Wines</a></li>
                  <li class="li" style="float: right; padding-right: 10px"><a href="https://blog.corgijan.dev/aboutme">Contact</a></li>
                </ul>
                <main>

                <div>
                """
footer = """
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

                {{title}}: <br>
                <input type="text" id="recipesFilter" onkeyup="filterRecipes()" placeholder="Search for variety">
                {% if recipes_count >= 50 %}
                <select id="sortSelector" onchange="sortRecipes()"><option value="asc">aufsteigend</option><option value="desc">absteigend</option></select>
                {% endif %}
                <ul id="recipesList">
                    {% for r in recipes%}
                    <li><h2><a href="/grapes/{{r.id|e}}">{{ r.title|e}}<span style="display:none">{{r.tags|e}}</span></a></h2></li>
                    {% endfor %}
                    
                    <li><h2><a href="/edit_{{title | lower}}/new"> + </a></h2></li>
                </ul>
                """
edit_page = """
                <form method="post" enctype="multipart/form-data" action="/grapes">
                Image:<br>{% if has_image %}<img src="{{ img_url }}"><br>{% endif %}<input type="file" name="image" accept="image/webp, image/jpeg, image/png" /><br>
                Title:<br> <input name="title" value="{{r.title|e}}" /><br>
                Tags (commaseparated list):<br> <input name="tags" value="{{r.tags|e}}"/><br>
                Info:<br> <textarea name="grape_info" rows="5" cols="33">{{r.grape_info|e}}</textarea><br>
                Taste:<br> <textarea name="taste_info" rows="5" cols="33">{{r.taste_info|e}}</textarea><br><br>
                {% if authenticated %}
                    <input name="pass" value="" type="hidden"/><br>
                {% else %}
                    Passphrase:<br> <input name="pass"/><br>
                {%endif%}
                <input type="hidden" name="id" value="{{r.id|e}}"/><br>
                <div class="del" style="display:none">To delete, please enter Title:<br><input id="del-title" name="del-title" value="" onkeyup="document.getElementById('del-submit').innerHTML = document.getElementById('del-title').value!='' ? 'Löschen' : 'Abschicken'"/></div><br>
                <div style="display:flex; gap:10px;">
                    <button  id="del-submit" type="submit">Submit</button>
                    <button class="del" type="button" onclick="for (let e of document.getElementsByClassName('del')) {e.style.display = e.style.display=='none' ? 'block' : 'none'}">Delete</button>
                </div>
                </form>
                <br>
                <br>
                *all info are released in the public domain and can be used freely 
                <br>
                """
recipe_page = """
                <p></p>
                <h1>{{r.title|e}}</h1>
                {% if has_image %}<img src="{{ img_url }}"><br>{% endif %}
                <h3>Tags: {{r.tags|e}}</h3>
                <h3 style="text-decoration: underline;"> Zutaten: </h3>
                <h4><p class="pre">{{r.grape_info|e}}</p></h4>
                <h3 style="text-decoration: underline;"> Zubereitung: </h3>
                <h4><p class="pre">{{r.taste_info|e}}</p></h4>
                <a href="/edit_grape/{{r.id}}">Editieren</a>
                """
