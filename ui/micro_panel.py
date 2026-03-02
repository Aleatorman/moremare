import customtkinter as ctk
from tkinter import messagebox
from src.clinical.micro.micro_manager import MicroManager

class MicroPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = MicroManager()
        self.current_micro_id = None
        
        self.lists = {
            'morphologies': [], 'social_contexts': [], 'physical_contexts': [],
            'interactions': [], 'inclinations': [], 'tendencies': [], 'actors': [],
            'effects': [], 'noproblems': []
        }
        
        self.containers = {} 
        self._setup_ui()
        self._refresh_history_tab()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="2. Análisis Microcontingencial", font=("Arial", 22, "bold"), text_color="#333").pack(anchor="w", pady=(0, 10))
        self.tabview = ctk.CTkTabview(self, width=900, height=600)
        self.tabview.pack(fill="both", expand=True)
        self.tabview.add("Nueva Microcontingencia")
        self.tabview.add("Historial Guardado")
        
        self._setup_tab_capture(self.tabview.tab("Nueva Microcontingencia"))
        self._setup_tab_history(self.tabview.tab("Historial Guardado"))

    def _setup_tab_capture(self, parent_frame):
        top_bar = ctk.CTkFrame(parent_frame, fg_color="transparent")
        top_bar.pack(fill="x", pady=5)
        ctk.CTkLabel(top_bar, text="Nombre de la Situación:", font=("Arial", 12, "bold"), text_color="#555").pack(side="left", padx=5)
        self.entry_label = ctk.CTkEntry(top_bar, width=300, placeholder_text="Ej: Discusión...", fg_color="white", text_color="black")
        self.entry_label.pack(side="left", padx=5)
        ctk.CTkButton(top_bar, text="🧹 Limpiar", width=100, fg_color="#95a5a6", command=self._prepare_new).pack(side="left", padx=10)
        ctk.CTkButton(top_bar, text="💾 GUARDAR", width=120, fg_color="#27ae60", command=self._save_data).pack(side="right", padx=5)

        self.scroll = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, pady=10)

        # A. Morfología
        molar_opts = ["- Molar -", "Direccionalidad", "Variación", "Vigor", "Preferencia", "Persistencia"]
        molecular_opts = ["- Molecular -", "Frecuencia", "Duración", "Intensidad", "Latencia"]
        self._build_section("A. Morfología de la Conducta", "morphologies", [
            {'type': 'combo', 'key': 'type', 'vals': ["Hacer", "Decir", "Pensar/Sentir"], 'w': 100},
            {'type': 'combo', 'key': 'class', 'vals': ["Efectiva", "Afectiva"], 'w': 100},
            {'type': 'combo', 'key': 'molar', 'vals': molar_opts, 'w': 130},
            {'type': 'combo', 'key': 'molecular', 'vals': molecular_opts, 'w': 130},
            {'type': 'entry', 'key': 'description', 'ph': 'Descripción...', 'w': 250, 'fill': True}
        ], lambda i: f"🔸 {i.get('type','')} ({i.get('class','')}) | {i.get('molar','')} / {i.get('molecular','')} -> {i.get('description','')}")

        # B. Contextos
        self._build_section("B1. Contexto Social", "social_contexts", [
            {'type': 'combo', 'key': 'type', 'vals': ["Familia", "Trabajo", "Amistad"], 'w': 120},
            {'type': 'entry', 'key': 'description', 'ph': 'Descripción...', 'w': 300, 'fill': True}
        ], lambda i: f"👥 {i.get('type','')}: {i.get('description','')}")

        self._build_section("B2. Contexto Físico", "physical_contexts", [
            {'type': 'combo', 'key': 'element', 'vals': ["Lugar", "Objeto", "Ruido"], 'w': 120},
            {'type': 'entry', 'key': 'description', 'ph': 'Descripción...', 'w': 300, 'fill': True}
        ], lambda i: f"🏠 {i.get('element','')}: {i.get('description','')}")

        self._build_section("B3. Interacciones", "interactions", [
            {'type': 'entry', 'key': 'expected', 'ph': 'Esperado', 'w': 250},
            {'type': 'entry', 'key': 'competence', 'ph': 'Competencia', 'w': 250, 'fill': True}
        ], lambda i: f"⚖️ {i.get('expected','')} | {i.get('competence','')}")

        # B4. Inclinaciones (OPCIONES ACTUALIZADAS)
        b4_opts = ["Gustos", "Preferencias", "Estados de ánimo", "Condiciones biológicas", "Conductas previas asociadas"]
        self._build_section("B4. Inclinaciones", "inclinations", [
            {'type': 'combo', 'key': 'category', 'vals': b4_opts, 'w': 250},
            {'type': 'entry', 'key': 'description', 'ph': 'Observación...', 'w': 300, 'fill': True}
        ], lambda i: f"❤️ {i.get('category','')}: {i.get('description','')}")

        # B5. Tendencias (SECCIÓN NUEVA)
        self._build_section("B5. Tendencias", "tendencies", [
            {'type': 'combo', 'key': 'category', 'vals': ["Hábitos", "Costumbres"], 'w': 150},
            {'type': 'entry', 'key': 'description', 'ph': 'Descripción...', 'w': 300, 'fill': True}
        ], lambda i: f"🔄 {i.get('category','')}: {i.get('description','')}")

        # C. Actores
        roles_c = ["Auspiciador", "Regulador de inclinaciones", "Mediador", "Mediado", "Regulador de tendencia"]
        self._build_section("C. Actores (Los Otros)", "actors", [
            {'type': 'entry', 'key': 'name', 'ph': 'Nombre', 'w': 120},
            {'type': 'combo', 'key': 'role', 'vals': roles_c, 'w': 200}, 
            {'type': 'entry', 'key': 'response', 'ph': 'Respuesta...', 'w': 300, 'fill': True}
        ], lambda i: f"👤 {i.get('name','')} ({i.get('role','')}): {i.get('response','')}")

        # D. Efectos (ACTUALIZADO CON "Sin efecto")
        self._build_section("D. Efectos", "effects", [
            {'type': 'combo', 'key': 'type', 'vals': ["Sobre otros", "Sobre sí mismo", "Sin efecto"], 'w': 150},
            {'type': 'entry', 'key': 'description', 'ph': 'Descripción...', 'w': 300, 'fill': True}
        ], lambda i: f"⚡ {i.get('type','')}: {i.get('description','')}")

        # E. No Problemático (ACTUALIZADO EL NOMBRE)
        self._build_section("E. Circunstancias del ejercicio no problemático de la conducta", "noproblems", [
            {'type': 'entry', 'key': 'situation', 'ph': 'Situación', 'w': 200},
            {'type': 'entry', 'key': 'description', 'ph': '¿Por qué no ocurre?', 'w': 300, 'fill': True}
        ], lambda i: f"✅ {i.get('situation','')}: {i.get('description','')}")

    def _setup_tab_history(self, parent_frame):
        ctk.CTkButton(parent_frame, text="🔄 Actualizar", command=self._refresh_history_tab, fg_color="gray").pack(anchor="e", pady=5)
        self.scroll_history = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        self.scroll_history.pack(fill="both", expand=True)

    def _build_section(self, title, list_key, fields_config, format_func):
        ctk.CTkLabel(self.scroll, text=title, font=("Arial", 14, "bold"), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(15, 5))
        input_frame = ctk.CTkFrame(self.scroll, fg_color="#F8F9F9", corner_radius=6, border_width=1, border_color="#D5DBDB")
        input_frame.pack(fill="x", padx=10, pady=5)
        
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
        list_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        list_container.pack(fill="x", padx=10)
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

    def _refresh_history_tab(self):
        for w in self.scroll_history.winfo_children(): w.destroy()
        micros = self.manager.get_available_micros(self.patient_id)
        for m in micros:
            mid, label = m[0], m[1]
            row = ctk.CTkFrame(self.scroll_history, fg_color="white", border_width=1, border_color="#ccc")
            row.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(row, text=f"📄 {label}", font=("Arial", 13, "bold"), text_color="#333").pack(side="left", padx=15, pady=10)
            
            # BOTÓN ELIMINAR
            ctk.CTkButton(row, text="Eliminar", fg_color="#e74c3c", width=80, command=lambda i=mid: self._delete_entry(i)).pack(side="right", padx=10)
            
            # BOTÓN EDITAR
            ctk.CTkButton(row, text="Editar", fg_color="#3498db", width=80, command=lambda i=mid: self._load_into_editor(i)).pack(side="right", padx=5)
            
            # BOTÓN DETALLE (NUEVO)
            ctk.CTkButton(row, text="Detalle", fg_color="#27ae60", hover_color="#2ecc71", width=80, command=lambda i=mid: self._show_details(i)).pack(side="right", padx=5)

    def _show_details(self, micro_id):
        """Muestra una ventana emergente simple con todos los registros de la microcontingencia."""
        data = self.manager.get_full_microcontingency(micro_id)
        if not data: return
        
        detail_win = ctk.CTkToplevel(self)
        detail_win.title(f"Detalles de Microcontingencia")
        detail_win.geometry("600x700")
        detail_win.grab_set() # Fuerza a que la ventana esté en foco
        
        scroll = ctk.CTkScrollableFrame(detail_win, fg_color="white")
        scroll.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(scroll, text=f"Análisis: {data['label']}", font=("Arial", 18, "bold"), text_color="#2c3e50").pack(anchor="w", pady=(0, 15))
        
        # Función auxiliar para pintar las secciones
        def add_detail_section(title, list_key, format_func):
            items = data.get(list_key, [])
            if items:
                ctk.CTkLabel(scroll, text=title, font=("Arial", 14, "bold"), text_color="#2980b9").pack(anchor="w", pady=(10, 5))
                for item in items:
                    ctk.CTkLabel(scroll, text=format_func(item), font=("Arial", 12), text_color="#333", justify="left", wraplength=530).pack(anchor="w", padx=15, pady=2)

        # Usar la función para mostrar todo
        add_detail_section("A. Morfología", "morphologies", lambda i: f"• {i.get('type','')} ({i.get('class','')}) | {i.get('molar','')} / {i.get('molecular','')} -> {i.get('description','')}")
        add_detail_section("B1. Contexto Social", "social_contexts", lambda i: f"• {i.get('type','')}: {i.get('description','')}")
        add_detail_section("B2. Contexto Físico", "physical_contexts", lambda i: f"• {i.get('element','')}: {i.get('description','')}")
        add_detail_section("B3. Interacciones", "interactions", lambda i: f"• Esperado: {i.get('expected','')} | Competencia: {i.get('competence','')}")
        add_detail_section("B4. Inclinaciones", "inclinations", lambda i: f"• {i.get('category','')}: {i.get('description','')}")
        add_detail_section("B5. Tendencias", "tendencies", lambda i: f"• {i.get('category','')}: {i.get('description','')}")
        add_detail_section("C. Actores", "actors", lambda i: f"• {i.get('name','')} ({i.get('role','')}): {i.get('response','')}")
        add_detail_section("D. Efectos", "effects", lambda i: f"• {i.get('type','')}: {i.get('description','')}")
        add_detail_section("E. Circunstancias de No Problema", "noproblems", lambda i: f"• {i.get('situation','')}: {i.get('description','')}")

        ctk.CTkButton(detail_win, text="Cerrar", fg_color="gray", command=detail_win.destroy).pack(pady=10)


    def _delete_entry(self, mid):
        if messagebox.askyesno("Confirmar", "¿Eliminar este registro permanentemente?"):
            s, m = self.manager.delete_micro(mid)
            if s: self._refresh_history_tab()
            else: messagebox.showerror("Error", m)

    def _load_into_editor(self, micro_id):
        data = self.manager.get_full_microcontingency(micro_id)
        if data:
            self._fill_form(data)
            self.tabview.set("Nueva Microcontingencia")

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
        if not label: return messagebox.showwarning("Aviso", "Falta nombre.")
        data = {k: v for k, v in self.lists.items()}
        data['label'] = label
        s, m = (self.manager.update_micro(self.current_micro_id, data) if self.current_micro_id else self.manager.create_micro(self.patient_id, data))
        if s: 
            messagebox.showinfo("Éxito", m)
            self._refresh_history_tab()
        else: messagebox.showerror("Error", m)