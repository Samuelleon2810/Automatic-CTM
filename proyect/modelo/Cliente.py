# modelo/Cliente.py
from data.database import db # Instancia de SQLAlchemy
from typing import List

class Cliente(db.Model):
    """
    Clase que representa un Cliente, mapeada a la tabla 'clientes'.
    
    Esta clase es fundamentalmente un Data Transfer Object (DTO) 
    para el ORM
    """
    __tablename__ = 'clientes'
    
    # --- Atributos
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column('cliente_nombre', db.String(100), nullable=False)
    apellido = db.Column('cliente_apellido', db.String(100), nullable=True)
    documento = db.Column('cliente_documento', db.String(20), unique=True, nullable=False)
    
    # Foreign Key
    banco_id = db.Column('cliente_banco', db.Integer, db.ForeignKey('bancos.id'), nullable=False)
    
    # Relaciones
    cuentas = db.relationship('Cuenta', back_populates='titular', lazy='dynamic')
    banco = db.relationship('Banco', back_populates='clientes')

    def __init__(self, nombre: str, apellido: str, documento: str):
        self.nombre = nombre
        self.apellido = apellido
        self.documento = documento

    # --- Métodos de Acceso (Getter) ---
    
    def get_nombre_completo(self) -> str:
        """
        
        Retorna el nombre completo del cliente.
        
        """
        return f"{self.nombre} {self.apellido or ''}".strip()

    def get_documento(self) -> str:
        """
        Retorna el documento del cliente.
        
        """
        return self.documento

    def get_cuentas(self) -> List['Cuenta']:
        """
        Retorna la lista de objetos Cuenta asociados a este cliente.
        
        """
        return self.cuentas.all() # Retorna todas las cuentas asociadas

    def __repr__(self):
        return f"<Cliente {self.id} - {self.get_nombre_completo()} - DNI: {self.documento}>"