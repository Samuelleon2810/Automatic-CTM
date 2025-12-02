"""
Datos iniciales para el sistema ATM
"""
from data.database import db
from modelo.Banco import Banco
from modelo.Cliente import Cliente
from modelo.Cuenta import Cuenta
from modelo.Tarjeta import Tarjeta
from modelo.Cajero import Cajero


def cargar_datos_iniciales():
    """
    Carga datos de prueba en el sistema
    """
    # Verificar si ya hay datos
    if Banco.query.first():
        print("⚠️  Ya existen datos en la base de datos. Omitiendo carga inicial.")
        return
    
    print("📦 Cargando datos iniciales...")
    
    # Crear Banco
    banco = Banco(
        nombre="Banco del Sol",
        codigo="BDS001",
        limite_max_diario_global=10000.00
    )
    db.session.add(banco)
    db.session.flush()
    
    # Crear Cajeros
    cajero1 = Cajero(
        codigo="ATM001",
        ubicacion="Centro Comercial Plaza Mayor",
        monto_inicial=50000.00
    )
    cajero1.banco = banco
    
    cajero2 = Cajero(
        codigo="ATM002",
        ubicacion="Universidad Distrital - Sede Centro",
        monto_inicial=30000.00
    )
    cajero2.banco = banco
    
    cajero3 = Cajero(
        codigo="ATM003",
        ubicacion="Terminal de Transporte",
        monto_inicial=40000.00
    )
    cajero3.banco = banco
    
    db.session.add_all([cajero1, cajero2, cajero3])
    
    # Cliente 1: Juan Pérez
    cliente1 = Cliente(
        nombre="Juan Pérez",
        documento="1234567890",
        email="juan.perez@email.com",
        telefono="3001234567"
    )
    banco.agregar_cliente(cliente1)
    
    # Cuenta de ahorros para Juan
    cuenta1 = Cuenta(
        numero_cuenta="0001-0001-0001",
        tipo="AHORROS",
        saldo=5430.50,
        limite_diario=3000.00
    )
    cliente1.agregar_cuenta(cuenta1)
    
    # Tarjeta para cuenta1
    tarjeta1 = Tarjeta(
        numero_tarjeta="1234-5678-9012-3456",
        pin="1234"
    )
    tarjeta1.cuenta = cuenta1
    db.session.add(tarjeta1)
    
    # Cliente 2: María García
    cliente2 = Cliente(
        nombre="María García",
        documento="9876543210",
        email="maria.garcia@email.com",
        telefono="3109876543"
    )
    banco.agregar_cliente(cliente2)
    
    # Cuenta corriente para María
    cuenta2 = Cuenta(
        numero_cuenta="0002-0002-0002",
        tipo="CORRIENTE",
        saldo=12500.75,
        limite_diario=5000.00
    )
    cliente2.agregar_cuenta(cuenta2)
    
    # Tarjeta para cuenta2
    tarjeta2 = Tarjeta(
        numero_tarjeta="9876-5432-1098-7654",
        pin="5678"
    )
    tarjeta2.cuenta = cuenta2
    db.session.add(tarjeta2)
    
    # Cliente 3: Carlos Rodríguez
    cliente3 = Cliente(
        nombre="Carlos Rodríguez",
        documento="1122334455",
        email="carlos.rodriguez@email.com",
        telefono="3201122334"
    )
    banco.agregar_cliente(cliente3)
    
    # Cuenta de ahorros para Carlos
    cuenta3 = Cuenta(
        numero_cuenta="0003-0003-0003",
        tipo="AHORROS",
        saldo=8750.25,
        limite_diario=2500.00
    )
    cliente3.agregar_cuenta(cuenta3)
    
    # Tarjeta para cuenta3
    tarjeta3 = Tarjeta(
        numero_tarjeta="1111-2222-3333-4444",
        pin="9999"
    )
    tarjeta3.cuenta = cuenta3
    db.session.add(tarjeta3)
    
    # Cliente 4: Ana Martínez (múltiples cuentas)
    cliente4 = Cliente(
        nombre="Ana Martínez",
        documento="5566778899",
        email="ana.martinez@email.com",
        telefono="3155667788"
    )
    banco.agregar_cliente(cliente4)
    
    # Primera cuenta de Ana (Ahorros)
    cuenta4a = Cuenta(
        numero_cuenta="0004-0004-0001",
        tipo="AHORROS",
        saldo=15000.00,
        limite_diario=4000.00
    )
    cliente4.agregar_cuenta(cuenta4a)
    
    tarjeta4a = Tarjeta(
        numero_tarjeta="5555-6666-7777-8888",
        pin="1111"
    )
    tarjeta4a.cuenta = cuenta4a
    db.session.add(tarjeta4a)
    
    # Segunda cuenta de Ana (Corriente)
    cuenta4b = Cuenta(
        numero_cuenta="0004-0004-0002",
        tipo="CORRIENTE",
        saldo=25000.00,
        limite_diario=6000.00
    )
    cliente4.agregar_cuenta(cuenta4b)
    
    tarjeta4b = Tarjeta(
        numero_tarjeta="8888-7777-6666-5555",
        pin="2222"
    )
    tarjeta4b.cuenta = cuenta4b
    db.session.add(tarjeta4b)
    
    # Cliente 5: Luis Fernández (cuenta con saldo bajo)
    cliente5 = Cliente(
        nombre="Luis Fernández",
        documento="9988776655",
        email="luis.fernandez@email.com",
        telefono="3189988776"
    )
    banco.agregar_cliente(cliente5)
    
    cuenta5 = Cuenta(
        numero_cuenta="0005-0005-0005",
        tipo="AHORROS",
        saldo=150.00,
        limite_diario=500.00
    )
    cliente5.agregar_cuenta(cuenta5)
    
    tarjeta5 = Tarjeta(
        numero_tarjeta="1212-3434-5656-7878",
        pin="4321"
    )
    tarjeta5.cuenta = cuenta5
    db.session.add(tarjeta5)
    
    # Commit de todos los cambios
    db.session.commit()
    
    print("✅ Datos iniciales cargados:")
    print(f"   - 1 Banco: {banco.nombre}")
    print(f"   - 3 Cajeros ATM")
    print(f"   - 5 Clientes")
    print(f"   - 6 Cuentas")
    print(f"   - 6 Tarjetas")
    print("\n📋 Tarjetas de prueba:")
    print("   1. 1234-5678-9012-3456 | PIN: 1234 | Juan Pérez | $5,430.50")
    print("   2. 9876-5432-1098-7654 | PIN: 5678 | María García | $12,500.75")
    print("   3. 1111-2222-3333-4444 | PIN: 9999 | Carlos Rodríguez | $8,750.25")
    print("   4. 5555-6666-7777-8888 | PIN: 1111 | Ana Martínez (A) | $15,000.00")
    print("   5. 8888-7777-6666-5555 | PIN: 2222 | Ana Martínez (C) | $25,000.00")
    print("   6. 1212-3434-5656-7878 | PIN: 4321 | Luis Fernández | $150.00")


def limpiar_datos():
    """
    Elimina todos los datos de la base de datos
    """
    print("🗑️  Limpiando base de datos...")
    
    # Eliminar en orden inverso a las dependencias
    from modelo.Operacion import Operacion
    
    db.session.query(Operacion).delete()
    db.session.query(Tarjeta).delete()
    db.session.query(Cuenta).delete()
    db.session.query(Cliente).delete()
    db.session.query(Cajero).delete()
    db.session.query(Banco).delete()
    
    db.session.commit()
    print("✅ Base de datos limpiada")


# Script para ejecutar desde línea de comandos
if __name__ == "__main__":
    from flask import Flask
    from config import config
    
    app = Flask(__name__)
    app.config.from_object(config['development'])
    
    from data.database import init_db
    init_db(app)
    
    with app.app_context():
        # Limpiar datos existentes
        limpiar_datos()
        
        # Cargar datos iniciales
        cargar_datos_iniciales()
