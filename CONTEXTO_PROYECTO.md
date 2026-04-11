# CONTEXTO_PROYECTO.md - Sistema de Facturación

**Versión:** 1.2  
**Última actualización:** 11 de abril de 2026  
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
