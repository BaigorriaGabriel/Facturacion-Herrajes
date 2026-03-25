# services/producto_service.py
from models import Producto
from repositories.producto_repository import ProductoRepository

class ProductoService:
    def __init__(self, repository: ProductoRepository):
        self._repository = repository

    def get_all_products(self):
        return self._repository.get_all()

    def create_product(self, codigo, descripcion, precio):
        if self._repository.get_by_code(codigo):
            raise ValueError(f"Producto con código {codigo} ya existe.")
        
        nuevo_producto = Producto(codigo, descripcion, precio)
        self._repository.add(nuevo_producto)
        return nuevo_producto

    def update_product(self, codigo, descripcion, precio):
        return self._repository.update(codigo, descripcion, precio)

    def delete_product(self, codigo):
        # Future: check if product is in any non-finalized invoice, etc.
        return self._repository.delete(codigo)
