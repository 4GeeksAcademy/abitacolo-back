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
from models import db, User, Mueble, Favorito
from sqlalchemy.orm.exc import NoResultFound
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
    data = request.get_json()
    if not data or not 'email' in data or not 'password' in data or not 'address' in data:
        abort(400)
    user = User(
        email=data['email'],
        password=data['password'],
        address=data['address'],
        is_active=data.get('is_active', True)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 201
#Get de todos los usuarios
@app.route('/users', methods=['GET'])
def get_all_user():
    all_users = User.query.all()
    return jsonify([user.serialize() for user in all_users])
#Get de un usuario único
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    selectedUser = User.query.get(id)
    
    if selectedUser:
        return jsonify(selectedUser.serialize()),201
    else:
        return jsonify({'msg': 'No hemos encontrado el usuario que buscas, prueba a registrarte'})
#Borrar usuario
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    selectedUser = User.query.get(id)
    if selectedUser:
        db.session.delete(selectedUser)
        db.session.commit()
        return jsonify({'msg': f'Hemos borrado correctamente el usuario {id}'}),201 
    else:
        return jsonify({'msg': 'No hemos encontrado el usuario'})

#PUT USUARIO
@app.route('/users/<int:id>', methods=['PUT'])
def editar_usuario(id):
    try:
        user = User.query.filter_by(id=id).one()
    except NoResultFound:
        abort(404, description="Usuario no encontrado")

    request_json = request.get_json()

    if not request_json:
        abort(400, description="No se proporcionaron datos para actualizar")

    # Lista de campos permitidos para actualizar
    campos_permitidos = ['email', 'password', 'address',
                         ]

    # Actualizar los campos del mueble
    for key, value in request_json.items():
        if key in campos_permitidos:
            setattr(user, key, value)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Error al guardar en la base de datos: {str(e)}")

    return jsonify({
        "mensaje": "Usuario actualizado correctamente",
        "mueble": user.serialize()
    }), 200   

#GET Favoritos
@app.route('/user/favourites', methods=['GET'])
def get_userFavourites():
   favourites = Favorito.query.all()
   all_user_favourites = list(map(lambda x : x.serialize(), favourites))
    
   return jsonify(all_user_favourites),201

#Post de Favoritos

""" @app.route('/favourite/mueble/<string:id_codigo>', methods=['POST'])
def post_userFavourites(id_codigo):
    data = request.get_json()
    user_id = data.get("user_id")

    user = User.query.get(id)

    mueble_favourite = Mueble.query.get(id_codigo)

    user_favourite = Favorito(
       user_id = user.id,
        mueble_id = id_codigo
    )

    db.session.add(user_favourite)
    db.session.commit()

    return jsonify(user_favourite.serialize()),201 """

@app.route('/favourite/mueble/<string:id_codigo>', methods=['POST'])
def post_user_favourites(id_codigo):
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    mueble = Mueble.query.get(id_codigo)
    if not mueble:
        return jsonify({"error": "Mueble not found"}), 404

    existing_favorite = Favorito.query.filter_by(user_id=user_id, mueble_id=id_codigo).first()
    if existing_favorite:
        return jsonify({"error": "Favorite already exists"}), 409

    user_favourite = Favorito(
        user_id=user_id,
        mueble_id=id_codigo
    )

    db.session.add(user_favourite)
    db.session.commit()

    return jsonify(user_favourite.serialize()), 201
    

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
        fondo=request_body['fondo'],
        personalidad = request_body['personalidad']


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
    try:
        mueble = Mueble.query.filter_by(id_codigo=id_codigo).one()
    except NoResultFound:
        abort(404, description="Mueble no encontrado")

    request_json = request.get_json()

    if not request_json:
        abort(400, description="No se proporcionaron datos para actualizar")

    # Lista de campos permitidos para actualizar
    campos_permitidos = ['nombre', 'disponible', 'color', 'espacio', 'estilo', 'categoria', 
                         'precio_mes', 'fecha_entrega', 'fecha_recogida', 'ancho', 'altura', 
                         'fondo', 'personalidad', 'imagen']

    # Actualizar los campos del mueble
    for key, value in request_json.items():
        if key in campos_permitidos:
            setattr(mueble, key, value)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        abort(500, description=f"Error al guardar en la base de datos: {str(e)}")

    return jsonify({
        "mensaje": "Mueble actualizado correctamente",
        "mueble": mueble.serialize()
    }), 200
  
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
