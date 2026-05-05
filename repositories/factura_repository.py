# repositories/factura_repository.py
from models import Factura, FacturaItem, Cliente, Producto
from database import Database
import datetime

class FacturaRepository:
    def __init__(self, cliente_repo, producto_repo, db=None):
        """
        Inicializa el repositorio de facturas con SQLite.
        
        Args:
            cliente_repo: Instancia de ClienteRepository
            producto_repo: Instancia de ProductoRepository
            db: Instancia de Database. Si es None, obtiene la instancia singleton.
        """
        self.cliente_repository = cliente_repo
        self.producto_repository = producto_repo
        self.db = db if db is not None else Database()

    def get_all(self):
        """Obtiene todas las facturas desde la BD."""
        facturas = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, numero, cliente_id, fecha, repartidor, dia_reparto, 
                       subtotal_general, total 
                FROM FACTURAS 
                ORDER BY numero
            ''')
            rows = cursor.fetchall()
            
            for row in rows:
                factura = self._build_factura_from_row(row, conn)
                if factura:
                    facturas.append(factura)
        
        return facturas

    def _build_factura_from_row(self, row, conn):
        """Construye un objeto Factura a partir de una fila de BD."""
        # Obtener cliente por su ID de BD
        cursor = conn.cursor()
        cursor.execute('SELECT codigo FROM CLIENTES WHERE id = ?', (row['cliente_id'],))
        cliente_row = cursor.fetchone()
        
        if not cliente_row:
            return None
        
        cliente = self.cliente_repository.get_by_code(cliente_row['codigo'])
        if not cliente:
            return None
        
        factura = Factura(
            cliente=cliente,
            numero_factura=row['numero'],
            repartidor=row['repartidor'],
            dia_reparto=row['dia_reparto']
        )
        factura.fecha = datetime.date.fromisoformat(row['fecha'])
        
        # Obtener items de la factura
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, producto_id, cantidad, precio_unitario, subtotal 
            FROM ITEMS_FACTURA 
            WHERE factura_id = ?
            ORDER BY id
        ''', (row['id'],))
        
        items_rows = cursor.fetchall()
        for item_row in items_rows:
            # Obtener producto por ID
            producto = self._get_producto_by_id(item_row['producto_id'])
            if producto:
                item = FacturaItem(producto, item_row['cantidad'])
                item.precio_unitario = item_row['precio_unitario']
                item.subtotal = item_row['subtotal']
                factura.items.append(item)
        
        factura.subtotal_general = row['subtotal_general']
        factura.total = row['total']
        
        return factura

    def _get_producto_by_id(self, producto_id):
        """Obtiene un producto por su ID de BD interno."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT codigo, descripcion, precio FROM PRODUCTOS WHERE id = ?', (producto_id,))
            row = cursor.fetchone()
            if row:
                return Producto(row['codigo'], row['descripcion'], row['precio'])
        return None

    def _get_cliente_id(self, codigo_cliente):
        """Obtiene el ID interno de BD de un cliente por su código."""
        cliente, cliente_id = self.cliente_repository.get_by_code_with_id(codigo_cliente)
        return cliente_id

    def _get_producto_id(self, codigo_producto):
        """Obtiene el ID interno de BD de un producto por su código."""
        producto, producto_id = self.producto_repository.get_by_code_with_id(codigo_producto)
        return producto_id

    def get_by_number(self, numero):
        """Obtiene una factura por su número."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, numero, cliente_id, fecha, repartidor, dia_reparto, 
                       subtotal_general, total 
                FROM FACTURAS 
                WHERE numero = ?
            ''', (numero,))
            row = cursor.fetchone()
            
            if row:
                return self._build_factura_from_row(row, conn)
        
        return None

    def get_next_invoice_number(self):
        """Obtiene el próximo número de factura."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT MAX(CAST(numero AS INTEGER)) as max_num FROM FACTURAS')
            row = cursor.fetchone()
            
            if row and row['max_num']:
                return row['max_num'] + 1
            return 1

    def add(self, factura):
        """Agrega una nueva factura a la BD."""
        if factura.numero is None:
            factura.numero = self.get_next_invoice_number()
        
        if self.get_by_number(factura.numero):
            return False
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener cliente_id
                cliente_id = self._get_cliente_id(factura.cliente.codigo)
                if not cliente_id:
                    return False
                
                # Insertar factura
                cursor.execute('''
                    INSERT INTO FACTURAS 
                    (numero, cliente_id, fecha, repartidor, dia_reparto, subtotal_general, total) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(factura.numero),
                    cliente_id,
                    factura.fecha.isoformat(),
                    factura.repartidor,
                    factura.dia_reparto,
                    factura.subtotal_general,
                    factura.total
                ))
                
                factura_id = cursor.lastrowid
                
                # Insertar items
                for item in factura.items:
                    producto_id = self._get_producto_id(item.producto.codigo)
                    if producto_id:
                        cursor.execute('''
                            INSERT INTO ITEMS_FACTURA 
                            (factura_id, producto_id, cantidad, precio_unitario, subtotal) 
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            factura_id,
                            producto_id,
                            item.cantidad,
                            item.precio_unitario,
                            item.subtotal
                        ))
                
                conn.commit()
            return True
        except Exception as e:
            print(f"Error al agregar factura: {e}")
            return False

    def update(self, numero, updated_factura):
        """Actualiza una factura existente."""
        factura_actual = self.get_by_number(numero)
        if not factura_actual:
            return False
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener factura_id de BD
                cursor.execute('SELECT id FROM FACTURAS WHERE numero = ?', (numero,))
                row = cursor.fetchone()
                if not row:
                    return False
                
                factura_id = row['id']
                cliente_id = self._get_cliente_id(updated_factura.cliente.codigo)
                
                # Actualizar factura
                cursor.execute('''
                    UPDATE FACTURAS 
                    SET cliente_id = ?, fecha = ?, repartidor = ?, dia_reparto = ?, 
                        subtotal_general = ?, total = ?
                    WHERE id = ?
                ''', (
                    cliente_id,
                    updated_factura.fecha.isoformat(),
                    updated_factura.repartidor,
                    updated_factura.dia_reparto,
                    updated_factura.subtotal_general,
                    updated_factura.total,
                    factura_id
                ))
                
                # Eliminar items antiguos
                cursor.execute('DELETE FROM ITEMS_FACTURA WHERE factura_id = ?', (factura_id,))
                
                # Insertar items nuevos
                for item in updated_factura.items:
                    producto_id = self._get_producto_id(item.producto.codigo)
                    if producto_id:
                        cursor.execute('''
                            INSERT INTO ITEMS_FACTURA 
                            (factura_id, producto_id, cantidad, precio_unitario, subtotal) 
                            VALUES (?, ?, ?, ?, ?)
                        ''', (
                            factura_id,
                            producto_id,
                            item.cantidad,
                            item.precio_unitario,
                            item.subtotal
                        ))
                
                conn.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar factura: {e}")
            return False

    def delete(self, numero):
        """Elimina una factura por su número."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener factura_id
                cursor.execute('SELECT id FROM FACTURAS WHERE numero = ?', (numero,))
                row = cursor.fetchone()
                if not row:
                    return False
                
                factura_id = row['id']
                
                # Eliminar items (con cascada, pero lo hacemos explícito)
                cursor.execute('DELETE FROM ITEMS_FACTURA WHERE factura_id = ?', (factura_id,))
                
                # Eliminar factura
                cursor.execute('DELETE FROM FACTURAS WHERE id = ?', (factura_id,))
                
                conn.commit()
            return True
        except Exception:
            return False
