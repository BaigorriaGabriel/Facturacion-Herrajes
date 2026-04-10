# repositories/cliente_repository.py
import json
from models import Cliente

class ClienteRepository:
    def __init__(self, filepath="data/clientes.json"):
        self.filepath = filepath
        self.clientes = self._load()

    def _load(self):
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
                return [Cliente.from_dict(c) for c in data]
        except (FileNotFoundError, json.JSONDecodeError):
            # If the file doesn't exist or is empty, start with an empty list
            return []

    def _save(self):
        with open(self.filepath, "w") as f:
            json.dump([c.to_dict() for c in self.clientes], f, indent=4)

    def get_all(self):
        return self.clientes

    def get_by_code(self, codigo):
        codigo_normalizado = codigo.upper()
        return next((c for c in self.clientes if c.codigo == codigo_normalizado), None)

    def add(self, cliente):
        if self.get_by_code(cliente.codigo):
            # Or raise an exception, depending on desired error handling
            return False 
        self.clientes.append(cliente)
        self._save()
        return True

    def update(self, codigo, nombre, adicional, descuento, saldo):
        codigo_normalizado = codigo.upper()
        cliente = self.get_by_code(codigo_normalizado)
        if cliente:
            cliente.nombre = nombre
            cliente.adicional = adicional
            cliente.descuento = descuento
            cliente.saldo = saldo
            self._save()
            return True
        return False

    def delete(self, codigo):
        codigo_normalizado = codigo.upper()
        cliente = self.get_by_code(codigo_normalizado)
        if cliente:
            self.clientes.remove(cliente)
            self._save()
            return True
        return False
