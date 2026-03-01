import customtkinter as ctk
from src.clinical.patient_manager import PatientManager
from tkinter import messagebox

class PatientFormWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_save_success):
        super().__init__(parent)
        
        self.on_save_success = on_save_success # Función para actualizar la lista atrás
        self.patient_manager = PatientManager()

        # Configuración de la ventana
        self.title("Nuevo Expediente")
        self.geometry("500x650")
        self.resizable(False, False)
        
        # Hacemos que la ventana sea modal (bloquea la de atrás)
        self.transient(parent)
        self.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        # --- Título ---
        ctk.CTkLabel(self, text="Datos de Identificación (Módulo 1)", 
                    font=("Roboto", 18, "bold")).pack(pady=(20, 10))

        # --- Frame para datos demográficos (2 columnas) ---
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(fill="x", padx=20)

        # Nombre / Código
        ctk.CTkLabel(grid_frame, text="Nombre / Código:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_name = ctk.CTkEntry(grid_frame, width=200, placeholder_text="Ej: J.P. o Juan Pérez")
        self.entry_name.grid(row=0, column=1, pady=5, padx=10)

        # Edad
        ctk.CTkLabel(grid_frame, text="Edad:").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_age = ctk.CTkEntry(grid_frame, width=200)
        self.entry_age.grid(row=1, column=1, pady=5, padx=10)

        # Sexo
        ctk.CTkLabel(grid_frame, text="Sexo:").grid(row=2, column=0, sticky="w", pady=5)
        self.combo_sex = ctk.CTkComboBox(grid_frame, values=["Hombre", "Mujer", "Otro"], width=200)
        self.combo_sex.grid(row=2, column=1, pady=5, padx=10)

        # Ocupación
        ctk.CTkLabel(grid_frame, text="Ocupación:").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_job = ctk.CTkEntry(grid_frame, width=200)
        self.entry_job.grid(row=3, column=1, pady=5, padx=10)

        # --- Áreas de Texto Grande ---
        
        # Motivo de Consulta
        ctk.CTkLabel(self, text="Motivo de Consulta (Texto del paciente):", anchor="w").pack(fill="x", padx=25, pady=(15, 0))
        self.txt_motive = ctk.CTkTextbox(self, height=100)
        self.txt_motive.pack(fill="x", padx=20, pady=5)

        # Metas Terapéuticas
        ctk.CTkLabel(self, text="Metas y Expectativas:", anchor="w").pack(fill="x", padx=25, pady=(10, 0))
        self.txt_goals = ctk.CTkTextbox(self, height=80)
        self.txt_goals.pack(fill="x", padx=20, pady=5)

        # --- Botones de Acción ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="Cancelar", fg_color="gray", 
                     command=self.destroy).pack(side="left", padx=10)
        
        ctk.CTkButton(btn_frame, text="Guardar Expediente", 
                     command=self._handle_save).pack(side="left", padx=10)

    def _handle_save(self):
        # Recolectar datos
        name = self.entry_name.get()
        age = self.entry_age.get()
        sex = self.combo_sex.get()
        job = self.entry_job.get()
        # En textbox se usa "1.0" para leer desde la línea 1, caracter 0 hasta el final
        motive = self.txt_motive.get("1.0", "end-1c") 
        goals = self.txt_goals.get("1.0", "end-1c")

        # Validación básica
        if not name or not motive.strip():
            messagebox.showwarning("Faltan datos", "El nombre y el motivo de consulta son obligatorios.")
            return

        # Guardar en BD
        success, msg = self.patient_manager.create_patient(name, age, sex, job, motive, goals)

        if success:
            messagebox.showinfo("Éxito", "Paciente creado correctamente.")
            self.on_save_success() # Refrescar la lista del dashboard
            self.destroy() # Cerrar ventana
        else:
            messagebox.showerror("Error", f"No se pudo guardar: {msg}")