import customtkinter as ctk
from tkinter import messagebox
from ui.clinical_window import ClinicalWindow
from src.clinical.patient_manager import PatientManager
from src.utils.backup_manager import BackupManager  # <--- IMPORTANTE

class DashboardWindow(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        # Gestores
        self.patient_manager = PatientManager()
        self.backup_manager = BackupManager() # <--- INICIALIZAR

        # Configuración de ventana principal
        self.title("Panel Principal - Análisis Contingencial")
        self.geometry("1200x800")
        self.state("zoomed") 

        # Layout Principal: Sidebar (Izq) + Main Area (Der)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._setup_sidebar()
        self._setup_main_area()
        self._load_patient_list()

    def _setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Agenda Semanal", font=("Roboto", 24, "bold"))
        self.logo_label.pack(pady=30, padx=20)

        # Aquí iría un widget de calendario o lista de citas futuras
        self.lbl_citas = ctk.CTkLabel(self.sidebar, text="No hay citas próximas\n(Módulo en construcción)", text_color="gray")
        self.lbl_citas.pack(pady=50)

        # --- SECCIÓN DE SISTEMA (Abajo) ---
        spacer = ctk.CTkLabel(self.sidebar, text="") 
        spacer.pack(expand=True) # Empuja lo siguiente hacia abajo

        # Botón RESPALDO
        self.btn_backup = ctk.CTkButton(self.sidebar, text="💾 Crear Respaldo DB", 
                                      fg_color="#27ae60", hover_color="#2ecc71",
                                      command=self._do_backup)
        self.btn_backup.pack(padx=20, pady=10, fill="x", side="bottom")
        
        self.btn_logout = ctk.CTkButton(self.sidebar, text="Cerrar Sesión", fg_color="#c0392b", command=self.destroy)
        self.btn_logout.pack(padx=20, pady=10, fill="x", side="bottom")

    def _setup_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Encabezado
        self.header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(self.header, text="Expedientes Activos", font=("Roboto", 24, "bold")).pack(side="left")
        ctk.CTkButton(self.header, text="+ Nuevo Paciente", command=self._open_new_patient_modal).pack(side="right")

        # Lista de Pacientes (Scroll)
        self.scroll_patients = ctk.CTkScrollableFrame(self.main_frame)
        self.scroll_patients.pack(fill="both", expand=True)

    def _load_patient_list(self):
        # Limpiar lista actual
        for widget in self.scroll_patients.winfo_children():
            widget.destroy()

        patients = self.patient_manager.get_all_patients()
        
        if not patients:
            ctk.CTkLabel(self.scroll_patients, text="No hay pacientes registrados.").pack(pady=20)
            return

        # Encabezados de tabla simulada
        header_frame = ctk.CTkFrame(self.scroll_patients, height=40, fg_color=("gray85", "gray25"))
        header_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(header_frame, text="Listado", font=("Roboto", 12, "bold")).pack(side="left", padx=10)

        for p in patients:
            self._create_patient_row(p)

    def _create_patient_row(self, patient):
        row = ctk.CTkFrame(self.scroll_patients, height=50)
        row.pack(fill="x", pady=5)
        
        # Icono o ID
        ctk.CTkLabel(row, text="📂", font=("Arial", 20)).pack(side="left", padx=15)
        
        # Info
        info_text = f"{patient['code_name']}   {patient['age']} años   ({patient['occupation']})"
        ctk.CTkLabel(row, text=info_text, font=("Roboto", 14)).pack(side="left", padx=10)
        
        # Botón Abrir
        ctk.CTkButton(row, text="Abrir", width=100, 
                      command=lambda p_id=patient['id']: self._open_clinical_window(p_id)).pack(side="right", padx=10)

    # --- ACCIONES ---

    def _do_backup(self):
        """Ejecuta el respaldo y avisa al usuario."""
        success, msg = self.backup_manager.create_backup()
        if success:
            messagebox.showinfo("Respaldo Exitoso", f"Copia de seguridad guardada en carpeta 'backups'.\n\nArchivo: {msg}")
        else:
            messagebox.showerror("Error", f"No se pudo crear respaldo: {msg}")

    def _open_new_patient_modal(self):
        # Ventana emergente simple
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nuevo Expediente")
        dialog.geometry("500x600")
        
        # Forzar foco
        dialog.after(100, dialog.lift)
        dialog.grab_set() 
        
        ctk.CTkLabel(dialog, text="Datos de Identificación (Módulo 1)", font=("Roboto", 16, "bold")).pack(pady=20)
        
        # Campos
        entries = {}
        fields = [("Nombre / Código:", "code_name"), ("Edad:", "age"), ("Ocupación:", "occupation")]
        
        for label_text, key in fields:
            frame = ctk.CTkFrame(dialog, fg_color="transparent")
            frame.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(frame, text=label_text, width=120, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame, width=250)
            entry.pack(side="right")
            entries[key] = entry

        # Sexo (Combobox)
        frame_sex = ctk.CTkFrame(dialog, fg_color="transparent")
        frame_sex.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_sex, text="Sexo:", width=120, anchor="w").pack(side="left")
        combo_sex = ctk.CTkComboBox(frame_sex, values=["Mujer", "Hombre", "Otro"], width=250)
        combo_sex.pack(side="right")

        # Motivo
        ctk.CTkLabel(dialog, text="Motivo de Consulta (Texto del paciente):", anchor="w").pack(fill="x", padx=20, pady=(10,0))
        txt_motive = ctk.CTkTextbox(dialog, height=100)
        txt_motive.pack(fill="x", padx=20, pady=5)

        # Metas (NUEVO CAMPO)
        ctk.CTkLabel(dialog, text="Metas y Expectativas:", anchor="w").pack(fill="x", padx=20, pady=(10,0))
        txt_goals = ctk.CTkEntry(dialog, placeholder_text="Objetivos iniciales...")
        txt_goals.pack(fill="x", padx=20, pady=5)

        def save():
            # Validar y guardar
            data = {k: v.get() for k, v in entries.items()}
            data['sex'] = combo_sex.get()
            data['motive'] = txt_motive.get("1.0", "end-1c")
            data['goals'] = txt_goals.get() # Capturar metas

            if not data['code_name']: return

            try:
                data['age'] = int(data['age'])
            except:
                messagebox.showerror("Error", "La edad debe ser un número")
                return

            success, msg = self.patient_manager.create_patient(data)
            if success:
                self._load_patient_list()
                dialog.destroy()
            else:
                messagebox.showerror("Error", msg)

        # Botonera
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)
        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="gray", command=dialog.destroy).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Guardar Expediente", command=save).pack(side="left", padx=10)

    def _open_clinical_window(self, patient_id):
        # Abrir la ventana compleja de módulos
        ClinicalWindow(patient_id, self)