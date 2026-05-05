# repositories/cliente_repository.py
from models import Cliente
from database import Database

class ClienteRepository:
    def __init__(self, db=None):
        """
        Inicializa el repositorio de clientes con SQLite.
        
        Args:
            db: Instancia de Database. Si es None, obtiene la instancia singleton.
        """
        self.db = db if db is not None else Database()

    def get_all(self):
        """Obtiene todos los clientes desde la BD."""
        clientes = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, codigo, nombre, dato_adicional, descuento_1, descuento_2, saldo FROM CLIENTES ORDER BY codigo')
            rows = cursor.fetchall()
            for row in rows:
                cliente = Cliente(
                    codigo=row['codigo'],
                    nombre=row['nombre'],
                    adicional=row['dato_adicional'],
                    descuento_1=bool(row['descuento_1']),
                    descuento_2=bool(row['descuento_2']),
                    saldo=row['saldo']
                )
                clientes.append(cliente)
        return clientes

    def get_by_code(self, codigo):
        """Obtiene un cliente por su código."""
        codigo_normalizado = codigo.upper()
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, codigo, nombre, dato_adicional, descuento_1, descuento_2, saldo FROM CLIENTES WHERE UPPER(codigo) = ?', 
                         (codigo_normalizado,))
            row = cursor.fetchone()
            if row:
                return Cliente(
                    codigo=row['codigo'],
                    nombre=row['nombre'],
                    adicional=row['dato_adicional'],
                    descuento_1=bool(row['descuento_1']),
                    descuento_2=bool(row['descuento_2']),
                    saldo=row['saldo']
                )
        return None

    def get_by_code_with_id(self, codigo):
        """Obtiene un cliente y su ID interno de BD por su código."""
        codigo_normalizado = codigo.upper()
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, codigo, nombre, dato_adicional, descuento_1, descuento_2, saldo FROM CLIENTES WHERE UPPER(codigo) = ?', 
                         (codigo_normalizado,))
            row = cursor.fetchone()
            if row:
                cliente = Cliente(
                    codigo=row['codigo'],
                    nombre=row['nombre'],
                    adicional=row['dato_adicional'],
                    descuento_1=bool(row['descuento_1']),
                    descuento_2=bool(row['descuento_2']),
                    saldo=row['saldo']
                )
                return cliente, row['id']
        return None, None

    def add(self, cliente):
        """Agrega un nuevo cliente a la BD."""
        if self.get_by_code(cliente.codigo):
            return False
        
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO CLIENTES (codigo, nombre, dato_adicional, descuento_1, descuento_2, saldo) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    cliente.codigo,
                    cliente.nombre,
                    cliente.adicional,
                    int(cliente.descuento_1),
                    int(cliente.descuento_2),
                    cliente.saldo
                ))
                conn.commit()
            return True
        except Exception:
            return False

    def update(self, codigo, nombre, adicional, descuento_1, descuento_2, saldo):
        """Actualiza un cliente existente."""
        codigo_normalizado = codigo.upper()
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE CLIENTES 
                    SET nombre = ?, dato_adicional = ?, descuento_1 = ?, descuento_2 = ?, saldo = ? 
                    WHERE UPPER(codigo) = ?
                ''', (nombre, adicional, int(descuento_1), int(descuento_2), saldo, codigo_normalizado))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False

    def delete(self, codigo):
        """Elimina un cliente por su código."""
        codigo_normalizado = codigo.upper()
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM CLIENTES WHERE UPPER(codigo) = ?', (codigo_normalizado,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False

    def update_saldo(self, codigo, nuevo_saldo):
        """Actualiza solo el saldo de un cliente."""
        codigo_normalizado = codigo.upper()
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE CLIENTES SET saldo = ? WHERE UPPER(codigo) = ?', 
                             (nuevo_saldo, codigo_normalizado))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False
