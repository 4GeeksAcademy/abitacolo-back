"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for,abort
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Mueble
#from models import Person

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

#Post de Usuario
@app.route('/users', methods=['POST'])
def create_user():
    request = request.json
    if not request or not 'email' in request or not 'password' in request or not 'address' in request:
        abort(400)
    user = User(
        email=request['email'],
        password=request['password'],
        address=request['address'],
        is_active=request.get('is_active', True)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 201
#Get de usuarios
@app.route('/users', methods=['GET'])
def get_all_user():
    all_users = User.query.all()
    return jsonify([user.serialize() for user in all_users])

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user:
        return jsonify({user.serialize()}),201
    else:
        return jsonify({'msg': 'No hemos encontrado el usuario que buscas, prueba a registrarte'})




@app.route('/mueble', methods=['POST'])
def create_mueble():
    request_body = request.get_json()
    
    mueble = Mueble(
        id_codigo=request_body['id_codigo'],
        nombre=request_body['nombre'],
        disponible=request_body['disponible'],
        color=request_body['color'],
        espacio=request_body['espacio'],
        estilo=request_body['estilo'],
        categoria=request_body['categoria'],
        precio_mes=request_body['precio_mes'],
        ancho=request_body['ancho'],
        altura=request_body['altura'],
        fondo=request_body['fondo']

    )
    db.session.add(mueble)
    db.session.commit()
    return jsonify(mueble.serialize()), 201

@app.route('/mueble', methods=['GET'])
def get_all_muebles():
    all_muebles = Mueble.query.all()
    return jsonify([mueble.serialize() for mueble in all_muebles])
@app.route('/mueble/<string:id_codigo>', methods=['GET'])
def get_mueble(id_codigo):
    mueble = Mueble.query.get(id_codigo)
    if mueble:
     return jsonify(mueble.serialize()),201
    else:
        return jsonify({"msg" : "Mueble no encontrado"})

@app.route('/mueble/<string:id_codigo>', methods=['DELETE'])
def delete_mueble(id_codigo):
    mueble = Mueble.query.get(id_codigo)
    if mueble:
        db.session.delete(mueble)
        db.session.commit()
        return jsonify({"msg": "Mueble borrado correctamente"})
    else:
        return jsonify({"msg": "No encontramos el mueble que desea eliminar"})

@app.route('/mueble/<string:id_codigo>', methods=['PUT'])
def modificar_mueble(id_codigo):
   mueble = Mueble.query.get(id_codigo)
   print(mueble)
   request_json = request.get_json()

   if 'nombre' in request_json:
       mueble.nombre = request_json['nombre']
       db.session.commit()
       return jsonify({"Nuevo nombre"  : mueble.nombre})
   else:
       return jsonify({"msg": "No hemos encontrado el mueble para actualizar"})

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
