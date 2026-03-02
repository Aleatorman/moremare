import customtkinter as ctk
from tkinter import messagebox
from src.clinical.genesis.genesis_manager import GenesisManager

class StylesWindow(ctk.CTkToplevel):
    """Ventana para evaluar los 12 Estilos Interactivos (Ribes, 1990)"""
    def __init__(self, parent, current_styles, on_save_callback):
        super().__init__(parent)
        self.title("Evaluación de Estilos Interactivos (Génesis)")
        self.geometry("600(700")
        self.transient(parent)
        self.grab_set()
        
        self.on_save_callback = on_save_callback
        self.style_entries = {}
        
        # Los 12 arreglos contingenciales genéricos para evaluar estilos
        self.styles_list = [
            "Toma de decisiones", "Tolerancia a la ambigüedad", 
            "Tolerancia a la frustración", "Logro", 
            "Flexibilidad al cambio", "Tendencia a la transgresión", 
            "Curiosidad", "Tendencia al riesgo", 
            "Dependencia de señales", "Responsividad a nuevas contingencias", 
            "Impulsividad / No impulsividad", "Reducción de conflicto"
        ]

        self._setup_ui(current_styles)

    def _setup_ui(self, current_styles):
        ctk.CTkLabel(self, text="Modos consistentes de interacción histórica", 
                     font=("Roboto", 16, "bold")).pack(pady=15)
        
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        for style in self.styles_list:
            frame = ctk.CTkFrame(scroll, fg_color="transparent")
            frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(frame, text=f"{style}:", font=("Roboto", 12, "bold"), width=200, anchor="w").pack(side="left")
            
            # Buscamos si ya tiene un valor guardado
            initial_val = ""
            for s in current_styles:
                if s['arrangement_type'] == style:
                    initial_val = s['response_style']
                    break
            
            entry = ctk.CTkEntry(frame, placeholder_text="Describa la tendencia...")
            entry.insert(0, initial_val)
            entry.pack(side="left", fill="x", expand=True, padx=10)
            self.style_entries[style] = entry

        ctk.CTkButton(self, text="Confirmar Estilos Interactivos", 
                      command=self._save_and_close, fg_color="#27ae60").pack(pady=20)

    def _save_and_close(self):
        data = []
        for style, entry in self.style_entries.items():
            data.append({'arrangement_type': style, 'response_style': entry.get()})
        self.on_save_callback(data)
        self.destroy()

class GenesisPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = GenesisManager()
        
        self.micro_map = {}
        self.current_micro_id = None
        self.current_genesis_id = None
        self.interactive_styles = [] # Lista de dicts: {type, style}

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

        # SECCIÓN NUEVA: ESTILOS INTERACTIVOS (PUNTO 2)
        styles_frame = ctk.CTkFrame(self.scroll_form, fg_color="#fcf3cf") # Color crema para destacar
        styles_frame.pack(fill="x", pady=10, padx=5)
        
        ctk.CTkLabel(styles_frame, text="Estrategias de Interacción (Génesis Funcional)", 
                     font=("Roboto", 14, "bold"), text_color="#935116").pack(side="left", padx=15, pady=10)
        
        self.btn_styles = ctk.CTkButton(styles_frame, text="📋 EVALUAR ESTILOS INTERACTIVOS", 
                                        command=self._open_styles_window, fg_color="#d4ac0d", text_color="black")
        self.btn_styles.pack(side="right", padx=15, pady=10)

        # Rejilla de Historia Tradicional
        self.grid_frame = ctk.CTkFrame(self.scroll_form, fg_color="transparent")
        self.grid_frame.pack(fill="x", expand=True)
        self.grid_frame.grid_columnconfigure((0,1,2), weight=1)

        # Columna 1: Historia Micro
        col1 = ctk.CTkFrame(self.grid_frame); col1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self._create_header(col1, "A. Historia de la\nMicrocontingencia")
        self.txt_circunstancia = self._add_field(col1, "Circunstancia de inicio:")
        self.txt_situacion = self._add_field(col1, "Situación de inicio:")
        self.txt_disp_pasado = self._add_field(col1, "Disposiciones pasadas:")

        # Columna 2: Funcionalidad Otros Contextos
        col2 = ctk.CTkFrame(self.grid_frame); col2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self._create_header(col2, "B. Funcionalidad en\nOtros Contextos")
        self.txt_func_no_prob = self._add_field(col2, "Función en contextos NO problemáticos:")
        self.txt_efect_no_prob = self._add_field(col2, "Efectividad/Efectos:")

        # Columna 3: Recursos Disponibles
        col3 = ctk.CTkFrame(self.grid_frame); col3.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        self._create_header(col3, "C. Disponibilidad de\nRecursos / Conductas")
        self.txt_micro_no_prob = self._add_field(col3, "Microcontingencias NO problemáticas:")
        self.txt_resp_adecuadas = self._add_field(col3, "Respuestas adecuadas semejantes:")

        # Narrativa final
        ctk.CTkLabel(self.scroll_form, text="D. Descripción Narrativa del Origen", 
                     font=("Roboto", 14, "bold")).pack(anchor="w", pady=(20, 5))
        self.txt_origen_narrativo = ctk.CTkTextbox(self.scroll_form, height=80)
        self.txt_origen_narrativo.pack(fill="x", pady=5)

        self.btn_save = ctk.CTkButton(self.scroll_form, text="GUARDAR ANÁLISIS DE GÉNESIS", 
                                      height=45, command=self._save_data)
        self.btn_save.pack(fill="x", pady=30)

    def _open_styles_window(self):
        if not self.current_micro_id:
            messagebox.showwarning("Atención", "Seleccione una microcontingencia primero.")
            return
        StylesWindow(self, self.interactive_styles, self._on_styles_saved)

    def _on_styles_saved(self, styles_data):
        self.interactive_styles = styles_data
        self.btn_styles.configure(text="✅ ESTILOS EVALUADOS", fg_color="#27ae60", text_color="white")

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
            
            # Cargar Estilos Interactivos (Asumimos que el manager ahora los devuelve)
            self.interactive_styles = data.get('interactive_styles', [])
            if self.interactive_styles:
                self.btn_styles.configure(text="✅ ESTILOS EVALUADOS", fg_color="#27ae60", text_color="white")
        else:
            self.current_genesis_id = None
            self.status_indicator.configure(text="⚪ PENDIENTE", text_color="gray")
            self.btn_styles.configure(text="📋 EVALUAR ESTILOS INTERACTIVOS", fg_color="#d4ac0d", text_color="black")

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

        # Guardamos todo, incluyendo los estilos interactivos
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
        ctk.CTkLabel(parent, text=text, font=("Roboto", 14, "bold"), text_color="lightblue").pack(pady=10)
        ctk.CTkFrame(parent, height=2, fg_color="gray").pack(fill="x", padx=10, pady=(0, 10))

    def _add_field(self, parent, label_text):
        ctk.CTkLabel(parent, text=label_text, font=("Roboto", 11, "bold"), wraplength=180).pack(anchor="w", padx=10)
        txt = ctk.CTkTextbox(parent, height=60)
        txt.pack(fill="x", padx=10, pady=(2, 10))
        return txt