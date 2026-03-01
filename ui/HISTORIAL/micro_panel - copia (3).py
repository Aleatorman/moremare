import customtkinter as ctk
from tkinter import messagebox
from src.clinical.micro.micro_manager import MicroManager

class MicroPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = MicroManager()
        
        self.current_micro_id = None
        
        # Listas en memoria
        self.actors_list = []
        self.inclinations_list = []
        self.effects_list = []

        self._setup_ui()
        self._load_micros_list()

    def _setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(header, text="2. Análisis Microcontingencial", font=("Arial", 22, "bold"), text_color="#333").pack(side="left")

        # Controles Superiores
        controls = ctk.CTkFrame(self, fg_color="#EBEBEB", corner_radius=8)
        controls.pack(fill="x", pady=10, ipady=5)

        ctk.CTkLabel(controls, text="Seleccionar Situación:", font=("Arial", 12, "bold"), text_color="#555").pack(side="left", padx=15)
        self.combo_micros = ctk.CTkComboBox(controls, width=300, command=self._on_micro_selected, fg_color="white", text_color="black")
        self.combo_micros.pack(side="left", padx=10)

        ctk.CTkButton(controls, text="+ Nueva", width=80, fg_color="#3498db", command=self._prepare_new).pack(side="left", padx=10)
        ctk.CTkButton(controls, text="💾 GUARDAR", width=120, fg_color="#27ae60", command=self._save_data).pack(side="right", padx=15)

        # Scroll principal
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        # ---------------------------------------------------------
        # A. MORFOLOGÍA
        # ---------------------------------------------------------
        self._section_header("A. Morfología de la Conducta")
        f_morph = ctk.CTkFrame(self.scroll, fg_color="transparent")
        f_morph.pack(fill="x", padx=10)
        
        # Tipo (Hacer/Decir...) y Clase (Efectiva/Afectiva)
        self.combo_morph_type = ctk.CTkComboBox(f_morph, values=["Hacer", "Decir", "Pensar/Sentir"], width=150, fg_color="white", text_color="black")
        self.combo_morph_type.pack(side="left", padx=(0, 10))
        
        self.combo_morph_class = ctk.CTkComboBox(f_morph, values=["Efectiva", "Afectiva"], width=150, fg_color="white", text_color="black")
        self.combo_morph_class.pack(side="left", padx=(0, 10))
        
        self.entry_metrics = ctk.CTkEntry(f_morph, placeholder_text="Métricas (Duración, Frecuencia...)", fg_color="white", text_color="black")
        self.entry_metrics.pack(side="left", fill="x", expand=True)

        self.txt_problem = self._textarea("Descripción detallada de la conducta problema:")

        # ---------------------------------------------------------
        # B. CONTEXTO E INTERACCIONES (DISEÑO SOLICITADO)
        # ---------------------------------------------------------
        self._section_header("B. Contexto e Interacciones Sociales")
        
        card_b = ctk.CTkFrame(self.scroll, fg_color="#F9F9F9", corner_radius=8, border_width=1, border_color="#E0E0E0")
        card_b.pack(fill="x", padx=10, pady=5)

        # --- 1. CONTEXTO SOCIAL (Selector) ---
        f_social = ctk.CTkFrame(card_b, fg_color="transparent")
        f_social.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(f_social, text="Contexto Social:", font=("Arial", 12, "bold"), text_color="#333").pack(side="left", padx=(0, 10))
        self.combo_social_type = ctk.CTkComboBox(f_social, values=["Familia", "Amistad", "Trabajo", "Aprendizaje"], width=200, fg_color="white", text_color="black")
        self.combo_social_type.pack(side="left")
        
        # Descripción opcional del contexto social (para detalles extra)
        self.txt_social_desc = ctk.CTkEntry(f_social, placeholder_text="Detalles adicionales (opcional)...", fg_color="white", text_color="black")
        self.txt_social_desc.pack(side="left", fill="x", expand=True, padx=10)

        # --- 2. CONTEXTO FÍSICO (Narrativo) ---
        ctk.CTkLabel(card_b, text="Contexto Físico (Lugar, objetos, ambiente):", font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w", padx=15, pady=(5, 0))
        self.txt_physical = ctk.CTkTextbox(card_b, height=60, fg_color="white", text_color="black", border_width=1, border_color="#ccc")
        self.txt_physical.pack(fill="x", padx=15, pady=(0, 15))

        # --- 3. INTERACCIONES (Labels ARRIBA del cuadro) ---
        # Grid para ponerlos lado a lado
        grid_inter = ctk.CTkFrame(card_b, fg_color="transparent")
        grid_inter.pack(fill="x", padx=10, pady=(0, 15))
        grid_inter.columnconfigure(0, weight=1)
        grid_inter.columnconfigure(1, weight=1)

        # Comportamientos Esperados
        f_exp = ctk.CTkFrame(grid_inter, fg_color="transparent")
        f_exp.grid(row=0, column=0, sticky="nsew", padx=5)
        
        ctk.CTkLabel(f_exp, text="Comportamientos Esperados:", font=("Arial", 11, "bold"), text_color="#333").pack(anchor="w")
        self.entry_expected = ctk.CTkEntry(f_exp, fg_color="white", text_color="black")
        self.entry_expected.pack(fill="x", pady=(2, 0))

        # Competencia Social
        f_comp = ctk.CTkFrame(grid_inter, fg_color="transparent")
        f_comp.grid(row=0, column=1, sticky="nsew", padx=5)
        
        ctk.CTkLabel(f_comp, text="Competencia Social (Capacidad de ejercer conductas esperadas):", font=("Arial", 11, "bold"), text_color="#333").pack(anchor="w")
        self.entry_competence = ctk.CTkEntry(f_comp, fg_color="white", text_color="black")
        self.entry_competence.pack(fill="x", pady=(2, 0))

        # --- 4. INCLINACIONES (Lista) ---
        ctk.CTkFrame(card_b, height=1, fg_color="#E0E0E0").pack(fill="x", padx=15, pady=5) # Separador
        
        ctk.CTkLabel(card_b, text="Inclinaciones a Actuar:", font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w", padx=15, pady=(5, 0))
        
        add_inc_frame = ctk.CTkFrame(card_b, fg_color="transparent")
        add_inc_frame.pack(fill="x", padx=10, pady=5)
        
        self.combo_inc_cat = ctk.CTkComboBox(add_inc_frame, values=["Gustos", "Preferencias", "Estado de ánimo", "Conducta biológica", "Conductas previas"], width=180, fg_color="white", text_color="black")
        self.combo_inc_cat.pack(side="left", padx=5)
        
        self.entry_inc_desc = ctk.CTkEntry(add_inc_frame, placeholder_text="Observación...", fg_color="white", text_color="black")
        self.entry_inc_desc.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(add_inc_frame, text="+", width=40, fg_color="#3498db", command=self._add_inclination_ui).pack(side="left", padx=5)
        
        self.inclinations_container = ctk.CTkFrame(card_b, fg_color="white", height=5)
        self.inclinations_container.pack(fill="x", padx=15, pady=(5, 15))

        # ---------------------------------------------------------
        # C. ACTORES
        # ---------------------------------------------------------
        self._section_header("C. Actores (Los Otros)")
        
        add_act_frame = ctk.CTkFrame(self.scroll, fg_color="#f0f0f0", corner_radius=6)
        add_act_frame.pack(fill="x", padx=10, pady=5)
        
        self.entry_act_name = ctk.CTkEntry(add_act_frame, placeholder_text="Nombre", width=120, fg_color="white", text_color="black")
        self.entry_act_name.pack(side="left", padx=5, pady=5)
        
        roles = ["Auspiciador", "Regulador de inclinación", "Moderador de la contingencia", "Mediado", "Regulador de la tendencia"]
        self.combo_act_role = ctk.CTkComboBox(add_act_frame, values=roles, width=180, fg_color="white", text_color="black")
        self.combo_act_role.pack(side="left", padx=5)
        
        self.entry_act_resp = ctk.CTkEntry(add_act_frame, placeholder_text="¿Qué hizo/dijo?", fg_color="white", text_color="black")
        self.entry_act_resp.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(add_act_frame, text="+", width=40, fg_color="#3498db", command=self._add_actor_ui).pack(side="left", padx=5)
        
        self.actors_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.actors_container.pack(fill="x", padx=10)

        # ---------------------------------------------------------
        # D. EFECTOS
        # ---------------------------------------------------------
        self._section_header("D. Efectos")
        
        add_eff_frame = ctk.CTkFrame(self.scroll, fg_color="#f0f0f0", corner_radius=6)
        add_eff_frame.pack(fill="x", padx=10, pady=5)
        
        self.combo_eff_type = ctk.CTkComboBox(add_eff_frame, values=["Sobre otros", "Sobre si mismo", "Sin efecto"], width=150, fg_color="white", text_color="black")
        self.combo_eff_type.pack(side="left", padx=5, pady=5)
        
        self.entry_eff_desc = ctk.CTkEntry(add_eff_frame, placeholder_text="Observación...", fg_color="white", text_color="black")
        self.entry_eff_desc.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(add_eff_frame, text="+", width=40, fg_color="#3498db", command=self._add_effect_ui).pack(side="left", padx=5)
        
        self.effects_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.effects_container.pack(fill="x", padx=10)

        # ---------------------------------------------------------
        # E. NO PROBLEMÁTICO
        # ---------------------------------------------------------
        self._section_header("E. Ejercicio NO Problemático")
        self.txt_noproblem = self._textarea("¿En qué situaciones NO ocurre el problema?")

    # --- HELPERS UI ---
    def _section_header(self, text):
        ctk.CTkLabel(self.scroll, text=text, font=("Arial", 14, "bold"), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(20, 5))

    def _textarea(self, label):
        if label: ctk.CTkLabel(self.scroll, text=label, font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w", padx=10)
        txt = ctk.CTkTextbox(self.scroll, height=60, fg_color="white", text_color="black", border_width=1, border_color="#ccc")
        txt.pack(fill="x", padx=10, pady=(0, 10))
        return txt

    # --- LÓGICA DE LISTAS (ADD/REMOVE/RENDER) ---
    def _add_inclination_ui(self):
        cat = self.combo_inc_cat.get()
        desc = self.entry_inc_desc.get()
        if not desc: return
        self.inclinations_list.append({'category': cat, 'description': desc})
        self.entry_inc_desc.delete(0, "end")
        self._render_list(self.inclinations_container, self.inclinations_list, 
                          lambda item: f"🔸 {item['category']}: {item['description']}", self._remove_inclination)

    def _remove_inclination(self, idx):
        self.inclinations_list.pop(idx)
        self._render_list(self.inclinations_container, self.inclinations_list, 
                          lambda item: f"🔸 {item['category']}: {item['description']}", self._remove_inclination)

    def _add_actor_ui(self):
        name = self.entry_act_name.get()
        if not name: return
        item = {'name': name, 'role': self.combo_act_role.get(), 'response': self.entry_act_resp.get()}
        self.actors_list.append(item)
        self.entry_act_name.delete(0, "end"); self.entry_act_resp.delete(0, "end")
        self._render_list(self.actors_container, self.actors_list,
                          lambda i: f"👤 {i['name']} ({i['role']}): {i['response']}", self._remove_actor)

    def _remove_actor(self, idx):
        self.actors_list.pop(idx)
        self._render_list(self.actors_container, self.actors_list,
                          lambda i: f"👤 {i['name']} ({i['role']}): {i['response']}", self._remove_actor)

    def _add_effect_ui(self):
        desc = self.entry_eff_desc.get()
        if not desc: return
        self.effects_list.append({'effect_type': self.combo_eff_type.get(), 'description': desc})
        self.entry_eff_desc.delete(0, "end")
        self._render_list(self.effects_container, self.effects_list,
                          lambda i: f"⚡ {i['effect_type']}: {i['description']}", self._remove_effect)

    def _remove_effect(self, idx):
        self.effects_list.pop(idx)
        self._render_list(self.effects_container, self.effects_list,
                          lambda i: f"⚡ {i['effect_type']}: {i['description']}", self._remove_effect)

    def _render_list(self, container, data_list, format_func, delete_func):
        for w in container.winfo_children(): w.destroy()
        for idx, item in enumerate(data_list):
            row = ctk.CTkFrame(container, fg_color="white", corner_radius=6, border_width=1, border_color="#ddd")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=format_func(item), text_color="#333", font=("Arial", 12)).pack(side="left", padx=10, pady=5)
            ctk.CTkButton(row, text="×", width=30, height=20, fg_color="transparent", text_color="red", hover_color="#fee",
                          command=lambda i=idx: delete_func(i)).pack(side="right", padx=5)

    # --- CARGA Y GUARDADO ---
    def _load_micros_list(self):
        micros = self.manager.get_available_micros(self.patient_id)
        self.micro_map = {f"#{m[0]}: {m[1][:40]}...": m[0] for m in micros}
        vals = list(self.micro_map.keys())
        if vals:
            self.combo_micros.configure(values=vals)
            self.combo_micros.set(vals[0])
            self._on_micro_selected(vals[0])
        else:
            self.combo_micros.configure(values=["Nueva"])
            self.combo_micros.set("Nueva")
            self._prepare_new()

    def _on_micro_selected(self, choice):
        mid = self.micro_map.get(choice)
        if mid:
            self.current_micro_id = mid
            data = self.manager.get_full_microcontingency(mid)
            if data: self._fill_form(data)

    def _prepare_new(self):
        self.current_micro_id = None
        self.combo_micros.set("--- Nueva ---")
        self._clear_form()

    def _clear_form(self):
        self.combo_morph_type.set("Hacer"); self.combo_morph_class.set("Efectiva")
        self.entry_metrics.delete(0, "end"); self.txt_problem.delete("1.0", "end")
        
        self.combo_social_type.set("Familia")
        self.txt_social_desc.delete(0, "end") # Cambio a Entry
        self.txt_physical.delete("1.0", "end")
        
        self.entry_expected.delete(0, "end")
        self.entry_competence.delete(0, "end")
        
        self.actors_list = []; self.inclinations_list = []; self.effects_list = []
        self.txt_noproblem.delete("1.0", "end")
        
        self._render_list(self.inclinations_container, [], None, None)
        self._render_list(self.actors_container, [], None, None)
        self._render_list(self.effects_container, [], None, None)

    def _fill_form(self, data):
        self._clear_form()
        self.combo_morph_type.set(data.get('morphology_type', 'Hacer'))
        self.combo_morph_class.set(data.get('morphology_class', 'Efectiva'))
        self.entry_metrics.insert(0, data.get('morphology_metrics', ''))
        self.txt_problem.insert("0.0", data.get('problem_desc', ''))
        
        self.combo_social_type.set(data.get('social_type', 'Familia'))
        self.txt_social_desc.insert(0, data.get('social_context', '')) # Cambio a Entry
        self.txt_physical.insert("0.0", data.get('physical_context', ''))
        
        self.entry_expected.insert(0, data.get('expected_behaviors', ''))
        self.entry_competence.insert(0, data.get('social_competence', ''))
        
        self.txt_noproblem.insert("0.0", data.get('non_problematic_desc', ''))

        self.actors_list = data.get('actors', [])
        self._render_list(self.actors_container, self.actors_list,
                          lambda i: f"👤 {i['name']} ({i['role']}): {i['response']}", self._remove_actor)

        self.inclinations_list = data.get('inclinations', [])
        self._render_list(self.inclinations_container, self.inclinations_list, 
                          lambda item: f"🔸 {item['category']}: {item['description']}", self._remove_inclination)

        self.effects_list = data.get('effects', [])
        self._render_list(self.effects_container, self.effects_list,
                          lambda i: f"⚡ {i['effect_type']}: {i['description']}", self._remove_effect)

    def _save_data(self):
        data = {
            'morphology_type': self.combo_morph_type.get(),
            'morphology_class': self.combo_morph_class.get(),
            'morphology_metrics': self.entry_metrics.get(),
            'problem_desc': self.txt_problem.get("1.0", "end-1c"),
            'social_type': self.combo_social_type.get(),
            'social_context': self.txt_social_desc.get(), # Cambio a Entry
            'physical_context': self.txt_physical.get("1.0", "end-1c"),
            'expected_behaviors': self.entry_expected.get(),
            'social_competence': self.entry_competence.get(),
            'non_problematic_desc': self.txt_noproblem.get("1.0", "end-1c"),
            'actors': self.actors_list,
            'inclinations': self.inclinations_list,
            'effects': self.effects_list
        }
        
        if not data['problem_desc']:
            messagebox.showwarning("Atención", "La descripción del problema es obligatoria.")
            return

        if self.current_micro_id:
            s, m = self.manager.update_micro(self.current_micro_id, data)
        else:
            s, m = self.manager.create_micro(self.patient_id, data)
        
        if s: 
            messagebox.showinfo("Éxito", m)
            self._load_micros_list()
        else: 
            messagebox.showerror("Error", m)