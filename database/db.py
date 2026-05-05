# database/db.py
import sqlite3
import os
from contextlib import contextmanager
from threading import Lock

class Database:
    """Clase centralizada para gestionar conexiones SQLite y esquema de BD."""
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls, db_path="database.db"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path="database.db"):
        if self._initialized:
            return
        
        self.db_path = db_path
        self._connection = None
        self._initialize_db()
        self._initialized = True
    
    def _initialize_db(self):
        """Inicializa la BD: crea archivo si no existe y crea tablas."""
        # Crear directorio si no existe
        db_dir = os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else "."
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Crear conexión y tablas
        with self.get_connection() as conn:
            self._create_tables(conn)
    
    def get_connection(self):
        """Retorna una conexión a la BD (context manager)."""
        return self._ConnectionContext(self.db_path)
    
    def _create_tables(self, conn):
        """Crea todas las tablas del esquema."""
        cursor = conn.cursor()
        
        # Tabla CLIENTES
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CLIENTES (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                dato_adicional TEXT,
                descuento_1 INTEGER DEFAULT 0,
                descuento_2 INTEGER DEFAULT 0,
                saldo REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla PRODUCTOS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS PRODUCTOS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                descripcion TEXT NOT NULL,
                precio REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla FACTURAS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS FACTURAS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE NOT NULL,
                cliente_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                repartidor TEXT,
                dia_reparto TEXT,
                subtotal_general REAL DEFAULT 0.0,
                total REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES CLIENTES(id)
            )
        ''')
        
        # Tabla ITEMS_FACTURA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ITEMS_FACTURA (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                factura_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (factura_id) REFERENCES FACTURAS(id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES PRODUCTOS(id)
            )
        ''')
        
        # Tabla PAGOS
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS PAGOS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                monto REAL NOT NULL,
                fecha TEXT NOT NULL,
                comentario TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES CLIENTES(id)
            )
        ''')
        
        conn.commit()
    
    class _ConnectionContext:
        """Context manager para manejar conexiones a SQLite."""
        
        def __init__(self, db_path):
            self.db_path = db_path
            self.conn = None
        
        def __enter__(self):
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
            return self.conn
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.conn:
                self.conn.close()
            return False
    
    def close(self):
        """Cierra la conexión (si existe)."""
        if self._connection:
            self._connection.close()
            self._connection = None


# Singleton instance
_db = None

def get_db(db_path="database.db"):
    """Obtiene la instancia singleton de la BD."""
    global _db
    if _db is None:
        _db = Database(db_path)
    return _db
