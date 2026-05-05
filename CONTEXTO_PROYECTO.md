# CONTEXTO_PROYECTO.md - Sistema de Facturación

**Versión:** 2.0  
**Última actualización:** 3 de mayo de 2026  
**Estado:** Activo y en desarrollo - Con persistencia en SQLite

> **⚠️ IMPORTANTE:** Este archivo debe mantenerse actualizado conforme se realizan modificaciones en el código. Cualquier cambio en funcionalidades, interfaz, lógica o comportamiento debe ser documentado aquí inmediatamente.

---

## 1. Descripción General

Sistema de facturación de escritorio para pequeñas empresas. Permite gestionar clientes, productos y crear facturas de forma simple e intuitiva. La aplicación funciona completamente en una sola computadora sin requerir servidor o conexión a internet.

**Característica principal:** Interfaz en una sola pantalla con buscadores en lugar de dropdowns, diseñada para ser escalable cuando el volumen de datos crezca.

---

## 2. Objetivo del Proyecto

Desarrollar una herramienta de facturación simple y funcional que:

- ✅ Permita gestionar clientes (CRUD completo)
- ✅ Permita gestionar productos (CRUD completo)
- ✅ Permita crear y gestionar facturas
- ✅ Calcule automáticamente totales con descuentos
- ✅ Registre datos de reparto (repartidor y día)
- ✅ **COMPLETADO:** Migración a SQLite con persistencia real
- ✅ Sistema de aumentos/rebajas masivos de precios
- ✅ Exportación de productos a Excel
- 🔄 **Futuro:** Generar PDF de facturas
- 🔄 **Futuro:** Funcionalidades adicionales avanzadas

---

## 3. Tecnología

| Componente | Tecnología |
|-----------|------------|
| Lenguaje | Python 3.11+ |
| Interfaz | Tkinter (GUI nativa) |
| Persistencia | SQLite 3 (database.db) |
| ORM / Queries | sqlite3 de Python (queries SQL nativas) |
| Arquitectura | 4 capas (UI, Services, Repositories, Database) |
| Tipo | Aplicación de escritorio (100% local) |

---

## 4. Estado Actual del Sistema

**🟢 Completamente funcional con SQLite:**

- ✅ Sistema CRUD completo para todas las entidades (Clientes, Productos, Facturas, Pagos)
- ✅ Interfaz gráfica operativa
- ✅ Cálculos de facturas funcionando
- ✅ Buscadores implementados
- ✅ Filtros en tablas implementados
- ✅ Persistencia real en SQLite (base de datos database.db)
- ✅ Datos persisten entre sesiones
- ✅ Sistema de aumentos/rebajas masivos de precios con selección avanzada
- ✅ Columna de Precio Recomendado (+80%) en tabla de productos
- ✅ Exportación de productos a Excel (.xlsx)
- ✅ Relaciones y restricciones de integridad en BD

**🔄 En desarrollo / Futuro:**

- Exportación a PDF de facturas
- Reportes y análisis de datos
- Funcionalidades adicionales avanzadas

---

## 5. Funcionalidades Actuales

### 5.1 Gestión de Clientes

**Pantalla:** ClientesView

**Campos de cliente:**
- `codigo` (único, clave primaria)
- `nombre` (nombre del cliente)
- `adicional` (dirección, CUIT, RUC, etc.)
- `descuento_1` (bool: primer descuento del 8%)
- `descuento_2` (bool: segundo descuento del 8%)
- `saldo` (monto pendiente de pago)

**Operaciones:**
- ✅ Crear cliente
- ✅ Editar cliente
- ✅ Eliminar cliente
- ✅ Listar clientes con buscador/filtro

**Notas importantes:**
- Los descuentos funcionan como bloques de 8% acumulativos (compuestos)
- 0 descuentos activos = sin descuento
- 1 descuento activo = 8% de descuento
- 2 descuentos activos = 8% × 8% = 7.68% de descuento efectivo (NO 16%)
- Los descuentos se aplican automáticamente a todas las facturas de ese cliente

### 5.2 Gestión de Productos

**Pantalla:** ProductosView

**Campos de producto (edición/creación):**
- `codigo` (único, clave primaria)
- `descripcion` (nombre/descripción del producto)
- `precio` (precio unitario actual)

**Columnas de visualización en tabla:**
- Código
- Descripción
- Precio Unitario
- **Precio Recomendado (+80%)** - Calculado automáticamente como `precio * 1.80` (sin edición)

**Operaciones:**
- ✅ Crear producto
- ✅ Editar producto
- ✅ Eliminar producto
- ✅ Listar productos con buscador/filtro
- ✅ Exportar todos los productos a Excel (.xlsx)

**Notas importantes:**
- El precio es el precio actual en catálogo
- Cuando se agrega un producto a una factura, el precio se COPIA al item
- Cambios de precio en el catálogo NO afectan facturas ya creadas
- El Precio Recomendado (+80%) se calcula automáticamente solo para visualización
  - Se usa como recomendación de precio de reventa para clientes
  - No es editable, se actualiza automáticamente cuando cambia el precio unitario
  - Aparece con formato moneda ($)
  - **Lógica centralizada en ProductoService.get_precio_recomendado()** para facilitar migraciones a BD
- **Exportación a Excel:** Botón "Exportar a Excel" permite descargar todos los productos en formato .xlsx incluyendo precio recomendado

### 5.3 Gestión de Facturas

**Pantalla:** FacturasView + FacturaFormView

**Campos de factura:**
- `numero` (identificador único de factura)
- `cliente` (seleccionado mediante buscador)
- `fecha` (por defecto: hoy)
- `repartidor` (nombre del repartidor, texto libre)
- `dia_reparto` (ej: Lunes, Martes, etc.)
- `items` (lista de productos en la factura)

