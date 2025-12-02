"""
Clase Tarjeta - Representa una tarjeta débito asociada a una cuenta
"""
from enum import Enum
from typing import Optional
import bcrypt
from data.database import db


class EstadoTarjeta(str, Enum):
    """
    Estados posibles de una tarjeta
    """
    ACTIVA = "ACTIVA"
    BLOQUEADA = "BLOQUEADA"
    INACTIVA = "INACTIVA"
    VENCIDA = "VENCIDA"


class Tarjeta(db.Model):
    """
    Representa una tarjeta débito vinculada a una cuenta
    """
    __tablename__ = 'tarjetas'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_tarjeta = db.Column(db.String(20), unique=True, nullable=False, index=True)
    pin_hash = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Enum(EstadoTarjeta), default=EstadoTarjeta.ACTIVA, nullable=False)
    intentos_fallidos = db.Column(db.Integer, default=0)
    max_intentos = db.Column(db.Integer, default=3)
    
    # Foreign Keys
    cuenta_id = db.Column(db.Integer, db.ForeignKey('cuentas.id'), nullable=False, unique=True)
    
    # Relaciones
    cuenta = db.relationship('Cuenta', back_populates='tarjeta')
    
    def __init__(self, numero_tarjeta: str, pin: str = "1234", cuenta=None):
        self.numero_tarjeta = numero_tarjeta
        self.set_pin(pin)
        self.estado = EstadoTarjeta.ACTIVA
        self.intentos_fallidos = 0
        self.max_intentos = 3
        if cuenta:
            self.cuenta = cuenta
    
    def set_pin(self, pin: str) -> None:
        """
        Establece el PIN de la tarjeta (hasheado)
        
        Args:
            pin: PIN en texto plano
        """
        if not pin or len(pin) != 4 or not pin.isdigit():
            raise ValueError("El PIN debe ser de 4 dígitos numéricos")
        
        salt = bcrypt.gensalt()
        self.pin_hash = bcrypt.hashpw(pin.encode('utf-8'), salt).decode('utf-8')
    
    def verificar_pin(self, pin: str) -> bool:
        """
        Verifica si el PIN proporcionado es correcto
        
        Args:
            pin: PIN a verificar
            
        Returns:
            bool: True si el PIN es correcto
        """
        if self.estado != EstadoTarjeta.ACTIVA:
            raise ValueError(f"Tarjeta en estado {self.estado.value}")
        
        try:
            es_correcto = bcrypt.checkpw(
                pin.encode('utf-8'), 
                self.pin_hash.encode('utf-8')
            )
            
            if es_correcto:
                self.reset_intentos()
                return True
            else:
                self.incrementar_falla()
                return False
                
        except Exception as e:
            raise ValueError(f"Error al verificar PIN: {str(e)}")
    
    def incrementar_falla(self) -> None:
        """
        Incrementa el contador de intentos fallidos
        Bloquea la tarjeta si se alcanza el máximo
        """
        self.intentos_fallidos += 1
        
        if self.intentos_fallidos >= self.max_intentos:
            self.estado = EstadoTarjeta.BLOQUEADA
        
        db.session.flush()
    
    def reset_intentos(self) -> None:
        """
        Resetea el contador de intentos fallidos
        """
        self.intentos_fallidos = 0
        db.session.flush()
    
    def invalidar(self) -> None:
        """
        Invalida/bloquea la tarjeta permanentemente
        """
        self.estado = EstadoTarjeta.BLOQUEADA
        db.session.flush()
    
    def activar(self) -> None:
        """
        Activa una tarjeta bloqueada (requiere autorización)
        """
        if self.estado == EstadoTarjeta.BLOQUEADA:
            self.estado = EstadoTarjeta.ACTIVA
            self.intentos_fallidos = 0
            db.session.flush()
    
    def esta_activa(self) -> bool:
        """
        Verifica si la tarjeta está activa
        
        Returns:
            bool: True si está activa
        """
        return self.estado == EstadoTarjeta.ACTIVA
    
    def puede_usarse(self) -> tuple[bool, str]:
        """
        Verifica si la tarjeta puede ser usada
        
        Returns:
            tuple: (puede_usarse, mensaje_error)
        """
        if self.estado == EstadoTarjeta.BLOQUEADA:
            return False, "Tarjeta bloqueada. Contacte al banco."
        
        if self.estado == EstadoTarjeta.INACTIVA:
            return False, "Tarjeta inactiva."
        
        if self.estado == EstadoTarjeta.VENCIDA:
            return False, "Tarjeta vencida."
        
        if not self.cuenta.activa:
            return False, "Cuenta asociada inactiva."
        
        return True, ""
    
    def get_intentos_restantes(self) -> int:
        """
        Obtiene el número de intentos restantes
        
        Returns:
            int: Intentos restantes antes del bloqueo
        """
        return max(0, self.max_intentos - self.intentos_fallidos)
    
    @staticmethod
    def buscar_por_numero(numero_tarjeta: str) -> Optional['Tarjeta']:
        """
        Busca una tarjeta por su número
        
        Args:
            numero_tarjeta: Número de tarjeta
            
        Returns:
            Tarjeta o None si no existe
        """
        return Tarjeta.query.filter_by(numero_tarjeta=numero_tarjeta).first()
    
    def __repr__(self):
        return f"<Tarjeta {self.numero_tarjeta} - Estado: {self.estado.value}>"
