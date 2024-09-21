header = """
                <!DOCTYPE html>
                <html>
                <head>
                <title>Rebenberg Corgijan</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <link rel="stylesheet" href="/static/style.css">
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
                  overflow: visible;
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
                  overflow: visible;
                  background-color: #333;
                }
                
                </style>
                
                <nav class="navbar navbar-expand-xl fixed-top navbar-custom top-nav-regular navbar-dark"><a class="navbar-brand" href="/">🍷 Rebenberg</a><button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#main-navbar" aria-controls="main-navbar" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>

  <div class="collapse navbar-collapse" id="main-navbar">
    <ul class="navbar-nav ml-auto">
          <li class="nav-item">
            <a class="nav-link" href="/">Home</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/grapes">Grapes</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="/regions">Regions</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="https://www.corgijan.dev">About Me</a>
          </li></ul>
  </div>

  

  
    <div class="avatar-container">
      <div class="avatar-img-border">
        <a href="/">
          <img alt="Navigation bar avatar" class="avatar-img" src="http://blog.corgijan.dev/assets/images/ava.jpg">
        </a>
      </div>
    </div>
  

</nav>
                

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
                    <li><h2><a href="/{{title | lower}}/{{r.id|e}}">{{ r.title|e}}<span style="display:none">{{r.tags|e}}</span></a></h2></li>
                    {% endfor %}
                    
                    <li><h2><a href="/edit_{{title | lower}}/new"> + </a></h2></li>
                </ul>
                """
edit_page = """
                <h1>Edit Grape</h1>
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

edit_page_region = """
                <p>Edit Region</p>
                <form method="post" enctype="multipart/form-data" action="/{{title|lower}}">
                Image:<br>{% if has_image %}<img src="{{ img_url }}"><br>{% endif %}<input type="file" name="image" accept="image/webp, image/jpeg, image/png" /><br>
                Title:<br> <input name="title" value="{{r.title|e}}" /><br>
                Tags (commaseparated list):<br> <input name="tags" value="{{r.tags|e}}"/><br>
                Region Info:<br> <textarea name="region_info" rows="5" cols="33">{{r.regio_info|e}}</textarea><br>
                Region Grapes:<br> <textarea name="taste_info" rows="5" cols="33">{{r.taste_info|e}}</textarea><br><br>
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
                <h3 style="text-decoration: underline;">  </h3>
                <h4><p class="pre">{{r.grape_info|e}}</p></h4>
                <h3 style="text-decoration: underline;">  </h3>
                <h4><p class="pre">{{r.taste_info|e}}</p></h4>
                <a href="/edit_{{title|lower}}/{{r.id}}">Editieren</a>
                """
