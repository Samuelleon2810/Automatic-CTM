"""
Configuración de la base de datos con SQLAlchemy
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from BACKEND.services import Cajero

class Base(DeclarativeBase):
    """Clase base para todos los modelos"""
    pass

# Instancia global de SQLAlchemy
db = SQLAlchemy(model_class=Base)


def init_db(app):
    """
    Inicializa la base de datos con la aplicación Flask
    
    Args:
        app: Instancia de Flask
    """
    db.init_app(app)
    
    with app.app_context():
        # Importar todos los modelos para que SQLAlchemy los conozca
        from modelo import (
            Banco, Cliente, Cuenta, Tarjeta, Operacion, RegistroOperaciones
        )
        
        # Crear todas las tablas
        db.create_all()
        print(" Base de datos inicializada correctamente")


def reset_db(app):
    """
    Elimina y recrea todas las tablas (⚠️ CUIDADO: elimina todos los datos)
    
    Args:
        app: Instancia de Flask
    """
    with app.app_context():
        db.drop_all()
        db.create_all()
        print(" Base de datos reseteada correctamente")


def seed_db(app):
    """
    Carga datos iniciales en la base de datos
    
    Args:
        app: Instancia de Flask
    """
    with app.app_context():
        from data.datosIniciales import cargar_datos_iniciales
        cargar_datos_iniciales()
        print(" Datos iniciales cargados correctamente")