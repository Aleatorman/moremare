import customtkinter as ctk
from tkinter import messagebox
from src.clinical.micro.micro_manager import MicroManager

class MicroPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = MicroManager()
        
        # Estado actual
        self.current_micro_id = None
        self.actors_list = [] # Memoria temporal de actores para la UI

        self._setup_ui()
        self._load_micros_list()

    def _setup_ui(self):
        # Header del Módulo
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(header, text="2. Análisis Microcontingencial", font=("Arial", 22, "bold"), text_color="#333").pack(side="left")

        # --- PANEL SUPERIOR: SELECCIÓN Y CREACIÓN ---
        controls = ctk.CTkFrame(self, fg_color="#EBEBEB", corner_radius=8)
        controls.pack(fill="x", pady=10, ipady=5)

        ctk.CTkLabel(controls, text="Seleccionar Situación:", font=("Arial", 12, "bold"), text_color="#555").pack(side="left", padx=15)
        
        self.combo_micros = ctk.CTkComboBox(controls, width=350, command=self._on_micro_selected, 
                                            fg_color="white", text_color="black", dropdown_fg_color="white", dropdown_text_color="black")
        self.combo_micros.pack(side="left", padx=10)

        # Botones de Acción
        self.btn_new = ctk.CTkButton(controls, text="+ Nueva", width=80, fg_color="#3498db", command=self._prepare_new)
        self.btn_new.pack(side="left", padx=10)
        
        self.btn_save = ctk.CTkButton(controls, text="💾 GUARDAR CAMBIOS", width=120, fg_color="#27ae60", command=self._save_data)
        self.btn_save.pack(side="right", padx=15)

        # --- ÁREA DE TRABAJO (FORMULARIO CON SCROLL) ---
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        # 1. MORFOLOGÍA
        self._section_header("A. Morfología de la Conducta")
        f1 = ctk.CTkFrame(self.scroll, fg_color="transparent")
        f1.pack(fill="x", padx=10)
        
        self.combo_morph = ctk.CTkComboBox(f1, values=["Hacer", "Decir", "Pensar/Sentir"], width=150, fg_color="white", text_color="black")
        self.combo_morph.pack(side="left", padx=(0, 10))
        
        self.entry_metrics = ctk.CTkEntry(f1, placeholder_text="Métricas (Duración, Frecuencia, Intensidad...)", width=400, fg_color="white", text_color="black")
        self.entry_metrics.pack(side="left", fill="x", expand=True)

        self.txt_problem = self._textarea("Descripción detallada de la conducta problema:")

        # 2. CONTEXTO
        self._section_header("B. Contexto Situacional")
        self.txt_social = self._textarea("Contexto Social (¿Quiénes estaban?):")
        self.txt_physical = self._textarea("Contexto Físico (Lugar, objetos, ambiente):")
        self.txt_dispo = self._textarea("Disposiciones (Historia/Gustos/Estados):")

        # 3. ACTORES (AQUÍ ESTÁ EL CAMBIO VISUAL)
        self._section_header("C. Actores (Los Otros)")
        
        # Formulario pequeño para agregar
        add_frame = ctk.CTkFrame(self.scroll, fg_color="#f0f0f0", corner_radius=6)
        add_frame.pack(fill="x", padx=10, pady=5)
        
        self.entry_act_name = ctk.CTkEntry(add_frame, placeholder_text="Nombre", width=150, fg_color="white", text_color="black")
        self.entry_act_name.pack(side="left", padx=5, pady=5)
        
        self.combo_act_role = ctk.CTkComboBox(add_frame, values=["Mediador", "Dispensador", "Facilitador", "Instigador"], width=120, fg_color="white", text_color="black")
        self.combo_act_role.pack(side="left", padx=5)
        
        self.entry_act_resp = ctk.CTkEntry(add_frame, placeholder_text="¿Qué hizo/dijo?", width=300, fg_color="white", text_color="black")
        self.entry_act_resp.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(add_frame, text="+", width=40, fg_color="#3498db", command=self._add_actor_ui).pack(side="left", padx=5)

        # Contenedor de la lista de actores
        self.actors_container = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.actors_container.pack(fill="x", padx=10, pady=5)

        # 4. CONSECUENCIAS
        self._section_header("D. Consecuencias")
        self.combo_conseq = ctk.CTkComboBox(self.scroll, values=["Refuerzo Positivo", "Refuerzo Negativo", "Castigo", "Extinción"], width=200, fg_color="white", text_color="black")
        self.combo_conseq.pack(anchor="w", padx=10, pady=5)
        self.txt_conseq_desc = self._textarea("Descripción de la consecuencia:")

        # 5. NO PROBLEMÁTICO
        self._section_header("E. Ejercicio NO Problemático")
        self.txt_noproblem = self._textarea("¿En qué situaciones NO ocurre el problema?")


    # --- HELPERS UI ---
    def _section_header(self, text):
        ctk.CTkLabel(self.scroll, text=text, font=("Arial", 14, "bold"), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(20, 5))

    def _textarea(self, label):
        if label:
            ctk.CTkLabel(self.scroll, text=label, font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w", padx=10)
        txt = ctk.CTkTextbox(self.scroll, height=60, fg_color="white", text_color="black", border_width=1, border_color="#ccc")
        txt.pack(fill="x", padx=10, pady=(0, 10))
        return txt

    # --- LÓGICA DE ACTORES VISUAL ---
    def _add_actor_ui(self):
        name = self.entry_act_name.get()
        role = self.combo_act_role.get()
        resp = self.entry_act_resp.get()
        
        if not name: return

        # Agregar a memoria
        self.actors_list.append({'name': name, 'role': role, 'response': resp})
        
        # Limpiar inputs
        self.entry_act_name.delete(0, "end")
        self.entry_act_resp.delete(0, "end")
        
        # Refrescar vista
        self._render_actors_list()

    def _render_actors_list(self):
        # Limpiar contenedor visual
        for widget in self.actors_container.winfo_children():
            widget.destroy()

        for idx, actor in enumerate(self.actors_list):
            # --- AQUÍ ESTABA EL PROBLEMA: CAMBIAMOS EL COLOR A BLANCO ---
            row = ctk.CTkFrame(self.actors_container, fg_color="white", corner_radius=6, border_width=1, border_color="#ddd")
            row.pack(fill="x", pady=2)
            
            # Texto oscuro para que se lea en fondo blanco
            info = f"👤 {actor['name']} ({actor['role']}): {actor['response']}"
            ctk.CTkLabel(row, text=info, text_color="#333", font=("Arial", 12)).pack(side="left", padx=10, pady=5)
            
            # Botón eliminar sutil
            ctk.CTkButton(row, text="×", width=30, height=20, fg_color="transparent", text_color="#e74c3c", hover_color="#fce4ec",
                          command=lambda i=idx: self._remove_actor(i)).pack(side="right", padx=5)

    def _remove_actor(self, index):
        self.actors_list.pop(index)
        self._render_actors_list()

    # --- LÓGICA DE DATOS ---
    def _load_micros_list(self):
        micros = self.manager.get_available_micros(self.patient_id)
        
        self.micro_map = {}
        values = []
        if micros:
            for m in micros:
                display = f"#{m[0]}: {m[1][:40]}..."
                self.micro_map[display] = m[0]
                values.append(display)
            self.combo_micros.configure(values=values)
            self.combo_micros.set(values[0])
            self._on_micro_selected(values[0])
        else:
            self.combo_micros.configure(values=["Nueva Microcontingencia"])
            self.combo_micros.set("Nueva Microcontingencia")
            self._prepare_new()

    def _on_micro_selected(self, choice):
        micro_id = self.micro_map.get(choice)
        if not micro_id: return
        
        self.current_micro_id = micro_id
        data = self.manager.get_full_microcontingency(micro_id)
        
        if data:
            self._fill_form(data)
        
    def _prepare_new(self):
        self.current_micro_id = None
        self.combo_micros.set("--- Creando Nueva ---")
        self._clear_form()

    def _clear_form(self):
        self.combo_morph.set("Hacer")
        self.entry_metrics.delete(0, "end")
        self.txt_problem.delete("1.0", "end")
        self.txt_social.delete("1.0", "end")
        self.txt_physical.delete("1.0", "end")
        self.txt_dispo.delete("1.0", "end")
        self.combo_conseq.set("Refuerzo Positivo")
        self.txt_conseq_desc.delete("1.0", "end")
        self.txt_noproblem.delete("1.0", "end")
        self.actors_list = []
        self._render_actors_list()

    def _fill_form(self, data):
        self._clear_form()
        self.combo_morph.set(data.get('morphology_type', 'Hacer'))
        self.entry_metrics.insert(0, data.get('morphology_metrics', ''))
        self.txt_problem.insert("0.0", data.get('problem_desc', ''))
        self.txt_social.insert("0.0", data.get('social_context', ''))
        self.txt_physical.insert("0.0", data.get('physical_context', ''))
        self.txt_dispo.insert("0.0", data.get('dispositions', ''))
        self.combo_conseq.set(data.get('consequence_type', 'Refuerzo Positivo'))
        self.txt_conseq_desc.insert("0.0", data.get('consequence_desc', ''))
        self.txt_noproblem.insert("0.0", data.get('non_problematic_desc', ''))
        
        self.actors_list = data.get('actors', [])
        self._render_actors_list()

    def _save_data(self):
        data = {
            'morphology_type': self.combo_morph.get(),
            'morphology_metrics': self.entry_metrics.get(),
            'problem_desc': self.txt_problem.get("1.0", "end-1c"),
            'social_context': self.txt_social.get("1.0", "end-1c"),
            'physical_context': self.txt_physical.get("1.0", "end-1c"),
            'dispositions': self.txt_dispo.get("1.0", "end-1c"),
            'consequence_type': self.combo_conseq.get(),
            'consequence_desc': self.txt_conseq_desc.get("1.0", "end-1c"),
            'non_problematic_desc': self.txt_noproblem.get("1.0", "end-1c"),
            'actors': self.actors_list
        }

        if not data['problem_desc']:
            messagebox.showwarning("Faltan datos", "Describe el problema principal.")
            return

        if self.current_micro_id:
            success, msg = self.manager.update_micro(self.current_micro_id, data)
        else:
            success, msg = self.manager.create_micro(self.patient_id, data)
        
        if success:
            messagebox.showinfo("Guardado", msg)
            self._load_micros_list() # Refrescar lista
        else:
            messagebox.showerror("Error", msg)