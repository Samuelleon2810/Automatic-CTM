"""
Clase Banco - Gestiona clientes, cuentas y políticas del banco
"""
from typing import List, Optional
from datetime import date
from data.database import db
from .Operacion import Operacion

class Banco(db.Model):
    """
    Representa el banco que gestiona clientes, cuentas y operaciones
    """
    __tablename__ = 'bancos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    limite_max_diario_global = db.Column(db.Numeric(15, 2), default=5000.00)
    
    # Relaciones
    clientes = db.relationship('Cliente', back_populates='banco', cascade='all, delete-orphan')
    cajeros = db.relationship('Cajero', back_populates='banco', cascade='all, delete-orphan')
    
    def __init__(self, nombre: str, codigo: str, limite_max_diario_global: float = 5000.00):
        self.nombre = nombre
        self.codigo = codigo
        self.limite_max_diario_global = limite_max_diario_global
    
    def emitir_tarjeta(self, cuenta) -> 'Tarjeta':
        """
        Emite una nueva tarjeta para una cuenta
        
        Args:
            cuenta: Cuenta asociada a la tarjeta
            
        Returns:
            Tarjeta: Nueva tarjeta creada
        """
        from modelo.Tarjeta import Tarjeta
        import random
        
        # Generar número de tarjeta único
        numero_tarjeta = self._generar_numero_tarjeta()
        
        tarjeta = Tarjeta(
            numero_tarjeta=numero_tarjeta,
            cuenta=cuenta
        )
        
        db.session.add(tarjeta)
        db.session.flush()
        
        return tarjeta
    
    def bloquear_tarjeta(self, tarjeta: 'Tarjeta') -> None:
        """
        Bloquea una tarjeta por seguridad
        
        Args:
            tarjeta: Tarjeta a bloquear
        """
        tarjeta.invalidar()
        db.session.commit()
    
    def validar_transaccion(self, cuenta: 'Cuenta', monto: float) -> bool:
        """
        Valida si una transacción puede realizarse
        
        Args:
            cuenta: Cuenta que realizará la transacción
            monto: Monto de la transacción
            
        Returns:
            bool: True si la transacción es válida
        """
        # Validar saldo suficiente
        if cuenta.saldo < monto:
            return False
        
        # Validar límite diario de la cuenta
        total_retirado_hoy = self.get_total_retirado_hoy(cuenta, date.today())
        if total_retirado_hoy + monto > cuenta.limite_diario:
            return False
        
        # Validar límite global del banco
        if total_retirado_hoy + monto > self.limite_max_diario_global:
            return False
        
        return True
    
    def registrar_operacion(self, operacion: 'Operacion') -> None:
        """
        Registra una operación en el sistema
        
        Args:
            operacion: Operación a registrar
        """
        from modelo.RegistroOperaciones import RegistroOperaciones
        
        registro = RegistroOperaciones.get_instance()
        registro.registrar(operacion)
    
    def get_total_retirado_hoy(self, cuenta: 'Cuenta', fecha: date) -> float:
        """
        Obtiene el total retirado hoy de una cuenta
        
        Args:
            cuenta: Cuenta a consultar
            fecha: Fecha de consulta
            
        Returns:
            float: Total retirado en el día
        """
        from modelo.Operacion import Retiro
        from datetime import datetime
        
        inicio_dia = datetime.combine(fecha, datetime.min.time())
        fin_dia = datetime.combine(fecha, datetime.max.time())
        
        total = db.session.query(db.func.sum(Retiro.monto)).filter(
            Retiro.cuenta_id == cuenta.id,
            Retiro.fecha >= inicio_dia,
            Retiro.fecha <= fin_dia
        ).scalar()
        
        return float(total) if total else 0.0
    
    def _generar_numero_tarjeta(self) -> str:
        """
        Genera un número de tarjeta único
        
        Returns:
            str: Número de tarjeta formato XXXX-XXXX-XXXX-XXXX
        """
        import random
        from modelo.Tarjeta import Tarjeta
        
        while True:
            # Generar 16 dígitos
            digitos = [str(random.randint(0, 9)) for _ in range(16)]
            numero = '-'.join([
                ''.join(digitos[0:4]),
                ''.join(digitos[4:8]),
                ''.join(digitos[8:12]),
                ''.join(digitos[12:16])
            ])
            
            # Verificar que no exista
            existe = Tarjeta.query.filter_by(numero_tarjeta=numero).first()
            if not existe:
                return numero
    
    def agregar_cliente(self, cliente: 'Cliente') -> None:
        """
        Agrega un cliente al banco
        
        Args:
            cliente: Cliente a agregar
        """
        cliente.banco = self
        db.session.add(cliente)
        db.session.commit()
    
    def obtener_cliente_por_documento(self, documento: str) -> Optional['Cliente']:
        """
        Obtiene un cliente por su documento
        
        Args:
            documento: Documento del cliente
            
        Returns:
            Cliente o None si no existe
        """
        from modelo.Cliente import Cliente
        return Cliente.query.filter_by(documento=documento, banco_id=self.id).first()
    
    def __repr__(self):
        return f"<Banco {self.nombre} ({self.codigo})>"
