from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, Enum, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    name = Column(String(80), nullable=False)
    password = Column(String(80), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    address = Column(String(80), unique=True, nullable=False)
    nationality = Column(String(80), nullable=False)
    birth_date = Column(Date, nullable=False)

    alquileres = relationship('Alquiler', back_populates='user')
    favoritos = relationship('Favorito', back_populates='user')

    def __repr__(self):
        return f'<User {self.email}>'
    
    def generate_password(self, password):
        return bcrypt.generate_password_hash(password)
    
    def create_user(self, email, password, name, address, nationality, birth_date, is_active=True):
        hashed_password = self.generate_password(password).decode('utf-8')
        new_user = User(
            email=email,
            name=name,
            password=hashed_password,
            address=address,
            nationality=nationality,
            birth_date=birth_date,
            is_active=is_active
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "nombre": self.name,
            "is_active": self.is_active,
            "address": self.address,
            "nationality": self.nationality,
            "birth_date": self.birth_date,
            "favourites": [favourite.serialize() for favourite in self.favoritos]
        }

class Mueble(db.Model):
    __tablename__ = 'mueble'
    
    id_codigo = Column(String, primary_key=True)
    nombre = Column(String(50), nullable=False)
    disponible = Column(Boolean, nullable=False)
    color = Column(Enum("Natural", "Blanco / Beige / Gris", "Negro / Gris Oscuro", "Tonos Pastel", "Tonos Vivos", "Dorado / Plateado", name="color_mueble"), nullable=False)
    espacio = Column(Enum("Salón / Comedor", "Dormitorio", "Recibidor", "Zona de Trabajo", "Exterior", "Otras", name="espacio_mueble"), nullable=False)
    estilo = Column(Enum("Industrial", "Clásico", "Minimalista", "Nórdico", "Rústico", "Vintage / Mid-Century", "Otros", name="estilo_mueble"), nullable=False)
    categoria = Column(Enum("Armarios y Cómodas", "Estanterias y Baldas", "Mesas y Escritorios", "Aparadores", "Camas y Cabeceros", "Mesillas", "Sillones y Sofás", "Lámparas", "Sillas y Taburetes", "Percheros", "Marcos y Espejos", "Otros Objetos", name="categoria_mueble"), nullable=False)
    precio_mes = Column(Integer, nullable=False)
    fecha_entrega = Column(String)
    fecha_recogida = Column(String)
    ancho = Column(Float, nullable=False)
    altura = Column(Float, nullable=False)
    fondo = Column(Float, nullable=False)
    personalidad = Column(String, nullable=False)
    imagen = Column(String(255))

    alquileres = relationship('Alquiler', back_populates='mueble')
    favoritos = relationship('Favorito', back_populates='mueble')

    def __repr__(self):
        return f'<Mueble {self.id_codigo}>'

    def serialize(self):
        return {
            "id_codigo": self.id_codigo,
            "nombre": self.nombre,
            "disponible": self.disponible,
            "color": self.color,
            "espacio": self.espacio,
            "estilo": self.estilo,
            "categoria": self.categoria,
            "precio_mes": self.precio_mes,
            "fecha_entrega": self.fecha_entrega,
            "fecha_recogida": self.fecha_recogida,
            "ancho": self.ancho,
            "altura": self.altura,
            "fondo": self.fondo,
            "imagen": self.imagen,
            "personalidad": self.personalidad,
            "favoritos": [favorito.serialize() for favorito in self.favoritos]
        }

class Alquiler(db.Model):
    __tablename__ = 'alquiler'
    
    id = Column(Integer, primary_key=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    pago_mensual = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    mueble_id = Column(String, ForeignKey('mueble.id_codigo'), nullable=False)

    user = relationship('User', back_populates='alquileres')
    mueble = relationship('Mueble', back_populates='alquileres')

    def __repr__(self):
        return f'<Alquiler {self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "pago_mensual": self.pago_mensual,
            "user_id": self.user_id,
            "mueble_id": self.mueble_id
        }

class Favorito(db.Model):
    __tablename__ = "favorito"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    mueble_id = Column(String, ForeignKey('mueble.id_codigo'), nullable=False)

    user = relationship('User', back_populates='favoritos')
    mueble = relationship('Mueble', back_populates='favoritos')

    def __repr__(self):
        return f'<Favorito {self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "mueble_id": self.mueble_id
        }
