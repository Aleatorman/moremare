import customtkinter as ctk
from tkinter import messagebox, ttk
from src.clinical.intervention.intervention_manager import InterventionManager
import datetime

class InterventionGuideWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Guía Clínica: Intervención y Desprofesionalización")
        self.geometry("850x650")
        self.transient(parent)
        self.grab_set()
        self._setup_ui()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="📖 Asistente Clínico: Planeación de la Intervención", font=("Roboto", 18, "bold"), text_color="#2980b9").pack(pady=15)
        
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(scroll, text="FASE 1: Desprofesionalización (Toma de Decisiones)", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(10,5))
        f1_text = ("El usuario debe elegir la solución, evaluando con el psicólogo:\n"
                   "• Motivación: ¿Qué tanto desea realmente implementar esta opción?\n"
                   "• Costo Emocional: ¿Qué le implicará afectivamente dar ese paso?\n"
                   "• Recursos: ¿Tiene el tiempo, dinero, o red de apoyo para hacerlo?\n"
                   "• Efectos: ¿Qué pasará a corto y largo plazo si toma esa ruta?")
        ctk.CTkLabel(scroll, text=f1_text, justify="left", text_color="#2c3e50").pack(anchor="w", padx=15)

        ctk.CTkLabel(scroll, text="FASE 2: Naturaleza de la Interacción (Estrategias)", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(20,5))
        f2_text = ("NO programes técnicas basadas en adjetivos (ej. 'técnica para la depresión'). Selecciona la estrategia según la carencia funcional:\n\n"
                   "1. Adquisición: El usuario NO SABE cómo hacer algo. Hay que enseñarle una conducta desde cero.\n"
                   "2. Precisión: El usuario sabe hacerlo, pero lo hace MAL (ej. habla muy bajito, o en un tono inadecuado).\n"
                   "3. Oportunidad: El usuario sabe hacerlo, pero lo hace EN EL MOMENTO INCORRECTO (ej. reclama algo justo cuando la otra persona está furiosa).\n"
                   "4. Tendencia: La conducta ocurre, pero MUY POCO o DEMASIADO (alterar probabilidades).\n"
                   "5. Relación de Efecto: Hay que alterar qué pasa DESPUÉS de la conducta (consecuencias).")
        ctk.CTkLabel(scroll, text=f2_text, justify="left", text_color="#2c3e50", wraplength=750).pack(anchor="w", padx=15)

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
        
        ctk.CTkButton(header, text="📖 ABRIR GUÍA CLÍNICA", fg_color="#f39c12", text_color="white", 
                      command=self._open_guide).pack(side="right", padx=10)

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
        self.tab_biblioteca = self.tabview.add("📚 Biblioteca de Técnicas") 
        
        self._build_deprofessionalization_tab()
        self._build_strategies_tab()
        self._build_library_tab() 

        self.btn_save = ctk.CTkButton(self, text="💾 GUARDAR PLAN COMPLETO", height=45, 
                                      command=self._save_data, font=("Roboto", 14, "bold"))
        self.btn_save.pack(fill="x", pady=15, padx=5)

    def _open_guide(self):
        InterventionGuideWindow(self)

    def _build_library_tab(self):
        frame = ctk.CTkFrame(self.tab_biblioteca, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        warning_txt = ("⚠️ AVISO METODOLÓGICO: Selecciona y justifica la técnica según el Rubro Funcional "
                       "(la función que cumple en la contingencia) para evitar un eclecticismo inválido.")
        ctk.CTkLabel(frame, text=warning_txt, text_color="#d35400", font=("Roboto", 11, "italic"), 
                     wraplength=750, justify="left").pack(fill="x", pady=(0, 10))

        filter_frame = ctk.CTkFrame(frame, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(filter_frame, text="Enfoque:").pack(side="left", padx=5)
        self.combo_filter = ctk.CTkComboBox(filter_frame, width=140, values=["Todas", "Cognitivo-Conductual", "ABA", "Contextual/ACT", "Regulación Emocional", "Mindfulness", "Exposición", "Habilidades", "Auto-Manejo", "Estímulos", "Motivación", "Mantenimiento", "Compasión"],
                                            command=lambda _: self._refresh_library_table())
        self.combo_filter.set("Todas")
        self.combo_filter.pack(side="left", padx=5)
        
        ctk.CTkLabel(filter_frame, text="Rubro Funcional:").pack(side="left", padx=(15, 5))
        self.combo_rubro = ctk.CTkComboBox(filter_frame, width=250, values=["Todos los rubros", "Alterar disposiciones", "Alterar conducta propia", "Alterar conducta de otros", "Alterar prácticas macrocontingenciales", "Sin asignar"],
                                            command=lambda _: self._refresh_library_table())
        self.combo_rubro.set("Todos los rubros")
        self.combo_rubro.pack(side="left", padx=5)

        ctk.CTkButton(filter_frame, text="+ Añadir Nueva Técnica", fg_color="#27ae60", hover_color="#2ecc71", 
                      command=self._open_add_technique_modal).pack(side="right", padx=15)

        style = ttk.Style()
        style.configure("Treeview", rowheight=30)
        
        self.tree = ttk.Treeview(frame, columns=("Nombre", "Rubro", "Objetivo"), show="headings")
        self.tree.heading("Nombre", text="Nombre de la Técnica")
        self.tree.heading("Rubro", text="Rubro Funcional")
        self.tree.heading("Objetivo", text="Objetivo Clínico")
        self.tree.column("Nombre", width=180)
        self.tree.column("Rubro", width=220)
        self.tree.column("Objetivo", width=350)
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_technique_double_click)
        self._refresh_library_table()

    def _refresh_library_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        category = self.combo_filter.get()
        rubro = self.combo_rubro.get()
        techniques = self.manager.get_all_techniques(category, rubro)
        for t in techniques:
            self.tree.insert("", "end", values=(t['name'], t.get('rubro_funcional', 'Sin asignar'), t['objective']), tags=(t['method'],))

    def _on_technique_double_click(self, event):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected[0])
        name, rubro, obj = item['values'][0], item['values'][1], item['values'][2]
        method = item['tags'][0]
        detail = f"TÉCNICA: {name}\nRUBRO: {rubro}\n\nOBJETIVO: {obj}\n\nMÉTODO: {method}\n\n¿Desea agregar el nombre de esta técnica a su plan actual?"
        if messagebox.askyesno("Detalles de Técnica", detail):
            current_text = self.txt_techs.get("1.0", "end-1c")
            new_text = f"{current_text}\n- {name} ({rubro})" if current_text.strip() else f"- {name} ({rubro})"
            self.txt_techs.delete("1.0", "end")
            self.txt_techs.insert("0.0", new_text)
            self.tabview.set("Fase 2: Estrategias Funcionales")

    def _build_deprofessionalization_tab(self):
        top_bar = ctk.CTkFrame(self.tab_deprof, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(top_bar, text="Analice con el usuario los costos y beneficios de cada opción.", font=("Roboto", 12, "italic"), text_color="#7f8c8d").pack(side="left")
        ctk.CTkButton(top_bar, text="📄 Redactar Contrato Terapéutico", fg_color="#3498db", command=self._generate_contract).pack(side="right")

        scroll = ctk.CTkScrollableFrame(self.tab_deprof, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
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
            self.deprof_entries[option] = {'selected': var_selected, 'motivation': txt_mot, 'cost': txt_cost, 'resources': txt_res, 'effects': txt_eff}

    def _generate_contract(self):
        selected_options = []
        for opt, w in self.deprof_entries.items():
            if w['selected'].get() == 1:
                selected_options.append({
                    'name': opt,
                    'resources': w['resources'].get(),
                    'cost': w['cost'].get()
                })
                
        if not selected_options:
            messagebox.showwarning("Atención", "Por favor, marque al menos una opción de solución con la casilla de verificación para generar el contrato.")
            return

        date_str = datetime.date.today().strftime("%d de %B de %Y")
        
        contract_text = f"CONTRATO TERAPÉUTICO Y ACUERDO DE DESPROFESIONALIZACIÓN\n"
        contract_text += f"{'='*60}\n"
        contract_text += f"Fecha: {date_str}\n\n"
        contract_text += "Como parte del proceso de Análisis Contingencial, el usuario y el terapeuta acuerdan mutuamente llevar a cabo las siguientes rutas de solución para resolver la problemática planteada:\n\n"
        
        for i, opt in enumerate(selected_options):
            contract_text += f"SOLUCIÓN {i+1}: {opt['name']}\n"
            if opt['resources']:
                contract_text += f"- Recursos comprometidos: {opt['resources']}\n"
            if opt['cost']:
                contract_text += f"- Manejo de implicaciones: Se reconoce que este paso implicará: {opt['cost']}\n"
            contract_text += "\n"
            
        contract_text += "ACUERDOS DE RESPONSABILIDAD COMPARTIDA:\n"
        contract_text += "1. El USUARIO se compromete a implementar activamente las estrategias acordadas en su vida diaria, utilizando los recursos mencionados.\n"
        contract_text += "2. EL TERAPEUTA asume un rol de facilitador metodológico, dotando al usuario de las competencias necesarias, con el fin último de que el usuario logre autonomía e independencia del servicio psicológico.\n\n"
        
        contract_text += f"{'-'*25}                  {'-'*25}\n"
        contract_text += f"    Firma del Usuario                       Firma del Terapeuta\n"

        win = ctk.CTkToplevel(self)
        win.title("Contrato Terapéutico")
        win.geometry("700x600")
        win.grab_set()
        
        ctk.CTkLabel(win, text="Contrato Generado (Puedes copiar o imprimir este texto)", font=("Roboto", 14, "bold")).pack(pady=10)
        txt = ctk.CTkTextbox(win, font=("Consolas", 12), fg_color="#fcfcfc", text_color="black")
        txt.pack(fill="both", expand=True, padx=20, pady=10)
        txt.insert("0.0", contract_text)

    def _build_strategies_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_estrategias, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        ctk.CTkLabel(scroll, text="Objetivos Terapéuticos (Ajuste Funcional):", font=("Roboto", 12, "bold")).pack(anchor="w", pady=(10,0))
        self.txt_objs = ctk.CTkTextbox(scroll, height=60); self.txt_objs.pack(fill="x", pady=5)
        ctk.CTkLabel(scroll, text="Estrategias de Intervención (Dimensiones de la Interacción):", 
                     font=("Roboto", 14, "bold"), text_color="#27ae60").pack(anchor="w", pady=(20, 5))
        grid = ctk.CTkFrame(scroll, fg_color="transparent")
        grid.pack(fill="x"); grid.grid_columnconfigure((0, 1), weight=1)
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

    def _open_add_technique_modal(self):
        win = ctk.CTkToplevel(self)
        win.title("Añadir Nueva Técnica")
        win.geometry("550x700")
        win.grab_set()

        scroll = ctk.CTkScrollableFrame(win, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="Registrar Nueva Técnica", font=("Roboto", 18, "bold")).pack(pady=(0,15))

        entries = {}
        
        ctk.CTkLabel(scroll, text="Categoría (Enfoque Teórico):", anchor="w").pack(fill="x")
        entries['category'] = ctk.CTkComboBox(scroll, values=["Cognitivo-Conductual", "ABA", "Contextual/ACT", "Regulación Emocional", "Mindfulness", "Exposición", "Habilidades", "Auto-Manejo", "Estímulos", "Motivación", "Mantenimiento", "Compasión", "Otra"])
        entries['category'].pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(scroll, text="Rubro Funcional (Función en la contingencia):", anchor="w", text_color="#16a085", font=("Roboto", 12, "bold")).pack(fill="x")
        entries['rubro_funcional'] = ctk.CTkComboBox(scroll, values=["Alterar disposiciones", "Alterar conducta propia", "Alterar conducta de otros", "Alterar prácticas macrocontingenciales", "Sin asignar"])
        entries['rubro_funcional'].pack(fill="x", pady=(0, 10))

        fields = [("Nombre de la Técnica:", "name"), ("Objetivo Clínico (¿Para qué sirve?):", "objective"), 
                  ("Método (Instrucciones breves):", "method"), ("Pros / Ventajas:", "pros"), ("Cons / Desventajas:", "cons")]
        
        for label_text, key in fields:
            ctk.CTkLabel(scroll, text=label_text, anchor="w", font=("Roboto", 12, "bold")).pack(fill="x", pady=(5,2))
            entries[key] = ctk.CTkEntry(scroll)
            entries[key].pack(fill="x", pady=(0, 10))

        def save():
            data = {k: v.get() for k, v in entries.items()}
            if not data['name'] or not data['objective']:
                messagebox.showwarning("Atención", "El nombre y el objetivo son obligatorios.")
                return
            
            s, m = self.manager.add_technique(data)
            if s:
                messagebox.showinfo("Éxito", m)
                self._refresh_library_table()
                win.destroy()
            else:
                messagebox.showerror("Error", m)

        ctk.CTkButton(scroll, text="💾 GUARDAR TÉCNICA", fg_color="#27ae60", command=save, height=45, font=("Roboto", 14, "bold")).pack(pady=20, fill="x")