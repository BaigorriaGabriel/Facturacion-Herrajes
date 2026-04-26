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

    def apply_price_increase(self, producto_codigos, porcentaje):
        """
        Aplica un aumento de precio a múltiples productos.
        
        Args:
            producto_codigos: Lista de códigos de productos
            porcentaje: Porcentaje de aumento (ej: 10 para 10%)
        
        Returns:
            Número de productos actualizados
        
        Raises:
            ValueError: Si porcentaje <= 0 o si no hay productos a actualizar
        """
        if porcentaje <= 0:
            raise ValueError("El porcentaje debe ser mayor a 0")
        
        if not producto_codigos or len(producto_codigos) == 0:
            raise ValueError("Debe seleccionar al menos un producto")
        
        actualizados = 0
        for codigo in producto_codigos:
            producto = self._repository.get_by_code(codigo)
            if producto:
                # Calcular nuevo precio
                nuevo_precio = producto.precio * (1 + porcentaje / 100)
                # Redondear a 2 decimales
                nuevo_precio = round(nuevo_precio, 2)
                # Actualizar
                self._repository.update(codigo, producto.descripcion, nuevo_precio)
                actualizados += 1
        
        return actualizados
