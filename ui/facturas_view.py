import tkinter as tk
from tkinter import ttk, messagebox
# No longer need to import the global model
# from models import FACTURAS_MODEL

class FacturasView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        top_frame = ttk.Frame(self); top_frame.pack(pady=10, padx=10, fill="x")
        ttk.Button(top_frame, text="< Volver al Menú", command=lambda: self.controller.show_frame("MainMenu")).pack(side="left")
        ttk.Label(top_frame, text="Historial de Facturas", style="Heading.TLabel").pack(side="left", expand=True)

        btn_frame = ttk.Frame(self); btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Nueva Factura", command=lambda: self.controller.show_frame("FacturaFormView")).pack(side="left", padx=5)
        self.btn_editar = ttk.Button(btn_frame, text="Ver/Editar Factura", command=self.editar_factura, state="disabled")
        self.btn_editar.pack(side="left", padx=5)
        self.btn_eliminar = ttk.Button(btn_frame, text="Eliminar Factura", command=self.eliminar_factura, state="disabled", style="Danger.TButton")
        self.btn_eliminar.pack(side="left", padx=5)

        
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)

        self.search_vars = {}
        cols = ("Numero", "Fecha", "Cliente", "Repartidor", "Dia de Reparto", "Total")
        col_widths = {"Numero": 80, "Fecha": 100, "Cliente": 150, "Repartidor": 120, "Dia de Reparto": 120, "Total": 100}
        
        # Configurar columnas con grid basado en anchos de tabla
        for idx, col in enumerate(cols):
            search_frame.grid_columnconfigure(idx, weight=col_widths[col])
        
        for idx, col in enumerate(cols):
            self.search_vars[col] = tk.StringVar()
            search_entry = ttk.Entry(search_frame, textvariable=self.search_vars[col])
            search_entry.grid(row=0, column=idx, sticky="ew", padx=2)
            search_entry.bind("<KeyRelease>", lambda e: self.actualizar_lista())
        
        # Espacio para scrollbar
        search_frame.grid_columnconfigure(len(cols), weight=0, minsize=17)

        # Layout con grid
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        cols_data = ("Numero", "Fecha", "Cliente", "Repartidor", "Dia de Reparto", "Total")
        self.tree = ttk.Treeview(table_frame, columns=cols_data, show="headings")
        for col in cols_data: self.tree.heading(col, text=col)
        # Configurar ancho de columnas
        self.tree.column("Numero", width=80, anchor="center")
        self.tree.column("Fecha", width=100, anchor="center")
        self.tree.column("Cliente", width=150, anchor="w")
        self.tree.column("Repartidor", width=120, anchor="center")
        self.tree.column("Dia de Reparto", width=120, anchor="center")
        self.tree.column("Total", width=100, anchor="e")
        # Agregar scrollbars como miembros de table_frame
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _on_tree_select(self, event=None):
        es_seleccionado = bool(self.tree.selection())
        estado = "normal" if es_seleccionado else "disabled"
        self.btn_editar.config(state=estado)
        self.btn_eliminar.config(state=estado)

    def on_show(self, context=None): 
        for var in self.search_vars.values():
            var.set("")
        self.actualizar_lista()

    def actualizar_lista(self):
        self.tree.delete(*self.tree.get_children())
        
        # Use the service to get data
        facturas = self.controller.factura_service.get_all_invoices()
        
        search_terms = {col: var.get().lower() for col, var in self.search_vars.items()}
        
        facturas_filtradas = []
        for f in facturas:
            cliente_nombre = f.cliente.nombre.lower() if f.cliente else ""
            
            # The 'all' function requires an iterable. This generator expression creates one.
            if all((
                search_terms["Numero"] in str(f.numero),
                search_terms["Fecha"] in f.fecha.strftime('%d-%m-%Y'),
                search_terms["Cliente"] in cliente_nombre,
                search_terms["Repartidor"] in f.repartidor.lower(),
                search_terms["Dia de Reparto"] in f.dia_reparto.lower(),
                search_terms["Total"] in f"{f.total:.2f}"
            )):
                facturas_filtradas.append(f)

        for f in facturas_filtradas:
            cliente_nombre = f.cliente.nombre if f.cliente else "N/A"
            self.tree.insert("", "end", values=(f.numero, f.fecha.strftime('%d-%m-%Y'), cliente_nombre, f.repartidor, f.dia_reparto, f"{f.total:.2f}"))
        
        self._on_tree_select()

    def editar_factura(self):
        if not self.tree.selection():
            return
        selected_item = self.tree.selection()[0]
        num_factura = self.tree.item(selected_item, "values")[0]
        
        # Use the service to get the invoice
        factura = self.controller.factura_service.get_invoice_by_number(int(num_factura))
        
        if factura: 
            self.controller.show_frame("FacturaFormView", context=factura)

    def eliminar_factura(self):
        if not self.tree.selection():
            return
        selected_item = self.tree.selection()[0]
        num_factura = self.tree.item(selected_item, "values")[0]

        if messagebox.askyesno("Confirmar", f"¿Eliminar factura N°{num_factura}? Esta acción modificará el saldo del cliente."):
            self.controller.factura_service.delete_invoice(int(num_factura))
            self.actualizar_lista()
