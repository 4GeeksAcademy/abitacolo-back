"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""

import os
from flask import Flask, request, jsonify, abort
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import timedelta
from sqlalchemy.orm.exc import NoResultFound
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_bcrypt import Bcrypt

from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Mueble, Favorito

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "clave_secreta")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=30)
app.url_map.strict_slashes = False
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

db_url = os.getenv("DATABASE_URL", "sqlite:////tmp/test.db").replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or not all(key in data for key in ('email', 'password', 'address')):
        abort(400, description="Faltan campos por rellenar.")
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(
        email=data['email'],
        name=data['name'],
        password=hashed_password,
        address=data['address'],
        nationality=data['nationality'],
        birth_date=data['birth_date'],
        is_active=data.get('is_active', True)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 201

@app.route('/users', methods=['GET'])
def get_all_users():
    all_users = User.query.all()
    return jsonify([user.serialize() for user in all_users]), 200

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(404, description="User not found")
    return jsonify(user.serialize()), 200

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if not user:
        abort(404, description="User not found")
    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": f"User {id} deleted successfully"}), 200

@app.route('/users/<int:id>', methods=['PUT'])
def edit_user(id):
    try:
        user = User.query.filter_by(id=id).one()
    except NoResultFound:
        abort(404, description="User not found")
    
    data = request.get_json()
    if not data:
        abort(400, description="No data provided for update")
    
    allowed_fields = ['email', 'password', 'address']
    for key, value in data.items():
        if key in allowed_fields:
            setattr(user, key, value)
    
    db.session.commit()
    return jsonify({"msg": "User updated successfully", "user": user.serialize()}), 200

@app.route('/user/favourites', methods=['GET'])
def get_user_favourites():
    favourites = Favorito.query.all()
    return jsonify([fav.serialize() for fav in favourites]), 200

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

    user_favourite = Favorito(user_id=user_id, mueble_id=id_codigo)
    db.session.add(user_favourite)
    db.session.commit()

    return jsonify(user_favourite.serialize()), 201

@app.route('/mueble', methods=['POST'])
def create_muebles():
    request_body = request.get_json()

    if isinstance(request_body, list):
        muebles = []
        for mueble_data in request_body:
            required_fields = ['id_codigo', 'nombre', 'disponible', 'color', 'espacio', 'estilo', 'categoria', 'precio_mes', 'ancho', 'altura', 'fondo', 'personalidad']
            for field in required_fields:
                if field not in mueble_data:
                    return jsonify({"error": f"Missing field: {field}"}), 400

            mueble = Mueble(
                id_codigo=mueble_data['id_codigo'],
                nombre=mueble_data['nombre'],
                disponible=mueble_data['disponible'],
                color=mueble_data['color'],
                espacio=mueble_data['espacio'],
                estilo=mueble_data['estilo'],
                categoria=mueble_data['categoria'],
                precio_mes=mueble_data['precio_mes'],
                ancho=mueble_data['ancho'],
                altura=mueble_data['altura'],
                fondo=mueble_data['fondo'],
                personalidad=mueble_data['personalidad']
            )
            db.session.add(mueble)
            muebles.append(mueble)

        db.session.commit()
        return jsonify([mueble.serialize() for mueble in muebles]), 201

    elif isinstance(request_body, dict):
        required_fields = ['id_codigo', 'nombre', 'disponible', 'color', 'espacio', 'estilo', 'categoria', 'precio_mes', 'ancho', 'altura', 'fondo', 'personalidad']
        for field in required_fields:
            if field not in request_body:
                return jsonify({"error": f"Missing field: {field}"}), 400

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
            personalidad=request_body['personalidad']
        )
        db.session.add(mueble)
        db.session.commit()
        return jsonify(mueble.serialize()), 201

    return jsonify({"error": "Request body must be a JSON object or a list of JSON objects"}), 400

@app.route('/mueble', methods=['GET'])
def get_all_muebles():
    all_muebles = Mueble.query.all()
    return jsonify([mueble.serialize() for mueble in all_muebles]), 200

@app.route('/mueble/<string:id_codigo>', methods=['GET'])
def get_mueble(id_codigo):
    mueble = Mueble.query.get(id_codigo)
    if not mueble:
        abort(404, description="Mueble not found")
    return jsonify(mueble.serialize()), 200

@app.route('/mueble/<string:id_codigo>', methods=['DELETE'])
def delete_mueble(id_codigo):
    mueble = Mueble.query.get(id_codigo)
    if not mueble:
        abort(404, description="Mueble not found")
    db.session.delete(mueble)
    db.session.commit()
    return jsonify({"msg": f"Mueble {id_codigo} deleted successfully"}), 200

@app.route('/mueble/<string:id_codigo>', methods=['PUT'])
def modify_mueble(id_codigo):
    try:
        mueble = Mueble.query.filter_by(id_codigo=id_codigo).one()
    except NoResultFound:
        abort(404, description="Mueble not found")

    data = request.get_json()
    if not data:
        abort(400, description="No data provided for update")

    allowed_fields = ['nombre', 'disponible', 'color', 'espacio', 'estilo', 'categoria', 'precio_mes', 'fecha_entrega', 'fecha_recogida', 'ancho', 'altura', 'fondo', 'personalidad', 'imagen']
    for key, value in data.items():
        if key in allowed_fields:
            setattr(mueble, key, value)

    db.session.commit()
    return jsonify({"msg": "Mueble updated successfully", "mueble": mueble.serialize()}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not all(key in data for key in ('email', 'password')):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not bcrypt.check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"token": access_token, "user": user.serialize()}), 200

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify({"id": current_user_id, "message": "Access to protected route"}), 200

@app.route('/favoritos/<int:id>', methods=['DELETE'])
def delete_favorito(id):
    favorito = Favorito.query.get(id)
    
    if favorito is None:
        abort(404, description="Favorito no encontrado")
    
    try:
        db.session.delete(favorito)
        db.session.commit()
        return jsonify({"message": "Favorito eliminado con éxito"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=False)
