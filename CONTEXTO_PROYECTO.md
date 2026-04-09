# CONTEXTO_PROYECTO.md - Sistema de Facturación

**Versión:** 1.0  
**Última actualización:** 9 de abril de 2026  
**Estado:** Activo y en desarrollo

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
- 🔄 **Próximo paso:** Migrar a SQLite (persistencia real)
- 🔄 **Futuro:** Generar PDF de facturas
- 🔄 **Futuro:** Funcionalidades adicionales (aumentos masivos, etc.)

---

## 3. Tecnología

| Componente | Tecnología |
|-----------|-----------|
| Lenguaje | Python 3.11+ |
| Interfaz | Tkinter (GUI nativa) |
| Persistencia (actual) | JSON (en memoria) |
| Persistencia (futuro) | SQLite |
| Arquitectura | 3 capas (UI, Services, Models) |
| Tipo | Aplicación de escritorio (100% local) |

---

## 4. Estado Actual del Sistema

**🟢 Completamente funcional en memoria:**

- Sistema CRUD completo para las 3 entidades principales
- Interfaz gráfica operativa
- Cálculos de facturas funcionando
- Buscadores implementados
- Filtros en tablas implementados
- Almacenamiento en JSON (datos en memoria)

**❌ NO implementado aún:**

- Base de datos SQL
- Persistencia real (entre sesiones)
- Exportación a PDF
- Aumentos masivos de precios

---

## 5. Funcionalidades Actuales

### 5.1 Gestión de Clientes

**Pantalla:** ClientesView

**Campos de cliente:**
- `codigo` (único, clave primaria)
- `nombre` (nombre del cliente)
- `adicional` (dirección, CUIT, RUC, etc.)
- `descuento` (porcentaje, ej: 5%)
- `saldo` (monto pendiente de pago)

**Operaciones:**
- ✅ Crear cliente
- ✅ Editar cliente
- ✅ Eliminar cliente
- ✅ Listar clientes con buscador/filtro

**Notas importantes:**
- El descuento se aplica automáticamente a todas las facturas de ese cliente
- El saldo se actualiza cuando se crean/modifican/eliminan facturas

### 5.2 Gestión de Productos

**Pantalla:** ProductosView

**Campos de producto:**
- `codigo` (único, clave primaria)
- `descripcion` (nombre/descripción del producto)
- `precio` (precio unitario actual)

**Operaciones:**
- ✅ Crear producto
- ✅ Editar producto
- ✅ Eliminar producto
- ✅ Listar productos con buscador/filtro

**Notas importantes:**
- El precio es el precio actual en catálogo
- Cuando se agrega un producto a una factura, el precio se COPIA al item
- Cambios de precio en el catálogo NO afectan facturas ya creadas

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
- `descuento` = subtotal_general × (descuento_cliente / 100)
- `total_final` = subtotal_general - descuento

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

---

## 6. Estructura de Datos (Models)

### Cliente
```python
class Cliente:
    - codigo: str (único)
    - nombre: str
    - adicional: str (dirección, CUIT, etc.)
    - descuento: int (porcentaje)
    - saldo: float (default: 0.0)
```

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

### 7.4 Capa de Modelos (Models)

- Archivo: `models.py`
- Clases puras sin lógica de persistencia
- Métodos auxiliares: `to_dict()`, `from_dict()`

---

## 8. Decisiones de Diseño (Muy Importante)

### 8.1 "TODO en memoria" (por ahora)

**Decisión:** El sistema almacena datos en JSON en memoria, NO en base de datos.

**Por qué:**
- Simplifica el desarrollo inicial
- Permite enfocarse en lógica de negocio y UI
- Hace más fácil migrar a SQLite después (cambio solo en Repository)

**Limitación actual:**
- Los datos se pierden cuando cierras la aplicación
- No hay persistencia entre sesiones

**Futuro:**
- Se reemplazará con SQLite manteniendo la misma interfaz

### 8.2 Separación en capas

**Decisión:** La arquitectura se divide en 3 capas (UI, Services, Models).

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

## 9. Flujo de Uso del Sistema

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

## 10. Funcionalidades Agregadas Recientemente

| Fecha | Funcionalidad | Cambio |
|-------|---------------|--------|
| 2026-04-09 | Campo "repartidor" | Agregado a Factura para rastrear quién reparte |
| 2026-04-09 | Campo "día de reparto" | Agregado a Factura para programar entregas |
| 2026-04-09 | Buscadores | Cambiado de Dropdown a Entry + filtrado |
| 2026-04-09 | Filtros en tablas | Agregados en ClientesView, ProductosView, FacturasView |
| 2026-04-09 | Refactor de arquitectura | Separación en UI, Services, Models, Repositories |
| 2026-04-09 | Actualización de saldos | Automática al crear/editar/eliminar facturas |

---

## 11. Plan de Evolución Futuro

### Fase 1: SQLite (próxima)

**Objetivo:** Persistencia real entre sesiones.

**Cambios:**
- Crear Database con tablas: clientes, productos, facturas, items
- Reemplazar `ClienteRepository`, `ProductoRepository`, `FacturaRepository`
- UI y Services NO cambian
- Pruebas para garantizar datos persisten

**Esfuerzo:** Medio

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

## 12. Criterios de Desarrollo (Reglas)

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

## 13. Cambios Recientes

Este registro mantiene un histórico de cambios significativos para referencia futura.

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
