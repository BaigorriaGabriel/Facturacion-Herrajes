import tkinter as tk
from tkinter import ttk, messagebox


class AumentosPreciosView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.productos_seleccionados = set()  # Set de códigos de productos seleccionados
        self.checkbox_vars = {}  # Dict: codigo -> BooleanVar
        self.items_tree = {}  # Dict: item_id -> codigo de producto
        
        # ============ HEADER ============
        top_frame = ttk.Frame(self)
        top_frame.pack(pady=10, padx=10, fill="x")
        ttk.Button(top_frame, text="< Volver al Menú", command=lambda: self.controller.show_frame("MainMenu")).pack(side="left")
        ttk.Label(top_frame, text="Aumentos de Precios", style="Heading.TLabel").pack(side="left", expand=True)

        # ============ BUSCADOR ============
        search_frame = ttk.LabelFrame(self, text="Buscar Productos", padding="10")
        search_frame.pack(fill="x", padx=10, pady=10)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self._filtrar_productos())
        ttk.Label(search_frame, text="Código o Descripción:").pack(side="left", padx=5)
        ttk.Entry(search_frame, textvariable=self.search_var, width=40).pack(side="left", padx=5, fill="x", expand=True)

        # ============ CONTROLES DE SELECCIÓN ============
        control_frame = ttk.Frame(self)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        self.select_all_var = tk.BooleanVar()
        ttk.Checkbutton(control_frame, text="Seleccionar todos", variable=self.select_all_var, command=self._toggle_select_all).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Limpiar selección", command=self._limpiar_seleccion).pack(side="left", padx=5)
        
        # Etiqueta de contador
        self.contador_label = ttk.Label(control_frame, text="Productos seleccionados: 0", style="Heading.TLabel")
        self.contador_label.pack(side="left", padx=20, expand=True)

        # ============ TABLA DE PRODUCTOS ============
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(table_frame, columns=("Seleccionar", "Codigo", "Descripcion", "Precio"), show="headings", height=15)
        
        # Configurar columnas
        self.tree.column("Seleccionar", width=45, anchor="center")
        self.tree.column("Codigo", width=80, anchor="center")
        self.tree.column("Descripcion", width=250, anchor="w")
        self.tree.column("Precio", width=120, anchor="e")
        
        self.tree.heading("Seleccionar", text="Seleccionar")
        self.tree.heading("Codigo", text="Código")
        self.tree.heading("Descripcion", text="Descripción")
        self.tree.heading("Precio", text="Precio Actual")
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Bind para cuando se hace click en la tabla (toggle checkbox)
        self.tree.bind("<Button-1>", self._on_tree_click)

        # ============ FORMULARIO DE AUMENTO ============
        form_frame = ttk.LabelFrame(self, text="Aplicar Aumento", padding="15")
        form_frame.pack(fill="x", padx=10, pady=10)
        
        form_frame.columnconfigure(1, weight=1)
        
        ttk.Label(form_frame, text="Porcentaje de aumento (%):").grid(row=0, column=0, sticky="w", padx=5, pady=10)
        self.porcentaje_var = tk.DoubleVar()
        porcentaje_entry = ttk.Entry(form_frame, textvariable=self.porcentaje_var, width=15)
        porcentaje_entry.grid(row=0, column=1, sticky="w", padx=5, pady=10)
        ttk.Label(form_frame, text="(Ej: 10 para 10%)").grid(row=0, column=2, sticky="w", padx=5, pady=10)
        
        # Botón aplicar con estilo
        ttk.Button(form_frame, text="Aplicar Aumento", command=self._aplicar_aumento, style="Accent.TButton").grid(row=0, column=3, sticky="e", padx=5, pady=10)

    def on_show(self, context=None):
        """Se llama cuando se muestra la vista"""
        self.search_var.set("")
        self.porcentaje_var.set(0)
        self._limpiar_seleccion()
        self._cargar_productos()

    def _cargar_productos(self):
        """Carga todos los productos en la tabla"""
        self.tree.delete(*self.tree.get_children())
        self.checkbox_vars.clear()
        self.items_tree.clear()
        
        productos = self.controller.producto_service.get_all_products()
        
        for producto in productos:
            # Crear checkbox var para este producto
            var = tk.BooleanVar(value=False)
            self.checkbox_vars[producto.codigo] = var
            
            # Insertar fila
            item_id = self.tree.insert("", "end", values=("☐", producto.codigo, producto.descripcion, f"${producto.precio:.2f}"))
            self.items_tree[item_id] = producto.codigo

    def _filtrar_productos(self):
        """Filtra productos según el texto de búsqueda"""
        search_text = self.search_var.get().lower()
        productos = self.controller.producto_service.get_all_products()
        
        # Filtrar
        productos_filtrados = [
            p for p in productos
            if search_text in p.codigo.lower() or search_text in p.descripcion.lower()
        ]
        
        # Actualizar tabla
        self.tree.delete(*self.tree.get_children())
        
        for producto in productos_filtrados:
            var = self.checkbox_vars.get(producto.codigo, tk.BooleanVar(value=False))
            checkbox_text = "☑" if var.get() else "☐"
            item_id = self.tree.insert("", "end", values=(checkbox_text, producto.codigo, producto.descripcion, f"${producto.precio:.2f}"))
            self.items_tree[item_id] = producto.codigo
        
        # Actualizar estado del checkbox "Seleccionar Todos"
        self._actualizar_vista_productos()

    def _on_tree_click(self, event):
        """Maneja clicks en la tabla para toggle de checkboxes"""
        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify('column', event.x, event.y)
        
        # Solo permitir toggle si se clickea en la primera columna (Seleccionar)
        if item and column == '#1':
            # Obtener el ancho y posición de la columna para validar que el click está en el checkbox
            col_bbox = self.tree.bbox(item, column)
            if col_bbox:
                col_x, col_y, col_width, col_height = col_bbox
                # Solo activar si el click está en la mitad central de la columna (donde está el checkbox)
                checkbox_center_x = col_x + col_width / 2
                checkbox_margin = col_width / 4  # Margen de tolerancia
                
                if checkbox_center_x - checkbox_margin <= event.x <= checkbox_center_x + checkbox_margin:
                    # Extraer el código directamente de los valores del item
                    valores = self.tree.item(item, "values")
                    if valores and len(valores) >= 2:
                        codigo = valores[1]  # El código está en la posición 1
                        var = self.checkbox_vars.get(codigo)
                        
                        if var:
                            var.set(not var.get())
                            self._actualizar_vista_productos()

    def _actualizar_vista_productos(self):
        """Actualiza la visualización de checkboxes y el contador"""
        # Contar seleccionados
        self.productos_seleccionados = {codigo for codigo, var in self.checkbox_vars.items() if var.get()}
        
        # Actualizar contador
        cant = len(self.productos_seleccionados)
        self.contador_label.config(text=f"Productos seleccionados: {cant}")
        
        # Actualizar checkbox "Seleccionar todos"
        productos_filtrados = self._get_productos_filtrados()
        codigos_filtrados = {p.codigo for p in productos_filtrados}
        seleccionados_filtrados = self.productos_seleccionados & codigos_filtrados
        
        if len(seleccionados_filtrados) == len(codigos_filtrados) and len(codigos_filtrados) > 0:
            self.select_all_var.set(True)
        else:
            self.select_all_var.set(False)
        
        # Actualizar símbolos en la tabla
        self._refrescar_tabla()

    def _refrescar_tabla(self):
        """Refresca los símbolos de checkbox en la tabla visible"""
        for item in self.tree.get_children():
            valores = self.tree.item(item, "values")
            if valores and len(valores) >= 2:
                codigo = valores[1]
                var = self.checkbox_vars.get(codigo, tk.BooleanVar(value=False))
                checkbox_text = "☑" if var.get() else "☐"
                self.tree.item(item, values=(checkbox_text, valores[1], valores[2], valores[3]))

    def _toggle_select_all(self):
        """Toggle de seleccionar/deseleccionar todos los productos visibles"""
        productos_filtrados = self._get_productos_filtrados()
        codigos_filtrados = {p.codigo for p in productos_filtrados}
        
        # Verificar cuántos de los filtrados están actualmente seleccionados
        seleccionados_filtrados = self.productos_seleccionados & codigos_filtrados
        
        # Si NO todos están seleccionados, seleccionar todos
        # Si todos están seleccionados, deseleccionar todos
        if len(seleccionados_filtrados) < len(codigos_filtrados):
            # Seleccionar todos los filtrados
            for producto in productos_filtrados:
                var = self.checkbox_vars.get(producto.codigo)
                if var:
                    var.set(True)
        else:
            # Deseleccionar todos los filtrados
            for producto in productos_filtrados:
                var = self.checkbox_vars.get(producto.codigo)
                if var:
                    var.set(False)
        
        self._actualizar_vista_productos()

    def _get_productos_filtrados(self):
        """Obtiene los productos que coinciden con el filtro actual"""
        search_text = self.search_var.get().lower()
        productos = self.controller.producto_service.get_all_products()
        
        return [
            p for p in productos
            if search_text in p.codigo.lower() or search_text in p.descripcion.lower()
        ]

    def _limpiar_seleccion(self):
        """Limpia toda la selección"""
        for var in self.checkbox_vars.values():
            var.set(False)
        self.select_all_var.set(False)
        self._actualizar_vista_productos()

    def _aplicar_aumento(self):
        """Aplica el aumento de precios con validaciones y confirmación"""
        # Validar porcentaje
        try:
            porcentaje = self.porcentaje_var.get()
            if porcentaje <= 0:
                messagebox.showerror("Error", "El porcentaje debe ser mayor a 0")
                return
        except tk.TclError:
            messagebox.showerror("Error", "Ingrese un porcentaje válido")
            return
        
        # Validar que hay productos seleccionados
        if not self.productos_seleccionados:
            messagebox.showwarning("Advertencia", "Debe seleccionar al menos un producto")
            return
        
        # Obtener productos seleccionados
        productos_seleccionados = [
            p for p in self.controller.producto_service.get_all_products()
            if p.codigo in self.productos_seleccionados
        ]
        
        # Crear popup de confirmación con preview
        self._mostrar_confirmacion(porcentaje, productos_seleccionados)

    def _mostrar_confirmacion(self, porcentaje, productos):
        """Muestra popup de confirmación con preview de cambios"""
        dialog = tk.Toplevel(self)
        dialog.title("Confirmar Aumento de Precios")
        dialog.geometry("650x650")
        dialog.transient(self)
        dialog.grab_set()
        
        # Contenido
        content = ttk.Frame(dialog, padding="15")
        content.pack(fill="both", expand=True)
        
        # Mensaje principal
        mensaje = f"¿Seguro que querés aplicar un aumento del {porcentaje}% a {len(productos)} productos seleccionados?"
        ttk.Label(content, text=mensaje, wraplength=450, justify="center").pack(pady=15)
        
        # Separador
        ttk.Separator(content, orient="horizontal").pack(fill="x", pady=10)
        
        # Preview
        preview_label = ttk.Label(content, text=f"Productos a aumentar ({len(productos)}):", font=("", 10, "bold"))
        preview_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Scroll frame para ejemplos
        scroll_frame = ttk.Frame(content)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(scroll_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mostrar TODOS los productos
        for producto in productos:
            nuevo_precio = producto.precio * (1 + porcentaje / 100)
            texto = f"• {producto.codigo} - {producto.descripcion}: ${producto.precio:.2f} → ${nuevo_precio:.2f}"
            ttk.Label(scrollable_frame, text=texto, wraplength=400).pack(anchor="w", pady=3)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Separador
        ttk.Separator(content, orient="horizontal").pack(fill="x", pady=10)
        
        # Botones
        btn_frame = ttk.Frame(content)
        btn_frame.pack(fill="x", pady=10)
        
        def confirmar():
            try:
                self.controller.producto_service.apply_price_increase(list(self.productos_seleccionados), porcentaje)
                messagebox.showinfo("Éxito", f"¡Aumento aplicado a {len(productos)} productos!", parent=dialog)
                self._limpiar_seleccion()
                self._cargar_productos()
                self.porcentaje_var.set(0)  # Limpiar el campo de porcentaje
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dialog)
        
        ttk.Button(btn_frame, text="Sí, aplicar", command=confirmar, style="Accent.TButton").pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side="right", padx=5)
