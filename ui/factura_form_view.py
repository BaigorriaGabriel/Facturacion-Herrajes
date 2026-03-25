import tkinter as tk
from tkinter import ttk, messagebox
from models import Factura, FacturaItem

class FacturaFormView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.factura_actual = None
        self.editing = False
        self._build_widgets()

    def on_show(self, context=None):
        self.limpiar_formulario()
        # _load_data() is no longer needed as we fetch from services on demand
        if isinstance(context, Factura):
            self.editing = True
            self.factura_actual = context
            self.cargar_factura()
        else:
            self.editing = False
            # Create a new, empty Factura object for the form
            self.factura_actual = Factura(cliente=None) 
        self._on_tree_select()

    def _build_widgets(self):
        main_frame = ttk.Frame(self, padding="10"); main_frame.pack(fill="both", expand=True)
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(1, weight=1)

        left_frame = ttk.Frame(main_frame); left_frame.grid(row=0, column=0, rowspan=3, sticky="nsw", padx=(0, 10))

        ttk.Button(left_frame, text="< Volver", command=self.cancelar).pack(anchor="w", pady=(0,10))
        
        cliente_frame = ttk.LabelFrame(left_frame, text="Buscar Cliente", padding="10"); cliente_frame.pack(fill="x")
        self.cliente_search_var = tk.StringVar()
        self.cliente_search = ttk.Entry(cliente_frame, textvariable=self.cliente_search_var)
        self.cliente_search.pack(fill="x")
        self.cliente_listbox = tk.Listbox(cliente_frame)
        self.cliente_listbox.pack_forget()
        self.lbl_descuento = ttk.Label(cliente_frame, text="Descuento: -"); self.lbl_descuento.pack(anchor="w")
        self.lbl_saldo = ttk.Label(cliente_frame, text="Saldo Actual: -"); self.lbl_saldo.pack(anchor="w")
        self.cliente_search.bind("<KeyRelease>", self._search_cliente)
        self.cliente_search.bind("<FocusOut>", self._hide_cliente_listbox)
        self.cliente_listbox.bind("<<ListboxSelect>>", self._on_cliente_selected_from_list)

        repartidor_frame = ttk.LabelFrame(left_frame, text="Repartidor", padding="10"); repartidor_frame.pack(fill="x", pady=10)
        self.repartidor_var = tk.StringVar()
        ttk.Entry(repartidor_frame, textvariable=self.repartidor_var).pack(fill="x")

        dia_reparto_frame = ttk.LabelFrame(left_frame, text="Día de Reparto", padding="10")
        dia_reparto_frame.pack(fill="x", pady=10)
        self.dia_reparto_var = tk.StringVar()
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        self.dia_reparto_combobox = ttk.Combobox(dia_reparto_frame, textvariable=self.dia_reparto_var, values=dias_semana, state="readonly")
        self.dia_reparto_combobox.pack(fill="x")

        item_frame = ttk.LabelFrame(left_frame, text="Buscar Producto", padding="10"); item_frame.pack(fill="x", pady=20)
        self.producto_search_var = tk.StringVar()
        self.producto_search = ttk.Entry(item_frame, textvariable=self.producto_search_var)
        self.producto_search.pack(fill="x")
        self.producto_listbox = tk.Listbox(item_frame)
        self.producto_listbox.pack_forget()
        self.producto_search.bind("<KeyRelease>", self._search_producto)
        self.producto_search.bind("<FocusOut>", self._hide_producto_listbox)
        self.producto_listbox.bind("<<ListboxSelect>>", self._on_producto_selected_from_list)
        self.lbl_precio_unitario = ttk.Label(item_frame, text="Precio: -"); self.lbl_precio_unitario.pack(anchor="w", pady=5)
        
        qty_frame = ttk.Frame(item_frame); qty_frame.pack(fill="x", pady=5)
        ttk.Label(qty_frame, text="Cantidad:").pack(side="left")
        self.cantidad_var = tk.IntVar(value=1)
        ttk.Entry(qty_frame, textvariable=self.cantidad_var, width=5).pack(side="left", padx=5)
        
        ttk.Button(item_frame, text="Agregar a Factura", command=self.agregar_item).pack(fill="x", pady=5)

        total_frame = ttk.LabelFrame(left_frame, text="Totales", padding="10"); total_frame.pack(fill="x")
        self.lbl_subtotal = ttk.Label(total_frame, text="Subtotal: $0.00", font=("", 12)); self.lbl_subtotal.pack(anchor="w")
        self.lbl_total_descuento = ttk.Label(total_frame, text="Descuento: $0.00", font=("", 12)); self.lbl_total_descuento.pack(anchor="w")
        self.lbl_total = ttk.Label(total_frame, text="TOTAL: $0.00", font=("", 14, "bold")); self.lbl_total.pack(anchor="w", pady=5)

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

    def _search_cliente(self, event):
        search_term = self.cliente_search_var.get().lower()
        if not search_term:
            self.cliente_listbox.pack_forget()
            return
        
        # Fetch clients from service and filter
        all_clients = self.controller.cliente_service.get_all_clients()
        matches = [c for c in all_clients if search_term in c.nombre.lower() or search_term in c.codigo.lower()]
        
        self.cliente_listbox.delete(0, tk.END)
        for c in matches: self.cliente_listbox.insert(tk.END, f"{c.codigo} - {c.nombre}")
        
        if matches: self.cliente_listbox.pack(fill="x", expand=True)
        else: self.cliente_listbox.pack_forget()

    def _on_cliente_selected_from_list(self, event):
        if not self.cliente_listbox.curselection(): return
        
        selected_str = self.cliente_listbox.get(self.cliente_listbox.curselection()[0])
        codigo = selected_str.split(" - ")[0]
        
        all_clients = self.controller.cliente_service.get_all_clients()
        cliente_seleccionado = next((c for c in all_clients if c.codigo == codigo), None)

        if cliente_seleccionado:
            self.factura_actual.cliente = cliente_seleccionado
            self.cliente_search_var.set(f"{cliente_seleccionado.codigo} - {cliente_seleccionado.nombre}")
            self.lbl_descuento.config(text=f"Descuento: {cliente_seleccionado.descuento}%")
            self.lbl_saldo.config(text=f"Saldo Actual: ${cliente_seleccionado.saldo:.2f}")
            self.actualizar_totales()
            self.cliente_listbox.pack_forget()

    def _hide_cliente_listbox(self, event): self.after(200, lambda: self.cliente_listbox.pack_forget())

    def _search_producto(self, event):
        search_term = self.producto_search_var.get().lower()
        if not search_term:
            self.producto_listbox.pack_forget(); return

        all_products = self.controller.producto_service.get_all_products()
        matches = [p for p in all_products if search_term in p.descripcion.lower() or search_term in p.codigo.lower()]
        
        self.producto_listbox.delete(0, tk.END)
        for p in matches: self.producto_listbox.insert(tk.END, f"{p.codigo} - {p.descripcion}")

        if matches: self.producto_listbox.pack(fill="x", expand=True)
        else: self.producto_listbox.pack_forget()

    def _on_producto_selected_from_list(self, event):
        if not self.producto_listbox.curselection(): return

        selected_str = self.producto_listbox.get(self.producto_listbox.curselection()[0])
        codigo = selected_str.split(" - ")[0]
        
        all_products = self.controller.producto_service.get_all_products()
        self.selected_product = next((p for p in all_products if p.codigo == codigo), None)
        
        if self.selected_product:
            self.producto_search_var.set(f"{self.selected_product.codigo} - {self.selected_product.descripcion}")
            self.lbl_precio_unitario.config(text=f"Precio: ${self.selected_product.precio:.2f}")
            self.producto_listbox.pack_forget()

    def _hide_producto_listbox(self, event): self.after(200, lambda: self.producto_listbox.pack_forget())
    
    def agregar_item(self):
        if not self.factura_actual or not self.factura_actual.cliente:
            messagebox.showwarning("Cliente no seleccionado", "Por favor, seleccione un cliente primero.", parent=self); return
        
        if not hasattr(self, 'selected_product') or not self.selected_product:
             messagebox.showwarning("Producto no válido", "Por favor, seleccione un producto de la lista.", parent=self); return
        
        try:
            cantidad = self.cantidad_var.get()
            if cantidad <= 0:
                messagebox.showwarning("Datos inválidos", "La cantidad debe ser mayor que cero.", parent=self); return
            
            item = FacturaItem(self.selected_product, cantidad)
            self.factura_actual.agregar_item(item)
            self.actualizar_lista_items()
            self.actualizar_totales()
            self.selected_product = None; self.producto_search_var.set(""); self.lbl_precio_unitario.config(text="Precio: -")
        except tk.TclError:
            messagebox.showwarning("Cantidad inválida", "La cantidad debe ser un número entero.", parent=self)
    
    def quitar_item(self):
        if not self.items_tree.selection():
            messagebox.showwarning("Sin selección", "Seleccione un ítem para quitar.", parent=self); return

        idx = self.items_tree.index(self.items_tree.selection()[0])
        self.factura_actual.eliminar_item(idx)
        self.actualizar_lista_items(); self.actualizar_totales()

    def actualizar_lista_items(self):
        self.items_tree.delete(*self.items_tree.get_children())
        for item in self.factura_actual.items:
            self.items_tree.insert("", "end", values=(item.producto.descripcion, item.cantidad, f"{item.precio_unitario:.2f}", f"{item.subtotal:.2f}"))
        self._on_tree_select()

    def actualizar_totales(self):
        self.factura_actual.calcular_totales()
        self.lbl_subtotal.config(text=f"Subtotal: ${self.factura_actual.subtotal_general:.2f}")
        if self.factura_actual.cliente:
            descuento_valor = self.factura_actual.subtotal_general * (self.factura_actual.cliente.descuento / 100)
            self.lbl_total_descuento.config(text=f"Descuento: ${descuento_valor:.2f}")
        self.lbl_total.config(text=f"TOTAL: ${self.factura_actual.total:.2f}")

    def limpiar_formulario(self):
        self.factura_actual = None; self.editing = False
        self.cliente_search_var.set(""); self.producto_search_var.set(""); self.repartidor_var.set("")
        self.dia_reparto_var.set("")
        self.cliente_listbox.pack_forget(); self.producto_listbox.pack_forget()
        self.lbl_descuento.config(text="Descuento: -"); self.lbl_saldo.config(text="Saldo Actual: -")
        self.lbl_precio_unitario.config(text="Precio: -"); self.cantidad_var.set(1)
        self.items_tree.delete(*self.items_tree.get_children())
        self.lbl_subtotal.config(text="Subtotal: $0.00"); self.lbl_total_descuento.config(text="Descuento: $0.00")
        self.lbl_total.config(text="TOTAL: $0.00"); self.cliente_search.config(state="normal")

    def cargar_factura(self):
        if self.factura_actual.cliente:
            cliente = self.factura_actual.cliente
            self.cliente_search_var.set(f"{cliente.codigo} - {cliente.nombre}")
            self.lbl_descuento.config(text=f"Descuento: {cliente.descuento}%")
            self.lbl_saldo.config(text=f"Saldo Actual: ${cliente.saldo:.2f}")
            self.cliente_search.config(state="disabled")

        self.repartidor_var.set(self.factura_actual.repartidor)
        self.dia_reparto_var.set(self.factura_actual.dia_reparto)
        self.actualizar_lista_items()
        self.actualizar_totales()
    
    def guardar_factura(self):
        if not self.factura_actual.cliente or not self.factura_actual.items:
            messagebox.showerror("Error", "La factura debe tener un cliente y al menos un ítem.", parent=self); return
        
        # Populate the object with the latest data from the form
        self.factura_actual.repartidor = self.repartidor_var.get()
        self.factura_actual.dia_reparto = self.dia_reparto_var.get()
        
        try:
            if self.editing:
                self.controller.factura_service.update_invoice(self.factura_actual.numero, self.factura_actual)
            else:
                self.controller.factura_service.create_invoice(self.factura_actual)
            
            messagebox.showinfo("Éxito", "Factura guardada correctamente.", parent=self)
            self.controller.show_frame("FacturasView")

        except ValueError as e:
            messagebox.showerror("Error al guardar", str(e), parent=self)

    def cancelar(self):
        if messagebox.askyesno("Confirmar", "¿Desea cancelar? Se perderán los cambios no guardados.", parent=self):
            self.controller.show_frame("FacturasView")
