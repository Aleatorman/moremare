import customtkinter as ctk
from tkinter import messagebox
from src.clinical.macro.macro_manager import MacroManager

class LegendWindow(ctk.CTkToplevel):
    """Ventana de ayuda con definiciones y UN CASO PRÁCTICO"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Guía de Referencia y Ejemplo Práctico")
        self.geometry("800x700")
        self.transient(parent)
        self.grab_set()
        self._setup_ui()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="Guía de Códigos: Ejemplo 'El Estudiante'", font=("Arial", 18, "bold"), text_color="#2c3e50").pack(pady=(15, 5))
        ctk.CTkLabel(self, text="Caso: Pedro dice querer graduarse, pero sale de fiesta y reprueba.", font=("Arial", 12), text_color="#7f8c8d").pack(pady=(0, 10))
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=5)
        
        self._add_section_header(scroll, "👤 EL SUJETO (Pedro)", "#3498db")
        self._add_card(scroll, "SsE", "Sustitutiva Ejemplar (Creer/Decir en contexto ideal)", "Pedro dice en casa: 'Debo estudiar mucho para ser un profesional exitoso'.")
        self._add_card(scroll, "SꞩE", "No Sustitutiva Ejemplar (Hacer en contexto ideal)", "Pedro asiste a clases, compra libros y se inscribe a tiempo.")
        self._add_card(scroll, "SsɆ", "Sustitutiva NO Ejemplar (Creer/Decir en situación problema)", "Pedro dice en la fiesta: 'La vida es corta, una falta no me afecta'.")
        self._add_card(scroll, "SꞩɆ", "No Sustitutiva NO Ejemplar (Hacer en situación problema)", "Pedro falta los lunes, no entrega tareas y se embriaga.")

        self._add_section_header(scroll, "👥 LOS OTROS (Familia)", "#e67e22")
        self._add_card(scroll, "OsE", "Sustitutiva Ejemplar (Valores explícitos del grupo)", "La familia dice: 'Aquí lo más importante es la responsabilidad'.")
        self._add_card(scroll, "OꞩE", "No Sustitutiva Ejemplar (Exigencias formales)", "Pagan la colegiatura puntual y revisan sus boletas de calificaciones.")
        self._add_card(scroll, "OsɆ", "Sustitutiva NO Ejemplar (Lo que dicen en el conflicto)", "Dicen: 'Pobrecito, está estresado, déjenlo divertirse un poco'.")
        self._add_card(scroll, "OꞩɆ", "No Sustitutiva NO Ejemplar (Lo que permiten en la práctica)", "Le dan dinero extra para alcohol y le perdonan llegar tarde.")

        ctk.CTkButton(self, text="Entendido, volver a la matriz", fg_color="#3498db", height=40, command=lambda: self.after(100, self.destroy)).pack(pady=15)

    def _add_section_header(self, parent, text, color):
        ctk.CTkLabel(parent, text=text, font=("Arial", 14, "bold"), text_color=color).pack(anchor="w", pady=(15, 5))

    def _add_card(self, parent, code, title, example):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=6, border_width=1, border_color="#ddd")
        card.pack(fill="x", pady=4)
        left = ctk.CTkFrame(card, fg_color="transparent", width=60)
        left.pack(side="left", padx=10, pady=5)
        ctk.CTkLabel(left, text=code, font=("Arial", 16, "bold"), text_color="#2c3e50").pack()
        right = ctk.CTkFrame(card, fg_color="transparent")
        right.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        ctk.CTkLabel(right, text=title, font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(right, text=f'"{example}"', font=("Arial", 12), text_color="#333", wraplength=550, justify="left").pack(anchor="w")


class MatrixWindow(ctk.CTkToplevel):
    """Ventana flotante con la Tabla Teórica de 8x8"""
    def __init__(self, parent, current_points, on_close_callback):
        super().__init__(parent)
        self.title("Matriz de Interacciones Macrocontingenciales")
        self.geometry("980x780") 
        self.transient(parent)
        self.grab_set()
        self.active_points = set(current_points)
        self.on_close_callback = on_close_callback
        self.buttons = {} 
        self.headers = ["SsE", "SꞩE", "SsɆ", "SꞩɆ", "OsE", "OꞩE", "OsɆ", "OꞩɆ"]
        self._setup_ui()

    def _setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(pady=10, fill="x")
        ctk.CTkLabel(top_frame, text="Matriz de Interacción (8x8)", font=("Arial", 18, "bold")).pack()
        ctk.CTkButton(top_frame, text="📖 Ver Ejemplo y Simbología", fg_color="#8e44ad", hover_color="#9b59b6", width=220, command=self._open_legend).pack(pady=5)
        ctk.CTkLabel(top_frame, text="Haz clic en las intersecciones (Triángulo Inferior) para marcar.", text_color="gray").pack()

        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(expand=True, padx=20, pady=5)

        header_font = ("Arial", 11, "bold") 
        for col, text in enumerate(self.headers):
            ctk.CTkLabel(grid_frame, text=text, font=header_font, width=60, text_color="#2c3e50").grid(row=0, column=col+1, padx=2, pady=5)
        for row, text in enumerate(self.headers):
            ctk.CTkLabel(grid_frame, text=text, font=header_font, width=60, text_color="#2c3e50").grid(row=row+1, column=0, padx=5, pady=2)

        for r in range(8):
            for c in range(8):
                key = (r, c)
                if c >= r:
                    btn = ctk.CTkButton(grid_frame, text="", width=60, height=45, fg_color="#444444", state="disabled", border_width=0)
                else:
                    is_active = key in self.active_points
                    btn = ctk.CTkButton(grid_frame, text="", width=60, height=45, 
                                        fg_color="#2ecc71" if is_active else "#ecf0f1", 
                                        hover_color="#27ae60" if is_active else "#bdc3c7",
                                        border_width=1, border_color="#dcdcdc",
                                        command=lambda k=key: self._toggle_point(k))
                    self.buttons[key] = btn 
                btn.grid(row=r+1, column=c+1, padx=2, pady=2)

        ctk.CTkButton(self, text="Listo / Terminar Selección", height=40, font=("Arial", 12, "bold"), fg_color="#3498db", command=self._close).pack(pady=15)

    def _open_legend(self):
        LegendWindow(self)

    def _toggle_point(self, key):
        if key in self.active_points:
            self.active_points.remove(key)
            self.buttons[key].configure(fg_color="#ecf0f1", hover_color="#bdc3c7")
        else:
            self.active_points.add(key)
            self.buttons[key].configure(fg_color="#2ecc71", hover_color="#27ae60")

    def _close(self):
        self.on_close_callback(list(self.active_points))
        self.after(100, self.destroy)


class MacroPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = MacroManager()
        self.current_macro_id = None
        self.matrix_points = [] 
        
        self.lists = {'normative_functions': []}
        self.containers = {}

        self._setup_ui()
        self._refresh_history()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="3. Análisis Macrocontingencial", font=("Arial", 22, "bold"), text_color="#333").pack(anchor="w", pady=(0, 10))

        self.tabview = ctk.CTkTabview(self, width=900, height=600)
        self.tabview.pack(fill="both", expand=True)

        self.tabview.add("Nueva Macrocontingencia")
        self.tabview.add("Historial Guardado")
        
        self._setup_tab_capture(self.tabview.tab("Nueva Macrocontingencia"))
        self._setup_tab_history(self.tabview.tab("Historial Guardado"))

    def _setup_tab_capture(self, parent_frame):
        scroll = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # =========================================================
        # SECCIÓN 1: MAPA DE GRUPOS Y PRÁCTICAS DOMINANTES
        # =========================================================
        self._section_header(scroll, "1. Mapa de Grupos y Prácticas Dominantes")
        
        row1 = ctk.CTkFrame(scroll, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(row1, text="Tipo de Grupo:").pack(side="left", padx=5)
        self.combo_group_type = ctk.CTkComboBox(row1, values=["Familia", "Trabajo", "Pares", "Pareja", "Religión", "Sociedad", "Otro"])
        self.combo_group_type.pack(side="left", padx=5)
        
        ctk.CTkLabel(row1, text="Nombre/Detalle:").pack(side="left", padx=(15,5))
        self.entry_group_name = ctk.CTkEntry(row1, width=250, placeholder_text="Ej: Familia materna, Oficina...")
        self.entry_group_name.pack(side="left", padx=5)

        self.txt_beliefs = self._area_input(scroll, "Creencias y Valores del Grupo (¿Qué consideran bueno/malo?):")
        self.txt_customs = self._area_input(scroll, "Costumbres y Estilos de Vida (¿Qué es lo 'normal' o esperado que se haga?):")

        # =========================================================
        # SECCIÓN 2: FUNCIONES NORMATIVAS (Lista Dinámica Actualizada)
        # =========================================================
        self._section_header(scroll, "2. Análisis de Microcontingencias Ejemplares (Funciones Normativas)")
        
        # LISTA ACTUALIZADA CON TUS OPCIONES
        func_opts = [
            "Prescripción (moldear o instruir una relación)",
            "Indicación (señalar una opción por encima de otra)",
            "Facilitación (auspiciar o disponer condiciones)",
            "Justificación (instruir sobre consecuencias deseables)",
            "Sanción (llevar a cabo consecuencias concretas)",
            "Advertencia (señalar consecuencias que pueden ocurrir)",
            "Comparación (contraste de dos formas de relación)",
            "Condicionamiento (instruir requerimientos previos)",
            "Prohibición (señalar imposibilidad de una conducta)",
            "Expectativa (instruir sobre demandas sociales)"
        ]

        # Se amplió el ancho ('w': 380) del ComboBox para que se lea la descripción completa
        self._build_dynamic_list(scroll, "normative_functions", [
            {'type': 'combo', 'key': 'function_type', 'vals': func_opts, 'w': 380},
            {'type': 'entry', 'key': 'exercised_by', 'ph': '¿Quién la ejerce?', 'w': 140},
            {'type': 'entry', 'key': 'description', 'ph': 'Descripción...', 'w': 220, 'fill': True}
        ], lambda i: f"⚖️ {i.get('function_type','').split(' (')[0]} por {i.get('exercised_by','')}: {i.get('description','')}")

        # =========================================================
        # SECCIÓN 3: EVALUACIÓN DE LA CORRESPONDENCIA
        # =========================================================
        self._section_header(scroll, "3. Evaluación de la Correspondencia")
        
        self.txt_intra = self._large_area_input(scroll, "A. Análisis Intracontingencial:\n¿El usuario lee correctamente la situación actual o actúa como si estuviera en un contexto diferente/pasado?")
        self.txt_inter = self._large_area_input(scroll, "B. Análisis Intercontingencial:\n¿Cómo choca lo que el usuario hace con los valores y prácticas de este grupo dominante?")

        # =========================================================
        # SECCIÓN 4: MATRIZ Y BOTONES
        # =========================================================
        self.btn_open_matrix = ctk.CTkButton(scroll, text="📊 ABRIR MATRIZ INTERCONTINGENCIAL (0 marcados)", 
                                             height=45, fg_color="#8e44ad", hover_color="#9b59b6", font=("Arial", 12, "bold"),
                                             command=self._open_matrix_window)
        self.btn_open_matrix.pack(fill="x", padx=20, pady=20)

        action_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        action_frame.pack(fill="x", pady=20)
        ctk.CTkButton(action_frame, text="Nueva / Limpiar", fg_color="gray", width=120, command=self._reset_form).pack(side="left", padx=10)
        ctk.CTkButton(action_frame, text="💾 GUARDAR ANÁLISIS MACRO", fg_color="#27ae60", width=180, command=self._save).pack(side="right", padx=10)

    # --- HELPERS PARA LA INTERFAZ ---

    def _section_header(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Arial", 14, "bold"), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(20, 5))

    def _area_input(self, parent, label):
        ctk.CTkLabel(parent, text=label, font=("Arial", 11, "bold"), text_color="#555").pack(anchor="w", padx=15, pady=(10,0))
        entry = ctk.CTkEntry(parent, height=35) 
        entry.pack(fill="x", padx=15, pady=(0, 5))
        return entry

    def _large_area_input(self, parent, label):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold"), text_color="#d35400", justify="left").pack(anchor="w", padx=15, pady=(15,5))
        txt = ctk.CTkTextbox(parent, height=80, border_width=1, border_color="#ccc")
        txt.pack(fill="x", padx=15, pady=(0, 5))
        return txt

    # --- LÓGICA DE LISTA DINÁMICA ---
    
    def _build_dynamic_list(self, parent, list_key, fields_config, format_func):
        input_frame = ctk.CTkFrame(parent, fg_color="#F8F9F9", corner_radius=6, border_width=1, border_color="#D5DBDB")
        input_frame.pack(fill="x", padx=15, pady=5)
        entry_widgets = {} 
        for field in fields_config:
            if field['type'] == 'combo':
                w = ctk.CTkComboBox(input_frame, values=field['vals'], width=field.get('w', 150), fg_color="white", text_color="black")
                w.pack(side="left", padx=5, pady=8)
                entry_widgets[field['key']] = w
            elif field['type'] == 'entry':
                w = ctk.CTkEntry(input_frame, placeholder_text=field['ph'], width=field.get('w', 200), fg_color="white", text_color="black")
                if field.get('fill'): w.pack(side="left", fill="x", expand=True, padx=5, pady=8)
                else: w.pack(side="left", padx=5, pady=8)
                entry_widgets[field['key']] = w
        ctk.CTkButton(input_frame, text="Añadir", width=60, fg_color="#3498db", command=lambda: self._add_item(list_key, entry_widgets, format_func)).pack(side="left", padx=10)
        list_container = ctk.CTkFrame(parent, fg_color="transparent")
        list_container.pack(fill="x", padx=15)
        self.containers[list_key] = {'widget': list_container, 'format': format_func}

    def _add_item(self, list_key, widgets_dict, format_func):
        new_item = {k: w.get() for k, w in widgets_dict.items() if w.get()}
        if not new_item: return
        self.lists[list_key].append(new_item)
        for w in widgets_dict.values(): 
            if isinstance(w, ctk.CTkEntry): w.delete(0, "end")
        self._render_list_container(list_key)

    def _render_list_container(self, list_key):
        parent = self.containers[list_key]['widget']
        fmt = self.containers[list_key]['format']
        for w in parent.winfo_children(): w.destroy()
        for idx, item in enumerate(self.lists[list_key]):
            row = ctk.CTkFrame(parent, fg_color="white", border_width=1, border_color="#ddd")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=fmt(item), text_color="#333").pack(side="left", padx=10, pady=5)
            ctk.CTkButton(row, text="×", width=30, fg_color="transparent", text_color="red", command=lambda k=list_key, i=idx: self._remove_item(k, i)).pack(side="right", padx=5)

    def _remove_item(self, list_key, index):
        self.lists[list_key].pop(index)
        self._render_list_container(list_key)

    # --- PESTAÑA DE HISTORIAL Y GUARDADO ---

    def _setup_tab_history(self, parent_frame):
        ctk.CTkButton(parent_frame, text="🔄 Actualizar Lista", command=self._refresh_history, fg_color="gray").pack(anchor="e", pady=5)
        self.scroll_hist = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        self.scroll_hist.pack(fill="both", expand=True)

    def _open_matrix_window(self):
        MatrixWindow(self, self.matrix_points, self._on_matrix_closed)

    def _on_matrix_closed(self, new_points):
        self.matrix_points = new_points
        self.btn_open_matrix.configure(text=f"📊 ABRIR MATRIZ INTERCONTINGENCIAL ({len(self.matrix_points)} marcados)")

    def _save(self):
        g_name = self.entry_group_name.get()
        if not g_name: return messagebox.showwarning("Error", "Falta el nombre/detalle del grupo.")
        
        data = {
            'group_type': self.combo_group_type.get(),
            'group_name': g_name,
            'beliefs_values': self.txt_beliefs.get(),
            'customs_lifestyles': self.txt_customs.get(),
            'normative_functions': self.lists['normative_functions'],
            'intra_analysis': self.txt_intra.get("1.0", "end-1c"),
            'inter_analysis': self.txt_inter.get("1.0", "end-1c")
        }
        
        s, m = self.manager.save_macro(self.patient_id, self.current_macro_id, data, self.matrix_points)
        if s:
            messagebox.showinfo("Éxito", m)
            self._refresh_history()
            self._reset_form() 
        else: messagebox.showerror("Error", m)

    def _refresh_history(self):
        for w in self.scroll_hist.winfo_children(): w.destroy()
        macros = self.manager.get_macros(self.patient_id)
        if not macros:
            ctk.CTkLabel(self.scroll_hist, text="No hay registros guardados.", text_color="gray").pack(pady=20)
            return

        for m in macros:
            mid, name = m[0], m[1]
            row = ctk.CTkFrame(self.scroll_hist, fg_color="white", corner_radius=6, border_width=1, border_color="#ccc")
            row.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(row, text=f"📂 {name}", font=("Arial", 14, "bold"), text_color="#333").pack(side="left", padx=15, pady=10)
            
            ctk.CTkButton(row, text="Eliminar", fg_color="#e74c3c", width=80, command=lambda i=mid: self._delete_macro(i)).pack(side="right", padx=10)
            ctk.CTkButton(row, text="Editar / Ver", width=100, fg_color="#3498db", command=lambda i=mid: self._load_macro(i)).pack(side="right", padx=5)

    def _delete_macro(self, mid):
        if messagebox.askyesno("Confirmar", "¿Eliminar este análisis macrocontingencial?"):
            s, m = self.manager.delete_macro(mid)
            if s: self._refresh_history()
            else: messagebox.showerror("Error", m)

    def _load_macro(self, mid):
        data = self.manager.get_full_macro(mid)
        if not data: return
        self._reset_form()
        
        self.current_macro_id = data['id']
        self.combo_group_type.set(data['group_type'])
        self.entry_group_name.insert(0, data['group_name'])
        self.txt_beliefs.insert(0, data['beliefs_values'])
        self.txt_customs.insert(0, data['customs_lifestyles'])
        
        self.lists['normative_functions'] = data.get('normative_functions', [])
        self._render_list_container('normative_functions')
        
        self.txt_intra.insert("0.0", data['intra_analysis'])
        self.txt_inter.insert("0.0", data['inter_analysis'])
        
        self.matrix_points = data.get('matrix_points', [])
        self.btn_open_matrix.configure(text=f"📊 ABRIR MATRIZ INTERCONTINGENCIAL ({len(self.matrix_points)} marcados)")
        self.tabview.set("Nueva Macrocontingencia")

    def _reset_form(self):
        self.current_macro_id = None
        self.entry_group_name.delete(0, "end")
        self.txt_beliefs.delete(0, "end")
        self.txt_customs.delete(0, "end")
        self.txt_intra.delete("1.0", "end")
        self.txt_inter.delete("1.0", "end")
        self.lists['normative_functions'] = []
        self._render_list_container('normative_functions')
        self.matrix_points = []
        self.btn_open_matrix.configure(text="📊 ABRIR MATRIZ INTERCONTINGENCIAL (0 marcados)")