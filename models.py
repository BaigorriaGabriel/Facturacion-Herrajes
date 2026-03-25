# models.py
import datetime

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
        # This method needs access to the list of all products to find the match.
        # This dependency will be handled by the repository/service layer later.
        producto = next((p for p in productos if p.codigo == data["producto_codigo"]), None)
        if producto:
            item = FacturaItem(producto, data["cantidad"])
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
        for item_existente in self.items:
            if item_existente.producto.codigo == nuevo_item.producto.codigo:
                item_existente.cantidad += nuevo_item.cantidad
                item_existente.subtotal = item_existente.cantidad * item_existente.precio_unitario
                self.calcular_totales()
                return
        self.items.append(nuevo_item)
        self.calcular_totales()

    def eliminar_item(self, index):
        if 0 <= index < len(self.items):
            del self.items[index]
            self.calcular_totales()
            
    def calcular_totales(self):
        self.subtotal_general = sum(item.subtotal for item in self.items)
        if self.cliente:
            descuento = self.subtotal_general * (self.cliente.descuento / 100)
            self.total = self.subtotal_general - descuento
        else:
            self.total = self.subtotal_general
        
    def to_dict(self):
        return {
            "numero": self.numero,
            "cliente_codigo": self.cliente.codigo if self.cliente else None,
            "fecha": self.fecha.isoformat(),
            "repartidor": self.repartidor,
            "items": [item.to_dict() for item in self.items]
        }

    @staticmethod
    def from_dict(data, clientes, productos):
        # This method needs access to client and product lists.
        # This dependency will be handled by the repository/service layer later.
        cliente = next((c for c in clientes if c.codigo == data["cliente_codigo"]), None)
        if cliente:
            factura = Factura(cliente, numero_factura=data["numero"], repartidor=data.get("repartidor", ""))
            factura.fecha = datetime.date.fromisoformat(data["fecha"])
            
            factura.items = []
            if data.get("items"):
                for item_data in data["items"]:
                    item = FacturaItem.from_dict(item_data, productos)
                    if item:
                        factura.items.append(item)

            factura.calcular_totales()
            return factura
        return None
