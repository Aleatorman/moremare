import customtkinter as ctk
from tkinter import messagebox
from src.clinical.intervention.intervention_manager import InterventionManager
from src.clinical.micro.micro_manager import MicroManager
from src.clinical.patient_manager import PatientManager

class InterventionPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = InterventionManager()
        self.micro_manager = MicroManager()
        self.patient_manager = PatientManager()
        
        # Variables de los checkboxes
        self.var_s1 = ctk.IntVar()
        self.var_s2 = ctk.IntVar()
        self.var_s3 = ctk.IntVar()
        self.var_s4 = ctk.IntVar()
        self.var_s5 = ctk.IntVar()
        self.var_s6 = ctk.IntVar()
        self.var_s7 = ctk.IntVar()

        self._setup_ui()
        self._load_micros()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="5. Plan de Intervención", font=("Arial", 22, "bold"), text_color="#333").pack(anchor="w", pady=(0, 10))
        
        # --- SISTEMA DE PESTAÑAS (Restaurado) ---
        self.tabview = ctk.CTkTabview(self, width=900, height=600)
        self.tabview.pack(fill="both", expand=True)

        self.tabview.add("Plan de Intervención")
        self.tabview.add("Biblioteca de Técnicas")
        
        # Construir cada pestaña
        self._setup_tab_capture(self.tabview.tab("Plan de Intervención"))
        self._setup_tab_library(self.tabview.tab("Biblioteca de Técnicas"))

    def _setup_tab_capture(self, parent_frame):
        # Selector de Microcontingencia
        top_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        top_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(top_frame, text="Microcontingencia a intervenir:", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        self.combo_micros = ctk.CTkComboBox(top_frame, values=[], width=300, command=self._on_micro_selected)
        self.combo_micros.pack(side="left", padx=10)

        self.scroll = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, pady=10)

        # A. METAS VS OBJETIVOS
        ctk.CTkLabel(self.scroll, text="A. Contraste de Metas y Objetivos", font=("Arial", 14, "bold"), text_color="#2c3e50").pack(anchor="w", pady=(10, 5))
        frame_goals = ctk.CTkFrame(self.scroll, fg_color="#F8F9F9", corner_radius=6, border_width=1, border_color="#D5DBDB")
        frame_goals.pack(fill="x", pady=5, padx=5)
        
        col1 = ctk.CTkFrame(frame_goals, fg_color="transparent")
        col1.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(col1, text="Metas establecidas por el consultante:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.txt_patient_goals = ctk.CTkTextbox(col1, height=80, fg_color="#e8f6f3", text_color="#333")
        self.txt_patient_goals.pack(fill="x", pady=5)
        
        patient_data = self.patient_manager.get_patient_by_id(self.patient_id)
        if patient_data and patient_data.get('goals'):
            self.txt_patient_goals.insert("0.0", patient_data['goals'])
        self.txt_patient_goals.configure(state="disabled") 

        col2 = ctk.CTkFrame(frame_goals, fg_color="transparent")
        col2.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(col2, text="Objetivos terapéuticos (Redacción):", font=("Arial", 12, "bold"), text_color="#d35400").pack(anchor="w")
        self.txt_objectives = ctk.CTkTextbox(col2, height=80)
        self.txt_objectives.pack(fill="x", pady=5)

        # B. ANÁLISIS DE SOLUCIONES
        ctk.CTkLabel(self.scroll, text="B. Análisis de Soluciones", font=("Arial", 14, "bold"), text_color="#2c3e50").pack(anchor="w", pady=(20, 5))
        frame_sols = ctk.CTkFrame(self.scroll, fg_color="#F8F9F9", border_width=1, border_color="#D5DBDB")
        frame_sols.pack(fill="x", pady=5, padx=5)
        
        sol_row1 = ctk.CTkFrame(frame_sols, fg_color="transparent")
        sol_row1.pack(fill="x", padx=10, pady=5)
        ctk.CTkCheckBox(sol_row1, text="Cambio macrocontingencial", variable=self.var_s1).pack(side="left", padx=15)
        ctk.CTkCheckBox(sol_row1, text="Mantenimiento macrocontingencial", variable=self.var_s2).pack(side="left", padx=15)
        ctk.CTkCheckBox(sol_row1, text="Mantenimiento microcontingencial", variable=self.var_s3).pack(side="left", padx=15)

        sol_row2 = ctk.CTkFrame(frame_sols, fg_color="transparent")
        sol_row2.pack(fill="x", padx=10, pady=5)
        ctk.CTkCheckBox(sol_row2, text="Cambiar la conducta de otros", variable=self.var_s4).pack(side="left", padx=15)
        ctk.CTkCheckBox(sol_row2, text="Cambiar la conducta propia", variable=self.var_s5).pack(side="left", padx=15)
        ctk.CTkCheckBox(sol_row2, text="Opción nuevas microcontingencias", variable=self.var_s6).pack(side="left", padx=15)

        sol_row3 = ctk.CTkFrame(frame_sols, fg_color="transparent")
        sol_row3.pack(fill="x", padx=10, pady=(5, 10))
        ctk.CTkCheckBox(sol_row3, text="Opciones funcionales (mismas conductas)", variable=self.var_s7).pack(side="left", padx=15)

        # C. ESTRATEGIAS
        ctk.CTkLabel(self.scroll, text="C. Estrategias de Intervención", font=("Arial", 14, "bold"), text_color="#2c3e50").pack(anchor="w", pady=(20, 5))
        self.txt_morph = self._add_text_area("1. Alteración de la Morfología (¿Qué hará de forma diferente?)")
        self.txt_actors = self._add_text_area("2. Alteración de los Actores (¿Cómo interactuará con los demás?)")
        self.txt_context = self._add_text_area("3. Alteración del Contexto (Social/Físico)")

        # D. TÉCNICAS
        ctk.CTkLabel(self.scroll, text="D. Selección de Técnicas", font=("Arial", 14, "bold"), text_color="#2c3e50").pack(anchor="w", pady=(20, 5))
        ctk.CTkLabel(self.scroll, text="(Puedes buscar y enviar técnicas desde la pestaña 'Biblioteca de Técnicas')", text_color="gray", font=("Arial", 11)).pack(anchor="w", padx=10)
        self.txt_techs = ctk.CTkTextbox(self.scroll, height=80)
        self.txt_techs.pack(fill="x", padx=10, pady=5)

        # BOTÓN GUARDAR
        ctk.CTkButton(self.scroll, text="💾 GUARDAR PLAN DE INTERVENCIÓN", fg_color="#27ae60", font=("Arial", 14, "bold"), height=40, command=self._save_plan).pack(pady=25)

    def _setup_tab_library(self, parent_frame):
        # Filtros de Biblioteca
        filter_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(filter_frame, text="Filtrar por categoría:").pack(side="left", padx=5)

        cats = ["Todas", "Cognitivo-Conductual", "ABA", "Contextual/ACT", "Regulación Emocional", "Exposición", "Habilidades", "Mindfulness", "Auto-Manejo", "Estímulos", "Motivación", "Mantenimiento", "Compasión"]
        self.combo_filter = ctk.CTkComboBox(filter_frame, values=cats, width=200, command=self._load_library)
        self.combo_filter.pack(side="left", padx=10)

        self.library_scroll = ctk.CTkScrollableFrame(parent_frame, fg_color="#F8F9F9", border_width=1, border_color="#ccc")
        self.library_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        self._load_library("Todas")

    def _add_text_area(self, title):
        ctk.CTkLabel(self.scroll, text=title, font=("Arial", 12, "bold"), text_color="#555").pack(anchor="w", padx=10, pady=(10,0))
        txt = ctk.CTkTextbox(self.scroll, height=60, border_width=1, border_color="#ccc")
        txt.pack(fill="x", padx=10, pady=5)
        return txt

    def _load_library(self, category):
        for w in self.library_scroll.winfo_children(): 
            w.destroy()
            
        techs = self.manager.get_all_techniques(category)

        if not techs:
            ctk.CTkLabel(self.library_scroll, text="No hay técnicas cargadas en esta categoría.", text_color="gray").pack(pady=20)
            return

        for t in techs:
            card = ctk.CTkFrame(self.library_scroll, fg_color="white", corner_radius=6, border_width=1, border_color="#ddd")
            card.pack(fill="x", pady=5, padx=5)

            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(header, text=f"📌 {t['name']} ({t['category']})", font=("Arial", 14, "bold"), text_color="#2980b9").pack(side="left")

            ctk.CTkButton(header, text="➕ Enviar al Plan", width=120, height=28, fg_color="#3498db", hover_color="#2980b9",
                          command=lambda name=t['name']: self._add_tech_to_plan(name)).pack(side="right")

            body = ctk.CTkFrame(card, fg_color="transparent")
            body.pack(fill="x", padx=10, pady=(0, 5))

            ctk.CTkLabel(body, text=f"Objetivo: {t['objective']}", font=("Arial", 12, "bold"), text_color="#333", anchor="w").pack(fill="x")
            ctk.CTkLabel(body, text=f"Método: {t['method']}", font=("Arial", 12), text_color="#555", justify="left", wraplength=700, anchor="w").pack(fill="x", pady=3)
            ctk.CTkLabel(body, text=f"👍 Pros: {t['pros']}   |   👎 Contras: {t['cons']}", font=("Arial", 11, "italic"), text_color="#7f8c8d", anchor="w").pack(fill="x", pady=(2,5))

    def _add_tech_to_plan(self, tech_name):
        current_text = self.txt_techs.get("1.0", "end-1c").strip()
        new_text = f"{current_text}, {tech_name}" if current_text else tech_name
        self.txt_techs.delete("1.0", "end")
        self.txt_techs.insert("1.0", new_text)
        
        # Opcional: Cambia a la pestaña del plan para que veas que se agregó
        self.tabview.set("Plan de Intervención")

    # --- Lógica de Carga y Guardado ---

    def _load_micros(self):
        self.micros_data = self.micro_manager.get_available_micros(self.patient_id)
        if self.micros_data:
            self.combo_micros.configure(values=[f"{m[0]} - {m[1]}" for m in self.micros_data])
            self.combo_micros.set(f"{self.micros_data[0][0]} - {self.micros_data[0][1]}")
            self._on_micro_selected(self.combo_micros.get())

    def _on_micro_selected(self, value):
        if not value: return
        self._clear_form()
        micro_id = int(value.split(" - ")[0])
        plan = self.manager.get_plan_by_micro(micro_id)
        if plan:
            self.txt_objectives.insert("0.0", plan['therapeutic_objectives'] or "")
            self.var_s1.set(plan['sol_cambio_macro'])
            self.var_s2.set(plan['sol_mant_macro'])
            self.var_s3.set(plan['sol_mant_micro'])
            self.var_s4.set(plan['sol_cambio_otros'])
            self.var_s5.set(plan['sol_cambio_propia'])
            self.var_s6.set(plan['sol_nuevas_micro'])
            self.var_s7.set(plan['sol_opciones_func'])
            self.txt_morph.insert("0.0", plan['strategy_morphology'] or "")
            self.txt_actors.insert("0.0", plan['strategy_actors'] or "")
            self.txt_context.insert("0.0", plan['strategy_context'] or "")
            self.txt_techs.insert("0.0", plan['techniques_text'] or "")

    def _clear_form(self):
        self.txt_objectives.delete("1.0", "end")
        for var in [self.var_s1, self.var_s2, self.var_s3, self.var_s4, self.var_s5, self.var_s6, self.var_s7]: var.set(0)
        self.txt_morph.delete("1.0", "end")
        self.txt_actors.delete("1.0", "end")
        self.txt_context.delete("1.0", "end")
        self.txt_techs.delete("1.0", "end")

    def _save_plan(self):
        val = self.combo_micros.get()
        if not val: return messagebox.showwarning("Aviso", "Selecciona una microcontingencia.")
        micro_id = int(val.split(" - ")[0])
        
        data = {
            'objs': self.txt_objectives.get("1.0", "end-1c"),
            's1': self.var_s1.get(), 's2': self.var_s2.get(), 's3': self.var_s3.get(),
            's4': self.var_s4.get(), 's5': self.var_s5.get(), 's6': self.var_s6.get(), 's7': self.var_s7.get(),
            'morph': self.txt_morph.get("1.0", "end-1c"),
            'actors': self.txt_actors.get("1.0", "end-1c"),
            'context': self.txt_context.get("1.0", "end-1c"),
            'techs': self.txt_techs.get("1.0", "end-1c")
        }
        success, msg = self.manager.save_plan(self.patient_id, micro_id, data)
        if success: messagebox.showinfo("Éxito", msg)
        else: messagebox.showerror("Error", msg)