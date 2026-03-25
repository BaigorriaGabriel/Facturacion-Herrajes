# repositories/factura_repository.py
import json
from models import Factura, FacturaItem, Cliente, Producto

class FacturaRepository:
    def __init__(self, cliente_repo, producto_repo, filepath="data/facturas.json"):
        self.filepath = filepath
        self.cliente_repository = cliente_repo
        self.producto_repository = producto_repo
        self.facturas = self._load()

    def _load(self):
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
                clientes = self.cliente_repository.get_all()
                productos = self.producto_repository.get_all()
                # Create a temporary list, then filter out None values
                # This handles cases where an invoice's client/product may have been deleted
                facturas_loaded = [Factura.from_dict(f_data, clientes, productos) for f_data in data]
                return [f for f in facturas_loaded if f is not None]
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save(self):
        with open(self.filepath, "w") as f:
            # The to_dict method on the models handles conversion
            json.dump([f.to_dict() for f in self.facturas], f, indent=4)

    def get_all(self):
        return self.facturas

    def get_by_number(self, numero):
        return next((f for f in self.facturas if f.numero == numero), None)
    
    def get_next_invoice_number(self):
        if not self.facturas:
            return 1
        return max(f.numero for f in self.facturas) + 1

    def add(self, factura):
        if factura.numero is None:
            factura.numero = self.get_next_invoice_number()
        
        if self.get_by_number(factura.numero):
            return False

        self.facturas.append(factura)
        self._save()
        return True

    def update(self, numero, updated_factura):
        factura = self.get_by_number(numero)
        if factura:
            # Replace the old instance with the new one
            index = self.facturas.index(factura)
            self.facturas[index] = updated_factura
            self._save()
            return True
        return False

    def delete(self, numero):
        factura = self.get_by_number(numero)
        if factura:
            self.facturas.remove(factura)
            self._save()
            return True
        return False
