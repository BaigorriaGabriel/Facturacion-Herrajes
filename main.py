import tkinter as tk
from tkinter import ttk, font
import json
import os

# 1. Import new architecture components
from ui.main_menu import MainMenu
from ui.clientes_view import ClientesView
from ui.productos_view import ProductosView
from ui.facturas_view import FacturasView
from ui.factura_form_view import FacturaFormView

from repositories.cliente_repository import ClienteRepository
from repositories.producto_repository import ProductoRepository
from repositories.factura_repository import FacturaRepository

from services.cliente_service import ClienteService
from services.producto_service import ProductoService
from services.factura_service import FacturaService

def setup_temporary_data():
    """Crea archivos de datos temporales si no existen para demostración."""
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists("data/facturas.json"):
        with open("data/facturas.json", "w") as f:
            json.dump([], f)

    if not os.path.exists("data/clientes.json"):
        clientes = [
            {"codigo": "C001", "nombre": "Consumidor Final", "adicional": "", "descuento": 0, "saldo": 0.0},
            {"codigo": "C002", "nombre": "Juan Perez", "adicional": "RUC: 12345678-9", "descuento": 5, "saldo": 0.0},
        ]
        with open("data/clientes.json", "w") as f:
            json.dump(clientes, f, indent=4)

    if not os.path.exists("data/productos.json"):
        productos = [
            {"codigo": "P001", "descripcion": "Martillo", "precio": 15.50},
            {"codigo": "P002", "descripcion": "Destornillador", "precio": 5.00},
        ]
        with open("data/productos.json", "w") as f:
            json.dump(productos, f, indent=4)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Facturación")
        self.geometry("1400x900")
        self.minsize(1200, 700)

        self._setup_styles()
        
        # 2. Instantiate all layers
        self._initialize_services()

        # 3. Create main container and frames
        container = self._create_main_container()
        self.frames = {}
        
        # 4. Pass services to the UI frames
        # The controller (self) now holds the services
        views = (MainMenu, ClientesView, ProductosView, FacturasView, FacturaFormView)
        for F in views:
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")
        
    def _setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=11)
        self.option_add("*Font", default_font)
        self.style.configure("TButton", padding=8, font=("", 11))
        self.style.configure("TLabel", padding=4, font=("", 11))
        self.style.configure("TEntry", padding=4, font=("", 11))
        self.style.configure("Treeview.Heading", font=("", 12, "bold"))
        self.style.configure("Treeview", rowheight=28, font=("", 11))
        self.style.configure("Heading.TLabel", font=("", 16, "bold"))
        self.style.configure("Danger.TButton", foreground="white", background="#e74c3c")
        self.style.map("Danger.TButton", background=[("active", "#c0392b")])
        self.style.configure("Accent.TButton", foreground="white", background="#27ae60")
        self.style.map("Accent.TButton", background=[("active", "#229954")])
        
    def _initialize_services(self):
        # Repositories
        cliente_repo = ClienteRepository()
        producto_repo = ProductoRepository()
        factura_repo = FacturaRepository(cliente_repo, producto_repo)
        
        # Services - store them on the controller
        self.cliente_service = ClienteService(cliente_repo)
        self.producto_service = ProductoService(producto_repo)
        self.factura_service = FacturaService(factura_repo, self.cliente_service)

    def _create_main_container(self):
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        return container

    def show_frame(self, page_name, context=None):
        frame = self.frames[page_name]
        if hasattr(frame, "on_show"):
            frame.on_show(context)
        frame.tkraise()

if __name__ == "__main__":
    setup_temporary_data()
    app = App()
    app.mainloop()
