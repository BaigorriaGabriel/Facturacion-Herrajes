import tkinter as tk
from tkinter import ttk, messagebox
from models import PRODUCTOS_MODEL, Producto

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

        for col in cols:
            self.search_vars[col] = tk.StringVar()
            search_entry = ttk.Entry(search_frame, textvariable=self.search_vars[col], width=15)
            search_entry.pack(side="left", fill="x", expand=True)
            search_entry.bind("<KeyRelease>", lambda e: self.actualizar_lista())

        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for col in cols: self.tree.heading(col, text=col.replace("Descripcion", "Descripción"))
        self.tree.heading("Precio", text="Precio Unitario")
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
        
        productos = PRODUCTOS_MODEL.obtener_todos()
        
        search_terms = {col: var.get().lower() for col, var in self.search_vars.items()}
        
        productos_filtrados = [
            p for p in productos if
            all(search_terms[col] in str(getattr(p, col.lower())).lower() for col in self.search_vars)
        ]

        for p in productos_filtrados: self.tree.insert("", "end", values=(p.codigo, p.descripcion, f"{p.precio:.2f}"))
        self._on_tree_select()
    def open_form_producto(self, producto=None): FormProducto(self, producto)
    def editar_producto(self):
        if i := self.tree.selection():
            p = next((p for p in PRODUCTOS_MODEL.obtener_todos() if p.codigo == self.tree.item(i[0], "values")[0]), None)
            if p: self.open_form_producto(p)
    def eliminar_producto(self):
        if i := self.tree.selection():
            if messagebox.askyesno("Confirmar", "¿Eliminar producto seleccionado?", parent=self):
                PRODUCTOS_MODEL.eliminar(self.tree.item(i[0], "values")[0]); self.actualizar_lista()

class FormProducto(tk.Toplevel):
    def __init__(self, parent, producto=None):
        super().__init__(parent)
        self.transient(parent); self.grab_set()
        self.title("Formulario de Producto"); self.geometry("400x250")
        self.parent = parent; self.producto_a_editar = producto
        
        self._build_widgets()
        if producto: self.cargar_datos_producto()

    def _build_widgets(self):
        form = ttk.Frame(self, padding="20"); form.pack(expand=True, fill="both")
        form.columnconfigure(1, weight=1)
        
        self.codigo_var = tk.StringVar(); self.descripcion_var = tk.StringVar(); self.precio_var = tk.DoubleVar()
        self.codigo_entry = ttk.Entry(form, textvariable=self.codigo_var)

        fields = {"Código:": self.codigo_entry, "Descripción:": ttk.Entry(form, textvariable=self.descripcion_var),
                  "Precio:": ttk.Entry(form, textvariable=self.precio_var)}
        for i, (text, widget) in enumerate(fields.items()):
            ttk.Label(form, text=text).grid(row=i, column=0, sticky="w", pady=10, padx=5)
            widget.grid(row=i, column=1, sticky="ew", pady=10, padx=5)
        
        ttk.Button(form, text="Guardar", command=self.guardar_producto).grid(row=len(fields), column=0, columnspan=2, pady=20)
    
    def cargar_datos_producto(self):
        p = self.producto_a_editar
        self.codigo_var.set(p.codigo); self.codigo_entry.config(state="disabled")
        self.descripcion_var.set(p.descripcion); self.precio_var.set(p.precio)

    def guardar_producto(self):
        try:
            codigo, desc, precio = self.codigo_var.get().strip(), self.descripcion_var.get().strip(), self.precio_var.get()
            if not codigo or not desc: raise ValueError("Código y Descripción son obligatorios.")
        except (tk.TclError, ValueError) as e:
            messagebox.showerror("Error de validación", str(e), parent=self)
            return

        if self.producto_a_editar:
            PRODUCTOS_MODEL.actualizar(codigo, desc, precio)
        elif not PRODUCTOS_MODEL.agregar(Producto(codigo, desc, precio)):
            messagebox.showerror("Error", "El código de producto ya existe.", parent=self)
            return
            
        self.parent.actualizar_lista(); self.destroy()
