import tkinter as tk
from tkinter import ttk, messagebox
from models import Pago
import datetime

class PagosView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        top_frame = ttk.Frame(self); top_frame.pack(pady=10, padx=10, fill="x")
        ttk.Button(top_frame, text="< Volver al Menú", command=lambda: self.controller.show_frame("MainMenu")).pack(side="left")
        ttk.Label(top_frame, text="Gestión de Pagos", style="Heading.TLabel").pack(side="left", expand=True)

        btn_frame = ttk.Frame(self); btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Agregar Pago", command=self.open_form_pago).pack(side="left", padx=5)
        self.btn_eliminar = ttk.Button(btn_frame, text="Eliminar Pago", command=self.eliminar_pago, state="disabled", style="Danger.TButton")
        self.btn_eliminar.pack(side="left", padx=5)

        
        search_frame = ttk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)

        self.search_vars = {}
        cols = ("ID", "Cliente", "Monto", "Fecha", "Comentario")
        col_widths = {"ID": 50, "Cliente": 150, "Monto": 100, "Fecha": 100, "Comentario": 200}
        
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
        for col in cols: self.tree.heading(col, text=col)
        # Configurar ancho de columnas
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Cliente", width=150, anchor="w")
        self.tree.column("Monto", width=100, anchor="e")
        self.tree.column("Fecha", width=100, anchor="center")
        self.tree.column("Comentario", width=200, anchor="w")
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
        self.btn_eliminar.config(state=estado)

    def on_show(self, context=None): 
        for var in self.search_vars.values():
            var.set("")
        self.actualizar_lista()

    def actualizar_lista(self):
        self.tree.delete(*self.tree.get_children())
        
        # Use the service to get data
        pagos = self.controller.pago_service.get_all_payments()
        
        search_terms = {col: var.get().lower() for col, var in self.search_vars.items()}
        
        # Mapeo de columnas a atributos (para columnas especiales)
        def get_valor_columna(pago, col):
            if col == "ID":
                return str(pago.id).lower()
            elif col == "Cliente":
                return pago.cliente.nombre.lower()
            elif col == "Monto":
                return str(pago.monto).lower()
            elif col == "Fecha":
                return pago.fecha.strftime('%d-%m-%Y').lower()
            elif col == "Comentario":
                return pago.comentario.lower()
            return ""
        
        pagos_filtrados = [
            p for p in pagos if
            all(search_terms[col] in get_valor_columna(p, col) for col in self.search_vars)
        ]

        for p in pagos_filtrados:
            self.tree.insert("", "end", values=(p.id, p.cliente.nombre, f"${p.monto:.2f}", p.fecha.strftime('%d-%m-%Y'), p.comentario))
        self._on_tree_select()

    def open_form_pago(self, pago=None): 
        FormPago(self, self.controller, pago)

    def eliminar_pago(self):
        if not self.tree.selection():
            return
        selected_item = self.tree.selection()[0]
        pago_id = int(self.tree.item(selected_item, "values")[0])

        if messagebox.askyesno("Confirmar", f"¿Eliminar pago #{pago_id}?"):
            self.controller.pago_service.delete_payment(pago_id)
            self.actualizar_lista()

