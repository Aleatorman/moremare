import customtkinter as ctk
from tkinter import messagebox
from src.clinical.genesis.genesis_manager import GenesisManager

class StylesWindow(ctk.CTkToplevel):
    """Ventana para evaluar los 12 Estilos Interactivos con Panel Guía Dinámico"""
    def __init__(self, parent, current_styles, on_save_callback):
        super().__init__(parent)
        self.title("Evaluación de Estilos Interactivos (Génesis)")
        self.geometry("1100x700") # Ventana más ancha para acomodar los dos paneles
        self.transient(parent)
        self.grab_set()
        
        self.on_save_callback = on_save_callback
        self.current_styles = current_styles
        self.style_entries = {}
        
        self._build_guide_dictionary()
        self._setup_ui()

    def _build_guide_dictionary(self):
        """Diccionario clínico con las instrucciones para cada estilo"""
        self.guides = {
            "Toma de decisiones": (
                "SITUACIÓN GENÉRICA:\nVarias opciones disponibles con consecuencias inciertas.\n\n"
                "¿QUÉ OBSERVAR?\nEl tiempo que tarda en elegir, si delega la elección a otros, o si evade la situación.\n\n"
                "❌ INCORRECTO (Rasgo):\n'Es muy indeciso'.\n\n"
                "✅ CORRECTO (Conducta):\n'Ante decisiones escolares o laborales, delega la responsabilidad a sus padres tras semanas de evitación'."
            ),
            "Tolerancia a la ambigüedad": (
                "SITUACIÓN GENÉRICA:\nEntornos nuevos, poco estructurados o sin instrucciones/reglas claras.\n\n"
                "¿QUÉ OBSERVAR?\nSi se paraliza, si exige reglas obsesivamente, o si ensaya respuestas nuevas.\n\n"
                "❌ INCORRECTO:\n'Es muy ansioso cuando no sabe qué hacer'.\n\n"
                "✅ CORRECTO:\n'Cuando se le asignan tareas abiertas sin pasos explícitos, suspende la actividad y exige que se le dicte exactamente qué hacer'."
            ),
            "Tolerancia a la frustración": (
                "SITUACIÓN GENÉRICA:\nUn reforzador o resultado esperado se retrasa, se retira sin aviso o se bloquea.\n\n"
                "¿QUÉ OBSERVAR?\nReacciones físicas y verbales inmediatas ante el bloqueo y si abandona la meta.\n\n"
                "❌ INCORRECTO:\n'Tiene muy baja tolerancia a la frustración'.\n\n"
                "✅ CORRECTO:\n'Ante la cancelación de planes, tiende a alzar la voz, golpear objetos cercanos y abandonar la actividad el resto del día'."
            ),
            "Logro": (
                "SITUACIÓN GENÉRICA:\nTareas que imponen un criterio de excelencia, competencia o rendimiento.\n\n"
                "¿QUÉ OBSERVAR?\nSi excede el criterio mínimo requerido, o si abandona al primer error.\n\n"
                "❌ INCORRECTO:\n'Es muy perfeccionista'.\n\n"
                "✅ CORRECTO:\n'Ante entregas laborales, invierte horas de sueño extras para sobrepasar las especificaciones pedidas, repitiendo el trabajo ante errores mínimos'."
            ),
            "Flexibilidad al cambio": (
                "SITUACIÓN GENÉRICA:\nCambio repentino de rutinas, reglas o condiciones de vida.\n\n"
                "¿QUÉ OBSERVAR?\nTiempo de adaptación, frecuencia de quejas, intentos de forzar la regla anterior.\n\n"
                "❌ INCORRECTO:\n'Es muy rígido mentalmente'.\n\n"
                "✅ CORRECTO:\n'Al cambiarle de supervisor en el trabajo, pasó tres meses intentando aplicar el formato del jefe anterior, quejándose diariamente'."
            ),
            "Tendencia a la transgresión": (
                "SITUACIÓN GENÉRICA:\nNormas explícitas donde existe una baja probabilidad de ser sancionado u observado.\n\n"
                "¿QUÉ OBSERVAR?\nSi rompe la regla sistemáticamente cuando no hay supervisión.\n\n"
                "❌ INCORRECTO:\n'Es deshonesto o rebelde'.\n\n"
                "✅ CORRECTO:\n'Si percibe que no hay cámaras o jefes cerca, ignora los protocolos de seguridad y omite pasos del proceso'."
            ),
            "Curiosidad": (
                "SITUACIÓN GENÉRICA:\nPresencia de estímulos novedosos pero que son irrelevantes para la tarea actual.\n\n"
                "¿QUÉ OBSERVAR?\nSi interrumpe su comportamiento actual para explorar o manipular lo nuevo.\n\n"
                "❌ INCORRECTO:\n'Se distrae fácilmente'.\n\n"
                "✅ CORRECTO:\n'Interrumpe conversaciones formales sistemáticamente para ir a explorar objetos o sonidos nuevos en la habitación'."
            ),
            "Tendencia al riesgo": (
                "SITUACIÓN GENÉRICA:\nOpciones con alta ganancia potencial pero con alta probabilidad de pérdida, castigo o daño.\n\n"
                "¿QUÉ OBSERVAR?\nSi elige repetidamente la opción arriesgada a pesar del historial de pérdidas.\n\n"
                "❌ INCORRECTO:\n'Es adicto a la adrenalina'.\n\n"
                "✅ CORRECTO:\n'En temas financieros y de pareja, opta por la alternativa de ganancia rápida ignorando las consecuencias legales o emocionales a largo plazo'."
            ),
            "Dependencia de señales": (
                "SITUACIÓN GENÉRICA:\nTareas o interacciones donde faltan instrucciones, pistas directas o retroalimentación inmediata.\n\n"
                "¿QUÉ OBSERVAR?\nSi requiere aprobación constante, validación o pasos dictados para avanzar.\n\n"
                "❌ INCORRECTO:\n'Es muy inseguro'.\n\n"
                "✅ CORRECTO:\n'No avanza en ninguna tarea personal si no recibe confirmación verbal (un \"está bien\") por parte de su pareja en cada paso'."
            ),
            "Responsividad a nuevas contingencias": (
                "SITUACIÓN GENÉRICA:\nLas consecuencias cambian (lo que antes funcionaba para obtener algo, ya no funciona).\n\n"
                "¿QUÉ OBSERVAR?\nSi ajusta rápidamente su conducta a la nueva realidad o persiste inútilmente en la vieja.\n\n"
                "❌ INCORRECTO:\n'Está estancado en el pasado'.\n\n"
                "✅ CORRECTO:\n'A pesar de que el llanto ya no le genera atención por parte de su madre, continúa llorando con mayor intensidad durante horas'."
            ),
            "Impulsividad / No impulsividad": (
                "SITUACIÓN GENÉRICA:\nElección entre una recompensa pequeña inmediata vs. una recompensa grande pero demorada.\n\n"
                "¿QUÉ OBSERVAR?\nSi cede a la opción inmediata sacrificando constantemente los planes a largo plazo.\n\n"
                "❌ INCORRECTO:\n'Tiene poco autocontrol'.\n\n"
                "✅ CORRECTO:\n'Sistemáticamente gasta su dinero en gratificaciones de fin de semana, imposibilitando el ahorro pactado para su colegiatura'."
            ),
            "Reducción de conflicto": (
                "SITUACIÓN GENÉRICA:\nChoque directo entre dos personas, o enfrentamiento a dos demandas incompatibles al mismo tiempo.\n\n"
                "¿QUÉ OBSERVAR?\nSi huye de la situación, si negocia, si ataca verbalmente o si cede inmediatamente.\n\n"
                "❌ INCORRECTO:\n'Es evitativo y sumiso'.\n\n"
                "✅ CORRECTO:\n'Ante discusiones de pareja donde se le confronta, opta por quedarse en silencio, salir de la casa físicamente y no tocar el tema por días'."
            )
        }

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=6) # Panel Izquierdo (Formulario)
        self.grid_columnconfigure(1, weight=4) # Panel Derecho (Guía)
        self.grid_rowconfigure(0, weight=1)

        # ================= PANEL IZQUIERDO =================
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        ctk.CTkLabel(left_frame, text="Evaluación de Estilos Interactivos", font=("Roboto", 20, "bold")).pack(pady=(0, 10))
        
        scroll = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        for style_name in self.guides.keys():
            frame = ctk.CTkFrame(scroll, border_width=1, fg_color=("gray95", "gray15"))
            frame.pack(fill="x", pady=6, padx=5)
            
            ctk.CTkLabel(frame, text=style_name, font=("Roboto", 13, "bold"), text_color="#2980b9", anchor="w").pack(fill="x", padx=10, pady=(5,0))
            
            # Buscamos si ya tiene un valor guardado
            initial_val = ""
            for s in self.current_styles:
                if s['arrangement_type'] == style_name:
                    initial_val = s['response_style']
                    break
            
            entry = ctk.CTkTextbox(frame, height=50)
            entry.insert("0.0", initial_val)
            entry.pack(fill="x", padx=10, pady=5)
            self.style_entries[style_name] = entry
            
            # EL TRUCO: Al hacer clic (FocusIn) en este cuadro, actualizamos el panel derecho
            entry.bind("<FocusIn>", lambda event, name=style_name: self._update_guide_panel(name))

        ctk.CTkButton(left_frame, text="💾 GUARDAR Y CERRAR EVALUACIÓN", command=self._save_and_close, 
                      fg_color="#27ae60", hover_color="#2ecc71", height=45).pack(pady=15, fill="x")

        # ================= PANEL DERECHO (EL ENTRENADOR) =================
        right_frame = ctk.CTkFrame(self, fg_color="#fdfefe", border_color="#f1c40f", border_width=2)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 15), pady=15)
        
        ctk.CTkLabel(right_frame, text="🧠 Entrenador Clínico", font=("Roboto", 18, "bold"), text_color="#d35400").pack(pady=(15, 5))
        ctk.CTkLabel(right_frame, text="Haz clic en un campo para ver la guía", text_color="gray").pack()
        
        self.lbl_guide_title = ctk.CTkLabel(right_frame, text="Selecciona un estilo...", font=("Roboto", 14, "bold"), wraplength=350)
        self.lbl_guide_title.pack(pady=(20, 10), padx=10)
        
        self.txt_guide_content = ctk.CTkTextbox(right_frame, font=("Roboto", 13), fg_color="transparent", text_color="#2c3e50")
        self.txt_guide_content.pack(fill="both", expand=True, padx=15, pady=10)
        self.txt_guide_content.insert("0.0", "Evita usar adjetivos o etiquetas de personalidad.\n\nDescribe físicamente qué hace el paciente y en qué situación concreta lo hace.")
        self.txt_guide_content.configure(state="disabled")

    def _update_guide_panel(self, style_name):
        """Actualiza el texto del panel derecho según el campo seleccionado"""
        self.lbl_guide_title.configure(text=f"Evaluando: {style_name}")
        
        self.txt_guide_content.configure(state="normal")
        self.txt_guide_content.delete("0.0", "end")
        self.txt_guide_content.insert("0.0", self.guides[style_name])
        self.txt_guide_content.configure(state="disabled")

    def _save_and_close(self):
        data = []
        for style_name, entry in self.style_entries.items():
            text_val = entry.get("0.0", "end-1c").strip()
            if text_val: # Solo guardamos los que el terapeuta llenó
                data.append({'arrangement_type': style_name, 'response_style': text_val})
        self.on_save_callback(data)
        self.destroy()


