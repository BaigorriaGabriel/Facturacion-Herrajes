# models.py
import datetime

import datetime
import json

class Cliente:
    def __init__(self, codigo, nombre, adicional, descuento, saldo=0.0):
        self.codigo = codigo
        self.nombre = nombre
        self.adicional = adicional
        self.descuento = descuento
        self.saldo = saldo

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        return Cliente(**data)

class ClientesModel:
    def __init__(self):
        self.filepath = "data/clientes.json"
        self.clientes = self._load()

    def _load(self):
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
                return [Cliente.from_dict(c) for c in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save(self):
        with open(self.filepath, "w") as f:
            json.dump([c.to_dict() for c in self.clientes], f, indent=4)

    def agregar(self, cliente):
        if any(c.codigo == cliente.codigo for c in self.clientes):
            return False
        self.clientes.append(cliente)
        self._save()
        return True

    def obtener_todos(self):
        return self.clientes

    def actualizar(self, codigo, nombre, adicional, descuento, saldo):
        for cliente in self.clientes:
            if cliente.codigo == codigo:
                cliente.nombre = nombre
                cliente.adicional = adicional
                cliente.descuento = descuento
                cliente.saldo = saldo
                self._save()
                return True
        return False

    def eliminar(self, codigo):
        self.clientes = [c for c in self.clientes if c.codigo != codigo]
        self._save()

class Producto:
    def __init__(self, codigo, descripcion, precio):
        self.codigo = codigo
        self.descripcion = descripcion
        self.precio = precio
    
    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        return Producto(**data)

class ProductosModel:
    def __init__(self):
        self.filepath = "data/productos.json"
        self.productos = self._load()

    def _load(self):
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
                return [Producto.from_dict(p) for p in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save(self):
        with open(self.filepath, "w") as f:
            json.dump([p.to_dict() for p in self.productos], f, indent=4)

    def agregar(self, producto):
        if any(p.codigo == producto.codigo for p in self.productos):
            return False
        self.productos.append(producto)
        self._save()
        return True

    def obtener_todos(self):
        return self.productos

    def actualizar(self, codigo, descripcion, precio):
        for producto in self.productos:
            if producto.codigo == codigo:
                producto.descripcion = descripcion
                producto.precio = precio
                self._save()
                return True
        return False

    def eliminar(self, codigo):
        self.productos = [p for p in self.productos if p.codigo != codigo]
        self._save()

# Instancias globales
CLIENTES_MODEL = ClientesModel()
PRODUCTOS_MODEL = ProductosModel()

class FacturaItem:
    def __init__(self, producto, cantidad):
        self.producto = producto
        self.cantidad = cantidad
        self.precio_unitario = producto.precio
        self.subtotal = self.cantidad * self.precio_unitario

    def to_dict(self):
        return {
            "producto_codigo": self.producto.codigo,
            "cantidad": self.cantidad,
            "precio_unitario": self.precio_unitario
        }

    @staticmethod
    def from_dict(data, productos):
        producto = next((p for p in productos if p.codigo == data["producto_codigo"]), None)
        if producto:
            item = FacturaItem(producto, data["cantidad"])
            # El subtotal se calcula en el init, pero el precio unitario puede haber cambiado
            item.precio_unitario = data["precio_unitario"]
            item.subtotal = item.cantidad * item.precio_unitario
            return item
        return None

class Factura:
    def __init__(self, cliente, numero_factura=None, repartidor=""):
        self.numero = numero_factura
        self.cliente = cliente
        self.fecha = datetime.date.today()
        self.repartidor = repartidor
        self.items = []
        self.subtotal_general = 0.0
        self.total = 0.0



    def agregar_item(self, nuevo_item):
        # Verificar si el producto ya existe en los ítems de la factura
        for item_existente in self.items:
            if item_existente.producto.codigo == nuevo_item.producto.codigo:
                # Si existe, se suma la cantidad y se recalcula el subtotal del ítem
                item_existente.cantidad += nuevo_item.cantidad
                item_existente.subtotal = item_existente.cantidad * item_existente.precio_unitario
                self.calcular_totales()
                return # Termina la función para no agregar un nuevo ítem

        # Si no existe, se agrega el nuevo ítem a la lista
        self.items.append(nuevo_item)
        self.calcular_totales()

    def eliminar_item(self, index):
        if 0 <= index < len(self.items):
            del self.items[index]
            self.calcular_totales()
            
    def calcular_totales(self):
        self.subtotal_general = sum(item.subtotal for item in self.items)
        descuento = self.subtotal_general * (self.cliente.descuento / 100)
        self.total = self.subtotal_general - descuento
        
    def to_dict(self):
        return {
            "numero": self.numero,
            "cliente_codigo": self.cliente.codigo,
            "fecha": self.fecha.isoformat(),
            "repartidor": self.repartidor,
            "items": [item.to_dict() for item in self.items]
        }

    @staticmethod
    def from_dict(data, clientes, productos):
        cliente = next((c for c in clientes if c.codigo == data["cliente_codigo"]), None)
        if cliente:
            factura = Factura(cliente, numero_factura=data["numero"])
            factura.fecha = datetime.date.fromisoformat(data["fecha"])
            factura.repartidor = data.get("repartidor", "")
            factura.items = [FacturaItem.from_dict(item_data, productos) for item_data in data["items"]]
            factura.items = [item for item in factura.items if item] # Filtrar nulos si no se encontró producto
            factura.calcular_totales()
            return factura
        return None

class FacturasModel:
    def __init__(self):
        self.filepath = "data/facturas.json"
        self.facturas = self._load()

    def _load(self):
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
                clientes = CLIENTES_MODEL.obtener_todos()
                productos = PRODUCTOS_MODEL.obtener_todos()
                return [Factura.from_dict(f_data, clientes, productos) for f_data in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save(self):
        with open(self.filepath, "w") as f:
            json.dump([f.to_dict() for f in self.facturas], f, indent=4)

    def _generar_numero(self):
        if not self.facturas:
            return 1
        return max(f.numero for f in self.facturas) + 1

    def agregar(self, factura):
        if factura.numero is None:
            factura.numero = self._generar_numero()
        # Antes de agregar, se actualiza el saldo del cliente
        factura.cliente.saldo += factura.total
        CLIENTES_MODEL.actualizar(factura.cliente.codigo, factura.cliente.nombre, factura.cliente.adicional, factura.cliente.descuento, factura.cliente.saldo)
        self.facturas.append(factura)
        self._save()
        return True

    def obtener_todas(self):
        return self.facturas
    
    def obtener_por_numero(self, numero):
        return next((f for f in self.facturas if f.numero == numero), None)

    def actualizar(self, numero_factura, nueva_factura_data):
        factura_existente = self.obtener_por_numero(numero_factura)
        if not factura_existente:
            return False

        # Revertir el saldo anterior del cliente
        factura_existente.cliente.saldo -= factura_existente.total
        CLIENTES_MODEL.actualizar(factura_existente.cliente.codigo, factura_existente.cliente.nombre, factura_existente.cliente.adicional, factura_existente.cliente.descuento, factura_existente.cliente.saldo)
        
        # Actualizar la factura
        factura_existente.cliente = nueva_factura_data.cliente
        factura_existente.items = nueva_factura_data.items
        factura_existente.calcular_totales()
        
        # Aplicar el nuevo saldo al cliente (que podría ser el mismo u otro)
        factura_existente.cliente.saldo += factura_existente.total
        CLIENTES_MODEL.actualizar(factura_existente.cliente.codigo, factura_existente.cliente.nombre, factura_existente.cliente.adicional, factura_existente.cliente.descuento, factura_existente.cliente.saldo)
        self._save()
        return True

    def eliminar(self, numero):
        factura_a_eliminar = self.obtener_por_numero(numero)
        if factura_a_eliminar:
            # Revertir el saldo del cliente antes de eliminar
            factura_a_eliminar.cliente.saldo -= factura_a_eliminar.total
            CLIENTES_MODEL.actualizar(factura_a_eliminar.cliente.codigo, factura_a_eliminar.cliente.nombre, factura_a_eliminar.cliente.adicional, factura_a_eliminar.cliente.descuento, factura_a_eliminar.cliente.saldo)
            self.facturas = [f for f in self.facturas if f.numero != numero]
            self._save()
            return True
        return False

# Instancias globales
CLIENTES_MODEL = ClientesModel()
PRODUCTOS_MODEL = ProductosModel()
FACTURAS_MODEL = FacturasModel()
