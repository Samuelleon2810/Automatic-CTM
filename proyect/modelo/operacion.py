# modelo/operacion.py
from abc import ABC, abstractmethod
from datetime import datetime

class Operacion(ABC):
    """Clase abstracta base para todas las operaciones."""
    
    def __init__(self, tarjeta_num: str, monto: float):
        self.fecha_hora = datetime.now()
        self.tarjeta_num = tarjeta_num
        self.monto = monto
    
    @abstractmethod
    def get_tipo(self) -> str:
        pass
    
class Retiro(Operacion):
    """Implementa la clase Retiro"""
    def get_tipo(self) -> str:
        return "RETIRO"

class Deposito(Operacion):
    """Implementa la clase Deposito"""
    def get_tipo(self) -> str:
        return "DEPOSITO"

class ConsultaSaldo(Operacion):
    """Implementa la clase ConsultaSaldo"""
    def __init__(self, tarjeta_num: str, saldo_actual: float):
        super().__init__(tarjeta_num, 0.0)
        self.saldo_actual = saldo_actual

    def get_tipo(self) -> str:
        return "CONSULTA_SALDO"