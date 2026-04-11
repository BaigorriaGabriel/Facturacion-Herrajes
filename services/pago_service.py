# services/pago_service.py
from models import Pago
from repositories.pago_repository import PagoRepository

class PagoService:
    def __init__(self, repository: PagoRepository, cliente_service):
        self._repository = repository
        self._cliente_service = cliente_service

    def get_all_payments(self):
        return self._repository.get_all()

    def get_payments_by_cliente(self, codigo_cliente):
        return self._repository.get_by_cliente(codigo_cliente)

    def create_payment(self, cliente, monto, fecha=None, comentario=""):
        """Crea un pago y automáticamente resta del saldo del cliente."""
        if monto <= 0:
            raise ValueError("El monto debe ser mayor que cero.")
        
        if not cliente:
            raise ValueError("Debe seleccionar un cliente.")
        
        # Crear pago (el ID se asigna en el repositorio)
        pago = Pago(cliente, monto, fecha, comentario)
        pago = self._repository.add(pago)
        
        # Restar del saldo del cliente
        self._cliente_service.update_client_balance(cliente.codigo, -monto)
        
        return pago

    def delete_payment(self, pago_id):
        """Elimina un pago y suma el monto de vuelta al saldo del cliente."""
        pago = self._repository.get_by_id(pago_id)
        
        if pago:
            # Sumar el monto de vuelta al saldo del cliente
            self._cliente_service.update_client_balance(pago.cliente.codigo, pago.monto)
            
            # Eliminar el pago
            return self._repository.delete(pago_id)
        
        return False

    def get_payment_by_id(self, pago_id):
        return self._repository.get_by_id(pago_id)
