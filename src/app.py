"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planets, Characters, Favorites

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


#GET in here
#users, favorites
#people + /<int:people_id>, planets + /<int:planets_id>

#user + their favs
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))
    return jsonify(all_users), 200

@app.route('/users/favorites', methods=['GET'])
def get_all_favs():
    item = Favorites.query.all()
    all_favs = list(map(lambda x: x.serialize(), item))
    return jsonify(all_favs), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_id(user_id):
    user = User.query.get(user_id)
    return jsonify(user.serialize()), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favs(user_id):
    userfavs = Favorites.query.filter_by(user_id=user_id)
    all_user_favs = list(map(lambda x: x.serialize(), userfavs))
    return jsonify(all_user_favs), 200

#characters + characters_id
@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters = Characters.query.all()
    all_characters = list(map(lambda x: x.serialize(), characters))
    return jsonify(all_characters), 200

@app.route('/characters/<int:characters_id>', methods=['GET'])
def get_character_id(characters_id):
    character = Characters.query.get(characters_id)
    return jsonify(character.serialize()), 200

#planets + planets_id
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planets.query.all()
    all_planets = list(map(lambda x: x.serialize(), planets))
    return jsonify(all_planets), 200

@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_planet_id(planets_id):
    planet = Planets.query.get(planets_id)
    return jsonify(planet.serialize()), 200




#POST in here
#adding a character to one user's favorites
#adding a planet to one user's favorites

@app.route('/users/<int:user_id>/favorites/characters/<int:characters_id>', methods=['POST'])
def add_favorite_character(user_id, characters_id):
    character = Favorites.query.filter_by(characters_id=characters_id, user_id=user_id).first()
    if character is None:
        favcharacter = Characters.query.filter_by(id=characters_id).first()
        if favcharacter is None:
            return jsonify({'error': 'character not found'}), 404
        else:
            user = User.query.filter_by(id=user_id).first()
            if user is None:
                return jsonify({'error': 'user not found'}), 404
            else:
                favcharacter = Favorites(user_id=user_id, characters_id=characters_id)
                db.session.add(favcharacter)
                db.session.commit()
                return jsonify({'msg': 'character added to favorites!'}), 201
    else: 
        return jsonify({'error': 'character already in favorites'}), 201
    
@app.route('/users/<int:user_id>/favorites/planets/<int:planets_id>', methods=['POST'])
def add_favorite_planet(user_id, planets_id):
    planet = Favorites.query.filter_by(planets_id=planets_id, user_id=user_id).first()
    if planet is None:
        favplanet = Planets.query.filter_by(id=planets_id).first()
        if favplanet is None:
            return jsonify({'error': 'planet not found'}), 404
        else:
            user = User.query.filter_by(id=user_id).first()
            if user is None:
                return jsonify({'error': 'planet not found'}), 404
            else:
                favplanets = Favorites(user_id=user_id, planets_id=planets_id)
                db.session.add(favplanets)
                db.session.commit()
                return jsonify({'msg': 'planet added to favorites!'}), 201
    else: 
        return jsonify({'error': 'planet already in favorites'}), 201
    
    
    
# DELETE in here
# removing character from one user's favorites
# removing planet from one user's favorites

@app.route('/users/<int:user_id>/favorites/characters/<int:characters_id>', methods=['DELETE'])
def delete_favorite_character(user_id, characters_id):
    character = Favorites.query.filter_by(characters_id=characters_id, user_id=user_id).first()
    if character is None:
        return jsonify({'error': 'character not found in favorites'}), 404
    db.session.delete(character)
    db.session.commit()
    return jsonify({'msg': 'character removed from favorites!'}), 200

@app.route('/users/<int:user_id>/favorites/planets/<int:planets_id>', methods=['DELETE'])
def delete_favorite_planet(user_id, planets_id):
    planet = Favorites.query.filter_by(planets_id=planets_id, user_id=user_id).first()
    if planet is None:
        return jsonify({'error': 'planet not found in favorites'}), 404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({'msg': 'planet removed from favorites!'}), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
