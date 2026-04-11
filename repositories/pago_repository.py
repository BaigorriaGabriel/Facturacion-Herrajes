# repositories/pago_repository.py
import json
from models import Pago

class PagoRepository:
    def __init__(self, cliente_repository, filepath="data/pagos.json"):
        self.filepath = filepath
        self.cliente_repository = cliente_repository
        self.pagos = self._load()
        self._next_id = self._calculate_next_id()

    def _load(self):
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
                pagos = []
                for p in data:
                    if isinstance(p, dict):
                        pago = Pago.from_dict(p, self.cliente_repository.get_all())
                        if pago:
                            pagos.append(pago)
                return pagos
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _calculate_next_id(self):
        """Calcula el próximo ID basado en los pagos existentes."""
        if not self.pagos:
            return 1
        return max(p.id for p in self.pagos) + 1

    def _save(self):
        with open(self.filepath, "w") as f:
            json.dump([p.to_dict() for p in self.pagos], f, indent=4)

    def get_all(self):
        return self.pagos

    def get_by_id(self, pago_id):
        return next((p for p in self.pagos if p.id == pago_id), None)

    def get_by_cliente(self, codigo_cliente):
        codigo_normalizado = codigo_cliente.upper()
        return [p for p in self.pagos if p.cliente.codigo == codigo_normalizado]

    def add(self, pago):
        # Asignar ID autonumérico
        pago.id = self._next_id
        self._next_id += 1
        self.pagos.append(pago)
        self._save()
        return pago

    def delete(self, pago_id):
        pago = self.get_by_id(pago_id)
        if pago:
            self.pagos.remove(pago)
            self._save()
            return True
        return False
