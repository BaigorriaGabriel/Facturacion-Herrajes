import tkinter as tk
from tkinter import ttk, messagebox
from models import CLIENTES_MODEL, Cliente

class ClientesView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        top_frame = ttk.Frame(self); top_frame.pack(pady=10, padx=10, fill="x")
        ttk.Button(top_frame, text="< Volver al Menú", command=lambda: self.controller.show_frame("MainMenu")).pack(side="left")
        ttk.Label(top_frame, text="Gestión de Clientes", style="Heading.TLabel").pack(side="left", expand=True)

        btn_frame = ttk.Frame(self); btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Agregar Cliente", command=self.open_form_cliente).pack(side="left", padx=5)
        self.btn_editar = ttk.Button(btn_frame, text="Editar Cliente", command=self.editar_cliente, state="disabled")
        self.btn_editar.pack(side="left", padx=5)
        self.btn_eliminar = ttk.Button(btn_frame, text="Eliminar Cliente", command=self.eliminar_cliente, state="disabled", style="Danger.TButton")
        self.btn_eliminar.pack(side="left", padx=5)

        
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        self.search_vars = {}
        cols = ("Codigo", "Nombre", "Adicional", "Descuento", "Saldo")
        
        for col in cols:
            self.search_vars[col] = tk.StringVar()
            search_entry = ttk.Entry(search_frame, textvariable=self.search_vars[col], width=15)
            search_entry.pack(side="left", fill="x", expand=True)
            search_entry.bind("<KeyRelease>", lambda e: self.actualizar_lista())

        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols: self.tree.heading(col, text=col.replace("Adicional", "Dato Adicional"))
        self.tree.heading("Saldo", text="Saldo ($)")
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
        
        clientes = CLIENTES_MODEL.obtener_todos()
        
        search_terms = {col: var.get().lower() for col, var in self.search_vars.items()}
        
        clientes_filtrados = [
            c for c in clientes if
            all(search_terms[col] in str(getattr(c, col.lower() if col != "Adicional" else "adicional")).lower() for col in self.search_vars)
        ]

        for c in clientes_filtrados:
            self.tree.insert("", "end", values=(c.codigo, c.nombre, c.adicional, c.descuento, f"{c.saldo:.2f}"))
        self._on_tree_select()
    def open_form_cliente(self, cliente=None): FormCliente(self, cliente)
    def editar_cliente(self):
        if i := self.tree.selection():
            c = next((c for c in CLIENTES_MODEL.obtener_todos() if c.codigo == self.tree.item(i[0], "values")[0]), None)
            if c: self.open_form_cliente(c)
    def eliminar_cliente(self):
        if i := self.tree.selection():
            if messagebox.askyesno("Confirmar", "¿Eliminar cliente seleccionado?", parent=self):
                CLIENTES_MODEL.eliminar(self.tree.item(i[0], "values")[0]); self.actualizar_lista()

class FormCliente(tk.Toplevel):
    def __init__(self, parent, cliente=None):
        super().__init__(parent)
        self.transient(parent); self.grab_set()
        self.title("Formulario de Cliente"); self.geometry("400x350")
        self.parent = parent; self.cliente_a_editar = cliente
        
        self._build_widgets()
        if cliente: self.cargar_datos_cliente()

    def _build_widgets(self):
        form = ttk.Frame(self, padding="20"); form.pack(expand=True, fill="both")
        form.columnconfigure(1, weight=1)
        
        # Campos
        self.codigo_var = tk.StringVar(); self.nombre_var = tk.StringVar()
        self.adicional_var = tk.StringVar(); self.descuento_var = tk.DoubleVar()
        self.saldo_var = tk.DoubleVar()
        
        self.codigo_entry = ttk.Entry(form, textvariable=self.codigo_var)

        fields = {"Código:": self.codigo_entry, "Nombre:": ttk.Entry(form, textvariable=self.nombre_var),
                  "Dato Adicional:": ttk.Entry(form, textvariable=self.adicional_var),
                  "Descuento (%):": ttk.Entry(form, textvariable=self.descuento_var),
                  "Saldo ($):": ttk.Entry(form, textvariable=self.saldo_var)}

        for i, (text, widget) in enumerate(fields.items()):
            ttk.Label(form, text=text).grid(row=i, column=0, sticky="w", pady=5, padx=5)
            widget.grid(row=i, column=1, sticky="ew", pady=5, padx=5)

        ttk.Button(form, text="Guardar", command=self.guardar_cliente).grid(row=len(fields), column=0, columnspan=2, pady=20)

    def cargar_datos_cliente(self):
        c = self.cliente_a_editar
        self.codigo_var.set(c.codigo); self.codigo_entry.config(state="disabled")
        self.nombre_var.set(c.nombre); self.adicional_var.set(c.adicional)
        self.descuento_var.set(c.descuento); self.saldo_var.set(c.saldo)

    def guardar_cliente(self):
        try:
            codigo, nombre, adicional, descuento, saldo = (self.codigo_var.get().strip(), self.nombre_var.get().strip(),
                                                           self.adicional_var.get().strip(), self.descuento_var.get(), self.saldo_var.get())
            if not codigo or not nombre: raise ValueError("Código y Nombre son obligatorios.")
        except (tk.TclError, ValueError) as e:
            messagebox.showerror("Error de validación", str(e), parent=self)
            return

        if self.cliente_a_editar:
            CLIENTES_MODEL.actualizar(codigo, nombre, adicional, descuento, saldo)
        elif not CLIENTES_MODEL.agregar(Cliente(codigo, nombre, adicional, descuento, saldo)):
            messagebox.showerror("Error", "El código de cliente ya existe.", parent=self)
            return
        
        self.parent.actualizar_lista(); self.destroy()
