import customtkinter as ctk
from tkinter import messagebox
from src.clinical.genesis.genesis_manager import GenesisManager

class GenesisPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = GenesisManager()
        
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="4. Génesis del Problema e Historia", font=("Roboto", 22, "bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self, text="Análisis del origen, funcionalidad en otros contextos y recursos disponibles.", 
                     text_color="gray").pack(anchor="w", pady=(0, 20))

        # --- CONTENEDOR DE 3 COLUMNAS (Grid Layout) ---
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="x", expand=True)
        
        # Configurar pesos de columnas para que se expandan igual
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.grid_frame.grid_columnconfigure(1, weight=1)
        self.grid_frame.grid_columnconfigure(2, weight=1)

        # === COLUMNA 1: HISTORIA DE LA MICROCONTINGENCIA ===
        col1 = ctk.CTkFrame(self.grid_frame)
        col1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self._create_header(col1, "A. Historia de la\nMicrocontingencia")
        
        self.txt_circunstancia = self._add_field(col1, "Circunstancia de inicio (¿Cuándo empezó a valorarse como problema?):")
        self.txt_situacion = self._add_field(col1, "Situación de inicio (Origen de las relaciones):")
        self.txt_disp_pasado = self._add_field(col1, "Funciones disposicionales de otros en el pasado:")

        # === COLUMNA 2: FUNCIONALIDAD EN OTROS CONTEXTOS ===
        col2 = ctk.CTkFrame(self.grid_frame)
        col2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self._create_header(col2, "B. Funcionalidad en\nOtros Contextos")
        
        self.txt_func_no_prob = self._add_field(col2, "Función de la conducta en contextos NO problemáticos:")
        self.txt_efect_no_prob = self._add_field(col2, "Efectividad/Efectos en contextos no problemáticos:")

        # === COLUMNA 3: DISPONIBILIDAD DE OTRAS CONDUCTAS ===
        col3 = ctk.CTkFrame(self.grid_frame)
        col3.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        
        self._create_header(col3, "C. Disponibilidad de\nRecursos / Conductas")
        
        self.txt_micro_no_prob = self._add_field(col3, "Microcontingencias NO problemáticas (Recursos):")
        self.txt_resp_adecuadas = self._add_field(col3, "Respuestas adecuadas ante situaciones semejantes:")
        self.txt_resp_otras = self._add_field(col3, "Respuestas ante otros significativos (No problemáticas):")

        # === SECCIÓN INFERIOR: ORIGEN NARRATIVO ===
        self._create_section_title("D. Descripción Narrativa del Origen")
        self.txt_origen_narrativo = ctk.CTkTextbox(self, height=80)
        self.txt_origen_narrativo.pack(fill="x", pady=5)

        # BOTÓN GUARDAR
        ctk.CTkButton(self, text="GUARDAR ANÁLISIS HISTÓRICO", height=45, fg_color="darkblue", 
                      command=self._save_data).pack(fill="x", pady=30)

    def _create_header(self, parent, text):
        lbl = ctk.CTkLabel(parent, text=text, font=("Roboto", 14, "bold"), text_color="lightblue", justify="center")
        lbl.pack(pady=10, padx=5)
        ctk.CTkFrame(parent, height=2, fg_color="gray").pack(fill="x", padx=10, pady=(0, 10))

    def _add_field(self, parent, label_text):
        ctk.CTkLabel(parent, text=label_text, font=("Roboto", 11, "bold"), wraplength=250, justify="left").pack(anchor="w", padx=10, pady=(5,0))
        txt = ctk.CTkTextbox(parent, height=60)
        txt.pack(fill="x", padx=10, pady=(2, 10))
        return txt

    def _create_section_title(self, text):
        ctk.CTkLabel(self, text=text, font=("Roboto", 14, "bold"), text_color=("blue", "lightblue")).pack(anchor="w", pady=(20, 5))

    def _save_data(self):
        # Empaquetamos Columnas 1 y 4 (Narrativa) en "origin_history"
        origin_data = {
            'circunstancia': self.txt_circunstancia.get("1.0", "end-1c"),
            'situacion': self.txt_situacion.get("1.0", "end-1c"),
            'disp_pasado': self.txt_disp_pasado.get("1.0", "end-1c"),
            'narrativa_origen': self.txt_origen_narrativo.get("1.0", "end-1c")
        }

        # Empaquetamos Columnas 2 y 3 en "functional_history" (aprovechando el campo)
        func_data = {
            'func_no_prob': self.txt_func_no_prob.get("1.0", "end-1c"),
            'efect_no_prob': self.txt_efect_no_prob.get("1.0", "end-1c"),
            'micro_no_prob': self.txt_micro_no_prob.get("1.0", "end-1c"),
            'resp_adecuadas': self.txt_resp_adecuadas.get("1.0", "end-1c"),
            'resp_otras': self.txt_resp_otras.get("1.0", "end-1c")
        }

        success, msg = self.manager.save_genesis(self.patient_id, origin_data, func_data)
        if success:
            messagebox.showinfo("Éxito", msg)
        else:
            messagebox.showerror("Error", msg)

    def _load_data(self):
        data = self.manager.get_genesis_data(self.patient_id)
        if not data: return

        # Helper para llenar texto
        def fill(widget, text):
            if text:
                widget.delete("1.0", "end")
                widget.insert("0.0", text)

        # Desempaquetar Origen
        origin = data.get('origin_history', {})
        fill(self.txt_circunstancia, origin.get('circunstancia', ''))
        fill(self.txt_situacion, origin.get('situacion', ''))
        fill(self.txt_disp_pasado, origin.get('disp_pasado', ''))
        fill(self.txt_origen_narrativo, origin.get('narrativa_origen', ''))

        # Desempaquetar Funcionalidad/Recursos
        func = data.get('functional_history', {})
        fill(self.txt_func_no_prob, func.get('func_no_prob', ''))
        fill(self.txt_efect_no_prob, func.get('efect_no_prob', ''))
        fill(self.txt_micro_no_prob, func.get('micro_no_prob', ''))
        fill(self.txt_resp_adecuadas, func.get('resp_adecuadas', ''))
        fill(self.txt_resp_otras, func.get('resp_otras', ''))