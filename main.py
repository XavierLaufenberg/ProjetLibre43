from flask import Flask, render_template, redirect, request, session, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import bcrypt
import os
from bson.objectid import ObjectId

#charger les variables d'environnement
load_dotenv()

app = Flask("Pikapp")

MONGO_URI = os.getenv('MONGO_URI')

client = MongoClient(MONGO_URI)
db = client.get_database("pikApp")
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    # Pokémons
    pokemon_data = list(db['pokemons'].find({}))
    # Dresseurs
    dresseur_data = list(db['dresseurs'].find({}))
    # Calcul du nombre de pokémons attrapés
    for dresseur in dresseur_data:
        dresseur["nb_pokemons"] = len(dresseur.get("pokemons_attrapes", []))

    return render_template( "index.html",pokemons=pokemon_data,dresseurs=dresseur_data)

@app.route('/pokemons')
def pokemons():
    pokemon_data = list(db['pokemons'].find({}))
    return render_template('front/all_pokemons.html',pokemons=pokemon_data)

@app.route('/dresseurs')
def all_dresseurs():
    dresseur_data = list(db['dresseurs'].find({}))
    dresseur_data = sorted(
    dresseur_data,
    key=lambda d: len(dresseur_data.get("pokemons_attrapes", [])),reverse=True) # Calcul du nombre de pokémons

    for dresseur in dresseur_data:
        dresseur["nb_pokemons"] = len(dresseur_data.get("pokemons_attrapes", []))

    return render_template('front/dresseurs.html',dresseurs=dresseur_data)



#####GESTION UTILISATEURS######
@app.route('/signup')
def signup():
    avatar_dir = os.path.join(app.static_folder, "images/avatar")
    avatars = os.listdir(avatar_dir)
    avatar_paths = [f"/static/images/avatar/{a}" for a in avatars]
    return render_template("front/signup.html",avatars=avatar_paths)


@app.route('/register', methods=['POST'])
def register():
    utilisateur = request.form['utilisateur']
    mdp = request.form['mot_de_passe']
    avatar = request.form['avatar']
    password_hash = bcrypt.hashpw(mdp.encode('utf-8'), bcrypt.gensalt())
    user = {
        "pseudo": utilisateur,
        "password": password_hash,   # à hasher plus tard !
        "avatar": avatar,
        "role" : "user",
        "pokemons_attrapes": []
    }
    db['dresseurs'].insert_one(user)
    session['role'] = 'user'
    session['util'] = utilisateur
    return redirect(url_for('index'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si c'est un GET, afficher le formulaire
    if request.method == 'GET':
        return render_template('front/login.html')

    # Sinon, POST = tentative de connexion
    utilisateur = request.form.get('utilisateur')
    mot_de_passe = request.form.get('mot_de_passe')

    if not utilisateur or not mot_de_passe:
        return render_template('front/login.html', erreur="Veuillez remplir tous les champs")

    db_utils = db.dresseurs
    util = db_utils.find_one({'pseudo': utilisateur})

    if not util:
        return render_template('front/login.html', erreur="Le nom d'utilisateur n'existe pas")

    # Vérification du mot de passe (hashé avec bcrypt)
    if bcrypt.checkpw(mot_de_passe.encode('utf-8'), util['password']):
        # Création de la session, on créer les cookies pour une session
        session['role'] = util['role']
        session['util'] = utilisateur
        return redirect(url_for("index"))
    else:
        return render_template('front/login.html', erreur="Le mot de passe est incorrect")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))




###Ajout pokemon 
#Affichage du templates
@app.route("/pokemon/add")
def add_pokemon():
    return render_template("front/new_pokemon.html")

#Création du post, du pokemon
@app.route("/pokemon/create", methods = ['POST'])
def create_pokemon(): 
    nom = request.form['nom']
    description = request.form['description']
    type_pokemon = request.form['type']

    image = request.files["image"]

    if image:
        nom_fichier = secure_filename(image.filename)
        upload_path = os.path.join(app.static_folder, "images/pokemon_user", nom_fichier)
        image.save(upload_path)

        image_path = f'/static/images/pokemon_user/{nom_fichier}'

    else: 
        image_path = ""    

    pokemon = { 
        "nom": nom,
        "image" : image_path,
        "description" : description,
        "type" : type_pokemon
    }
    db['pokemons'].insert_one(pokemon)
    return redirect(url_for("/front/pokemons"))


#### ADMIN ####
@app.route('/admin')
def admin(): 
    pokemon_data = list(db['pokemons'].find({}))
    dresseur_data = list(db['dresseurs'].find({}))
    if 'util' in session and session['role'] == 'admin':
        return render_template('admin/back_accueil.html', pokemons = pokemon_data, dresseurs = dresseur_data)
    else: 
        return render_template('index.html', erreur = "vous n'avez pas les droits d'accès",  pokemons = pokemon_data, dresseurs = dresseur_data)


@app.route('/admin/update_role/<user_id>', methods= ['POST'])
def update_role(user_id):
    if 'util' in session and session['role'] == 'admin':
        new_role = request.form.get('role')

        db['dresseurs'].update_one(
            {"_id" : ObjectId(user_id)},
            {"$set" : {"role": new_role}}
        )
    return redirect(url_for('admin'))   

@app.route("/admin/delete_user/<user_id>")
def delete_user(user_id):
    if 'util' in session and session['role'] == 'admin':
        db['dresseurs'].delete_one({"_id" : ObjectId(user_id)})
    return redirect(url_for('admin')) 


@app.route('/admin/user/<user_id>')
def show_user(user_id):
    if 'util' in session and session['role'] == 'admin':
        user = db['dresseurs'].find_one({"_id" : ObjectId(user_id)})

        if not user:
            return redirect(url_for('admin'))
        
        return render_template('admin/back_user.html', user=user)
    
    return redirect(url_for('index')) 








app.run(host='0.0.0.0', port=81)