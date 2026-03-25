# services/cliente_service.py
from models import Cliente
from repositories.cliente_repository import ClienteRepository

class ClienteService:
    def __init__(self, repository: ClienteRepository):
        self._repository = repository

    def get_all_clients(self):
        return self._repository.get_all()

    def create_client(self, codigo, nombre, adicional, descuento, saldo=0.0):
        # Business logic could be added here, e.g., validation
        if self._repository.get_by_code(codigo):
            raise ValueError(f"Cliente con código {codigo} ya existe.")
        
        # Using the model class to create a new instance
        nuevo_cliente = Cliente(codigo, nombre, adicional, descuento, saldo=saldo)
        self._repository.add(nuevo_cliente)
        return nuevo_cliente

    def update_client(self, codigo, nombre, adicional, descuento, saldo):
        # In a real scenario, you might not allow direct saldo updates from here
        return self._repository.update(codigo, nombre, adicional, descuento, saldo)

    def delete_client(self, codigo):
        # Add business logic, e.g., check if client has outstanding invoices
        return self._repository.delete(codigo)
    
    def update_client_balance(self, codigo, amount):
        """ Atomically updates a client's balance. """
        client = self._repository.get_by_code(codigo)
        if client:
            client.saldo += amount
            return self.update_client(
                client.codigo, 
                client.nombre, 
                client.adicional, 
                client.descuento, 
                client.saldo
            )
        return False
