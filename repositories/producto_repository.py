# repositories/producto_repository.py
from models import Producto
from database import Database

class ProductoRepository:
    def __init__(self, db=None):
        """
        Inicializa el repositorio de productos con SQLite.
        
        Args:
            db: Instancia de Database. Si es None, obtiene la instancia singleton.
        """
        self.db = db if db is not None else Database()

    def get_all(self):
        """Obtiene todos los productos desde la BD."""
        productos = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, codigo, descripcion, precio FROM PRODUCTOS ORDER BY codigo')
            rows = cursor.fetchall()
            for row in rows:
                producto = Producto(row['codigo'], row['descripcion'], row['precio'])
                productos.append(producto)
        return productos

    def get_by_code(self, codigo):
        """Obtiene un producto por su código."""
        codigo_normalizado = codigo.upper()
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, codigo, descripcion, precio FROM PRODUCTOS WHERE UPPER(codigo) = ?', 
                         (codigo_normalizado,))
            row = cursor.fetchone()
            if row:
                return Producto(row['codigo'], row['descripcion'], row['precio'])
        return None

    def get_by_code_with_id(self, codigo):
        """Obtiene un producto y su ID interno de BD por su código."""
        codigo_normalizado = codigo.upper()
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, codigo, descripcion, precio FROM PRODUCTOS WHERE UPPER(codigo) = ?', 
                         (codigo_normalizado,))
            row = cursor.fetchone()
            if row:
                producto = Producto(row['codigo'], row['descripcion'], row['precio'])
                return producto, row['id']
        return None, None

    def add(self, producto):
        """Agrega un nuevo producto a la BD."""
        if self.get_by_code(producto.codigo):
            return False
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO PRODUCTOS (codigo, descripcion, precio) 
                    VALUES (?, ?, ?)
                ''', (producto.codigo, producto.descripcion, producto.precio))
                conn.commit()
            return True
        except Exception:
            return False

    def update(self, codigo, descripcion, precio):
        """Actualiza un producto existente."""
        codigo_normalizado = codigo.upper()
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE PRODUCTOS 
                    SET descripcion = ?, precio = ? 
                    WHERE UPPER(codigo) = ?
                ''', (descripcion, precio, codigo_normalizado))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False

    def delete(self, codigo):
        """Elimina un producto por su código."""
        codigo_normalizado = codigo.upper()
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM PRODUCTOS WHERE UPPER(codigo) = ?', (codigo_normalizado,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