**Campos de cada item:**
- `producto` (referencia al producto)
- `cantidad` (cantidad solicitada)
- `precio_unitario` (copiado del producto al momento de agregar)
- `subtotal` (cantidad × precio_unitario)

**Cálculos automáticos:**
- `subtotal_general` = suma de todos los subtotales
- `descuentos_aplicados` = según la configuración del cliente:
  - Si descuento_1 y descuento_2: total × 0.92 × 0.92 (descuento compuesto)
  - Si solo descuento_1: total × 0.92
  - Si ninguno: sin descuento
- `total_final` = subtotal_general con descuentos compuestos aplicados

**Operaciones:**
- ✅ Crear factura
- ✅ Editar factura
- ✅ Eliminar factura
- ✅ Listar facturas con buscador/filtro
- ✅ Agregar items a una factura
- ✅ Eliminar items de una factura
- ✅ Ver totales calculados

**Efecto en cliente:**
- Crear factura → Suma el total al saldo del cliente
- Editar factura → Resta el viejo total y suma el nuevo
- Eliminar factura → Resta el total del saldo del cliente

### 5.4 Gestión de Pagos

**Pantalla:** PagosView

**Campos de pago:**
- `id` (autonumérico, único, no editable)
- `cliente` (seleccionado mediante buscador)
- `monto` (monto del pago)
- `fecha` (por defecto: hoy)
- `comentario` (texto opcional)

**Operaciones:**
- ✅ Crear pago
- ✅ Eliminar pago
- ✅ Listar pagos con buscador/filtro

**Comportamiento del saldo:**
- ✅ Al crear pago → **Resta el monto del saldo del cliente**
- ✅ Al eliminar pago → **Suma el monto de vuelta al saldo del cliente**

**Generación de ID:**
- ID se asigna automáticamente (autonumérico incremental)
- No puede ser editado por el usuario
- No necesita ingreso manual

**Notas importantes:**
- Las facturas **suman** al saldo
- Los pagos **restan** al saldo
- El saldo del cliente se actualiza automáticamente en ambos casos

### 5.5 Aumentos y Rebajas de Precios

**Pantalla:** AumentosPreciosView

**Objetivo:** Aplicar aumentos o reducciones masivas de precios a múltiples productos con selección avanzada, validaciones y confirmación con preview.

**Componentes de interfaz:**
- **Buscador**: Filtra productos por código o descripción (búsqueda en tiempo real)
- **Lista de productos**: Tabla con columnas:
  - Seleccionar (ancho: 45px) - ☐/☑ Checkbox individual
  - Código
  - Descripción
  - Precio actual
- **Checkbox "Seleccionar todos"**: Selecciona/deselecciona todos los productos visibles (filtrados)
  - **Comportamiento inteligente**: Solo aparece marcado si TODOS los productos visibles están seleccionados
  - Si se aplica filtro y se seleccionan todos → checkbox ✅
  - Si se cambia de filtro → checkbox aparece ☐ (pero los productos anteriores siguen seleccionados)
  - Si se aplica otro filtro y hay productos no seleccionados entre los visibles → checkbox ☐
- **Contador dinámico**: Muestra "X productos seleccionados" (se actualiza en tiempo real)
- **Botón "Limpiar selección"**: Desmarca todos los productos
- **Input de porcentaje**: Campo numérico para ingresar el % de cambio
  - Positivo: aumento de precio (ej: 10 = 10% más caro)
  - Negativo: rebaja de precio (ej: -10 = 10% más barato)
  - Rango válido: -100 < valor < infinito
- **Botón "Aplicar cambio de precio"**: Inicia el proceso de cambio

**Interacción con checkboxes:**
- ✅ Click en checkbox: Solo se activa si se clickea directamente en el cuadrado del checkbox (área central)
- ✅ Click en otra parte de la fila: No selecciona (previene errores por clicks accidentales)
- ✅ Validación de área: Solo activa si el click está dentro del ±25% del ancho de la columna

**Validaciones:**
- ✅ Porcentaje ≠ 0 (no puede ser exactamente cero)
- ✅ Porcentaje ≥ -100% (no puede rebajar más del 100%)
- ✅ Al menos un producto seleccionado
- ✅ Permite valores positivos (aumentos de precio)
- ✅ Permite valores negativos (rebajas de precio)

**Flujo de cambio de precio:**

1. Usuario selecciona productos (individual o todos)
2. Ingresa porcentaje de cambio (ej: 10 para +10%, -5 para -5%)
3. Hace clic en "Aplicar cambio de precio"
4. Sistema valida:
   - Porcentaje ≠ 0 (no puede ser exactamente cero)
   - Porcentaje ≥ -100% (no puede rebajar más del 100%)
   - Al menos un producto
5. Se abre popup de confirmación (tamaño: 650x650px) que muestra:
   - Mensaje: "¿Seguro que querés aplicar un cambio de X% a N productos seleccionados?"
   - Lista completa de todos los productos:
     - Código - Descripción: $precio_actual → $nuevo_precio
     - Scrollable si hay muchos productos
   - Etiqueta: "Productos a modificar (X):" donde X es la cantidad total
   - Botones: "Sí, aplicar" y "Cancelar"
6. Si confirma:
   - Calcula nuevo precio: `nuevo_precio = precio * (1 + porcentaje / 100)`
   - Redondea a 2 decimales
   - Actualiza cada producto en el repositorio
   - Muestra mensaje de éxito
   - **Limpia el campo de porcentaje (vuelve a 0)**
   - Limpia la selección de productos
   - Recarga la lista de productos
7. Si cancela: cierra el popup

**Características importantes:**

