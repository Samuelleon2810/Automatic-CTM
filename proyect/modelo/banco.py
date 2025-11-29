# modelo/banco.py
from modelo.tarjeta import Tarjeta, EstadoTarjeta
from modelo.operacion import Operacion

class Banco:
    """Clase que representa el Sistema Bancario, administra Tarjetas y Cuentas."""
    
    def __init__(self, nombre: str, limite_max_diario_global: float):
        self.__nombre = nombre
        self.__limite_max_diario_global = limite_max_diario_global # Atributo Global
        # Base de datos en memoria (simulada)
        self.__tarjetas = {} # {numero_tarjeta: objeto Tarjeta}
        self.__registro_operaciones = []

    def agregar_tarjeta(self, tarjeta: Tarjeta):
        self.__tarjetas[tarjeta._Tarjeta__numero] = tarjeta

    def buscar_tarjeta(self, numero: str) -> Tarjeta | None:
        return self.__tarjetas.get(numero)

    def bloquear_tarjeta(self, numero: str):
        """Implementa bloquearTarjeta(t: Tarjeta)"""
        tarjeta = self.buscar_tarjeta(numero)
        if tarjeta:
            tarjeta._Tarjeta__estado = EstadoTarjeta.INVALIDADA
            print(f"[{self.__nombre}] Tarjeta {numero} bloqueada permanentemente.")

    def registrar_operacion(self, operacion: Operacion):
        """Implementa registrarOperacion(op: Operacion)"""
        self.__registro_operaciones.append(operacion)
        print(f"[{self.__nombre}] Operación {operacion.get_tipo()} registrada.")
        
    def validar_transaccion(self, monto: float) -> bool:
        """Implementa validarTransaccion(monto: Double)
        Simplemente verifica el límite máximo global del banco (puede ser más complejo).
        """
        return monto <= self.__limite_max_diario_global