import customtkinter as ctk
from tkinter import messagebox
from src.clinical.genesis.genesis_manager import GenesisManager

class GenesisPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = GenesisManager()
        
        self.micro_map = {} # Mapa: "Texto Combo" -> ID
        self.current_micro_id = None # ID seleccionado actualmente

        self._setup_ui()
        self._load_micros()

    def _setup_ui(self):
        # Título
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header, text="4. Génesis e Historia", font=("Roboto", 22, "bold")).pack(side="left")

        # --- PANEL SUPERIOR: SELECTOR MAESTRO ---
        self.selector_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"), corner_radius=10)
        self.selector_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(self.selector_frame, text="Seleccionar Microcontingencia:", font=("Roboto", 12, "bold")).pack(side="left", padx=15, pady=15)
        
        self.combo_micros = ctk.CTkComboBox(self.selector_frame, width=350, command=self._on_micro_selected)
        self.combo_micros.pack(side="left", padx=10)

        # INDICADOR VISUAL DE ESTADO (El toque gráfico)
        self.status_indicator = ctk.CTkLabel(self.selector_frame, text="⚪ Selecciona una opción", 
                                           font=("Roboto", 12, "bold"), text_color="gray")
        self.status_indicator.pack(side="left", padx=20)

        # --- ÁREA DE TRABAJO (FORMULARIO CON SCROLL) ---
        self.scroll_form = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_form.pack(fill="both", expand=True)

        # ESTRUCTURA DE 3 COLUMNAS
        self.grid_frame = ctk.CTkFrame(self.scroll_form, fg_color="transparent")
        self.grid_frame.pack(fill="x", expand=True)
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)
        self.grid_frame.grid_columnconfigure(2, weight=1)

        # Columna 1
        col1 = ctk.CTkFrame(self.grid_frame)
        col1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self._create_header(col1, "A. Historia de la\nMicrocontingencia")
        self.txt_circunstancia = self._add_field(col1, "Circunstancia de inicio:")
        self.txt_situacion = self._add_field(col1, "Situación de inicio:")
        self.txt_disp_pasado = self._add_field(col1, "Disposiciones pasadas:")

        # Columna 2
        col2 = ctk.CTkFrame(self.grid_frame)
        col2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self._create_header(col2, "B. Funcionalidad en\nOtros Contextos")
        self.txt_func_no_prob = self._add_field(col2, "Función en contextos NO problemáticos:")
        self.txt_efect_no_prob = self._add_field(col2, "Efectividad/Efectos:")

        # Columna 3
        col3 = ctk.CTkFrame(self.grid_frame)
        col3.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        self._create_header(col3, "C. Disponibilidad de\nRecursos / Conductas")
        self.txt_micro_no_prob = self._add_field(col3, "Microcontingencias NO problemáticas:")
        self.txt_resp_adecuadas = self._add_field(col3, "Respuestas adecuadas semejantes:")
        self.txt_resp_otras = self._add_field(col3, "Respuestas ante otros significativos:")

        # Narrativa
        ctk.CTkLabel(self.scroll_form, text="D. Descripción Narrativa del Origen", 
                     font=("Roboto", 14, "bold"), text_color=("blue", "lightblue")).pack(anchor="w", pady=(20, 5))
        self.txt_origen_narrativo = ctk.CTkTextbox(self.scroll_form, height=80)
        self.txt_origen_narrativo.pack(fill="x", pady=5)

        # BOTÓN DE ACCIÓN
        self.btn_save = ctk.CTkButton(self.scroll_form, text="GUARDAR ANÁLISIS", height=45, 
                                      fg_color="gray", state="disabled", command=self._save_data)
        self.btn_save.pack(fill="x", pady=30)


    def _load_micros(self):
        """Carga el dropdown inicial."""
        micros = self.manager.get_available_micros(self.patient_id)
        if not micros:
            self.combo_micros.set("No hay microcontingencias registradas")
            self.combo_micros.configure(state="disabled")
            return

        self.micro_map = {}
        display_values = []
        for m in micros:
            desc = m[1][:40] + "..." if len(m[1]) > 40 else m[1]
            label = f"#{m[0]}: {desc}"
            self.micro_map[label] = m[0]
            display_values.append(label)
        
        self.combo_micros.configure(values=display_values)
        # Seleccionar la primera por defecto y disparar evento
        self.combo_micros.set(display_values[0])
        self._on_micro_selected(display_values[0])

    def _on_micro_selected(self, choice):
        """Magia: Cuando cambias el combo, se cargan los datos."""
        micro_id = self.micro_map.get(choice)
        if not micro_id: return
        
        self.current_micro_id = micro_id
        
        # Consultar si ya existe génesis
        data = self.manager.get_genesis_by_micro_id(micro_id)
        
        self._clear_form() # Limpiar siempre antes de llenar

        if data:
            # CASO: YA EXISTE (MODO EDICIÓN)
            self.status_indicator.configure(text="✅ ANÁLISIS COMPLETADO (Modo Edición)", text_color="#2ecc71") # Verde
            self.btn_save.configure(text="ACTUALIZAR ANÁLISIS", fg_color="#d35400", state="normal") # Naranja
            
            # Llenar campos
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
            self.txt_resp_otras.insert("0.0", func.get('resp_otras', ''))
            
        else:
            # CASO: NUEVO (MODO CREACIÓN)
            self.status_indicator.configure(text="⚪ PENDIENTE DE ANÁLISIS", text_color="gray")
            self.btn_save.configure(text="GUARDAR NUEVO ANÁLISIS", fg_color="darkblue", state="normal")

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
            'resp_adecuadas': self.txt_resp_adecuadas.get("1.0", "end-1c"),
            'resp_otras': self.txt_resp_otras.get("1.0", "end-1c")
        }

        success, msg = self.manager.save_genesis(self.patient_id, self.current_micro_id, origin_data, func_data)
        
        if success:
            messagebox.showinfo("Éxito", msg)
            # Refrescar el estado visual
            self._on_micro_selected(self.combo_micros.get())
        else:
            messagebox.showerror("Error", msg)

    def _clear_form(self):
        widgets = [self.txt_circunstancia, self.txt_situacion, self.txt_disp_pasado, self.txt_origen_narrativo,
                   self.txt_func_no_prob, self.txt_efect_no_prob, self.txt_micro_no_prob, self.txt_resp_adecuadas, self.txt_resp_otras]
        for w in widgets: w.delete("1.0", "end")

    # --- HELPERS ---
    def _create_header(self, parent, text):
        lbl = ctk.CTkLabel(parent, text=text, font=("Roboto", 14, "bold"), text_color="lightblue", justify="center")
        lbl.pack(pady=10, padx=5)
        ctk.CTkFrame(parent, height=2, fg_color="gray").pack(fill="x", padx=10, pady=(0, 10))

    def _add_field(self, parent, label_text):
        ctk.CTkLabel(parent, text=label_text, font=("Roboto", 11, "bold"), wraplength=200, justify="left").pack(anchor="w", padx=10, pady=(5,0))
        txt = ctk.CTkTextbox(parent, height=60)
        txt.pack(fill="x", padx=10, pady=(2, 10))
        return txt