- **NO modifica facturas existentes**: Los precios ya grabados en facturas no cambian
- **Afecta futuros usos**: Solo impacta en nuevas facturas
- **Soporta aumentos y rebajas**: Permite tanto incrementar como reducir precios
- **Actualización en tiempo real**: La tabla se actualiza inmediatamente
- **Interfaz consistente**: Usa los mismos estilos y componentes del resto del sistema
- **Checkbox inteligente**: "Seleccionar todos" refleja solo el estado de los productos visibles
- **Campo de porcentaje auto-limpiable**: Se resetea a 0 después de aplicar cambio exitosamente
- **Prevención de errores**: Área reducida de click en checkbox evita selecciones accidentales
- **Popup optimizado**: Tamaño 650x650px para mostrar todos los elementos sin necesidad de redimensionar
- **Lista completa de productos**: Muestra TODOS los productos a modificar (no solo ejemplos) con scroll si es necesario
- **Visibilidad total**: El usuario puede verificar exactamente qué productos se van a modificar antes de confirmar

**Lógica de negocio (ProductoService.apply_price_increase):**

```python
def apply_price_increase(self, producto_codigos, porcentaje):
    """Aplica cambio de precio (aumento o rebaja) a múltiples productos"""
    # Validar porcentaje ≠ 0
    # Validar porcentaje ≥ -100%
    # Validar al menos un producto
    # Para cada producto:
    #   nuevo_precio = precio_actual * (1 + porcentaje / 100)
    #   redondear a 2 decimales
    #   actualizar en repository
```

### 5.6 Exportación de Productos a Excel

**Pantalla:** ProductosView - Botón "Exportar a Excel"

**Objetivo:** Exportar todos los productos a un archivo Excel (.xlsx) para análisis externo, reportes o integración con otros sistemas.

**Campos exportados:**
- Código
- Descripción  
- Precio (precio unitario actual)
- Precio Recomendado (calculado automáticamente como +80%)

**Características:**
- ✅ Headers con formato negrita
- ✅ Exporta TODOS los productos (no solo los filtrados)
- ✅ Incluye precio recomendado calculado automáticamente
- ✅ Permite elegir nombre y ubicación del archivo
- ✅ Validación: si no hay productos → mensaje "No hay productos para exportar"
- ✅ Confirmación: muestra mensaje de éxito al finalizar
- ✅ Formato: Archivo .xlsx (Excel moderno)

**Flujo:**
1. Usuario hace clic en "Exportar a Excel"
2. Sistema valida si hay productos
3. Abre diálogo de guardado (guardar archivo)
4. Usuario elige nombre y ubicación
5. Sistema genera archivo Excel con todos los productos
6. Muestra mensaje "Exportación realizada con éxito"

**Lógica de negocio (ProductoService.export_to_excel):**
- Obtiene todos los productos via `get_all_products()`
- Para cada producto, calcula `get_precio_recomendado(precio)`
- Genera workbook con openpyxl
- Guarda archivo en ubicación especificada

**Dependencias:**
- Librería: `openpyxl` (para generar archivos Excel)

---

## 6. Estructura de Datos (Models)

### Cliente
```python
class Cliente:
    - codigo: str (único)
    - nombre: str
    - adicional: str (dirección, CUIT, etc.)
    - descuento_1: bool (primer bloque de 8%)
    - descuento_2: bool (segundo bloque de 8%)
    - saldo: float (default: 0.0)
```
**Lógica de descuentos:**
- 0 activos: sin descuento (0%)
- 1 activo: 8% de descuento
- 2 activos: 7.68% de descuento efectivo (multiplica 0.92 × 0.92)

### Producto
```python
class Producto:
    - codigo: str (único)
    - descripcion: str
    - precio: float
```

### FacturaItem
```python
class FacturaItem:
    - producto: Producto
    - cantidad: int
    - precio_unitario: float (copiado en el momento)
    - subtotal: float (calculado)
```

### Factura
```python
class Factura:
    - numero: str (único)
    - cliente: Cliente
    - fecha: date
    - repartidor: str (texto libre)
    - dia_reparto: str
    - items: list[FacturaItem]
    - subtotal_general: float (calculado)
    - total: float (calculado con descuento)
```

### Pago
```python
class Pago:
    - id: int (autonumérico, único, no editable)
    - cliente: Cliente
    - monto: float
    - fecha: date
    - comentario: str (opcional)
```
**Comportamiento:**
- El ID se genera automáticamente (incremental)
- Al crear un pago: **resta el monto del saldo del cliente**
- Al eliminar un pago: **suma el monto de vuelta al saldo del cliente**

---

## 7. Arquitectura del Sistema

### 7.1 Diagrama de Capas

```
┌─────────────────────────────────────────────────────┐
│         CAPA PRESENTACIÓN (UI)                      │
│                                                     │
│  - MainMenu (menú principal)                        │
│  - ClientesView (CRUD clientes)                     │
│  - ProductosView (CRUD productos)                   │
│  - FacturasView (listado facturas)                  │
│  - FacturaFormView (crear/editar factura)           │
│                                                     │
│  Característica: Una sola pantalla (sin Toplevel)   │
└──────────────┬──────────────────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────────────────┐
│       CAPA LÓGICA (Services/Managers)                │
│                                                      │
│  - ClienteService (lógica de clientes)              │
│  - ProductoService (lógica de productos)            │
│  - FacturaService (lógica de facturas)              │
│                                                      │
│  Responsabilidad: Reglas de negocio, validaciones   │
└──────────────┬───────────────────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────────────────┐
│      CAPA DATOS (Repositories)                       │
│                                                      │
│  - ClienteRepository (acceso a clientes)            │
│  - ProductoRepository (acceso a productos)          │
│  - FacturaRepository (acceso a facturas)            │
│                                                      │
│  Responsabilidad: Persistencia, lectura/escritura   │
│  Formato actual: JSON en memoria                    │
│  Formato futuro: SQLite                             │
└──────────────┬───────────────────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────────────────┐
│            CAPA MODELOS (Models)                     │
│                                                      │
│  - Cliente, Producto, Factura, FacturaItem          │
│                                                      │
│  Responsabilidad: Definición de estructuras         │
└──────────────────────────────────────────────────────┘
```

