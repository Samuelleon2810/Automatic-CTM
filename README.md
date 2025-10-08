# 🏦 Sistema de Cajero Automático - Banco XYZ

## 📋 Descripción General
Este proyecto implementa un **sistema de cajero automático (ATM)** para un banco, desarrollado bajo el **paradigma de programación orientada a objetos (POO)**.  
El objetivo es permitir a los clientes realizar operaciones bancarias seguras como **retiros, consignaciones, consultas de saldo y compra de entradas**, con control de acceso mediante **tarjetas y contraseñas**.

El sistema fue diseñado y modelado utilizando **UML (Lenguaje de Modelado Unificado)**, incluyendo diagramas de **casos de uso** y **clases**, para representar la estructura y comportamiento del sistema.

---

## 🧩 Modelo de Negocio

El Banco permite que:
- Cada **Cliente** tenga una o varias **Cuentas**.
- Cada **Cuenta** puede tener como máximo **una Tarjeta Débito**, vinculada directamente al titular.
- Cada **Tarjeta** tiene un **PIN** y un **límite de intentos (3)** antes de ser bloqueada.
- Cada día existe un **límite máximo de retiro**.
- El sistema de **Cajero Automático** interactúa con las cuentas del banco para permitir operaciones seguras.
- Se puede escalar fácilmente para incluir nuevas operaciones (por ejemplo, compra de entradas de teatro, pago de servicios, etc.).

---

## 🎯 Objetivos del Sistema

1. Permitir operaciones seguras de retiro y consignación.
2. Garantizar autenticación por contraseña con número máximo de intentos.
3. Controlar los montos máximos diarios por tarjeta.
4. Facilitar la extensión del sistema con nuevas operaciones.
5. Modelar de forma clara las relaciones entre entidades del banco mediante UML.

---

## 🧱 Diagrama de Clases (Resumen)

**Principales clases del sistema:**

- **Banco**
  - Gestiona clientes, cuentas y cajeros.
  - Supervisa políticas de seguridad y límites diarios.
- **Cliente**
  - Tiene una o más cuentas.
- **Cuenta**
  - Almacena saldo y referencia a una tarjeta.
- **Tarjeta**
  - Permite la autenticación y ejecución de operaciones.
  - Posee número, PIN, intentos y estado.
- **Cajero**
  - Permite interactuar con el sistema mediante operaciones bancarias.
- **Operacion**
  - Clase abstracta para representar acciones genéricas.
- **Retiro** y **Consignacion**
  - Extienden Operacion y afectan el saldo de la cuenta.
- **EntradaTeatro** (extensible)
  - Representa una futura funcionalidad del sistema (compra de entradas).

---

## ⚙️ Funcionalidades Principales

- Autenticación mediante PIN con máximo de 3 intentos.
- Control del monto máximo diario.
- Retiros y consignaciones.
- Consultas de saldo.
- Posibilidad de ampliación modular.

---

## 🧠 Estructura del Proyecto

```
/BancoATM
│
├── /src
│   ├── Banco.java
│   ├── Cliente.java
│   ├── Cuenta.java
│   ├── Tarjeta.java
│   ├── Cajero.java
│   ├── Operacion.java
│   ├── Retiro.java
│   ├── Consignacion.java
│   └── EntradaTeatro.java
│
├── /uml
│   ├── DiagramaCasosDeUso.png
│   └── DiagramaClases.png
│
└── README.md
```

---

## 🚀 Futuras Extensiones

- Pago de servicios públicos.
- Transferencias entre cuentas.
- Sistema de alertas y notificaciones al cliente.
- Interfaz gráfica para interacción visual con el usuario.

---

## 🧑‍💻 Autores
**Samuel Leonardo Acosta Cruz**
Estudiante de Ingeniería de Sistemas  
Universidad Distrital Francisco José de Caldas  
Colombia 🇨🇴

**Nicolas Martínez Pineda**
Estudiante de Ingeniería de Sistemas  
Universidad Distrital Francisco José de Caldas  
Colombia 🇨🇴

**Mateo**
Estudiante de Ingeniería de Sistemas  
Universidad Distrital Francisco José de Caldas  
Colombia 🇨🇴


