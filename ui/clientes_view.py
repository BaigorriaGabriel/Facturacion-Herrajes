import tkinter as tk
from tkinter import ttk, messagebox
from models import Cliente

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
        col_widths = {"Codigo": 80, "Nombre": 150, "Adicional": 200, "Descuento": 100, "Saldo": 100}
        
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
        
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols: self.tree.heading(col, text=col.replace("Adicional", "Dato Adicional"))
        self.tree.heading("Saldo", text="Saldo ($)")
        # Configurar ancho de columnas
        self.tree.column("Codigo", width=80, anchor="center")
        self.tree.column("Nombre", width=150, anchor="w")
        self.tree.column("Adicional", width=200, anchor="w")
        self.tree.column("Descuento", width=100, anchor="center")
        self.tree.column("Saldo", width=100, anchor="e")
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
        clientes = self.controller.cliente_service.get_all_clients()
        
        search_terms = {col: var.get().lower() for col, var in self.search_vars.items()}
        
        clientes_filtrados = [
            c for c in clientes if
            all(search_terms[col] in str(getattr(c, col.lower() if col != "Adicional" else "adicional")).lower() for col in self.search_vars)
        ]

        for c in clientes_filtrados:
            self.tree.insert("", "end", values=(c.codigo, c.nombre, c.adicional, c.descuento, f"{c.saldo:.2f}"))
        self._on_tree_select()

    def open_form_cliente(self, cliente=None): 
        # Pass the controller to the form
        FormCliente(self, self.controller, cliente)

    def editar_cliente(self):
        if not self.tree.selection():
            return
        selected_item = self.tree.selection()[0]
        codigo_cliente = self.tree.item(selected_item, "values")[0]
        
        # Find the client object using the service
        cliente = next((c for c in self.controller.cliente_service.get_all_clients() if c.codigo == codigo_cliente), None)
        
        if cliente: 
            self.open_form_cliente(cliente)

    def eliminar_cliente(self):
        if not self.tree.selection():
            return
        selected_item = self.tree.selection()[0]
        codigo_cliente = self.tree.item(selected_item, "values")[0]

        if messagebox.askyesno("Confirmar", f"¿Eliminar cliente {codigo_cliente}?"):
            self.controller.cliente_service.delete_client(codigo_cliente)
            self.actualizar_lista()

class FormCliente(tk.Toplevel):
    def __init__(self, parent, controller, cliente=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("Formulario de Cliente")
        self.geometry("400x350")
        
        self.parent = parent
        self.controller = controller # Store the controller
        self.cliente_a_editar = cliente
        
        self._build_widgets()
        if cliente: 
            self.cargar_datos_cliente()

    def _build_widgets(self):
        form = ttk.Frame(self, padding="20")
        form.pack(expand=True, fill="both")
        form.columnconfigure(1, weight=1)
        
        self.codigo_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.adicional_var = tk.StringVar()
        self.descuento_var = tk.DoubleVar()
        self.saldo_var = tk.DoubleVar()
        
        self.codigo_entry = ttk.Entry(form, textvariable=self.codigo_var)
        self.saldo_entry = ttk.Entry(form, textvariable=self.saldo_var)

        fields = {
            "Código:": self.codigo_entry,
            "Nombre:": ttk.Entry(form, textvariable=self.nombre_var),
            "Dato Adicional:": ttk.Entry(form, textvariable=self.adicional_var),
            "Descuento (%):": ttk.Entry(form, textvariable=self.descuento_var),
            "Saldo ($):": self.saldo_entry
        }
        
        for i, (text, widget) in enumerate(fields.items()):
            ttk.Label(form, text=text).grid(row=i, column=0, sticky="w", pady=5, padx=5)
            widget.grid(row=i, column=1, sticky="ew", pady=5, padx=5)

        ttk.Button(form, text="Guardar", command=self.guardar_cliente).grid(row=len(fields), column=0, columnspan=2, pady=20)

    def cargar_datos_cliente(self):
        c = self.cliente_a_editar
        self.codigo_var.set(c.codigo)
        self.codigo_entry.config(state="disabled") # Don't allow editing the primary key
        self.nombre_var.set(c.nombre)
        self.adicional_var.set(c.adicional)
        self.descuento_var.set(c.descuento)
        self.saldo_var.set(c.saldo)

    def guardar_cliente(self):
        try:
            # Read all variables from the form first
            codigo = self.codigo_var.get().strip()
            nombre = self.nombre_var.get().strip()
            adicional = self.adicional_var.get().strip()
            descuento = self.descuento_var.get()
            saldo = self.saldo_var.get()
            
            if not codigo or not nombre:
                raise ValueError("Código y Nombre son obligatorios.")

        except (tk.TclError, ValueError) as e:
            messagebox.showerror("Error de validación", str(e), parent=self)
            return

        try:
            if self.cliente_a_editar:
                self.controller.cliente_service.update_client(codigo, nombre, adicional, descuento, saldo)
            else:
                self.controller.cliente_service.create_client(codigo, nombre, adicional, descuento, saldo)
            
            self.parent.actualizar_lista()
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
