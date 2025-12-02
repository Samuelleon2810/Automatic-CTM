"""
Clase Cajero - Representa un cajero automático (ATM)
"""
from typing import Optional
from decimal import Decimal
from data.database import db


class Cajero(db.Model):
    """
    Representa un cajero automático (ATM) físico
    """
    __tablename__ = 'cajeros'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    ubicacion = db.Column(db.String(200), nullable=False)
    monto_cajero = db.Column(db.Numeric(15, 2), default=100000.00)
    activo = db.Column(db.Boolean, default=True)
    
    # Foreign Keys
    banco_id = db.Column(db.Integer, db.ForeignKey('bancos.id'), nullable=False)
    
    # Relaciones
    banco = db.relationship('Banco', back_populates='cajeros')
    operaciones = db.relationship('Operacion', back_populates='cajero')
    
    # Sesión actual
    tarjeta_insertada_id = db.Column(db.Integer, db.ForeignKey('tarjetas.id'), nullable=True)
    tarjeta_insertada = db.relationship('Tarjeta', foreign_keys=[tarjeta_insertada_id])
    
    def __init__(self, codigo: str, ubicacion: str, monto_inicial: float = 100000.00):
        self.codigo = codigo
        self.ubicacion = ubicacion
        self.monto_cajero = Decimal(str(monto_inicial))
        self.activo = True
    
    def insertar_tarjeta(self, tarjeta: 'Tarjeta') -> tuple[bool, str]:
        """
        Inserta una tarjeta en el cajero
        
        Args:
            tarjeta: Tarjeta a insertar
            
        Returns:
            tuple: (exito, mensaje)
        """
        if not self.activo:
            return False, "Cajero fuera de servicio"
        
        if self.tarjeta_insertada:
            return False, "Ya hay una tarjeta insertada"
        
        # Verificar que la tarjeta puede usarse
        puede_usarse, mensaje = tarjeta.puede_usarse()
        if not puede_usarse:
            return False, mensaje
        
        self.tarjeta_insertada = tarjeta
        db.session.flush()
        return True, "Tarjeta insertada correctamente"
    
    def expulsar_tarjeta(self) -> None:
        """
        Expulsa la tarjeta del cajero
        """
        self.tarjeta_insertada = None
        db.session.flush()
    
    def solicitar_pin(self) -> str:
        """
        Solicita el PIN (en implementación real vendría del frontend)
        
        Returns:
            str: Placeholder para el PIN
        """
        # En la implementación real, esto vendría del frontend
        return ""
    
    def procesar_retiro(self, tarjeta: 'Tarjeta', monto: float) -> tuple[bool, str]:
        """
        Procesa un retiro de efectivo
        
        Args:
            tarjeta: Tarjeta que realiza el retiro
            monto: Monto a retirar
            
        Returns:
            tuple: (exito, mensaje)
        """
        from modelo.Operacion import Retiro
        
        try:
            # Validar que hay efectivo suficiente
            if self.monto_cajero < Decimal(str(monto)):
                return False, "Cajero sin efectivo suficiente"
            
            # Crear y ejecutar operación de retiro
            retiro = Retiro(tarjeta.cuenta, monto, self)
            db.session.add(retiro)
            
            if retiro.ejecutar():
                return True, f"Retiro exitoso de ${monto}"
            else:
                return False, retiro.mensaje_error or "Error al procesar retiro"
                
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"
    
    def procesar_deposito(self, tarjeta: 'Tarjeta', monto: float, 
                         tipo: str = 'EFECTIVO') -> tuple[bool, str]:
        """
        Procesa un depósito
        
        Args:
            tarjeta: Tarjeta que realiza el depósito
            monto: Monto a depositar
            tipo: Tipo de depósito ('EFECTIVO' o 'CHEQUE')
            
        Returns:
            tuple: (exito, mensaje)
        """
        from modelo.Operacion import Deposito
        
        try:
            # Crear y ejecutar operación de depósito
            deposito = Deposito(tarjeta.cuenta, monto, tipo, self)
            db.session.add(deposito)
            
            if deposito.ejecutar():
                return True, f"Depósito exitoso de ${monto}"
            else:
                return False, deposito.mensaje_error or "Error al procesar depósito"
                
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"
    
    def consultar_saldo(self, tarjeta: 'Tarjeta') -> tuple[bool, float, str]:
        """
        Consulta el saldo de una cuenta
        
        Args:
            tarjeta: Tarjeta asociada a la cuenta
            
        Returns:
            tuple: (exito, saldo, mensaje)
        """
        from modelo.Operacion import ConsultaSaldo
        
        try:
            # Crear y ejecutar operación de consulta
            consulta = ConsultaSaldo(tarjeta.cuenta, self)
            db.session.add(consulta)
            
            if consulta.ejecutar():
                saldo = tarjeta.cuenta.consultar_saldo()
                return True, saldo, "Consulta exitosa"
            else:
                return False, 0.0, consulta.mensaje_error or "Error al consultar saldo"
                
        except Exception as e:
            db.session.rollback()
            return False, 0.0, f"Error: {str(e)}"
    
    def imprimir_comprobante(self, operacion: 'Operacion') -> str:
        """
        Genera un comprobante de operación
        
        Args:
            operacion: Operación realizada
            
        Returns:
            str: Comprobante en formato texto
        """
        from datetime import datetime
        
        comprobante = f"""
{'='*50}
          BANCO - COMPROBANTE
{'='*50}
Cajero: {self.codigo}
Ubicación: {self.ubicacion}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
{'='*50}
Operación: {operacion.__class__.__name__}
Cuenta: {operacion.cuenta.numero_cuenta}
{'='*50}
"""
        
        if operacion.monto:
            comprobante += f"Monto: ${operacion.monto}\n"
        
        if hasattr(operacion, 'saldo_consultado'):
            comprobante += f"Saldo Disponible: ${operacion.saldo_consultado}\n"
        
        comprobante += f"""{'='*50}
Estado: {'EXITOSA' if operacion.exitosa else 'FALLIDA'}
"""
        
        if operacion.mensaje_error:
            comprobante += f"Mensaje: {operacion.mensaje_error}\n"
        
        comprobante += f"{'='*50}\n"
        
        return comprobante
    
    def tiene_efectivo_suficiente(self, monto: float) -> bool:
        """
        Verifica si el cajero tiene efectivo suficiente
        
        Args:
            monto: Monto a verificar
            
        Returns:
            bool: True si hay efectivo suficiente
        """
        return self.monto_cajero >= Decimal(str(monto))
    
    def recargar_efectivo(self, monto: float) -> None:
        """
        Recarga efectivo en el cajero
        
        Args:
            monto: Monto a recargar
        """
        self.monto_cajero += Decimal(str(monto))
        db.session.flush()
    
    def __repr__(self):
        return f"<Cajero {self.codigo} - {self.ubicacion}>"
