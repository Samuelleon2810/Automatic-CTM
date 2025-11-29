# ui/ui_cajero.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QStackedWidget,
    QMessageBox, QApplication, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSlot
from servicio.cajero import Cajero
from modelo.tarjeta import Tarjeta
from modelo.cuenta import Cuenta

class VentanaCajero(QMainWindow):
    def __init__(self, cajero: Cajero):
        super().__init__()
        self.setWindowTitle("ATM - DESARROLLO CAJERO")
        self.setGeometry(100, 100, 500, 400)
        
        self.cajero = cajero
        self.setup_ui()
        self.show()

    def setup_ui(self):
        # 1. Widget Contenedor Central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 2. QStackedWidget para las pantallas
        self.stacked_widget = QStackedWidget()
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.stacked_widget)

        # 3. Definición de Pantallas
        self.screen_inicio = self.create_screen_inicio()
        self.screen_pin = self.create_screen_pin()
        self.screen_menu = self.create_screen_menu()
        self.screen_retiro = self.create_screen_retiro()
        self.screen_message = self.create_screen_message()

        self.stacked_widget.addWidget(self.screen_inicio)
        self.stacked_widget.addWidget(self.screen_pin)
        self.stacked_widget.addWidget(self.screen_menu)
        self.stacked_widget.addWidget(self.screen_retiro)
        self.stacked_widget.addWidget(self.screen_message)

        self.stacked_widget.setCurrentIndex(0) # Inicia en la pantalla de inicio

    # --- Creación de Pantallas ---

    def create_screen_inicio(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(QLabel("<h1>Bienvenido al Cajero Automático</h1>", alignment=Qt.AlignmentFlag.AlignCenter))
        layout.addWidget(QLabel("<h2>1. Inserte su Tarjeta (Ej: 456123 o 789456)</h2>", alignment=Qt.AlignmentFlag.AlignCenter))
        
        self.input_tarjeta = QLineEdit()
        self.input_tarjeta.setPlaceholderText("Ingrese número de tarjeta...")
        layout.addWidget(self.input_tarjeta)
        
        btn_insertar = QPushButton("Insertar Tarjeta")
        btn_insertar.clicked.connect(self.handle_insertar_tarjeta)
        layout.addWidget(btn_insertar)
        return widget

    def create_screen_pin(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(QLabel("<h1>Ingrese su PIN</h1>", alignment=Qt.AlignmentFlag.AlignCenter))
        
        self.input_pin = QLineEdit()
        self.input_pin.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.input_pin)
        
        # Teclado Numérico
        teclado = QWidget()
        grid = QGridLayout(teclado)
        
        botones = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('Borrar', 3, 0), ('0', 3, 1), ('Aceptar', 3, 2),
        ]

        for text, row, col in botones:
            btn = QPushButton(text)
            if text.isdigit() or text == '0':
                btn.clicked.connect(lambda _, t=text: self.input_pin.setText(self.input_pin.text() + t))
            elif text == 'Borrar':
                btn.clicked.connect(self.input_pin.backspace)
            elif text == 'Aceptar':
                btn.clicked.connect(self.handle_verificar_pin)
            grid.addWidget(btn, row, col)
            
        layout.addWidget(teclado)
        return widget

    def create_screen_menu(self):
        widget = QWidget()
        layout = QGridLayout(widget)
        
        btn_retiro = QPushButton("Retiro de Efectivo")
        btn_retiro.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3)) # Va a la pantalla de retiro
        
        btn_deposito = QPushButton("Depósito")
        btn_deposito.clicked.connect(lambda: self.handle_operacion_simple(4, "deposito"))
        
        btn_saldo = QPushButton("Consulta de Saldo")
        btn_saldo.clicked.connect(lambda: self.handle_operacion_simple(4, "saldo"))
        
        btn_salir = QPushButton("Expulsar Tarjeta")
        btn_salir.clicked.connect(self.handle_expulsar_tarjeta)

        layout.addWidget(QLabel("<h1>Seleccione una Operación</h1>", alignment=Qt.AlignmentFlag.AlignCenter), 0, 0, 1, 2)
        layout.addWidget(btn_retiro, 1, 0)
        layout.addWidget(btn_deposito, 1, 1)
        layout.addWidget(btn_saldo, 2, 0)
        layout.addWidget(btn_salir, 2, 1)
        
        return widget

    def create_screen_retiro(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(QLabel("<h1>Monto a Retirar</h1>", alignment=Qt.AlignmentFlag.AlignCenter))
        
        self.input_monto_retiro = QLineEdit()
        self.input_monto_retiro.setPlaceholderText("Ej: 100.00")
        layout.addWidget(self.input_monto_retiro)
        
        btn_aceptar = QPushButton("Aceptar Retiro")
        btn_aceptar.clicked.connect(self.handle_procesar_retiro)
        
        btn_cancelar = QPushButton("Cancelar y Volver al Menú")
        btn_cancelar.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2)) # Vuelve al menú
        
        layout.addWidget(btn_aceptar)
        layout.addWidget(btn_cancelar)
        return widget
        
    def create_screen_message(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.label_message_title = QLabel("", alignment=Qt.AlignmentFlag.AlignCenter)
        self.label_message_body = QLabel("", alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.label_message_title)
        layout.addWidget(self.label_message_body)
        
        btn_continuar = QPushButton("Continuar / Volver al Menú")
        btn_continuar.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2)) # Vuelve al menú por defecto
        
        btn_terminar = QPushButton("Expulsar Tarjeta y Terminar")
        btn_terminar.clicked.connect(self.handle_expulsar_tarjeta)
        
        layout.addWidget(btn_continuar)
        layout.addWidget(btn_terminar)
        return widget

    # --- Manejadores de Eventos (Slots) ---

    @pyqtSlot()
    def handle_insertar_tarjeta(self):
        # Lógica de la Pantalla 0
        numero_tarjeta = self.input_tarjeta.text().strip()
        if not numero_tarjeta:
            QMessageBox.warning(self, "Error", "Debe ingresar un número de tarjeta.")
            return

        # Llama a tu lógica POO
        msg = self.cajero.insertar_tarjeta(numero_tarjeta)

        if "ERROR" in msg:
            QMessageBox.critical(self, "Error de Tarjeta", msg)
        else:
            QMessageBox.information(self, "Tarjeta", msg)
            self.input_pin.clear()
            self.stacked_widget.setCurrentIndex(1) # Va a la pantalla de PIN

    @pyqtSlot()
    def handle_verificar_pin(self):
        # Lógica de la Pantalla 1
        pin = self.input_pin.text()

        # Llama a tu lógica POO
        success, msg = self.cajero.verificar_pin(pin)

        if success:
            QMessageBox.information(self, "Login Exitoso", msg)
            self.stacked_widget.setCurrentIndex(2) # Va al Menú
        else:
            QMessageBox.warning(self, "PIN Incorrecto", msg)
            if "bloqueada" in msg:
                 self.stacked_widget.setCurrentIndex(0) # Vuelve al inicio

    @pyqtSlot()
    def handle_procesar_retiro(self):
        # Lógica de la Pantalla 3
        try:
            monto = float(self.input_monto_retiro.text())
            
            # Llama a tu lógica POO
            success, msg = self.cajero.procesar_retiro(monto)

            self.show_message_screen("Retiro de Efectivo", msg, success)
            self.input_monto_retiro.clear()
            
        except ValueError:
            QMessageBox.warning(self, "Error de Monto", "Por favor, ingrese un número válido.")
        except Exception as e:
            QMessageBox.critical(self, "Error del Sistema", str(e))
            
    def handle_operacion_simple(self, target_screen_index: int, tipo_op: str):
        # Maneja Depósito y Saldo (Simplificado)
        
        if tipo_op == "saldo":
            success, msg = self.cajero.consultar_saldo()
            self.show_message_screen("Consulta de Saldo", msg, success)
        
        elif tipo_op == "deposito":
            # Nota: El depósito en un cajero real requeriría un hardware para contar el efectivo.
            # Aquí lo simplificamos solicitando un monto.
            monto, ok = QMessageBox.getItem(
                self, "Depósito", "Ingrese el monto a depositar:", ["100.00", "500.00", "1000.00", "Otro"], 
                editable=True
            )
            if ok and monto:
                try:
                    monto_float = float(monto)
                    success, msg = self.cajero.procesar_deposito(monto_float)
                    self.show_message_screen("Depósito", msg, success)
                except ValueError:
                    self.show_message_screen("Error de Monto", "Monto de depósito no válido.", False)

    @pyqtSlot()
    def handle_expulsar_tarjeta(self):
        msg = self.cajero.expulsar_tarjeta()
        QMessageBox.information(self, "Adiós", msg)
        self.stacked_widget.setCurrentIndex(0) # Vuelve al inicio
        self.input_tarjeta.clear()
        
    # --- Utilidades de la UI ---
    
    def show_message_screen(self, title: str, body: str, success: bool):
        self.label_message_title.setText(f"<h1>{title}</h1>")
        # Dar formato al mensaje de estado
        style = "color: green;" if success else "color: red;"
        self.label_message_body.setText(f"<p style='{style}'>{body}</p>")
        self.stacked_widget.setCurrentIndex(4) # Va a la pantalla de mensajes

# --- Fin de ui/ui_cajero.py ---