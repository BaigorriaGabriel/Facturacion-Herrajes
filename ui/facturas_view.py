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

        for col in cols:
            self.search_vars[col] = tk.StringVar()
            search_entry = ttk.Entry(search_frame, textvariable=self.search_vars[col], width=15)
            search_entry.pack(side="left", fill="x", expand=True)
            search_entry.bind("<KeyRelease>", lambda e: self.actualizar_lista())

        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols: self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
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
