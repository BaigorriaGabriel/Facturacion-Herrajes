import tkinter as tk
from tkinter import ttk, messagebox
from models import FACTURAS_MODEL

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
        cols = ("Numero", "Fecha", "Cliente", "Repartidor", "Total")

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
        
        facturas = FACTURAS_MODEL.obtener_todas()
        
        search_terms = {col: var.get().lower() for col, var in self.search_vars.items()}
        
        facturas_filtradas = []
        for f in facturas:
            if all(
                (term in str(getattr(f, col.lower(), "")).lower() if col not in ["Cliente", "Fecha", "Total"] 
                 else term in f.cliente.nombre.lower() if col == "Cliente" 
                 else term in f.fecha.strftime('%d-%m-%Y') if col == "Fecha"
                 else term in str(f.total) if col == "Total"
                 else True) 
                for col, term in search_terms.items()
            ):
                facturas_filtradas.append(f)

        for f in facturas_filtradas:
            self.tree.insert("", "end", values=(f.numero, f.fecha.strftime('%d-%m-%Y'), f.cliente.nombre, f.repartidor, f"{f.total:.2f}"))
        self._on_tree_select()
    def editar_factura(self):
        if i := self.tree.selection():
            num = self.tree.item(i[0], "values")[0]
            factura = FACTURAS_MODEL.obtener_por_numero(int(num))
            if factura: self.controller.show_frame("FacturaFormView", context=factura)
    def eliminar_factura(self):
        if i := self.tree.selection():
            if messagebox.askyesno("Confirmar", "¿Eliminar factura seleccionada? Esta acción modificará el saldo del cliente.", parent=self):
                FACTURAS_MODEL.eliminar(int(self.tree.item(i[0], "values")[0])); self.actualizar_lista()