### 7.2 Capa de Presentación (UI)

- Archivo: `ui/main_menu.py`, `ui/clientes_view.py`, etc.
- Framework: Tkinter
- Característica: Una sola pantalla (frames que se "intercambian")
- Componentes clave:
  - Tablas (Treeview)
  - Buscadores/filtros (Entry + filtraje en vivo)
  - Botones (CRUD)
  - Formularios

### 7.3 Capa de Lógica (Services/Managers)

- Archivo: `services/cliente_service.py`, etc.
- Responsabilidades:
  - Validaciones de negocio
  - Cálculos (totales, descuentos)
  - Coordinación entre repositorios
  - Actualización de saldos

### 7.4 Capa de Repositorios (Data Access Layer)

- Archivos: `repositories/cliente_repository.py`, `repositories/producto_repository.py`, etc.
- Interfaz uniforme: `get_all()`, `get_by_code()`, `add()`, `update()`, `delete()`
- Backend: Queries SQL contra SQLite
- Métodos especializados: `get_by_code_with_id()` (IDs internos), `update_saldo()`, etc.
- Manejo de relaciones: FK entre clientes, productos y facturas
- Transacciones: Uso de context managers para integridad

### 7.5 Capa de Base de Datos (Database Layer)

- Archivo: `database/db.py`
- Clase: `Database` (singleton, conexión centralizada)
- Funciones: `get_db()` para obtener instancia
- Responsabilidades:
  - Inicializar conexión SQLite
  - Crear tablas si no existen
  - Proporcionar context managers para conexiones
  - Manejar row_factory para acceso por nombre
- Context manager: `_ConnectionContext` para manejo seguro de conexiones

### 7.6 Capa de Modelos (Models)

- Archivo: `models.py`
- Clases puras sin lógica de persistencia
- Métodos auxiliares: `to_dict()`, `from_dict()`
- Independientes de la capa de datos (funciona tanto con JSON como SQLite)

---

## 8. Métodos Centralizados de Servicios

### 8.1 ProductoService

**Método: get_precio_recomendado(precio)**

```python
PORCENTAJE_RECOMENDADO = 80  # Constante de clase

def get_precio_recomendado(self, precio):
    """
    Calcula el precio recomendado (+80%) para un producto.
    
    Args:
        precio: float - Precio unitario del producto
    
    Returns:
        float - Precio recomendado (precio * 1.80), redondeado a 2 decimales
    
    Propósito:
    - Centralizar la lógica de cálculo de precio recomendado
    - Facilitar cambios futuros sin tocar múltiples vistas
    - Preparar para migración a BD (solo cambiar aquí la implementación)
    
    Uso actual:
    - ProductosView.actualizar_lista() → muestra precio recomendado en tabla
    
    Uso futuro (BD):
    - En SQLite, puede implementarse como COMPUTED COLUMN o calcularse aquí
    """
```

**Ventajas de esta centralización:**
- ✅ Cambiar el porcentaje: editar solo una línea en ProductoService.PORCENTAJE_RECOMENDADO
- ✅ Futura migración a BD: solo cambiar la implementación de este método
- ✅ Reutilizable: cualquier vista puede usar este método
- ✅ Consistencia: un único lugar donde se define la lógica

---

## 9. Decisiones de Diseño (Muy Importante)

### 9.1 Persistencia en SQLite

**Decisión:** El sistema almacena datos en SQLite (database.db), NO en JSON en memoria.

**Ventajas:**
- ✅ Persistencia real entre sesiones
- ✅ Integridad referencial con FK
- ✅ Escalable para grandes volúmenes de datos
- ✅ Consultas eficientes
- ✅ Transacciones atómicas
- ✅ Sin servidor externo (archivo local)

**Implementación:**
- Base de datos única: `database.db`
- Gestión centralizada en `database/db.py`
- Singleton pattern para conexiones
- Context managers para manejo seguro

**Tablas:**
- CLIENTES, PRODUCTOS, FACTURAS, ITEMS_FACTURA, PAGOS
- Ver sección "9. Esquema de Base de Datos SQLite" para detalles

### 9.2 Migración automática JSON → SQLite

**Proceso:**
- Al iniciar la app, se verifica si la BD está vacía
- Si está vacía y existen archivos JSON, se migran automáticamente
- Los archivos JSON se mantienen como backup
- La migración es transparente para el usuario

**Función:** `migrate_data_if_needed()` en `main.py`

### 9.3 Separación en capas

**Decisión:** La arquitectura se divide en 4 capas (UI, Services, Repositories, Database).


**Por qué:**
- UI no conoce detalles de persistencia
- Services encapsula lógica de negocio
- Repository es el único lugar que cambia con SQLite
- Facilita testing y mantenimiento

**Ventaja para migraciones:**
- Para agregar SQLite solo cambias los Repositories
- La UI y Services NO necesitan cambios

### 8.3 Una sola pantalla (sin Toplevel)

**Decisión:** No usar ventanas emergentes (Toplevel). Todo en frames que se muestran/ocultan.

**Por qué:**
- Mejor experiencia de usuario
- Menos complejidad en manejo de eventos
- UI consistente y previsible

### 8.4 Buscadores en lugar de Dropdowns

**Decisión:** Usar Entry + filtrado en vivo en lugar de Combobox/Dropdown.

**Por qué:**
- Escalable: con 1000 clientes, dropdown es inutilizable
- UX mejorada: escribes "Juan" y solo ves a Juan
- Preparado para el crecimiento futuro

### 8.5 Precio copiado en items

**Decisión:** Cuando agregas un producto a una factura, el precio actual se copia al item.

**Por qué:**
- Si cambias el precio en el catálogo, las facturas antiguas mantienen su precio original
- Garantiza consistencia histórica
- Refleja la realidad: vendiste a ese precio en ese momento

### 8.6 Descuento por cliente

