import customtkinter as ctk
from src.clinical.patient_manager import PatientManager
from ui.patient_form import PatientFormWindow  
from ui.clinical_window import ClinicalWindow 

class DashboardWindow(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()

        # Configuración de la ventana principal
        self.title("Panel Principal - Análisis Contingencial")
        self.geometry("1000x600")
        
        # Datos del usuario logueado (por si los necesitamos luego)
        self.user_id = user_id
        self.patient_manager = PatientManager()

        # Layout principal: 2 columnas
        self.grid_columnconfigure(1, weight=1) # El lado derecho se expande
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL IZQUIERDO: AGENDA ---
        self.frame_agenda = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.frame_agenda.grid(row=0, column=0, sticky="nsew")
        
        self.lbl_agenda = ctk.CTkLabel(self.frame_agenda, text="Agenda Semanal", font=("Roboto", 20, "bold"))
        self.lbl_agenda.pack(pady=20, padx=20)

        # (Placeholder visual para la agenda)
        self.agenda_placeholder = ctk.CTkLabel(self.frame_agenda, text="No hay citas próximas\n(Módulo en construcción)", text_color="gray")
        self.agenda_placeholder.pack(pady=50)


        # --- PANEL DERECHO: PACIENTES ---
        self.frame_patients = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_patients.grid(row=0, column=1, sticky="nsew")

        # Cabecera de Pacientes
        self.header_frame = ctk.CTkFrame(self.frame_patients, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=20)

        self.lbl_patients = ctk.CTkLabel(self.header_frame, text="Expedientes Activos", font=("Roboto", 20, "bold"))
        self.lbl_patients.pack(side="left")

        self.btn_new_patient = ctk.CTkButton(self.header_frame, text="+ Nuevo Paciente", command=self.open_new_patient_modal)
        self.btn_new_patient.pack(side="right")

        # Lista de Pacientes (Scrollable)
        self.scroll_frame = ctk.CTkScrollableFrame(self.frame_patients, label_text="Listado")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Cargar los datos
        self.refresh_patient_list()

    def refresh_patient_list(self):
        """Borra la lista actual y la vuelve a cargar de la BD."""
        # Limpiar widgets anteriores
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        patients = self.patient_manager.get_all_patients()

        if not patients:
            ctk.CTkLabel(self.scroll_frame, text="No hay pacientes registrados.").pack(pady=20)
            return

        for p in patients:
            # p = (id, code_name, motive)
            card = ctk.CTkFrame(self.scroll_frame)
            card.pack(fill="x", pady=5)
            
            # Nombre del paciente
            lbl_name = ctk.CTkLabel(card, text=f"📂 {p[1]}", font=("Roboto", 14, "bold"))
            lbl_name.pack(side="left", padx=10, pady=10)
            
            # Motivo (truncado si es muy largo)
            motive_text = (p[2][:30] + '...') if len(p[2]) > 30 else p[2]
            lbl_motive = ctk.CTkLabel(card, text=motive_text, text_color="gray")
            lbl_motive.pack(side="left", padx=10)

            # Botón "Abrir"
            btn_open = ctk.CTkButton(card, text="Abrir", width=80, 
                                   command=lambda pid=p[0]: self.open_patient_file(pid))
            btn_open.pack(side="right", padx=10)

    def open_new_patient_modal(self):
        PatientFormWindow(self, on_save_success=self.refresh_patient_list)

    def open_patient_file(self, patient_id):
        ClinicalWindow(patient_id, self)