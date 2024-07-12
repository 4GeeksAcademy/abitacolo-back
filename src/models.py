from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, Enum, Date, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(80), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    address = Column(String(80), unique=True, nullable=False)

    alquileres = relationship('Alquiler', back_populates='user')
    favoritos = relationship('Favorito', back_populates='user')

    def __repr__(self):
        return f'<User {self.email}>'

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "address": self.address
        }

class Mueble(db.Model):
    __tablename__ = 'mueble'
    
    id = Column(Integer, primary_key=True)
    disponible = Column(Boolean, nullable=False)
    color = Column(String(50), nullable=False)
    espacio = Column(Enum("salón/comedor", "dormitorio", "recibidor", "zona de trabajo", "exterior", "otras", name="espacio_muebles"), nullable=False)
    estilo = Column(Enum("industrial", "clásico", "minimalista", "nórdico", "rústico", "vintage/mid-century", "otras", name="estilo_muebles"), nullable=False)
    precio_mes = Column(Integer, nullable=False)
    medidas = Column(String(50), nullable=False)

    alquileres = relationship('Alquiler', back_populates='mueble')
    favoritos = relationship('Favorito', back_populates='mueble')

    def __repr__(self):
        return f'<Mueble {self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "disponible": self.disponible,
            "color": self.color,
            "espacio": self.espacio.value,
            "estilo": self.estilo.value,
            "precio_mes": self.precio_mes,
            "medidas": self.medidas
        }
    
class Alquiler(db.Model):
    __tablename__ = 'alquiler'
    
    id = Column(Integer, primary_key=True)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    pago_mensual = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    mueble_id = Column(Integer, ForeignKey('mueble.id'), nullable=False)

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
    mueble_id = Column(Integer, ForeignKey('mueble.id'), nullable=False)

    user = relationship('User', back_populates='favoritos')
    mueble = relationship('Mueble', back_populates='favoritos')

    def __repr__(self):
        return f'<Favorito {self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "mueble_id": self.mueble_id,
        }
