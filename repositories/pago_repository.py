# repositories/pago_repository.py
from models import Pago
from database import Database
import datetime

class PagoRepository:
    def __init__(self, cliente_repository, db=None):
        """
        Inicializa el repositorio de pagos con SQLite.
        
        Args:
            cliente_repository: Instancia de ClienteRepository
            db: Instancia de Database. Si es None, obtiene la instancia singleton.
        """
        self.cliente_repository = cliente_repository
        self.db = db if db is not None else Database()

    def get_all(self):
        """Obtiene todos los pagos desde la BD."""
        pagos = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.cliente_id, p.monto, p.fecha, p.comentario, c.codigo 
                FROM PAGOS p
                JOIN CLIENTES c ON p.cliente_id = c.id
                ORDER BY p.id DESC
            ''')
            rows = cursor.fetchall()
            
            for row in rows:
                cliente = self.cliente_repository.get_by_code(row['codigo'])
                if cliente:
                    pago = Pago(
                        cliente=cliente,
                        monto=row['monto'],
                        fecha=datetime.date.fromisoformat(row['fecha']),
                        comentario=row['comentario'],
                        pago_id=row['id']
                    )
                    pagos.append(pago)
        
        return pagos

    def get_by_id(self, pago_id):
        """Obtiene un pago por su ID."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.cliente_id, p.monto, p.fecha, p.comentario, c.codigo 
                FROM PAGOS p
                JOIN CLIENTES c ON p.cliente_id = c.id
                WHERE p.id = ?
            ''', (pago_id,))
            row = cursor.fetchone()
            
            if row:
                cliente = self.cliente_repository.get_by_code(row['codigo'])
                if cliente:
                    return Pago(
                        cliente=cliente,
                        monto=row['monto'],
                        fecha=datetime.date.fromisoformat(row['fecha']),
                        comentario=row['comentario'],
                        pago_id=row['id']
                    )
        
        return None

    def get_by_cliente(self, codigo_cliente):
        """Obtiene todos los pagos de un cliente."""
        codigo_normalizado = codigo_cliente.upper()
        pagos = []
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.cliente_id, p.monto, p.fecha, p.comentario, c.codigo 
                FROM PAGOS p
                JOIN CLIENTES c ON p.cliente_id = c.id
                WHERE UPPER(c.codigo) = ?
                ORDER BY p.id DESC
            ''', (codigo_normalizado,))
            rows = cursor.fetchall()
            
            for row in rows:
                cliente = self.cliente_repository.get_by_code(row['codigo'])
                if cliente:
                    pago = Pago(
                        cliente=cliente,
                        monto=row['monto'],
                        fecha=datetime.date.fromisoformat(row['fecha']),
                        comentario=row['comentario'],
                        pago_id=row['id']
                    )
                    pagos.append(pago)
        
        return pagos

    def _get_cliente_id(self, codigo_cliente):
        """Obtiene el ID interno de BD de un cliente por su código."""
        cliente, cliente_id = self.cliente_repository.get_by_code_with_id(codigo_cliente)
        return cliente_id

    def add(self, pago):
        """Agrega un nuevo pago a la BD y asigna ID autonumérico."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Obtener cliente_id
                cliente_id = self._get_cliente_id(pago.cliente.codigo)
                if not cliente_id:
                    return pago
                
                # Insertar pago
                cursor.execute('''
                    INSERT INTO PAGOS (cliente_id, monto, fecha, comentario) 
                    VALUES (?, ?, ?, ?)
                ''', (
                    cliente_id,
                    pago.monto,
                    pago.fecha.isoformat(),
                    pago.comentario
                ))
                
                conn.commit()
                
                # Obtener el ID asignado
                pago.id = cursor.lastrowid
            
            return pago
        except Exception as e:
            print(f"Error al agregar pago: {e}")
            return pago

    def delete(self, pago_id):
        """Elimina un pago por su ID."""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM PAGOS WHERE id = ?', (pago_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
