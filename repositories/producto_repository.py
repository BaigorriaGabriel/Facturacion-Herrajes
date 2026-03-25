# repositories/producto_repository.py
import json
from models import Producto

class ProductoRepository:
    def __init__(self, filepath="data/productos.json"):
        self.filepath = filepath
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

    def get_all(self):
        return self.productos

    def get_by_code(self, codigo):
        return next((p for p in self.productos if p.codigo == codigo), None)

    def add(self, producto):
        if self.get_by_code(producto.codigo):
            return False
        self.productos.append(producto)
        self._save()
        return True

    def update(self, codigo, descripcion, precio):
        producto = self.get_by_code(codigo)
        if producto:
            producto.descripcion = descripcion
            producto.precio = precio
            self._save()
            return True
        return False

    def delete(self, codigo):
        producto = self.get_by_code(codigo)
        if producto:
            self.productos.remove(producto)
            self._save()
            return True
        return False