**Decisión:** El descuento es un atributo del cliente, no del producto ni de la factura.

**Por qué:**
- Típico: algunos clientes tienen descuento fijo (mayoristas)
- Se aplica automáticamente a todas sus facturas
- Simplifica cálculos y evita errores

---

## 10. PREPARACIÓN PARA MIGRACIÓN A BD (SQLite)

### ⚠️ IMPORTANTE PARA MIGRACIÓN

El código está diseñado y centralizado para facilitar la migración a SQLite sin tocar la UI.

**Qué cambiar:**
1. **Repositories** (`repositories/*.py`)
   - Cambiar de: lectura/escritura de JSON
   - Cambiar a: consultas SQLite
   - Que devuelvan: los mismos objetos (Cliente, Producto, etc.)

2. **Services** (parcialmente)
   - La mayoría **NO necesita cambios**
   - EXCEPTO métodos de cálculo que sean complejos:
     - `ProductoService.get_precio_recomendado()` - ✅ YA centralizado
     - `FacturaService` cálculos de descuentos - revisar

3. **UI** - ❌ **NO cambiar nada**
   - Las vistas llaman a Services
   - Services llaman a Repositories
   - Cambiar Repositories = cambiar persistencia sin tocar UI

**Métodos centralizados (preparados para BD):**

| Método | Servicio | Razón |
|--------|----------|-------|
| `get_precio_recomendado(precio)` | ProductoService | +80% recomendado, centralizado para evitar duplicar lógica |
| `apply_price_increase()` | ProductoService | Cambios masivos de precio |
| Cálculos de factura | FacturaService | Totales y descuentos compuestos |

**Flujo de migración (ya completado):**

```
✅ 1. Crear database/db.py con configuración de SQLite
✅ 2. Crear repositories con soporte SQLite
✅ 3. Modificar repositories para usar SQLite en lugar de JSON
✅ 4. Cambiar main.py: inicializar BD y migrar datos
✅ 5. Probar que todo funciona igual
✅ 6. Mantener archivos JSON como backup (reversible)
```

---

## 9. Esquema de Base de Datos SQLite

### Tablas principales:

#### CLIENTES
```sql
CREATE TABLE CLIENTES (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    dato_adicional TEXT,
    descuento_1 INTEGER DEFAULT 0,     -- 0=False, 1=True
    descuento_2 INTEGER DEFAULT 0,
    saldo REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### PRODUCTOS
```sql
CREATE TABLE PRODUCTOS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    descripcion TEXT NOT NULL,
    precio REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### FACTURAS
```sql
CREATE TABLE FACTURAS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT UNIQUE NOT NULL,
    cliente_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,                -- ISO format (YYYY-MM-DD)
    repartidor TEXT,
    dia_reparto TEXT,
    subtotal_general REAL DEFAULT 0.0,
    total REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES CLIENTES(id)
)
```

#### ITEMS_FACTURA
```sql
CREATE TABLE ITEMS_FACTURA (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    factura_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY (factura_id) REFERENCES FACTURAS(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES PRODUCTOS(id)
)
```

#### PAGOS
```sql
CREATE TABLE PAGOS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    monto REAL NOT NULL,
    fecha TEXT NOT NULL,                -- ISO format (YYYY-MM-DD)
    comentario TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES CLIENTES(id)
)
```

**Notas de diseño:**
- IDs internos de BD (INTEGER PK) para relaciones rápidas
- Códigos (cliente, producto) siguen siendo únicos y accesibles
- Fechas guardadas en formato ISO TEXT para compatibilidad
- Booleanos almacenados como INTEGER (0/1)
- Cascada en DELETE para ITEMS_FACTURA (eliminar factura → eliminar items)
- Timestamps para auditoría (created_at)
- Row factory habilitado para acceso por nombre en queries

## 10. Migración de Datos JSON a SQLite

**Proceso automático:**
- Al iniciar la app, `main.py` verifica si la BD está vacía
- Si está vacía, migra datos de archivos JSON (si existen)
- Esto permite transición gradual sin perder datos existentes
- Los archivos JSON se mantienen como backup (no se eliminan automáticamente)

**Función de migración:** `migrate_data_if_needed()` en `main.py`
- Migra productos y clientes automáticamente
- Facturas y pagos pueden migrarse después si es necesario
- Solo ejecuta una vez (detecta si BD ya tiene datos)

---

## 11. Flujo de Uso del Sistema

### Caso 1: Crear una factura

1. Usuario abre la app → Ve MainMenu
2. Hace clic en "Gestionar Facturas"
3. Ve FacturasView (listado vacío inicialmente)
4. Hace clic en "Nueva Factura" → Abre FacturaFormView
5. Busca cliente (ó lo selecciona si existe) mediante buscador
6. Ingresa "repartidor" (ej: "Juan")
7. Selecciona "día de reparto" (ej: "Lunes")
8. Busca producto en el buscador
9. Ingresa cantidad (ej: 5)
10. Hace clic en "Agregar item"
11. El sistema:
    - Copia el precio actual del producto
    - Calcula subtotal (5 × precio)
    - Suma al subtotal general
    - Aplica descuento del cliente
    - Calcula total final
12. Puede agregar más items (repetir 8-11)
13. Hace clic en "Guardar"
14. El sistema:
    - Crea la factura
    - Suma el total al saldo del cliente
    - Regresa a FacturasView
15. Usuario ve la factura creada en la lista

### Caso 2: Editar factura

1. Usuario selecciona factura de la lista
2. Hace clic en "Editar"
3. FacturaFormView se abre con datos de la factura
4. Puede:
   - Cambiar cliente
   - Cambiar repartidor
   - Cambiar día de reparto
   - Agregar/eliminar items
5. Hace clic en "Guardar"
6. El sistema:
   - Resta el viejo total del saldo del cliente anterior
   - Suma el nuevo total al cliente (igual o diferente)
   - Si cambió cliente: actualiza ambos saldos
