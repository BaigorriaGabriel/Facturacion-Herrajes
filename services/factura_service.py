# services/factura_service.py
from models import Factura
from repositories.factura_repository import FacturaRepository
from services.cliente_service import ClienteService

class FacturaService:
    def __init__(self, repository: FacturaRepository, cliente_service: ClienteService):
        self._repository = repository
        self._cliente_service = cliente_service

    def get_all_invoices(self):
        return self._repository.get_all()

    def get_invoice_by_number(self, numero):
        return self._repository.get_by_number(numero)

    def create_invoice(self, factura: Factura):
        """ Creates a new invoice and updates the client's balance. """
        if factura.numero and self._repository.get_by_number(factura.numero):
            raise ValueError(f"Factura con número {factura.numero} ya existe.")

        # Business logic: Calculate totals and update client balance
        factura.calcular_totales()
        self._cliente_service.update_client_balance(factura.cliente.codigo, factura.total)
        
        return self._repository.add(factura)

    def update_invoice(self, numero, updated_factura_data: Factura):
        """ Updates an invoice and adjusts client balances accordingly. """
        existing_invoice = self._repository.get_by_number(numero)
        if not existing_invoice:
            return False

        # 1. Revert the old balance from the original client
        self._cliente_service.update_client_balance(existing_invoice.cliente.codigo, -existing_invoice.total)

        # 2. If the client has changed, the new client needs to be fetched for the updated invoice
        if existing_invoice.cliente.codigo != updated_factura_data.cliente.codigo:
            # The UI should pass the full client object, this is a safeguard
            pass 

        # 3. Recalculate totals for the updated data
        updated_factura_data.calcular_totales()
        
        # 4. Apply the new balance to the potentially new client
        self._cliente_service.update_client_balance(updated_factura_data.cliente.codigo, updated_factura_data.total)
        
        # 5. Persist the change
        return self._repository.update(numero, updated_factura_data)


    def delete_invoice(self, numero):
        """ Deletes an invoice and reverts the client's balance. """
        invoice_to_delete = self._repository.get_by_number(numero)
        if not invoice_to_delete:
            return False
            
        # Business logic: Revert client's balance
        self._cliente_service.update_client_balance(invoice_to_delete.cliente.codigo, -invoice_to_delete.total)
        
        return self._repository.delete(numero)
