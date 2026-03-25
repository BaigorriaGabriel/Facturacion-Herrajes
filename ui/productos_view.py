import tkinter as tk
from tkinter import ttk, messagebox
from models import Producto

class ProductosView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        top_frame = ttk.Frame(self); top_frame.pack(pady=10, padx=10, fill="x")
        ttk.Button(top_frame, text="< Volver al Menú", command=lambda: self.controller.show_frame("MainMenu")).pack(side="left")
        ttk.Label(top_frame, text="Gestión de Productos", style="Heading.TLabel").pack(side="left", expand=True)

        btn_frame = ttk.Frame(self); btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Agregar Producto", command=self.open_form_producto).pack(side="left", padx=5)
        self.btn_editar = ttk.Button(btn_frame, text="Editar Producto", command=self.editar_producto, state="disabled")
        self.btn_editar.pack(side="left", padx=5)
        self.btn_eliminar = ttk.Button(btn_frame, text="Eliminar Producto", command=self.eliminar_producto, state="disabled", style="Danger.TButton")
        self.btn_eliminar.pack(side="left", padx=5)

        
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)

        self.search_vars = {}
        cols = ("Codigo", "Descripcion", "Precio")
        col_widths = {"Codigo": 80, "Descripcion": 250, "Precio": 120}
        
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
        for col in cols: self.tree.heading(col, text=col.replace("Descripcion", "Descripción"))
        self.tree.heading("Precio", text="Precio Unitario")
        # Configurar ancho de columnas
        self.tree.column("Codigo", width=80, anchor="center")
        self.tree.column("Descripcion", width=250, anchor="w")
        self.tree.column("Precio", width=120, anchor="e")
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
        
        productos = self.controller.producto_service.get_all_products()
        
        search_terms = {col: var.get().lower() for col, var in self.search_vars.items()}
        
        productos_filtrados = [
            p for p in productos if
            all(search_terms[col] in str(getattr(p, col.lower())).lower() for col in self.search_vars)
        ]

        for p in productos_filtrados: 
            self.tree.insert("", "end", values=(p.codigo, p.descripcion, f"{p.precio:.2f}"))
        self._on_tree_select()

    def open_form_producto(self, producto=None): 
        FormProducto(self, self.controller, producto)

    def editar_producto(self):
        if not self.tree.selection():
            return
        selected_item = self.tree.selection()[0]
        codigo_producto = self.tree.item(selected_item, "values")[0]
        
        producto = next((p for p in self.controller.producto_service.get_all_products() if p.codigo == codigo_producto), None)
        
        if producto: 
            self.open_form_producto(producto)

    def eliminar_producto(self):
        if not self.tree.selection():
            return
        selected_item = self.tree.selection()[0]
        codigo_producto = self.tree.item(selected_item, "values")[0]

        if messagebox.askyesno("Confirmar", f"¿Eliminar producto {codigo_producto}?"):
            self.controller.producto_service.delete_product(codigo_producto)
            self.actualizar_lista()

class FormProducto(tk.Toplevel):
    def __init__(self, parent, controller, producto=None):
        super().__init__(parent)
        self.transient(parent); self.grab_set()
        self.title("Formulario de Producto"); self.geometry("400x250")
        
        self.parent = parent
        self.controller = controller
        self.producto_a_editar = producto
        
        self._build_widgets()
        if producto: 
            self.cargar_datos_producto()

    def _build_widgets(self):
        form = ttk.Frame(self, padding="20"); form.pack(expand=True, fill="both")
        form.columnconfigure(1, weight=1)
        
        self.codigo_var = tk.StringVar()
        self.descripcion_var = tk.StringVar()
        self.precio_var = tk.DoubleVar()
        
        self.codigo_entry = ttk.Entry(form, textvariable=self.codigo_var)

        fields = {
            "Código:": self.codigo_entry, 
            "Descripción:": ttk.Entry(form, textvariable=self.descripcion_var),
            "Precio:": ttk.Entry(form, textvariable=self.precio_var)
        }
        for i, (text, widget) in enumerate(fields.items()):
            ttk.Label(form, text=text).grid(row=i, column=0, sticky="w", pady=10, padx=5)
            widget.grid(row=i, column=1, sticky="ew", pady=10, padx=5)
        
        ttk.Button(form, text="Guardar", command=self.guardar_producto).grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def cargar_datos_producto(self):
        p = self.producto_a_editar
        self.codigo_var.set(p.codigo)
        self.codigo_entry.config(state="disabled")
        self.descripcion_var.set(p.descripcion)
        self.precio_var.set(p.precio)

    def guardar_producto(self):
        try:
            codigo = self.codigo_var.get().strip()
            desc = self.descripcion_var.get().strip()
            precio = self.precio_var.get()
            if not codigo or not desc: 
                raise ValueError("Código y Descripción son obligatorios.")
        except (tk.TclError, ValueError) as e:
            messagebox.showerror("Error de validación", str(e), parent=self)
            return

        try:
            if self.producto_a_editar:
                self.controller.producto_service.update_product(codigo, desc, precio)
            else:
                self.controller.producto_service.create_product(codigo, desc, precio)
            
            self.parent.actualizar_lista()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
