from flask import Flask, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import os

#charger les variables d'environnement
load_dotenv()

app = Flask("Pikapp")

MONGO_URI = os.getenv('MONGO_URI')

client = MongoClient(MONGO_URI)
db = client.get_database("pikApp")


@app.route('/')
def index():
    pokemon_data = list(db['pokemons'].find({}))
    return render_template("index.html", pokemons = pokemon_data)

app.run(host='0.0.0.0', port=81)