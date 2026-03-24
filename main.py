import tkinter as tk
from tkinter import ttk, font
from views.main_menu import MainMenu
from views.clientes_view import ClientesView
from views.productos_view import ProductosView
from views.facturas_view import FacturasView
from views.factura_form_view import FacturaFormView
import json
import os

def setup_temporary_data():
    """Crea archivos de datos temporales si no existen."""
    if not os.path.exists("data"):
        os.makedirs("data")

    clientes_path = "data/clientes.json"
    if not os.path.exists(clientes_path):
        clientes = [
            {"codigo": "C001", "nombre": "Consumidor Final", "adicional": "", "descuento": 0, "saldo": 0.0},
            {"codigo": "C002", "nombre": "Juan Perez", "adicional": "RUC: 12345678-9", "descuento": 5, "saldo": 0.0},
            {"codigo": "C003", "nombre": "Constructora ABC", "adicional": "Tel: 021-555-444", "descuento": 10, "saldo": 0.0},
            {"codigo": "C004", "nombre": "Maria Gonzalez", "adicional": "Dir: Av. Siempre Viva 123", "descuento": 0, "saldo": 0.0}
        ]
        with open(clientes_path, "w") as f:
            json.dump(clientes, f, indent=4)

    productos_path = "data/productos.json"
    if not os.path.exists(productos_path):
        productos = [
            {"codigo": "P001", "descripcion": "Martillo de Carpintero", "precio": 15.50},
            {"codigo": "P002", "descripcion": "Destornillador Phillips #2", "precio": 5.00},
            {"codigo": "P003", "descripcion": "Caja de 100 Clavos de 2 pulgadas", "precio": 3.25},
            {"codigo": "P004", "descripcion": "Cinta Metrica 5m", "precio": 8.00},
            {"codigo": "P005", "descripcion": "Pinza de Electricista", "precio": 12.75},
            {"codigo": "P006", "descripcion": "Bolsa de Cemento 25kg", "precio": 7.50},
            {"codigo": "P007", "descripcion": "Lata de Pintura Blanca 1L", "precio": 10.00},
            {"codigo": "P008", "descripcion": "Tubo PVC 1/2 pulgada x 3m", "precio": 2.50}
        ]
        with open(productos_path, "w") as f:
            json.dump(productos, f, indent=4)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Facturación")
        self.geometry("1024x768")

        # Estilo
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

        # Contenedor principal
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainMenu, ClientesView, ProductosView, FacturasView, FacturaFormView):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")

    def show_frame(self, page_name, context=None):
        frame = self.frames[page_name]
        if hasattr(frame, "on_show"):
            frame.on_show(context)
        frame.tkraise()

if __name__ == "__main__":
    setup_temporary_data()
    app = App()
    app.mainloop()