# =========================================================================
# EL PANEL PRINCIPAL DE GÉNESIS
# =========================================================================
class GenesisPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = GenesisManager()
        
        self.micro_map = {}
        self.current_micro_id = None
        self.current_genesis_id = None
        self.interactive_styles = [] 

        self._setup_ui()
        self._load_micros()

    def _setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header, text="4. Génesis del Problema", font=("Roboto", 22, "bold")).pack(side="left")

        # --- SELECTOR DE MICROCONTINGENCIA ---
        self.selector_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"), corner_radius=10)
        self.selector_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(self.selector_frame, text="Análisis para:", font=("Roboto", 12, "bold")).pack(side="left", padx=15, pady=15)
        self.combo_micros = ctk.CTkComboBox(self.selector_frame, width=350, command=self._on_micro_selected)
        self.combo_micros.pack(side="left", padx=10)

        self.status_indicator = ctk.CTkLabel(self.selector_frame, text="⚪ Pendiente", font=("Roboto", 12, "bold"), text_color="gray")
        self.status_indicator.pack(side="left", padx=20)

        # --- ÁREA DE TRABAJO ---
        self.scroll_form = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_form.pack(fill="both", expand=True)

        # SECCIÓN: ESTILOS INTERACTIVOS
        styles_frame = ctk.CTkFrame(self.scroll_form, fg_color="#fcf3cf") # Color crema para destacar
        styles_frame.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(styles_frame, text="Estrategias de Interacción (Génesis Funcional)", 
                     font=("Roboto", 14, "bold"), text_color="#935116").pack(side="left", padx=15, pady=10)
        
        self.btn_styles = ctk.CTkButton(styles_frame, text="📋 ABRIR EVALUADOR DE ESTILOS", 
                                        command=self._open_styles_window, fg_color="#d4ac0d", text_color="black", font=("Roboto", 12, "bold"))
        self.btn_styles.pack(side="right", padx=15, pady=10)

        # SECCIÓN: HISTORIA TRADICIONAL
        self.grid_frame = ctk.CTkFrame(self.scroll_form, fg_color="transparent")
        self.grid_frame.pack(fill="x", expand=True)
        self.grid_frame.grid_columnconfigure((0,1,2), weight=1)

        col1 = ctk.CTkFrame(self.grid_frame); col1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self._create_header(col1, "A. Historia de la\nMicrocontingencia")
        self.txt_circunstancia = self._add_field(col1, "Circunstancia de inicio:")
        self.txt_situacion = self._add_field(col1, "Situación de inicio:")
        self.txt_disp_pasado = self._add_field(col1, "Disposiciones pasadas:")

        col2 = ctk.CTkFrame(self.grid_frame); col2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self._create_header(col2, "B. Funcionalidad en\nOtros Contextos")
        self.txt_func_no_prob = self._add_field(col2, "Función en contextos NO problemáticos:")
        self.txt_efect_no_prob = self._add_field(col2, "Efectividad/Efectos:")

        col3 = ctk.CTkFrame(self.grid_frame); col3.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        self._create_header(col3, "C. Disponibilidad de\nRecursos / Conductas")
        self.txt_micro_no_prob = self._add_field(col3, "Microcontingencias NO problemáticas:")
        self.txt_resp_adecuadas = self._add_field(col3, "Respuestas adecuadas semejantes:")

        ctk.CTkLabel(self.scroll_form, text="D. Descripción Narrativa del Origen", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(20, 5))
        self.txt_origen_narrativo = ctk.CTkTextbox(self.scroll_form, height=80)
        self.txt_origen_narrativo.pack(fill="x", pady=5)

        self.btn_save = ctk.CTkButton(self.scroll_form, text="💾 GUARDAR ANÁLISIS DE GÉNESIS", 
                                      height=45, command=self._save_data, font=("Roboto", 14, "bold"))
        self.btn_save.pack(fill="x", pady=30)

    def _open_styles_window(self):
        if not self.current_micro_id:
            messagebox.showwarning("Atención", "Seleccione una microcontingencia primero.")
            return
        StylesWindow(self, self.interactive_styles, self._on_styles_saved)

    def _on_styles_saved(self, styles_data):
        self.interactive_styles = styles_data
        self.btn_styles.configure(text=f"✅ ESTILOS EVALUADOS ({len(styles_data)})", fg_color="#27ae60", text_color="white")

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
        
        data = self.manager.get_genesis_by_micro_id(micro_id)
        self._clear_form()

        if data:
            self.current_genesis_id = data['id']
            self.status_indicator.configure(text="✅ COMPLETADO", text_color="#2ecc71")
            
            origin = data['origin_history']
            self.txt_circunstancia.insert("0.0", origin.get('circunstancia', ''))
            self.txt_situacion.insert("0.0", origin.get('situacion', ''))
            self.txt_disp_pasado.insert("0.0", origin.get('disp_pasado', ''))
            self.txt_origen_narrativo.insert("0.0", origin.get('narrativa_origen', ''))

            func = data['functional_history']
            self.txt_func_no_prob.insert("0.0", func.get('func_no_prob', ''))
            self.txt_efect_no_prob.insert("0.0", func.get('efect_no_prob', ''))
            self.txt_micro_no_prob.insert("0.0", func.get('micro_no_prob', ''))
            self.txt_resp_adecuadas.insert("0.0", func.get('resp_adecuadas', ''))
            
            self.interactive_styles = data.get('interactive_styles', [])
            if self.interactive_styles:
                self.btn_styles.configure(text=f"✅ ESTILOS EVALUADOS ({len(self.interactive_styles)})", fg_color="#27ae60", text_color="white")
        else:
            self.current_genesis_id = None
            self.status_indicator.configure(text="⚪ PENDIENTE", text_color="gray")
            self.btn_styles.configure(text="📋 ABRIR EVALUADOR DE ESTILOS", fg_color="#d4ac0d", text_color="black")

    def _save_data(self):
        if not self.current_micro_id: return

        origin_data = {
            'circunstancia': self.txt_circunstancia.get("1.0", "end-1c"),
            'situacion': self.txt_situacion.get("1.0", "end-1c"),
            'disp_pasado': self.txt_disp_pasado.get("1.0", "end-1c"),
            'narrativa_origen': self.txt_origen_narrativo.get("1.0", "end-1c")
        }
        func_data = {
            'func_no_prob': self.txt_func_no_prob.get("1.0", "end-1c"),
            'efect_no_prob': self.txt_efect_no_prob.get("1.0", "end-1c"),
            'micro_no_prob': self.txt_micro_no_prob.get("1.0", "end-1c"),
            'resp_adecuadas': self.txt_resp_adecuadas.get("1.0", "end-1c")
        }

        success, msg = self.manager.save_genesis(
            self.patient_id, self.current_micro_id, origin_data, func_data, self.interactive_styles
        )
        
        if success:
            messagebox.showinfo("Éxito", msg)
            self._on_micro_selected(self.combo_micros.get())
        else:
            messagebox.showerror("Error", msg)

    def _clear_form(self):
        widgets = [self.txt_circunstancia, self.txt_situacion, self.txt_disp_pasado, self.txt_origen_narrativo,
                   self.txt_func_no_prob, self.txt_efect_no_prob, self.txt_micro_no_prob, self.txt_resp_adecuadas]
        for w in widgets: w.delete("1.0", "end")
        self.interactive_styles = []

    def _create_header(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Roboto", 14, "bold"), text_color="#3498db").pack(pady=10)
        ctk.CTkFrame(parent, height=2, fg_color="gray").pack(fill="x", padx=10, pady=(0, 10))

    def _add_field(self, parent, label_text):
        ctk.CTkLabel(parent, text=label_text, font=("Roboto", 11, "bold"), wraplength=180).pack(anchor="w", padx=10)
        txt = ctk.CTkTextbox(parent, height=60)
        txt.pack(fill="x", padx=10, pady=(2, 10))
        return txt