7. Regresa a FacturasView

### Caso 3: Eliminar factura

1. Usuario selecciona factura
2. Hace clic en "Eliminar"
3. Sistema pide confirmación
4. Si confirma:
   - Resta el total al saldo del cliente
   - Elimina la factura
   - Regresa a FacturasView

---

## 12. Funcionalidades Agregadas Recientemente

| Fecha | Funcionalidad | Cambio |
|-------|---------------|--------|
| 2026-04-09 | Campo "repartidor" | Agregado a Factura para rastrear quién reparte |
| 2026-04-09 | Campo "día de reparto" | Agregado a Factura para programar entregas |
| 2026-04-09 | Buscadores | Cambiado de Dropdown a Entry + filtrado |
| 2026-04-09 | Filtros en tablas | Agregados en ClientesView, ProductosView, FacturasView |
| 2026-04-09 | Refactor de arquitectura | Separación en UI, Services, Models, Repositories |
| 2026-04-09 | Actualización de saldos | Automática al crear/editar/eliminar facturas |
| 2026-04-24 | Aumentos masivos de precios | Sección completa con selección avanzada, checkboxes, filtrado, contador, confirmación y preview |

---

## 13. Plan de Evolución Futuro

### Fase 1: SQLite (COMPLETADO - 3 de mayo de 2026)

**Objetivo:** Persistencia real entre sesiones.

**✅ Cambios realizados:**
- ✅ Creado `database/db.py` con clase Database (singleton)
- ✅ Reemplazado `ClienteRepository` para usar SQLite
- ✅ Reemplazado `ProductoRepository` para usar SQLite
- ✅ Reemplazado `FacturaRepository` para usar SQLite (con soporte a items)
- ✅ Reemplazado `PagoRepository` para usar SQLite
- ✅ Actualizado `main.py` para inicializar DB automáticamente
- ✅ Agregada migración automática de datos JSON → SQLite
- ✅ UI y Services SIN CAMBIOS (funcionan igual)
- ✅ Probadas todas las operaciones CRUD
- ✅ Datos persisten entre sesiones

**Archivos nuevos creados:**
- `database/__init__.py`
- `database/db.py`

**Archivos modificados:**
- `repositories/cliente_repository.py` (JSON → SQLite)
- `repositories/producto_repository.py` (JSON → SQLite)
- `repositories/factura_repository.py` (JSON → SQLite)
- `repositories/pago_repository.py` (JSON → SQLite)
- `main.py` (inicialización de BD, migración de datos)

**Resultado:** 🟢 COMPLETADO - Funcionalidad 100% operativa

### Fase 2: PDF

**Objetivo:** Exportar facturas a PDF.

**Cambios:**
- Agregar botón "Exportar PDF" en FacturasView
- Crear módulo `pdf_generator.py`
- Usar librería `reportlab` o `fpdf`

**Esfuerzo:** Bajo-Medio

### Fase 3: Funcionalidades Avanzadas

**Posibles mejoras:**
- Aumento masivo de precios (por porcentaje)
- Historial de cambios
- Búsqueda avanzada de facturas (por rango de fechas, cliente, etc.)
- Reportes (ventas por cliente, productos más vendidos, etc.)
- Búsqueda por número de factura con búsqueda de factura por rango de fechas

**Esfuerzo:** Variable

---

## 14. Criterios de Desarrollo (Reglas)

### Obligatorios

- ✅ NO romper funcionalidades existentes
- ✅ NO reescribir todo desde cero
- ✅ Mantener arquitectura en capas (UI, Services, Models, Repositories)
- ✅ Mantener UI en una sola pantalla (sin Toplevel emergentes)
- ✅ Mantener uso de buscadores (no volver a Dropdowns)
- ✅ Mantener el sistema funcionando en memoria hasta integrar DB
- ✅ Escribir código escalable y fácil de adaptar a SQLite
- ✅ Actualizar CONTEXTO_PROYECTO.md con cada cambio significativo

### Buenas prácticas

- 📝 Código limpio y comentado
- 🧪 Testing cuando sea posible
- 📊 Validación de datos en Services
- 🔍 Manejo de excepciones robusto
- 📋 Usar nombres descriptivos para variables/funciones

### Antes de cambios grandes

1. Explicar brevemente qué se va a hacer
2. Asegurar que sea compatible con futuro uso de SQLite
3. Confirmar con el usuario si es necesario

---

## 15. Cambios Recientes

Este registro mantiene un histórico de cambios significativos para referencia futura.

### 2026-05-03 - Integración de Base de Datos SQLite

**Objetivo principal:** Migrar de almacenamiento en JSON (en memoria) a SQLite para persistencia real entre sesiones.

**✅ Cambios realizados:**

1. **Nueva capa de Base de Datos:**
   - ✅ Creado módulo `database/db.py` con clase `Database` (singleton)
   - ✅ Gestión centralizada de conexiones SQLite
   - ✅ Creación automática de tablas si no existen
   - ✅ Context managers para manejo seguro de conexiones
   - ✅ Row factory habilitado para acceso por nombre

2. **Esquema de BD creado:**
   - ✅ Tabla CLIENTES (id, codigo, nombre, dato_adicional, descuento_1, descuento_2, saldo)
   - ✅ Tabla PRODUCTOS (id, codigo, descripcion, precio)
   - ✅ Tabla FACTURAS (id, numero, cliente_id, fecha, repartidor, dia_reparto, subtotal_general, total)
   - ✅ Tabla ITEMS_FACTURA (id, factura_id, producto_id, cantidad, precio_unitario, subtotal)
   - ✅ Tabla PAGOS (id, cliente_id, monto, fecha, comentario)
   - ✅ Relaciones FK con CASCADE DELETE para integridad

