"""
Clase Operacion - Clase base abstracta para operaciones del ATM
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from decimal import Decimal
from data.database import db


class Operacion(db.Model, ABC):
    """
    Clase abstracta base para todas las operaciones
    """
    __tablename__ = 'operaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)  # Discriminador para herencia
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    monto = db.Column(db.Numeric(15, 2), nullable=True)
    descripcion = db.Column(db.Text)
    exitosa = db.Column(db.Boolean, default=False)
    mensaje_error = db.Column(db.String(200))
    
    # Foreign Keys
    cuenta_id = db.Column(db.Integer, db.ForeignKey('cuentas.id'), nullable=False)
    cajero_id = db.Column(db.Integer, db.ForeignKey('cajeros.id'))
    
    # Relaciones
    cuenta = db.relationship('Cuenta', back_populates='operaciones')
    cajero = db.relationship('Cajero', back_populates='operaciones')
    
    # Herencia de tabla única
    __mapper_args__ = {
        'polymorphic_identity': 'operacion',
        'polymorphic_on': tipo,
        'with_polymorphic': '*'
    }
    
    def __init__(self, cuenta, monto: Optional[float] = None, descripcion: str = ""):
        self.cuenta = cuenta
        self.monto = Decimal(str(monto)) if monto else None
        self.descripcion = descripcion
        self.fecha = datetime.now()
    
    @abstractmethod
    def ejecutar(self) -> bool:
        """
        Ejecuta la operación (debe ser implementado por subclases)
        
        Returns:
            bool: True si la operación fue exitosa
        """
        pass
    
    def marcar_exitosa(self) -> None:
        """Marca la operación como exitosa"""
        self.exitosa = True
        db.session.flush()
    
    def marcar_fallida(self, mensaje: str) -> None:
        """
        Marca la operación como fallida
        
        Args:
            mensaje: Mensaje de error
        """
        self.exitosa = False
        self.mensaje_error = mensaje
        db.session.flush()
    
    def __repr__(self):
        return f"<{self.__class__.__name__} ${self.monto} - {self.fecha}>"


class Retiro(Operacion):
    """
    Operación de retiro de efectivo
    """
    __mapper_args__ = {
        'polymorphic_identity': 'retiro'
    }
    
    def __init__(self, cuenta, monto: float, cajero=None):
        super().__init__(cuenta, monto, f"Retiro de efectivo - ${monto}")
        self.cajero = cajero
    
    def ejecutar(self) -> bool:
        """
        Ejecuta el retiro de la cuenta
        
        Returns:
            bool: True si el retiro fue exitoso
        """
        try:
            # Validar que el cajero tenga efectivo suficiente
            if self.cajero and self.cajero.monto_cajero < float(self.monto):
                self.marcar_fallida("Cajero sin efectivo suficiente")
                return False
            
            # Intentar realizar el retiro
            self.cuenta.retirar(float(self.monto))
            
            # Actualizar efectivo del cajero
            if self.cajero:
                self.cajero.monto_cajero -= float(self.monto)
            
            self.marcar_exitosa()
            db.session.commit()
            return True
            
        except ValueError as e:
            self.marcar_fallida(str(e))
            db.session.rollback()
            return False
        except Exception as e:
            self.marcar_fallida(f"Error inesperado: {str(e)}")
            db.session.rollback()
            return False


class Deposito(Operacion):
    """
    Operación de depósito de efectivo o cheque
    """
    tipo_deposito = db.Column(db.String(20))  # 'EFECTIVO' o 'CHEQUE'
    
    __mapper_args__ = {
        'polymorphic_identity': 'deposito'
    }
    
    def __init__(self, cuenta, monto: float, tipo_deposito: str = 'EFECTIVO', cajero=None):
        super().__init__(cuenta, monto, f"Depósito {tipo_deposito} - ${monto}")
        self.tipo_deposito = tipo_deposito
        self.cajero = cajero
    
    def ejecutar(self) -> bool:
        """
        Ejecuta el depósito en la cuenta
        
        Returns:
            bool: True si el depósito fue exitoso
        """
        try:
            # Realizar el depósito
            self.cuenta.depositar(float(self.monto))
            
            # Actualizar efectivo del cajero si es depósito de efectivo
            if self.cajero and self.tipo_deposito == 'EFECTIVO':
                self.cajero.monto_cajero += float(self.monto)
            
            self.marcar_exitosa()
            db.session.commit()
            return True
            
        except ValueError as e:
            self.marcar_fallida(str(e))
            db.session.rollback()
            return False
        except Exception as e:
            self.marcar_fallida(f"Error inesperado: {str(e)}")
            db.session.rollback()
            return False


class ConsultaSaldo(Operacion):
    """
    Operación de consulta de saldo
    """
    saldo_consultado = db.Column(db.Numeric(15, 2))
    
    __mapper_args__ = {
        'polymorphic_identity': 'consulta_saldo'
    }
    
    def __init__(self, cuenta, cajero=None):
        super().__init__(cuenta, None, "Consulta de saldo")
        self.cajero = cajero
    
    def ejecutar(self) -> bool:
        """
        Ejecuta la consulta de saldo
        
        Returns:
            bool: True si la consulta fue exitosa
        """
        try:
            self.saldo_consultado = Decimal(str(self.cuenta.consultar_saldo()))
            self.monto = self.saldo_consultado
            self.marcar_exitosa()
            db.session.commit()
            return True
            
        except Exception as e:
            self.marcar_fallida(f"Error al consultar saldo: {str(e)}")
            db.session.rollback()
            return False


class PagoRecibo(Operacion):
    """
    Operación de pago de recibos
    """
    nombre_servicio = db.Column(db.String(100))
    nit_recibo = db.Column(db.String(20))
    numero_referencia = db.Column(db.String(50))
    
    __mapper_args__ = {
        'polymorphic_identity': 'pago_recibo'
    }
    
    def __init__(self, cuenta, monto: float, nombre_servicio: str, 
                 numero_referencia: str, nit_recibo: str = "", cajero=None):
        super().__init__(cuenta, monto, f"Pago de {nombre_servicio} - ${monto}")
        self.nombre_servicio = nombre_servicio
        self.numero_referencia = numero_referencia
        self.nit_recibo = nit_recibo
        self.cajero = cajero
    
    def ejecutar(self) -> bool:
        """
        Ejecuta el pago del recibo
        
        Returns:
            bool: True si el pago fue exitoso
        """
        try:
            # Validar saldo suficiente
            if self.cuenta.saldo < self.monto:
                self.marcar_fallida("Saldo insuficiente para pago")
                return False
            
            # Realizar el pago (débito de la cuenta)
            self.cuenta.saldo -= self.monto
            
            self.marcar_exitosa()
            db.session.commit()
            return True
            
        except Exception as e:
            self.marcar_fallida(f"Error al procesar pago: {str(e)}")
            db.session.rollback()
            return False


class CompraEntradas(Operacion):
    """
    Operación de compra de entradas
    """
    nombre_evento = db.Column(db.String(100))
    codigo_entrada = db.Column(db.String(50))
    cantidad = db.Column(db.Integer)
    
    __mapper_args__ = {
        'polymorphic_identity': 'compra_entradas'
    }
    
    def __init__(self, cuenta, monto: float, nombre_evento: str, 
                 cantidad: int, cajero=None):
        super().__init__(cuenta, monto, f"Compra {cantidad} entrada(s) - {nombre_evento}")
        self.nombre_evento = nombre_evento
        self.cantidad = cantidad
        self.cajero = cajero
    
    def ejecutar(self) -> bool:
        """
        Ejecuta la compra de entradas
        
        Returns:
            bool: True si la compra fue exitosa
        """
        try:
            # Validar saldo suficiente
            if self.cuenta.saldo < self.monto:
                self.marcar_fallida("Saldo insuficiente para compra")
                return False
            
            # Generar código de entrada
            import random
            self.codigo_entrada = f"ENT-{random.randint(100000, 999999)}"
            
            # Realizar el pago
            self.cuenta.saldo -= self.monto
            
            self.marcar_exitosa()
            db.session.commit()
            return True
            
        except Exception as e:
            self.marcar_fallida(f"Error al procesar compra: {str(e)}")
            db.session.rollback()
            return False
