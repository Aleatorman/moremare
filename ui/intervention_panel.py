import customtkinter as ctk
from tkinter import messagebox, ttk
from src.clinical.intervention.intervention_manager import InterventionManager

class InterventionPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = InterventionManager()
        
        self.micro_map = {}
        self.current_micro_id = None
        
        self.solution_options = [
            "1. Alterar prácticas macrocontingenciales",
            "2. Desligar de prácticas macrocontingenciales",
            "3. Mantenimiento del comportamiento del usuario en la micro",
            "4. Cambio del comportamiento de los otros",
            "5. Cambio del comportamiento del propio usuario",
            "6. Inserción en nuevas microcontingencias",
            "7. Uso de conductas funcionales disponibles"
        ]
        
        self.deprof_entries = {}

        self._setup_ui()
        self._load_micros()

    def _setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header, text="5. Intervención y Desprofesionalización", font=("Roboto", 22, "bold")).pack(side="left")

        self.selector_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"), corner_radius=10)
        self.selector_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(self.selector_frame, text="Plan para Microcontingencia:", font=("Roboto", 12, "bold")).pack(side="left", padx=15, pady=15)
        self.combo_micros = ctk.CTkComboBox(self.selector_frame, width=350, command=self._on_micro_selected)
        self.combo_micros.pack(side="left", padx=10)

        self.status_indicator = ctk.CTkLabel(self.selector_frame, text="⚪ Pendiente", font=("Roboto", 12, "bold"), text_color="gray")
        self.status_indicator.pack(side="left", padx=20)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tab_deprof = self.tabview.add("Fase 1: Desprofesionalización")
        self.tab_estrategias = self.tabview.add("Fase 2: Estrategias Funcionales")
        self.tab_biblioteca = self.tabview.add("📚 Biblioteca de Técnicas") # Nueva pestaña
        
        self._build_deprofessionalization_tab()
        self._build_strategies_tab()
        self._build_library_tab() # Constructor de la nueva pestaña

        self.btn_save = ctk.CTkButton(self, text="💾 GUARDAR PLAN COMPLETO", height=45, 
                                      command=self._save_data, font=("Roboto", 14, "bold"))
        self.btn_save.pack(fill="x", pady=15, padx=5)

    def _build_library_tab(self):
        """Pestaña de consulta para seleccionar técnicas basadas en el catálogo de la BD"""
        frame = ctk.CTkFrame(self.tab_biblioteca, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Filtro por categoría clínica (Punto 1 conservado)
        filter_frame = ctk.CTkFrame(frame, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(filter_frame, text="Filtrar por Enfoque:").pack(side="left", padx=5)
        self.combo_filter = ctk.CTkComboBox(filter_frame, values=["Todas", "Cognitivo-Conductual", "ABA", "Contextual/ACT", "Regulación Emocional", "Mindfulness"],
                                            command=lambda _: self._refresh_library_table())
        self.combo_filter.set("Todas")
        self.combo_filter.pack(side="left", padx=5)

        # Tabla de técnicas (Uso de Treeview para visualización clara)
        style = ttk.Style()
        style.configure("Treeview", rowheight=30)
        
        self.tree = ttk.Treeview(frame, columns=("Nombre", "Objetivo"), show="headings")
        self.tree.heading("Nombre", text="Nombre de la Técnica")
        self.tree.heading("Objetivo", text="Objetivo Clínico")
        self.tree.column("Nombre", width=200)
        self.tree.column("Objetivo", width=450)
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_technique_double_click)
        self._refresh_library_table()

    def _refresh_library_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        category = self.combo_filter.get()
        techniques = self.manager.get_all_techniques(category)
        for t in techniques:
            self.tree.insert("", "end", values=(t['name'], t['objective']), tags=(t['method'],))

    def _on_technique_double_click(self, event):
        """Muestra detalles de la técnica y permite copiarla al plan"""
        selected = self.tree.selection()
        if not selected: return
        
        item = self.tree.item(selected[0])
        name = item['values'][0]
        obj = item['values'][1]
        method = item['tags'][0]

        detail = f"TÉCNICA: {name}\n\nOBJETIVO: {obj}\n\nMÉTODO: {method}\n\n¿Desea agregar el nombre de esta técnica a su plan actual?"
        if messagebox.askyesno("Detalles de Técnica", detail):
            current_text = self.txt_techs.get("1.0", "end-1c")
            new_text = f"{current_text}\n- {name}" if current_text.strip() else f"- {name}"
            self.txt_techs.delete("1.0", "end")
            self.txt_techs.insert("0.0", new_text)
            self.tabview.set("Fase 2: Estrategias Funcionales")

    def _build_deprofessionalization_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_deprof, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        ctk.CTkLabel(scroll, text="Analice con el usuario los costos y beneficios de cada opción de la Matriz de Soluciones.", 
                     font=("Roboto", 12, "italic"), text_color="#7f8c8d").pack(pady=10)

        for option in self.solution_options:
            frame = ctk.CTkFrame(scroll, border_width=1)
            frame.pack(fill="x", pady=8, padx=5)
            
            var_selected = ctk.IntVar(value=0)
            cb = ctk.CTkCheckBox(frame, text=option, variable=var_selected, font=("Roboto", 13, "bold"), text_color="#2980b9")
            cb.grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=10)
            
            ctk.CTkLabel(frame, text="Motivación:").grid(row=1, column=0, sticky="w", padx=10)
            txt_mot = ctk.CTkEntry(frame, width=140); txt_mot.grid(row=1, column=1, padx=5, pady=5)
            
            ctk.CTkLabel(frame, text="Costo Emocional:").grid(row=1, column=2, sticky="w", padx=10)
            txt_cost = ctk.CTkEntry(frame, width=140); txt_cost.grid(row=1, column=3, padx=5, pady=5)
            
            ctk.CTkLabel(frame, text="Recursos:").grid(row=2, column=0, sticky="w", padx=10)
            txt_res = ctk.CTkEntry(frame, width=140); txt_res.grid(row=2, column=1, padx=5, pady=5)
            
            ctk.CTkLabel(frame, text="Efectos:").grid(row=2, column=2, sticky="w", padx=10)
            txt_eff = ctk.CTkEntry(frame, width=140); txt_eff.grid(row=2, column=3, padx=5, pady=5)
            
            self.deprof_entries[option] = {
                'selected': var_selected, 'motivation': txt_mot, 'cost': txt_cost, 
                'resources': txt_res, 'effects': txt_eff
            }

    def _build_strategies_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_estrategias, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="Objetivos Terapéuticos (Ajuste Funcional):", font=("Roboto", 12, "bold")).pack(anchor="w", pady=(10,0))
        self.txt_objs = ctk.CTkTextbox(scroll, height=60); self.txt_objs.pack(fill="x", pady=5)

        ctk.CTkLabel(scroll, text="Estrategias de Intervención (Dimensiones de la Interacción):", 
                     font=("Roboto", 14, "bold"), text_color="#27ae60").pack(anchor="w", pady=(20, 5))

        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="x"); grid.grid_columnconfigure((0, 1), weight=1)

        # Parámetros funcionales derivados de Ribes
        self.txt_adq = self._add_param_field(grid, 0, 0, "1. Adquisición de Competencias")
        self.txt_prec = self._add_param_field(grid, 0, 1, "2. Precisión (Ajuste Dinámico)")
        self.txt_opp = self._add_param_field(grid, 1, 0, "3. Oportunidad (Discriminación)")
        self.txt_tend = self._add_param_field(grid, 1, 1, "4. Tendencia (Probabilidad)")
        self.txt_eff = self._add_param_field(grid, 2, 0, "5. Relación de Efecto")

        ctk.CTkLabel(scroll, text="Técnicas Seleccionadas (Doble clic en Biblioteca para agregar):", font=("Roboto", 12, "bold")).pack(anchor="w", pady=(20,0))
        self.txt_techs = ctk.CTkTextbox(scroll, height=80); self.txt_techs.pack(fill="x", pady=5)

    def _add_param_field(self, parent, row, col, label_text):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(frame, text=label_text, font=("Roboto", 11, "bold")).pack(anchor="w", padx=5)
        txt = ctk.CTkTextbox(frame, height=60); txt.pack(fill="both", expand=True, padx=5, pady=5)
        return txt

    def _load_micros(self):
        micros = self.manager.get_available_micros(self.patient_id)
        if not micros:
            self.combo_micros.set("No hay microcontingencias")
            return
        self.micro_map = {f"#{m[0]}: {m[1][:30]}": m[0] for m in micros}
        display_values = list(self.micro_map.keys())
        self.combo_micros.configure(values=display_values)
        self.combo_micros.set(display_values[0])
        self._on_micro_selected(display_values[0])

    def _on_micro_selected(self, choice):
        micro_id = self.micro_map.get(choice)
        if not micro_id: return
        self.current_micro_id = micro_id
        self._clear_form()
        data = self.manager.get_plan_by_micro(micro_id)
        if data:
            self.status_indicator.configure(text="✅ PLAN ACTIVO", text_color="#2ecc71")
            self.txt_objs.insert("0.0", data.get('therapeutic_objectives', ''))
            self.txt_adq.insert("0.0", data.get('strategy_adquisition', ''))
            self.txt_prec.insert("0.0", data.get('strategy_precision', ''))
            self.txt_opp.insert("0.0", data.get('strategy_opportunity', ''))
            self.txt_tend.insert("0.0", data.get('strategy_tendency', ''))
            self.txt_eff.insert("0.0", data.get('strategy_effect', ''))
            self.txt_techs.insert("0.0", data.get('techniques_text', ''))
            deprof_data = data.get('deprofessionalization', [])
            for dep in deprof_data:
                opt = dep['solution_option']
                if opt in self.deprof_entries:
                    w = self.deprof_entries[opt]
                    w['selected'].set(dep['is_selected'])
                    w['motivation'].insert(0, dep['user_motivation'])
                    w['cost'].insert(0, dep['emotional_cost'])
                    w['resources'].insert(0, dep['available_resources'])
                    w['effects'].insert(0, dep['short_long_term_effects'])
        else:
            self.status_indicator.configure(text="⚪ SIN PLAN", text_color="gray")

    def _save_data(self):
        if not self.current_micro_id: return
        plan_data = {
            'objs': self.txt_objs.get("1.0", "end-1c"), 'adq': self.txt_adq.get("1.0", "end-1c"),
            'prec': self.txt_prec.get("1.0", "end-1c"), 'opp': self.txt_opp.get("1.0", "end-1c"),
            'tend': self.txt_tend.get("1.0", "end-1c"), 'eff': self.txt_eff.get("1.0", "end-1c"),
            'techs': self.txt_techs.get("1.0", "end-1c")
        }
        deprof_data = []
        for opt, w in self.deprof_entries.items():
            if w['selected'].get() == 1 or w['motivation'].get():
                deprof_data.append({
                    'option': opt, 'selected': w['selected'].get(), 'motivation': w['motivation'].get(),
                    'cost': w['cost'].get(), 'resources': w['resources'].get(), 'effects': w['effects'].get()
                })
        success, msg = self.manager.save_plan(self.patient_id, self.current_micro_id, plan_data, deprof_data)
        if success:
            messagebox.showinfo("Éxito", msg)
            self._on_micro_selected(self.combo_micros.get())
        else:
            messagebox.showerror("Error", msg)

    def _clear_form(self):
        for w in [self.txt_objs, self.txt_adq, self.txt_prec, self.txt_opp, self.txt_tend, self.txt_eff, self.txt_techs]:
            w.delete("1.0", "end")
        for w in self.deprof_entries.values():
            w['selected'].set(0)
            for f in ['motivation', 'cost', 'resources', 'effects']: w[f].delete(0, "end")