3. **Repositorios actualizados:**
   - ✅ `ProductoRepository` - CRUD completo via SQLite
   - ✅ `ClienteRepository` - CRUD completo via SQLite + método `update_saldo()`
   - ✅ `FacturaRepository` - CRUD completo via SQLite con soporte a items y relaciones
   - ✅ `PagoRepository` - CRUD completo via SQLite con IDs autonuméricos
   - ✅ Métodos especializados: `get_by_code_with_id()` para manejar IDs internos

4. **Migración automática de datos:**
   - ✅ Función `migrate_data_if_needed()` en main.py
   - ✅ Detecta si BD está vacía y migra datos JSON → SQLite
   - ✅ Preserva datos existentes sin perder información
   - ✅ Solo ejecuta una vez (no interfiere en ejecuciones posteriores)

5. **Inicialización de aplicación:**
   - ✅ `main.py` ahora inicializa Database automáticamente
   - ✅ Pasa instancia de BD a todos los repositorios
   - ✅ Services y UI permanecen sin cambios

**Archivos creados:**
- `database/__init__.py` (inicialización del módulo)
- `database/db.py` (clase Database y gestión de conexiones)

**Archivos modificados:**
- `repositories/cliente_repository.py` (JSON → SQLite)
- `repositories/producto_repository.py` (JSON → SQLite)
- `repositories/factura_repository.py` (JSON → SQLite)
- `repositories/pago_repository.py` (JSON → SQLite)
- `main.py` (inicialización BD + migración de datos)
- `CONTEXTO_PROYECTO.md` (actualización completa de documentación)

**Compatibilidad:**
- ✅ UI completamente funcional sin cambios
- ✅ Services funcionan igual sin cambios
- ✅ Models adaptables a cualquier formato de persistencia
- ✅ Arquitectura en capas intacta

**Validación y Pruebas:**
- ✅ Pruebas CRUD para ProductoRepository
- ✅ Pruebas CRUD para ClienteRepository
- ✅ Pruebas CRUD para FacturaRepository (con items)
- ✅ Pruebas CRUD para PagoRepository
- ✅ Pruebas de relaciones y integridad referencial
- ✅ Pruebas de persistencia entre sesiones

**Estado:** 🟢 COMPLETADO - Funcionalidad 100% operativa

**Impacto:**
- ✅ Datos ahora persisten entre sesiones
- ✅ No hay pérdida de funcionalidad
- ✅ Arquitectura lista para futuras mejoras
- ✅ Base de datos local (sin servidor)

**Notas técnicas importantes:**
- Los booleanos se almacenan como INTEGER (0/1) en SQLite
- Las fechas se guardan en formato ISO TEXT (YYYY-MM-DD)
- IDs internos de BD vs códigos de usuario se manejan correctamente
- Migración de datos es automática pero reversible (archivos JSON se mantienen)

### 2026-04-29 - Exportación de Productos a Excel (.xlsx)

**Cambios:**
- ✅ Nueva funcionalidad: Exportar todos los productos a archivo Excel
- ✅ Botón "Exportar a Excel" agregado en ProductosView
- ✅ Nuevo método en ProductoService: `export_to_excel(filepath)`
- ✅ Headers en negrita: Código, Descripción, Precio, Precio Recomendado
- ✅ Exporta TODOS los productos (no solo los filtrados)
- ✅ Incluye precio recomendado (+80%) calculado automáticamente
- ✅ Validación: Muestra "No hay productos para exportar" si está vacío
- ✅ Confirmación: Muestra "Exportación realizada con éxito" al finalizar
- ✅ Formato: .xlsx (Excel moderno con openpyxl)

**Archivos creados:**
- Ninguno nuevo (solo modificaciones)

**Archivos modificados:**
- `services/producto_service.py` (nuevo método export_to_excel)
- `ui/productos_view.py` (botón y método exportar_a_excel)
- `CONTEXTO_PROYECTO.md` (documentación)

**Dependencias agregadas:**
- `openpyxl` (para generar archivos Excel)

**Estado:** Funcionalidad completamente operativa

**Notas técnicas:**
- El service accede a datos via `get_all_products()`
- Precio recomendado se calcula usando `get_precio_recomendado()`
- Mantiene separación de capas: UI → Service → Repository
- Compatible con futura migración a SQLite

**Cómo usar:**
1. En ProductosView, hacer clic en botón "Exportar a Excel"
2. Elegir ubicación y nombre del archivo
3. Se genera .xlsx con todos los productos

---

### 2026-04-11 - Gestión de Pagos: ID autonumérico e integración con saldo

**Cambios:**
- ✅ Nueva entidad: `Pago` con ID autonumérico (no editable)
- ✅ Nuevo servicio: `PagoService` que gestiona crear/eliminar pagos
- ✅ Nuevo repositorio: `PagoRepository` con persistencia en JSON
- ✅ Nueva vista: `PagosView` con tabla, filtros y buscadores
- ✅ Formulario de pago con ID readonly, cliente (buscador), monto, fecha, comentario
- ✅ Integración con saldo del cliente:
  - Crear pago → **resta** el monto del saldo
  - Eliminar pago → **suma** el monto de vuelta al saldo
- ✅ Botón "Gestionar Pagos" agregado al menú principal

**Archivos creados:**
- `models.py` (agregada clase `Pago`)
- `repositories/pago_repository.py` (new)
- `services/pago_service.py` (new)
- `ui/pagos_view.py` (new)

**Archivos modificados:**
- `main.py` (integración de PagosView y PagoService)
- `ui/main_menu.py` (botón "Gestionar Pagos")
- `CONTEXTO_PROYECTO.md` (documentación)

**Estado:** Sistema completamente funcional con gestión de pagos

**Notas técnicas:**
- ID se genera automáticamente en el repositorio (incremental)
- Pagos están en memoria, persistidos en `data/pagos.json`
- El saldo del cliente se actualiza automáticamente
- Los cambios en saldo se reflejan inmediatamente en la tabla de clientes

