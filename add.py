import json, requests

url="http://127.0.0.1:5000/"
passphrase="ichessegernekuchen"

rezepte = []
with open("data.txt", "r") as data:
    try:
        rezepte = json.loads(data.read())
    except:
        rezepte = []
    for rezept in rezepte:
        rezept['pass'] = passphrase
        rezept['del-title'] = ''
        r = requests.post(url, data=rezept)
        print(r.status_code)