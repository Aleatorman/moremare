import customtkinter as ctk
from tkinter import messagebox
from src.clinical.micro.micro_manager import MicroManager

class MicroPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = MicroManager()
        self.current_micro_id = None
        
        # Almacenes de listas en memoria
        self.lists = {
            'morphologies': [],
            'social_contexts': [],
            'physical_contexts': [],
            'interactions': [],
            'inclinations': [],
            'actors': [],
            'effects': [],
            'noproblems': []
        }
        
        # Referencias visuales
        self.containers = {} 

        self._setup_ui()
        # Cargar historial inicial en la pestaña 2
        self._refresh_history_tab()

    def _setup_ui(self):
        # Título Principal
        ctk.CTkLabel(self, text="2. Análisis Microcontingencial", font=("Arial", 22, "bold"), text_color="#333").pack(anchor="w", pady=(0, 10))

        # --- SISTEMA DE PESTAÑAS ---
        self.tabview = ctk.CTkTabview(self, width=900, height=600)
        self.tabview.pack(fill="both", expand=True)

        self.tabview.add("Nueva Microcontingencia")
        self.tabview.add("Historial Guardado")
        
        # Configurar las dos pestañas
        self._setup_tab_capture(self.tabview.tab("Nueva Microcontingencia"))
        self._setup_tab_history(self.tabview.tab("Historial Guardado"))

    def _setup_tab_capture(self, parent_frame):
        """Construye el formulario de captura en la Pestaña 1"""
        
        # Barra Superior de la Pestaña (Nombre y Botones)
        top_bar = ctk.CTkFrame(parent_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=5)

        ctk.CTkLabel(top_bar, text="Nombre de la Situación:", font=("Arial", 12, "bold"), text_color="#555").pack(side="left", padx=5)
        self.entry_label = ctk.CTkEntry(top_bar, width=300, placeholder_text="Ej: Discusión en la cena...", fg_color="white", text_color="black")
        self.entry_label.pack(side="left", padx=5)

        # Botón Limpiar/Nueva
        ctk.CTkButton(top_bar, text="🧹 Limpiar Campos", width=120, fg_color="#95a5a6", command=self._prepare_new).pack(side="left", padx=15)
        
        # Botón Guardar (Destacado)
        ctk.CTkButton(top_bar, text="💾 GUARDAR", width=120, fg_color="#27ae60", command=self._save_data).pack(side="right", padx=5)

        # Scroll del Formulario
        self.scroll = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, pady=10)

        # ======================================================================
        # CONSTRUCCIÓN DE SECCIONES (FÓRMULA C)
        # ======================================================================

        # A. MORFOLOGÍA
        self._build_section("A. Morfología de la Conducta", "morphologies", [
            {'type': 'combo', 'key': 'type', 'vals': ["Hacer", "Decir", "Pensar/Sentir"], 'w': 100},
            {'type': 'combo', 'key': 'class', 'vals': ["Efectiva", "Afectiva"], 'w': 100},
            {'type': 'entry', 'key': 'metrics', 'ph': 'Métricas (Dur/Frec)', 'w': 150},
            {'type': 'entry', 'key': 'description', 'ph': 'Descripción...', 'w': 300, 'fill': True}
        ], lambda i: f"🔸 {i['type']} ({i['class']}) - {i['metrics']}: {i['description']}")

        # B1. CONTEXTO SOCIAL
        self._build_section("B1. Contexto Social", "social_contexts", [
            {'type': 'combo', 'key': 'type', 'vals': ["Familia", "Amistad", "Trabajo", "Aprendizaje"], 'w': 150},
            {'type': 'entry', 'key': 'description', 'ph': 'Descripción...', 'w': 300, 'fill': True}
        ], lambda i: f"👥 {i['type']}: {i['description']}")

        # B2. CONTEXTO FÍSICO
        self._build_section("B2. Contexto Físico", "physical_contexts", [
            {'type': 'combo', 'key': 'element', 'vals': ["Lugar", "Objeto", "Ruido", "Temperatura", "Iluminación"], 'w': 120},
            {'type': 'entry', 'key': 'description', 'ph': 'Descripción...', 'w': 300, 'fill': True}
        ], lambda i: f"🏠 {i['element']}: {i['description']}")

        # B3. INTERACCIONES
        self._build_section("B3. Interacciones (Esperado vs Competencia)", "interactions", [
            {'type': 'entry', 'key': 'expected', 'ph': 'Comportamiento Esperado', 'w': 250},
            {'type': 'entry', 'key': 'competence', 'ph': 'Competencia Social Actual', 'w': 250, 'fill': True}
        ], lambda i: f"⚖️ Esperado: {i['expected']} | Competencia: {i['competence']}")

        # B4. INCLINACIONES
        self._build_section("B4. Inclinaciones a Actuar", "inclinations", [
            {'type': 'combo', 'key': 'category', 'vals': ["Gustos", "Preferencias", "Estado de ánimo", "Conducta biológica", "Previas"], 'w': 150},
            {'type': 'entry', 'key': 'description', 'ph': 'Observación...', 'w': 300, 'fill': True}
        ], lambda i: f"❤️ {i['category']}: {i['description']}")

        # C. ACTORES (ACTUALIZADO CON TUS OPCIONES)
        # Se aumentó el ancho 'w' a 230 para que quepan los textos largos
        roles_c = [
            "Auspiciador", 
            "Regulador de inclinaciones", 
            "Mediador de la contingencia", 
            "Mediado", 
            "Regulador de tendencia"
        ]
        
        self._build_section("C. Actores (Los Otros)", "actors", [
            {'type': 'entry', 'key': 'name', 'ph': 'Nombre', 'w': 120},
            {'type': 'combo', 'key': 'role', 'vals': roles_c, 'w': 230}, 
            {'type': 'entry', 'key': 'response', 'ph': '¿Qué hizo/dijo?', 'w': 300, 'fill': True}
        ], lambda i: f"👤 {i['name']} ({i['role']}): {i['response']}")

        # D. EFECTOS
        self._build_section("D. Efectos", "effects", [
            {'type': 'combo', 'key': 'type', 'vals': ["Sobre otros", "Sobre sí mismo", "Sin efecto"], 'w': 150},
            {'type': 'entry', 'key': 'description', 'ph': 'Descripción...', 'w': 300, 'fill': True}
        ], lambda i: f"⚡ {i['type']}: {i['description']}")

        # E. NO PROBLEMÁTICO
        self._build_section("E. Ejercicio NO Problemático", "noproblems", [
            {'type': 'entry', 'key': 'situation', 'ph': 'Situación/Contexto', 'w': 200},
            {'type': 'entry', 'key': 'description', 'ph': '¿Por qué no ocurre el problema aquí?', 'w': 300, 'fill': True}
        ], lambda i: f"✅ {i['situation']}: {i['description']}")

    def _setup_tab_history(self, parent_frame):
        """Construye la lista de historial en la Pestaña 2"""
        # Botón Refrescar
        ctk.CTkButton(parent_frame, text="🔄 Actualizar Lista", command=self._refresh_history_tab, fg_color="gray").pack(anchor="e", pady=5)
        
        # Scroll de items
        self.scroll_history = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        self.scroll_history.pack(fill="both", expand=True)

    # ======================================================================
    # LÓGICA DE UI (BUILDERS)
    # ======================================================================
    def _build_section(self, title, list_key, fields_config, format_func):
        ctk.CTkLabel(self.scroll, text=title, font=("Arial", 14, "bold"), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(20, 5))
        input_frame = ctk.CTkFrame(self.scroll, fg_color="#F0F0F0", corner_radius=6)
        input_frame.pack(fill="x", padx=10, pady=5)
        entry_widgets = {} 
        for field in fields_config:
            if field['type'] == 'combo':
                w = ctk.CTkComboBox(input_frame, values=field['vals'], width=field.get('w', 150), fg_color="white", text_color="black")
                w.pack(side="left", padx=5, pady=5)
                entry_widgets[field['key']] = w
            elif field['type'] == 'entry':
                w = ctk.CTkEntry(input_frame, placeholder_text=field['ph'], width=field.get('w', 200), fg_color="white", text_color="black")
                if field.get('fill'): w.pack(side="left", fill="x", expand=True, padx=5, pady=5)
                else: w.pack(side="left", padx=5, pady=5)
                entry_widgets[field['key']] = w
        ctk.CTkButton(input_frame, text="+", width=40, fg_color="#3498db", 
                      command=lambda: self._add_item(list_key, entry_widgets, format_func)).pack(side="left", padx=10)
        list_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        list_container.pack(fill="x", padx=10)
        self.containers[list_key] = {'widget': list_container, 'format': format_func}

    # ======================================================================
    # LÓGICA DE DATOS
    # ======================================================================
    def _add_item(self, list_key, widgets_dict, format_func):
        new_item = {}
        for key, widget in widgets_dict.items():
            val = widget.get()
            if not val: return 
            new_item[key] = val
        self.lists[list_key].append(new_item)
        for key, widget in widgets_dict.items():
            if isinstance(widget, ctk.CTkEntry): widget.delete(0, "end")
        self._render_list_container(list_key)

    def _remove_item(self, list_key, index):
        self.lists[list_key].pop(index)
        self._render_list_container(list_key)

    def _render_list_container(self, list_key):
        container_info = self.containers[list_key]
        parent = container_info['widget']
        fmt = container_info['format']
        data = self.lists[list_key]
        for w in parent.winfo_children(): w.destroy()
        for idx, item in enumerate(data):
            row = ctk.CTkFrame(parent, fg_color="white", corner_radius=6, border_width=1, border_color="#ddd")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=fmt(item), text_color="#333", font=("Arial", 12)).pack(side="left", padx=10, pady=5)
            ctk.CTkButton(row, text="×", width=30, height=20, fg_color="transparent", text_color="red", hover_color="#fee",
                          command=lambda k=list_key, i=idx: self._remove_item(k, i)).pack(side="right", padx=5)

    def _refresh_history_tab(self):
        """Carga la lista de microcontingencias en la Pestaña 2"""
        for w in self.scroll_history.winfo_children(): w.destroy()
        
        micros = self.manager.get_available_micros(self.patient_id)
        if not micros:
            ctk.CTkLabel(self.scroll_history, text="No hay análisis guardados.", text_color="gray").pack(pady=20)
            return

        for m in micros:
            mid, label = m[0], m[1]
            row = ctk.CTkFrame(self.scroll_history, fg_color="white", corner_radius=8, border_width=1, border_color="#ccc")
            row.pack(fill="x", pady=5, padx=5)
            
            ctk.CTkLabel(row, text=f"📄 {label}", font=("Arial", 14, "bold"), text_color="#333").pack(side="left", padx=15, pady=10)
            
            # Botón Editar (Carga en pestaña 1)
            ctk.CTkButton(row, text="Editar / Ver", fg_color="#3498db", width=100,
                          command=lambda i=mid: self._load_into_editor(i)).pack(side="right", padx=10)

    def _load_into_editor(self, micro_id):
        """Carga los datos y cambia a la pestaña 1"""
        data = self.manager.get_full_microcontingency(micro_id)
        if data:
            self._fill_form(data)
            self.tabview.set("Nueva Microcontingencia") # Cambiar foco

    def _prepare_new(self):
        self.current_micro_id = None
        self.entry_label.delete(0, "end")
        for k in self.lists: self.lists[k] = []
        for k in self.containers: self._render_list_container(k)

    def _fill_form(self, data):
        self._prepare_new()
        self.current_micro_id = data['id']
        self.entry_label.insert(0, data['label'])
        for key in self.lists.keys():
            self.lists[key] = data.get(key, [])
            self._render_list_container(key)

    def _save_data(self):
        label = self.entry_label.get()
        if not label:
            messagebox.showwarning("Faltan datos", "Escribe un nombre para la situación.")
            return

        data_package = {'label': label}
        for key, val in self.lists.items():
            data_package[key] = val

        if self.current_micro_id:
            s, m = self.manager.update_micro(self.current_micro_id, data_package)
        else:
            s, m = self.manager.create_micro(self.patient_id, data_package)
        
        if s:
            messagebox.showinfo("Guardado", m)
            self._refresh_history_tab() # Actualizar lista historial
        else:
            messagebox.showerror("Error", m)