---

### 2026-04-10 - Cambio en sistema de descuentos: bloques de 8% compuestos

**Cambios:**
- ✅ Reemplazado sistema de descuento numérico por bloques de 8% acumulativos (compuestos)
- ✅ Cliente ahora tiene `descuento_1` y `descuento_2` (booleanos) en lugar de `descuento` (porcentaje)
- ✅ Lógica de cálculo: 
  - 0 descuentos: sin descuento
  - 1 descuento: 8% 
  - 2 descuentos: 8% × 8% = 7.68% efectivo (compuesto, NO acumulado)
- ✅ UI de clientes: checkboxes "8% (1)" y "8% (2)" en lugar de campo numérico
- ✅ Tabla de clientes: columna "Descuentos" muestra "Sin descuento", "8%", o "8% + 8%"
- ✅ Factura: muestra descuentos aplicados con detalle (ej: "Descuentos: $XX.XX (8% + 8%)")

**Archivos modificados:**
- `models.py` (Cliente: descuento numérico → descuento_1, descuento_2 bool; Factura: nueva lógica de cálculo)
- `services/cliente_service.py` (parámetros create_client y update_client)
- `repositories/cliente_repository.py` (método update)
- `ui/clientes_view.py` (FormCliente con checkboxes, tabla actualizada)
- `ui/factura_form_view.py` (mostrar descuentos con nueva lógica)
- `CONTEXTO_PROYECTO.md` (documentación de cambios)

**Estado:** Sistema completamente funcional con nueva lógica de descuentos

**Notas técnicas:**
- `Factura.calcular_totales()`: ahora multiplica por 0.92 secuencialmente
- `Factura.obtener_descripcion_descuentos()`: retorna string descriptivo
- `Factura.obtener_descuento_valor()`: retorna monto total de descuento aplicado

---

### 2026-04-09 - Case-insensitive completo para códigos (Normalización total)

**Cambios:**
- ✅ Modelos (Cliente, Producto): Códigos normalizados a mayúsculas en `__init__`
- ✅ Repositorios: Búsquedas normalizadas (`get_by_code`, `update`, `delete`)
- ✅ UI (ClientesView, ProductosView): Normalización en búsquedas y eliminaciones
- ✅ UI (FacturaFormView): Normalización al seleccionar clientes y productos
- **Resultado:** `C002`, `c002`, `C002` → error "ya existe"

**Archivos modificados:** 
- `models.py` (Cliente, Producto)
- `repositories/cliente_repository.py` 
- `repositories/producto_repository.py`
- `ui/clientes_view.py`
- `ui/productos_view.py`
- `ui/factura_form_view.py`

**Estado:** Sistema completamente funcional en memoria

---

### 2026-04-09 - Códigos case-insensitive (normalizados a mayúsculas)

**Cambios:**
- ✅ Códigos de clientes siempre en mayúsculas (C002 = c002)
- ✅ Códigos de productos siempre en mayúsculas (P001 = p001)
- **Razón:** Evita duplicados accidentales por diferencia de mayúsculas/minúsculas

**Archivos modificados:** `models.py` - métodos `__init__` de Cliente y Producto

**Implementación:** Normalizado en `codigo.upper()` al crear/editar

**Estado:** Sistema completamente funcional en memoria

---

### 2026-04-09 - Reset de cantidad después de agregar producto

**Cambios:**
- ✅ Campo "cantidad" se resetea a 1 después de agregar un producto a factura
- **Razón:** Evita errores donde el usuario agrega un producto con la cantidad del anterior

**Archivo modificado:** `ui/factura_form_view.py` - método `agregar_item()`

**Estado:** Sistema completamente funcional en memoria

---

### 2026-04-09 - Versión Inicial Documentada

**Cambios:**
- ✅ Creado archivo CONTEXTO_PROYECTO.md como fuente de verdad
- ✅ Refactorización completa de arquitectura (3 capas)
- ✅ Campos "repartidor" y "día de reparto" agregados a facturas
- ✅ Buscadores implementados para clientes y productos
- ✅ Filtros agregados a todas las tablas
- ✅ Sistema de actualización automática de saldos de clientes

**Estado:** Sistema completamente funcional en memoria

---

## 14. Preguntas Frecuentes

### ¿Qué pasa si reinicio la aplicación? ¿Se pierden los datos?

Sí, actualmente se pierden. Es intencional (en memoria). Una vez agreguemos SQLite, los datos persistirán.

### ¿Por qué no usar Dropdowns?

Porque no escalan. Con 1000 clientes, un Dropdown es inutilizable. Los buscadores son mejor UX y están preparados para crecer.

### ¿Puedo cambiar el precio de un producto? ¿Afecta las facturas antiguas?

Sí, puedes cambiar el precio. NO afecta las facturas antiguas porque el precio se COPIA en el item. Las facturas mantienen su precio histórico.

### ¿Cómo se calcula el total de una factura?

1. Subtotal general = suma de (cantidad × precio) de todos los items
2. Descuento = subtotal general × (descuento del cliente / 100)
3. Total final = subtotal general - descuento

### ¿Qué es el "saldo" de un cliente?

Es el monto total que el cliente debe. Se actualiza automáticamente:
- +total cuando creas una factura
- Se ajusta cuando editas una factura
- -total cuando eliminas una factura

### ¿Se puede cambiar el cliente de una factura ya creada?

Sí. Cuando editas una factura y cambias de cliente:
- Resta el total del cliente anterior
- Suma el total al nuevo cliente
- Los saldos de ambos se actualizan correctamente

### ¿Cómo migrar a SQLite cuando llegue el momento?

Los Repositories (`ClienteRepository`, `ProductoRepository`, `FacturaRepository`) serán modificados para usar SQLite en lugar de JSON. La UI y Services no necesitarán cambios porque están desacopladas.

---

**Fin del documento**
