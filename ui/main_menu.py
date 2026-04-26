import tkinter as tk
from tkinter import ttk

class MainMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(expand=True)
        
        ttk.Label(main_frame, text="Menú Principal", style="Heading.TLabel").pack(pady=20)
        
        ttk.Button(main_frame, text="Gestionar Facturas", command=lambda: controller.show_frame("FacturasView")).pack(pady=10, fill="x")
        ttk.Button(main_frame, text="Gestionar Clientes", command=lambda: controller.show_frame("ClientesView")).pack(pady=10, fill="x")
        ttk.Button(main_frame, text="Gestionar Productos", command=lambda: controller.show_frame("ProductosView")).pack(pady=10, fill="x")
        ttk.Button(main_frame, text="Aumentos de Precios", command=lambda: controller.show_frame("AumentosPreciosView")).pack(pady=10, fill="x")
        ttk.Button(main_frame, text="Gestionar Pagos", command=lambda: controller.show_frame("PagosView")).pack(pady=10, fill="x")