class FormPago(tk.Toplevel):
    def __init__(self, parent, controller, pago=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("Formulario de Pago")
        self.geometry("450x350")
        
        self.parent = parent
        self.controller = controller
        self.pago_a_editar = pago
        self.cliente_seleccionado = None
        
        self._build_widgets()
        if pago: 
            self.cargar_datos_pago()

    def _build_widgets(self):
        form = ttk.Frame(self, padding="20")
        form.pack(expand=True, fill="both")
        form.columnconfigure(1, weight=1)
        
        # Obtener fecha actual para precarga
        hoy = datetime.date.today()
        
        self.id_var = tk.StringVar(value="-")
        self.cliente_search_var = tk.StringVar()
        self.monto_var = tk.DoubleVar()
        # Precargar fecha actual
        self.fecha_dd_var = tk.StringVar(value=f"{hoy.day:02d}")
        self.fecha_mm_var = tk.StringVar(value=f"{hoy.month:02d}")
        self.fecha_aaaa_var = tk.StringVar(value=f"{hoy.year:04d}")
        self.comentario_var = tk.StringVar()
        
        # Fila 0: ID (readonly)
        ttk.Label(form, text="ID:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        id_entry = ttk.Entry(form, textvariable=self.id_var, state="readonly")
        id_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)
        
        # Fila 1: Cliente (buscador)
        ttk.Label(form, text="Cliente:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        cliente_frame = ttk.Frame(form)
        cliente_frame.grid(row=1, column=1, sticky="ew", pady=5, padx=5)
        cliente_frame.columnconfigure(0, weight=1)
        
        self.cliente_search = ttk.Entry(cliente_frame, textvariable=self.cliente_search_var)
        self.cliente_search.grid(row=0, column=0, sticky="ew")
        self.cliente_listbox = tk.Listbox(cliente_frame)
        self.cliente_listbox.grid(row=1, column=0, sticky="ew")
        self.cliente_listbox.grid_remove()
        
        self.cliente_search.bind("<KeyRelease>", self._search_cliente)
        self.cliente_search.bind("<FocusOut>", self._hide_cliente_listbox)
        self.cliente_listbox.bind("<<ListboxSelect>>", self._on_cliente_selected)
        
        # Fila 2: Monto
        ttk.Label(form, text="Monto ($):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        ttk.Entry(form, textvariable=self.monto_var).grid(row=2, column=1, sticky="ew", pady=5, padx=5)
        
        # Fila 3: Fecha (DD/MM/AAAA)
        ttk.Label(form, text="Fecha (DD/MM/AAAA):").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        fecha_frame = ttk.Frame(form)
        fecha_frame.grid(row=3, column=1, sticky="ew", pady=5, padx=5)
        
        # Registrar validadores
        vcmd_dd = (self.register(self._validar_dd), "%S", "%P", "%V")
        vcmd_mm = (self.register(self._validar_mm), "%S", "%P", "%V")
        vcmd_aaaa = (self.register(self._validar_aaaa), "%S", "%P", "%V")
        
        # Campo DD
        self.entrada_dd = ttk.Entry(fecha_frame, textvariable=self.fecha_dd_var, width=2, justify="center", validate="key", validatecommand=vcmd_dd)
        self.entrada_dd.pack(side="left")
        self.entrada_dd.bind("<KeyRelease>", self._auto_tab_dd)
        ttk.Label(fecha_frame, text=" / ").pack(side="left")
        
        # Campo MM
        self.entrada_mm = ttk.Entry(fecha_frame, textvariable=self.fecha_mm_var, width=2, justify="center", validate="key", validatecommand=vcmd_mm)
        self.entrada_mm.pack(side="left")
        self.entrada_mm.bind("<KeyRelease>", self._auto_tab_mm)
        ttk.Label(fecha_frame, text=" / ").pack(side="left")
        
        # Campo AAAA
        self.entrada_aaaa = ttk.Entry(fecha_frame, textvariable=self.fecha_aaaa_var, width=4, justify="center", validate="key", validatecommand=vcmd_aaaa)
        self.entrada_aaaa.pack(side="left")
        
        # Fila 4: Comentario
        ttk.Label(form, text="Comentario:").grid(row=4, column=0, sticky="w", pady=5, padx=5)
        ttk.Entry(form, textvariable=self.comentario_var).grid(row=4, column=1, sticky="ew", pady=5, padx=5)

        ttk.Button(form, text="Guardar", command=self.guardar_pago).grid(row=5, column=0, columnspan=2, pady=20)

    def _validar_dd(self, texto_nuevo, valor_actual, evento):
        """Valida el campo DD (1-31)."""
        if evento == "focusout":
            return True
        if not texto_nuevo:
            return True
        if not texto_nuevo.isdigit():
            return False
        if len(valor_actual) > 2:
            return False
        return True

    def _validar_mm(self, texto_nuevo, valor_actual, evento):
        """Valida el campo MM (1-12)."""
        if evento == "focusout":
            return True
        if not texto_nuevo:
            return True
        if not texto_nuevo.isdigit():
            return False
        if len(valor_actual) > 2:
            return False
        return True

    def _validar_aaaa(self, texto_nuevo, valor_actual, evento):
        """Valida el campo AAAA (4 dígitos)."""
        if evento == "focusout":
            return True
        if not texto_nuevo:
            return True
        if not texto_nuevo.isdigit():
            return False
        if len(valor_actual) > 4:
            return False
        return True

    def _auto_tab_dd(self, event):
        """Saltar a MM cuando DD esté completo."""
        if len(self.fecha_dd_var.get()) == 2:
            self.entrada_mm.focus()

    def _auto_tab_mm(self, event):
        """Saltar a AAAA cuando MM esté completo."""
        if len(self.fecha_mm_var.get()) == 2:
            self.entrada_aaaa.focus()

    def _search_cliente(self, event):
        search_term = self.cliente_search_var.get().lower()
        if not search_term:
            self.cliente_listbox.grid_remove()
            return
        
        all_clients = self.controller.cliente_service.get_all_clients()
        matches = [c for c in all_clients if search_term in c.nombre.lower() or search_term in c.codigo.lower()]
        
        self.cliente_listbox.delete(0, tk.END)
        for c in matches: self.cliente_listbox.insert(tk.END, f"{c.codigo} - {c.nombre}")
        
        if matches: self.cliente_listbox.grid()
        else: self.cliente_listbox.grid_remove()

    def _on_cliente_selected(self, event):
        if not self.cliente_listbox.curselection(): return
        
        selected_str = self.cliente_listbox.get(self.cliente_listbox.curselection()[0])
        codigo = selected_str.split(" - ")[0].upper()
        
        all_clients = self.controller.cliente_service.get_all_clients()
        self.cliente_seleccionado = next((c for c in all_clients if c.codigo == codigo), None)
        
        if self.cliente_seleccionado:
            self.cliente_search_var.set(f"{self.cliente_seleccionado.codigo} - {self.cliente_seleccionado.nombre}")
            self.cliente_listbox.grid_remove()

    def _hide_cliente_listbox(self, event): self.after(200, lambda: self.cliente_listbox.grid_remove())

    def cargar_datos_pago(self):
        p = self.pago_a_editar
        self.id_var.set(str(p.id))
        self.cliente_search_var.set(f"{p.cliente.codigo} - {p.cliente.nombre}")
        self.cliente_seleccionado = p.cliente
        self.monto_var.set(p.monto)
        # Cargar fecha en los tres campos
        self.fecha_dd_var.set(f"{p.fecha.day:02d}")
        self.fecha_mm_var.set(f"{p.fecha.month:02d}")
        self.fecha_aaaa_var.set(f"{p.fecha.year:04d}")
        self.comentario_var.set(p.comentario)

    def guardar_pago(self):
        try:
            if not self.cliente_seleccionado:
                raise ValueError("Debe seleccionar un cliente.")
            
            monto = self.monto_var.get()
            if monto <= 0:
                raise ValueError("El monto debe ser mayor que cero.")
            
            # Construir fecha desde los tres campos
            dd = self.fecha_dd_var.get().strip()
            mm = self.fecha_mm_var.get().strip()
            aaaa = self.fecha_aaaa_var.get().strip()
            
            if not dd or not mm or not aaaa:
                # Si no hay fecha, usar hoy
                import datetime
                fecha = datetime.date.today()
            else:
                import datetime
                try:
                    dia = int(dd)
                    mes = int(mm)
                    anio = int(aaaa)
                    
                    # Validar rango
                    if not (1 <= dia <= 31):
                        raise ValueError("El día debe estar entre 1 y 31.")
                    if not (1 <= mes <= 12):
                        raise ValueError("El mes debe estar entre 1 y 12.")
                    if not (1900 <= anio <= 2100):
                        raise ValueError("El año debe estar entre 1900 y 2100.")
                    
                    fecha = datetime.date(anio, mes, dia)
                except ValueError as e:
                    raise ValueError(f"Fecha inválida: {str(e)}")
            
            comentario = self.comentario_var.get().strip()
            
            self.controller.pago_service.create_payment(self.cliente_seleccionado, monto, fecha, comentario)
            self.parent.actualizar_lista()
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}", parent=self)
            return
