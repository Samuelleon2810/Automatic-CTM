
class Cuenta:
    """Clase que representa la Cuenta Bancaria."""
    
    def __init__(self, numero: str, saldo_inicial: float, limite_diario: float = 1000.0):
        self.__numero = numero
        self.__saldo = saldo_inicial
        self.__limite_diario = limite_diario
        self.__total_retiros_diarios = 0.0

    # Getters (atributos de sólo lectura)
    def get_numero(self) -> str:
        return self.__numero

    def consultar_saldo(self) -> float:
        """Implementa consultarSaldo()"""
        return self.__saldo

    def get_limite_diario(self) -> float:
        return self.__limite_diario

    def get_total_retiros_diarios(self) -> float:
        return self.__total_retiros_diarios

    # Métodos de Operación
    def depositar(self, monto: float) -> bool:
        """Implementa depositar()"""
        if monto > 0:
            self.__saldo += monto
            return True
        return False

    def retirar(self, monto: float) -> bool:
        """Implementa retirar()"""
        # 1. Verificar saldo
        if monto > self.__saldo:
            return False # Saldo insuficiente

        # 2. Verificar límite diario
        if (self.__total_retiros_diarios + monto) > self.__limite_diario:
            return False # Límite excedido
        
        # 3. Realizar retiro
        self.__saldo -= monto
        self.actualizar_total_ret(monto)
        return True

    def actualizar_total_ret(self, monto: float):
        """Implementa actualizarTotalRet(monto: Double)"""
        self.__total_retiros_diarios += monto