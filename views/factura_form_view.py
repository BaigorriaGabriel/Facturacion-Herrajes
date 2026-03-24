import tkinter as tk
from tkinter import ttk, messagebox
from models import CLIENTES_MODEL, PRODUCTOS_MODEL, FACTURAS_MODEL, Factura, FacturaItem

class FacturaFormView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.factura_actual = None
        self.editing = False
        self._build_widgets()

    def on_show(self, context=None):
        self.limpiar_formulario()
        self._load_data()
        if isinstance(context, Factura):
            self.editing = True
            self.factura_actual = context
            self.cargar_factura()
        else:
            self.editing = False
            self.factura_actual = Factura(cliente=None)
        self._on_tree_select()

    def _build_widgets(self):
        # Frame principal con dos columnas
        main_frame = ttk.Frame(self, padding="10"); main_frame.pack(fill="both", expand=True)
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # --- Columna Izquierda (Datos y Totales) ---
        left_frame = ttk.Frame(main_frame); left_frame.grid(row=0, column=0, rowspan=3, sticky="nsw", padx=(0, 10))

        ttk.Button(left_frame, text="< Volver", command=self.cancelar).pack(anchor="w", pady=(0,10))
        
        # Datos Cliente
        cliente_frame = ttk.LabelFrame(left_frame, text="Buscar Cliente", padding="10"); cliente_frame.pack(fill="x")
        self.cliente_search_var = tk.StringVar()
        self.cliente_search = ttk.Entry(cliente_frame, textvariable=self.cliente_search_var)
        self.cliente_search.pack(fill="x")
        self.cliente_listbox = tk.Listbox(cliente_frame)
        self.cliente_listbox.pack(fill="x", expand=True)
        self.cliente_listbox.pack_forget() # Ocultar inicialmente
        self.lbl_descuento = ttk.Label(cliente_frame, text="Descuento: -"); self.lbl_descuento.pack(anchor="w")
        self.lbl_saldo = ttk.Label(cliente_frame, text="Saldo Actual: -"); self.lbl_saldo.pack(anchor="w")
        self.cliente_search.bind("<KeyRelease>", self._search_cliente)
        self.cliente_search.bind("<FocusOut>", self._hide_cliente_listbox)
        self.cliente_listbox.bind("<<ListboxSelect>>", self._on_cliente_selected_from_list)

        # Repartidor
        repartidor_frame = ttk.LabelFrame(left_frame, text="Repartidor", padding="10"); repartidor_frame.pack(fill="x", pady=10)
        self.repartidor_var = tk.StringVar()
        ttk.Entry(repartidor_frame, textvariable=self.repartidor_var).pack(fill="x")

        # Agregar Productos
        item_frame = ttk.LabelFrame(left_frame, text="Buscar Producto", padding="10"); item_frame.pack(fill="x", pady=20)
        self.producto_search_var = tk.StringVar()
        self.producto_search = ttk.Entry(item_frame, textvariable=self.producto_search_var)
        self.producto_search.pack(fill="x")
        self.producto_listbox = tk.Listbox(item_frame)
        self.producto_listbox.pack(fill="x", expand=True)
        self.producto_listbox.pack_forget() # Ocultar inicialmente
        self.producto_search.bind("<KeyRelease>", self._search_producto)
        self.producto_search.bind("<FocusOut>", self._hide_producto_listbox)
        self.producto_listbox.bind("<<ListboxSelect>>", self._on_producto_selected_from_list)
        self.lbl_precio_unitario = ttk.Label(item_frame, text="Precio: -"); self.lbl_precio_unitario.pack(anchor="w", pady=5)
        
        qty_frame = ttk.Frame(item_frame); qty_frame.pack(fill="x", pady=5)
        ttk.Label(qty_frame, text="Cantidad:").pack(side="left")
        self.cantidad_var = tk.IntVar(value=1)
        ttk.Entry(qty_frame, textvariable=self.cantidad_var, width=5).pack(side="left", padx=5)
        
        ttk.Button(item_frame, text="Agregar a Factura", command=self.agregar_item).pack(fill="x", pady=5)

        # Totales
        total_frame = ttk.LabelFrame(left_frame, text="Totales", padding="10"); total_frame.pack(fill="x")
        self.lbl_subtotal = ttk.Label(total_frame, text="Subtotal: $0.00", font=("", 12)); self.lbl_subtotal.pack(anchor="w")
        self.lbl_total_descuento = ttk.Label(total_frame, text="Descuento: $0.00", font=("", 12)); self.lbl_total_descuento.pack(anchor="w")
        self.lbl_total = ttk.Label(total_frame, text="TOTAL: $0.00", font=("", 14, "bold")); self.lbl_total.pack(anchor="w", pady=5)

        # --- Columna Derecha (Items y Acciones) ---
        right_frame = ttk.Frame(main_frame); right_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")
        right_frame.rowconfigure(1, weight=1)

        ttk.Label(right_frame, text="Detalle de Factura", style="Heading.TLabel").pack()
        
        cols = ("Producto", "Cantidad", "Precio Unit.", "Subtotal")
        self.items_tree = ttk.Treeview(right_frame, columns=cols, show="headings"); self.items_tree.pack(fill="both", expand=True, pady=10)
        self.items_tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        for col in cols: self.items_tree.heading(col, text=col)

        actions_frame = ttk.Frame(right_frame); actions_frame.pack(fill="x", pady=10)
        self.btn_quitar_item = ttk.Button(actions_frame, text="Quitar Producto Seleccionado", command=self.quitar_item, style="Danger.TButton", state="disabled")
        self.btn_quitar_item.pack(side="left", padx=5)
        ttk.Button(actions_frame, text="Guardar Factura", command=self.guardar_factura, style="Accent.TButton").pack(side="right", padx=5)

    def _on_tree_select(self, event=None):
        es_seleccionado = bool(self.items_tree.selection())
        self.btn_quitar_item.config(state="normal" if es_seleccionado else "disabled")

    def _load_data(self):
        self.clientes = CLIENTES_MODEL.obtener_todos()
        self.productos = PRODUCTOS_MODEL.obtener_todos()
    
    def _search_cliente(self, event):
        search_term = self.cliente_search_var.get().lower()
        if not search_term:
            self.cliente_listbox.pack_forget()
            return

        self.cliente_listbox.delete(0, tk.END)
        matches = [c for c in self.clientes if search_term in c.nombre.lower() or search_term in c.codigo.lower()]
        for c in matches:
            self.cliente_listbox.insert(tk.END, f"{c.codigo} - {c.nombre}")
        
        if matches:
            self.cliente_listbox.pack(fill="x", expand=True)
        else:
            self.cliente_listbox.pack_forget()

    def _on_cliente_selected_from_list(self, event):
        if not self.cliente_listbox.curselection():
            return
        
        idx = self.cliente_listbox.curselection()[0]
        selected_str = self.cliente_listbox.get(idx)
        codigo = selected_str.split(" - ")[0]
        
        cliente_seleccionado = next((c for c in self.clientes if c.codigo == codigo), None)

        if cliente_seleccionado:
            self.factura_actual.cliente = cliente_seleccionado
            self.cliente_search_var.set(f"{cliente_seleccionado.codigo} - {cliente_seleccionado.nombre}")
            self.lbl_descuento.config(text=f"Descuento: {cliente_seleccionado.descuento}%")
            self.lbl_saldo.config(text=f"Saldo Actual: ${cliente_seleccionado.saldo:.2f}")
            self.actualizar_totales()
            self.cliente_listbox.pack_forget()

    def _hide_cliente_listbox(self, event):
        # Pequeño delay para permitir que el click en la listbox se registre
        self.after(200, lambda: self.cliente_listbox.pack_forget())

    def _search_producto(self, event):
        search_term = self.producto_search_var.get().lower()
        if not search_term:
            self.producto_listbox.pack_forget()
            return

        self.producto_listbox.delete(0, tk.END)
        matches = [p for p in self.productos if search_term in p.descripcion.lower() or search_term in p.codigo.lower()]
        for p in matches:
            self.producto_listbox.insert(tk.END, f"{p.codigo} - {p.descripcion}")

        if matches:
            self.producto_listbox.pack(fill="x", expand=True)
        else:
            self.producto_listbox.pack_forget()

    def _on_producto_selected_from_list(self, event):
        if not self.producto_listbox.curselection():
            return

        idx = self.producto_listbox.curselection()[0]
        selected_str = self.producto_listbox.get(idx)
        codigo = selected_str.split(" - ")[0]
        
        producto_seleccionado = next((p for p in self.productos if p.codigo == codigo), None)
        
        if producto_seleccionado:
            self.producto_search_var.set(f"{producto_seleccionado.codigo} - {producto_seleccionado.descripcion}")
            self.lbl_precio_unitario.config(text=f"Precio: ${producto_seleccionado.precio:.2f}")
            self.producto_listbox.pack_forget()
            self.selected_product = producto_seleccionado # Guardar producto para agregar_item

    def _hide_producto_listbox(self, event):
        self.after(200, lambda: self.producto_listbox.pack_forget())
    
    def agregar_item(self):
        if not self.factura_actual or not self.factura_actual.cliente:
            messagebox.showwarning("Cliente no seleccionado", "Por favor, seleccione un cliente primero.", parent=self)
            return
        
        try:
            # Usar el producto guardado desde la selección de la lista
            if not hasattr(self, 'selected_product') or not self.selected_product:
                 messagebox.showwarning("Producto no válido", "Por favor, seleccione un producto de la lista.", parent=self)
                 return

            cantidad = self.cantidad_var.get()
            if cantidad <= 0:
                messagebox.showwarning("Datos inválidos", "La cantidad debe ser mayor que cero.", parent=self)
                return
            
            item = FacturaItem(self.selected_product, cantidad)
            self.factura_actual.agregar_item(item)
            self.actualizar_lista_items()
            self.actualizar_totales()
            # Limpiar para la próxima búsqueda
            self.selected_product = None
            self.producto_search_var.set("")
            self.lbl_precio_unitario.config(text="Precio: -")

        except tk.TclError:
            messagebox.showwarning("Cantidad inválida", "La cantidad debe ser un número entero.", parent=self)
    
    def quitar_item(self):
        selected_items = self.items_tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin selección", "Seleccione un producto de la lista de ítems para quitar.", parent=self)
            return

        idx = self.items_tree.index(selected_items[0])
        self.factura_actual.eliminar_item(idx)
        self.actualizar_lista_items()
        self.actualizar_totales()

    def actualizar_lista_items(self):
        self.items_tree.delete(*self.items_tree.get_children())
        for item in self.factura_actual.items:
            self.items_tree.insert("", "end", values=(item.producto.descripcion, item.cantidad, f"{item.precio_unitario:.2f}", f"{item.subtotal:.2f}"))
        self._on_tree_select()

    def actualizar_totales(self):
        if not self.factura_actual.cliente: return
        self.factura_actual.calcular_totales()
        self.lbl_subtotal.config(text=f"Subtotal: ${self.factura_actual.subtotal_general:.2f}")
        descuento_valor = self.factura_actual.subtotal_general * (self.factura_actual.cliente.descuento / 100)
        self.lbl_total_descuento.config(text=f"Descuento: ${descuento_valor:.2f}")
        self.lbl_total.config(text=f"TOTAL: ${self.factura_actual.total:.2f}")

    def limpiar_formulario(self):
        self.factura_actual = None
        self.cliente_search_var.set("")
        self.producto_search_var.set("")
        self.repartidor_var.set("")
        self.cliente_listbox.pack_forget()
        self.producto_listbox.pack_forget()
        self.lbl_descuento.config(text="Descuento: -")
        self.lbl_saldo.config(text="Saldo Actual: -")
        self.lbl_precio_unitario.config(text="Precio: -")
        self.cantidad_var.set(1)
        self.items_tree.delete(*self.items_tree.get_children())
        self.lbl_subtotal.config(text="Subtotal: $0.00")
        self.lbl_total_descuento.config(text="Descuento: $0.00")
        self.lbl_total.config(text="TOTAL: $0.00")
        self.cliente_search.config(state="normal")

    def cargar_factura(self):
        # Cargar cliente
        if self.factura_actual.cliente:
            cliente_str = f"{self.factura_actual.cliente.codigo} - {self.factura_actual.cliente.nombre}"
            self.cliente_search_var.set(cliente_str)
            self.lbl_descuento.config(text=f"Descuento: {self.factura_actual.cliente.descuento}%")
            self.lbl_saldo.config(text=f"Saldo Actual: ${self.factura_actual.cliente.saldo:.2f}")
            self.cliente_search.config(state="disabled")

        # Cargar repartidor
        self.repartidor_var.set(self.factura_actual.repartidor)

        # Cargar items
        self.actualizar_lista_items()
        self.actualizar_totales()
    
    def guardar_factura(self):
        if not self.factura_actual.cliente or not self.factura_actual.items:
            messagebox.showerror("Error", "La factura debe tener un cliente y al menos un ítem.", parent=self)
            return
        
        self.factura_actual.repartidor = self.repartidor_var.get()
        
        # Si la factura ya existe, se actualiza. Si no, se agrega.
        if FACTURAS_MODEL.obtener_por_numero(self.factura_actual.numero):
             FACTURAS_MODEL.actualizar(self.factura_actual.numero, self.factura_actual)
        else:
            FACTURAS_MODEL.agregar(self.factura_actual)
        
        messagebox.showinfo("Éxito", "Factura guardada correctamente.", parent=self)
        self.controller.show_frame("FacturasView")


    def cancelar(self):
        if messagebox.askyesno("Confirmar", "¿Desea cancelar? Se perderán los cambios no guardados.", parent=self):
            self.controller.show_frame("FacturasView")
