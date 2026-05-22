# 🐾 VetCare Pro — Sistema de Gestión de Clínica Veterinaria

Sistema completo desarrollado en Python con interfaz gráfica (CustomTkinter) 
y persistencia de datos en MongoDB.

---

## Estructura del proyecto

```
vetcare_pro/
├── app.py                    ← Punto de entrada principal
├── requirements.txt
│
├── models/                   ← Modelos de dominio (POO)
│   ├── persona.py            → Persona (abstracta), Cliente, Veterinario, Recepcionista
│   ├── animal.py             → Animal (abstracta), Perro, Gato, Ave, Reptil
│   └── cita.py               → Cita, HistorialMedico
│
├── database/                 ← Capa de persistencia
│   ├── db_connection.py      → Patrón SINGLETON (conexión MongoDB)
│   └── repositorios.py       → DAO para cada colección
│
├── patterns/                 ← Patrones de diseño
│   └── observer.py           → Patrón OBSERVER (notificaciones de citas)
│
├── utils/                    ← Capa de servicios
│   └── servicios.py          → Lógica de negocio
│
└── ui/                       ← Interfaz gráfica
    ├── frame_clientes.py     → Pantalla #2: Gestión de Clientes
    ├── frame_animales.py     → Pantalla #3: Gestión de Animales
    ├── frame_citas.py        → Pantalla #4: Gestión de Citas
    └── frame_veterinarios.py → Pantalla #5: Gestión de Veterinarios
```

---

## Instalación y ejecución

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. (Opcional) Iniciar MongoDB

Si tienes MongoDB instalado localmente:
```bash
mongod --dbpath /data/db
```

> Si MongoDB no está disponible, el sistema funciona en **modo demo** con datos en memoria.

### 3. Ejecutar la aplicación

```bash
cd vetcare_pro
python app.py
```

---

## Conceptos de POO

### Clases y Objetos
Todas las entidades del sistema son clases: `Persona`, `Animal`, `Cita`, `HistorialMedico`, etc.

### Herencia
```
Persona (abstracta)
├── Cliente
├── Veterinario
└── Recepcionista

Animal (abstracta)
├── Perro
├── Gato
├── Ave
└── Reptil
```

### Polimorfismo
`describir()` y `calcular_riesgo()` son implementados diferente en cada subclase de Animal:
- `Perro.calcular_riesgo()` → basado en edad y peso
- `Gato.calcular_riesgo()` → basado en si es indoor/outdoor
- `Ave.calcular_riesgo()` → basado en peso crítico
- `Reptil.calcular_riesgo()` → basado en si es venenoso

### Encapsulamiento
- Atributos privados con `_` (convención) y `__` (name mangling Python)
- `HistorialMedico` usa `__diagnostico`, `__tratamiento` con getters controlados
- `Cliente`, `Veterinario` exponen sus datos solo mediante properties

### Modularidad
Cada responsabilidad está en su propio módulo:
- `models/` → solo entidades de negocio
- `database/` → solo persistencia
- `patterns/` → solo patrones
- `utils/` → solo lógica de negocio
- `ui/` → solo interfaz gráfica

---

## Patrones de Diseño

### 1. SINGLETON — `database/db_connection.py`
```python
# Solo existe una instancia de la conexión MongoDB
conn1 = DatabaseConnection.get_instance()
conn2 = DatabaseConnection.get_instance()
assert conn1 is conn2  # True — misma instancia
```

### 2. OBSERVER — `patterns/observer.py`
```python
# Al agendar una cita, se notifica automáticamente a:
gestor_citas_global.registrar_cita(datos)
# → NotificadorVeterinario.update() → mensaje para el vet
# → NotificadorCliente.update()    → mensaje para el dueño
# → LogSistema.update()            → registro en log
```

---

## Interfaces gráficas (CustomTkinter)

| # | Pantalla        | Descripción |
|---|-----------------|-------------|
| 1 | Dashboard       | Estadísticas generales + citas recientes + accesos rápidos |
| 2 | Clientes        | Lista, busca y registra clientes con formulario modal |
| 3 | Animales        | Lista mascotas con filtro por tipo y muestra nivel de riesgo |
| 4 | Citas           | Agenda citas, cambia estados, ve notificaciones Observer |
| 5 | Veterinarios    | Vista en tarjetas con especialidad y colores diferenciados |

---

## Variables de entorno

```bash
MONGO_URI=mongodb://localhost:27017/    # URL de MongoDB (por defecto)
```

---

## Notas de diseño

- **Modo demo**: si MongoDB no está disponible al iniciar, los datos se almacenan en memoria RAM durante la sesión. Al cerrar la app se pierden (perfecto para demo/presentación).
- **Tema visual**: modo oscuro con paleta de colores médico-verde. Totalmente personalizable en `app.py` (diccionario `COLORS`).
- El archivo `app.py` es el único punto de entrada; no hay scripts separados.
