# modelo/Cuenta.py
from data.database import db 
from decimal import Decimal
from datetime import date
from typing import Optional, Tuple

class Cuenta(db.Model):
    """
    Clase que representa la Cuenta Bancaria, mapeada a la tabla 'cuentas'.
    """
    __tablename__ = 'cuentas'
    
    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    numero_cuenta = db.Column('cuenta_numeroCuenta', db.String(20), unique=True, nullable=False)
    saldo = db.Column('cuenta_saldo', db.Numeric(15, 2), default=Decimal('0.00'))
    limite_diario = db.Column('cuenta_limiteDiario', db.Numeric(15, 2), default=Decimal('1000.00'))
    total_retiros_diarios = db.Column('total_retiros_diarios', db.Numeric(15, 2), default=Decimal('0.00'))
    ultima_fecha_retiro = db.Column(db.Date, default=date.today)
    
    # Foreign Keys
    titular_id = db.Column('cuenta_titular', db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    tarjeta_id = db.Column('cuenta_tarjeta', db.Integer, db.ForeignKey('tarjetas.id'), nullable=True)
    
    # Relaciones
    titular = db.relationship('Cliente', back_populates='cuentas')
    operaciones = db.relationship('Operacion', back_populates='cuenta')
    
    def __init__(self, numero: str, saldo_inicial: float, limite_diario: float = 1000.0):
        self.numero_cuenta = numero
        self.saldo = Decimal(str(saldo_inicial))
        self.limite_diario = Decimal(str(limite_diario))
        self.total_retiros_diarios = Decimal('0.00')
        self.ultima_fecha_retiro = date.today()

    # --- Getters ---
    
    def get_numero(self) -> str:
        return self.numero_cuenta

    def consultar_saldo(self) -> Decimal:
        return self.saldo

    def get_limite_diario(self) -> Decimal:
        return self.limite_diario

    def get_total_retiros_diarios(self) -> Decimal:
        return self.total_retiros_diarios

    # --- Métodos de Operación ---

    def depositar(self, monto: float) -> bool:
        monto_dec = Decimal(str(monto))
        if monto_dec > 0:
            self.saldo += monto_dec # SQLAlchemy registra el cambio
            return True
        return False

    def retirar(self, monto: float) -> Tuple[bool, Optional[str]]:
        """Implementa retirar() con validaciones y persistencia ORM."""
        monto_dec = Decimal(str(monto))
        
        # 1. Verificar y Reiniciar Límite Diario si el día ha cambiado
        if self.ultima_fecha_retiro < date.today():
            self.total_retiros_diarios = Decimal('0.00')
            self.ultima_fecha_retiro = date.today()
        
        # 2. Verificar saldo
        if monto_dec > self.saldo:
            return False, "Saldo insuficiente."

        # 3. Verificar límite diario
        if (self.total_retiros_diarios + monto_dec) > self.limite_diario:
            return False, f"Límite diario de retiro excedido. Máximo: ${self.limite_diario}"
        
        # 4. Realizar retiro
        self.saldo -= monto_dec
        self.actualizar_total_ret(monto_dec)
        
        return True, None

    def actualizar_total_ret(self, monto: Decimal):
        self.total_retiros_diarios += monto
        
    def __repr__(self):
        return f"<Cuenta {self.numero_cuenta} - Saldo: ${self.saldo}>"