# servicio/cajero.py
from modelo.banco import Banco
from modelo.tarjeta import Tarjeta, EstadoTarjeta
from modelo.operacion import Retiro, Deposito, ConsultaSaldo , Operacion

class Cajero:
    """La clase principal que actúa como el controlador del cajero automático."""
    
    def __init__(self, id_cajero: str, banco: Banco):
        self.id = id_cajero
        self.banco = banco # Asociación con el Banco
        self.tarjeta_actual: Tarjeta | None = None

    # --- Flujo de Tarjeta y Autenticación ---
    def insertar_tarjeta(self, numero_tarjeta: str) -> str:
        """Implementa insertarTarjeta(t: Tarjeta)"""
        tarjeta = self.banco.buscar_tarjeta(numero_tarjeta)
        if tarjeta is None:
            return "ERROR: Tarjeta no reconocida por el banco."
        
        if tarjeta.get_estado() == EstadoTarjeta.INVALIDADA:
            return "ERROR: Tarjeta invalidada/bloqueada. Contacte a su banco."
        
        self.tarjeta_actual = tarjeta
        return f"Tarjeta insertada. Ingrese PIN para {tarjeta._Tarjeta__titular}."

    def verificar_pin(self, pin: str) -> tuple[bool, str]:
        if self.tarjeta_actual is None:
            return False, "ERROR: No hay tarjeta insertada."
        
        if self.tarjeta_actual.verificar_pin(pin):
            self.tarjeta_actual.reset_intentos()
            return True, "PIN correcto. Acceso concedido."
        else:
            self.tarjeta_actual.incrementar_falla()
            if self.tarjeta_actual.get_estado() == EstadoTarjeta.INVALIDADA:
                # El Cajero notifica al Banco que la tarjeta debe ser bloqueada
                self.banco.bloquear_tarjeta(self.tarjeta_actual._Tarjeta__numero) 
                return False, "PIN incorrecto. Tarjeta bloqueada. Expulsando tarjeta."
            else:
                intentos = Tarjeta.LIMITE_INTENTOS - self.tarjeta_actual.get_intentos_fallidos()
                return False, f"PIN incorrecto. Le quedan {intentos} intentos."

    def expulsar_tarjeta(self) -> str:
        self.tarjeta_actual = None
        return "Tarjeta expulsada. Gracias por usar el Cajero."

    # --- Flujo de Operaciones ---
    def procesar_retiro(self, monto: float) -> tuple[bool, str]:
        """Implementa procesarRetiro(t: Tarjeta, monto: Double)"""
        if self.tarjeta_actual is None or self.tarjeta_actual.get_estado() != EstadoTarjeta.ACTIVA:
            return False, "Operación no permitida."
        
        cuenta = self.tarjeta_actual.get_cuenta()
        
        # 1. Validación del Banco (Implementa validarTransaccion)
        if not self.banco.validar_transaccion(monto):
            return False, "ERROR: Monto excede el límite global del banco."

        # 2. Intento de retiro en la Cuenta
        if cuenta.retirar(monto):
            # 3. Registro de Operación y Comprobante
            op = Retiro(self.tarjeta_actual._Tarjeta__numero, monto)
            self.banco.registrar_operacion(op)
            self.imprimir_comprobante(op)
            return True, f"Retiro exitoso de ${monto:.2f}. Nuevo saldo: ${cuenta.consultar_saldo():.2f}"
        else:
            # Mensaje de error (saldo o límite diario)
            if monto > cuenta.consultar_saldo():
                 return False, "ERROR: Saldo insuficiente."
            else:
                 return False, "ERROR: Límite diario de retiro excedido."

    def procesar_deposito(self, monto: float) -> tuple[bool, str]:
        """Implementa procesarDeposito(monto: Double)"""
        if self.tarjeta_actual is None or self.tarjeta_actual.get_estado() != EstadoTarjeta.ACTIVA:
            return False, "Operación no permitida."
        
        cuenta = self.tarjeta_actual.get_cuenta()
        
        if cuenta.depositar(monto):
            op = Deposito(self.tarjeta_actual._Tarjeta__numero, monto)
            self.banco.registrar_operacion(op)
            self.imprimir_comprobante(op)
            return True, f"Depósito exitoso de ${monto:.2f}. Nuevo saldo: ${cuenta.consultar_saldo():.2f}"
        else:
            return False, "ERROR: El monto a depositar debe ser positivo."

    def consultar_saldo(self) -> tuple[bool, str]:
        """Implementa consultarSaldo()"""
        if self.tarjeta_actual is None or self.tarjeta_actual.get_estado() != EstadoTarjeta.ACTIVA:
            return False, "Operación no permitida."

        cuenta = self.tarjeta_actual.get_cuenta()
        saldo = cuenta.consultar_saldo()
        
        op = ConsultaSaldo(self.tarjeta_actual._Tarjeta__numero, saldo)
        self.banco.registrar_operacion(op)
        self.imprimir_comprobante(op)
        return True, f"Su saldo actual es: ${saldo:.2f}"


    def imprimir_comprobante(self, operacion: Operacion):
        """Implementa imprimirComprobante()"""
        print("\n--- IMPRIMIENDO COMPROBANTE ---")
        print(f"CAJERO ID: {self.id}")
        print(f"BANCO: {self.banco._Banco__nombre}")
        print(f"TIPO: {operacion.get_tipo()}")
        print(f"FECHA/HORA: {operacion.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}")
        if operacion.get_tipo() != "CONSULTA_SALDO":
            print(f"MONTO: ${operacion.monto:.2f}")
        elif isinstance(operacion, ConsultaSaldo):
             print(f"SALDO ACTUAL: ${operacion.saldo_actual:.2f}")
        print("-------------------------------\n")