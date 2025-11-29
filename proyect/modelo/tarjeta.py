# modelo/tarjeta.py
from modelo.cuenta import Cuenta
import enum

class EstadoTarjeta(enum.Enum):
    ACTIVA = "ACTIVA"
    INVALIDADA = "INVALIDADA" # Bloqueada por muchos intentos
    EXPULSADA = "EXPULSADA"

class Tarjeta:
    """Clase que representa la Tarjeta de Débito/Crédito."""
    
    LIMITE_INTENTOS = 3

    def __init__(self, numero: str, pin: str, titular: str, cuenta: Cuenta):
        self.__numero = numero
        self.__pin = pin
        self.__titular = titular
        self.__cuenta = cuenta # Asociación con la Cuenta
        self.__intentos_fallidos = 0
        self.__estado = EstadoTarjeta.ACTIVA

    # Getters
    def get_cuenta(self) -> Cuenta:
        """Devuelve el objeto Cuenta asociado (implementa el enlace del diagrama)."""
        return self.__cuenta

    def get_estado(self) -> EstadoTarjeta:
        return self.__estado

    def get_intentos_fallidos(self) -> int:
        return self.__intentos_fallidos

    # Métodos de Operación
    def verificar_pin(self, pin_ingresado: str) -> bool:
        """Implementa verificarPin(pin: String)"""
        if self.__estado == EstadoTarjeta.INVALIDADA:
            return False
        return self.__pin == pin_ingresado

    def incrementar_falla(self):
        """Implementa incrementFalla()"""
        self.__intentos_fallidos += 1
        if self.__intentos_fallidos >= self.LIMITE_INTENTOS:
            self.invalidar()

    def reset_intentos(self):
        """Implementa resetIntentos()"""
        self.__intentos_fallidos = 0

    def invalidar(self):
        """Implementa invalidar()"""
        self.__estado = EstadoTarjeta.INVALIDADA
        # Nota: La llamada a Banco.bloquearTarjeta(t) se haría desde el Cajero o Banco, no aquí directamente.