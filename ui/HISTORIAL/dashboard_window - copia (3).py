import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from ui.clinical_window import ClinicalWindow
from src.clinical.patient_manager import PatientManager
from src.utils.backup_manager import BackupManager
from src.clinical.appointments.appointment_manager import AppointmentManager

class DashboardWindow(ctk.CTk):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        
        # Gestores
        self.patient_manager = PatientManager()
        self.backup_manager = BackupManager()
        self.app_manager = AppointmentManager()

        # Configuración de ventana
        self.title("Sistema Clínico - Análisis Contingencial v1.0.0")
        self.geometry("1280x720")
        self.state("zoomed") 
        
        # COLORES ESTILO IMAGEN DE REFERENCIA
        self.col_sidebar = "#EBEBEB"      # Gris claro izquierda
        self.col_main = "#D9D9D9"         # Gris más oscuro derecha
        self.col_card = "#F5F5F5"         # Fondo tarjeta paciente
        self.col_blue = "#3498db"         # Azul botones
        self.col_red = "#e74c3c"          # Rojo salir
        self.text_color = "#2c3e50"       # Texto oscuro

        # Layout Principal: 2 Columnas
        # Columna 0: Sidebar (Fija, ~300px)
        # Columna 1: Main Area (Flexible)
        self.grid_columnconfigure(0, weight=0, minsize=320) 
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._setup_sidebar()
        self._setup_main_area()
        
        # Estado inicial
        self._load_patient_list()
        self._show_welcome_screen() # Mostrar Bienvenida al inicio

    def _setup_sidebar(self):
        """Panel izquierdo: Buscador, Filtros y Lista de Pacientes."""
        self.sidebar = ctk.CTkFrame(self, fg_color=self.col_sidebar, corner_radius=0, width=320)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) # Forzar ancho fijo

        # 1. Header Sidebar
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        # Icono simulado con texto
        ctk.CTkLabel(header, text="🧠 SISTEMA\nCLÍNICO", font=("Arial", 20, "bold"), 
                     text_color="black", justify="left").pack(side="left")

        # 2. Buscador
        self.entry_search = ctk.CTkEntry(self.sidebar, placeholder_text="Buscar paciente...", 
                                         fg_color="white", border_color="gray", border_width=1, text_color="black")
        self.entry_search.pack(fill="x", padx=20, pady=10)
        # Bind para buscar al escribir (Enter)
        self.entry_search.bind("<Return>", lambda event: self._load_patient_list(self.entry_search.get()))

        # 3. Filtros (Radio Buttons visuales - Funcionalidad "Todos" activa)
        self.filter_var = ctk.StringVar(value="Todos")
        filter_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=5)
        
        # Estilo visual de los filtros
        radio_style = {"text_color": "#555", "font": ("Arial", 12), "fg_color": self.col_blue}
        ctk.CTkRadioButton(filter_frame, text="Activo", variable=self.filter_var, value="Activo", **radio_style).pack(anchor="w", pady=2)
        ctk.CTkRadioButton(filter_frame, text="Inactivo", variable=self.filter_var, value="Inactivo", **radio_style).pack(anchor="w", pady=2)
        ctk.CTkRadioButton(filter_frame, text="Todos", variable=self.filter_var, value="Todos", command=lambda: self._load_patient_list(""), **radio_style).pack(anchor="w", pady=2)

        # 4. Contador de Pacientes
        self.lbl_count = ctk.CTkLabel(self.sidebar, text="PACIENTES (0)", font=("Arial", 12, "bold"), text_color="gray")
        self.lbl_count.pack(anchor="w", padx=20, pady=(20, 5))

        # 5. Lista de Pacientes (Scroll)
        self.scroll_patients = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.scroll_patients.pack(fill="both", expand=True, padx=10, pady=5)

        # 6. Botonera Inferior
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=20, side="bottom")
        
        ctk.CTkButton(bottom_frame, text="+ NUEVO PACIENTE", fg_color=self.col_blue, 
                      font=("Arial", 12, "bold"), height=40,
                      command=self._open_new_patient_modal).pack(fill="x", pady=5)
        
        ctk.CTkButton(bottom_frame, text="🚪 Salir", fg_color=self.col_red, 
                      font=("Arial", 12), height=30,
                      command=self.destroy).pack(fill="x", pady=5)

    def _setup_main_area(self):
        """Panel derecho: Dinámico (Bienvenida o Agenda)."""
        self.main_frame = ctk.CTkFrame(self, fg_color=self.col_main, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        
        # Barra Superior (Top Bar)
        self.top_bar = ctk.CTkFrame(self.main_frame, fg_color="#E0E0E0", height=50, corner_radius=0)
        self.top_bar.pack(fill="x", side="top")
        
        # Botón Volver (Funciona como "Ir a Inicio")
        ctk.CTkButton(self.top_bar, text="← Inicio", width=80, fg_color=self.col_blue,
                      command=self._show_welcome_screen).pack(side="left", padx=20, pady=10)
        
        self.lbl_title_main = ctk.CTkLabel(self.top_bar, text="Sistema Clínico de Análisis Contingencial", 
                                           font=("Arial", 16, "bold"), text_color="black")
        self.lbl_title_main.pack(side="left", padx=10)

        # Contenedor de contenido cambiante
        self.content_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True, padx=40, pady=40)

    # ============================================
    # VISTAS (PANTALLAS DEL LADO DERECHO)
    # ============================================

    def _show_welcome_screen(self):
        """Muestra la pantalla de bienvenida con el botón de Agenda."""
        self._clear_content()
        self.lbl_title_main.configure(text="Inicio")
        
        # Frame centralizado
        center_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Icono grande (texto)
        ctk.CTkLabel(center_frame, text="🏥", font=("Arial", 80)).pack(pady=10)
        
        # Texto Bienvenido
        ctk.CTkLabel(center_frame, text="BIENVENIDO", font=("Arial", 30, "bold"), text_color="#333").pack(pady=10)
        ctk.CTkLabel(center_frame, text="Selecciona un paciente a la izquierda o gestiona tu agenda.", 
                     font=("Arial", 14), text_color="gray").pack(pady=5)

        # BOTÓN AGENDA (Lo que pediste)
        ctk.CTkButton(center_frame, text="📅 IR A MI AGENDA", font=("Arial", 14, "bold"), 
                      height=50, width=200, fg_color=self.col_blue,
                      command=self._show_agenda_screen).pack(pady=30)
        
        # Botón Backup (Extra útil)
        ctk.CTkButton(center_frame, text="💾 Crear Respaldo", fg_color="gray", width=150,
                      command=self._do_backup).pack(pady=5)

    def _show_agenda_screen(self):
        """Muestra la interfaz de Agenda en el panel derecho."""
        self._clear_content()
        self.lbl_title_main.configure(text="Agenda Semanal")
        
        # Layout de Agenda
        agenda_frame = ctk.CTkFrame(self.content_container, fg_color="white", corner_radius=10)
        agenda_frame.pack(fill="both", expand=True)

        # Cabecera Agenda
        head = ctk.CTkFrame(agenda_frame, fg_color="transparent")
        head.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(head, text="Próximas Citas", font=("Arial", 20, "bold"), text_color="black").pack(side="left")
        ctk.CTkButton(head, text="+ Agendar Cita", fg_color=self.col_blue, command=self._open_appointment_modal).pack(side="right")

        # Lista de Citas
        self.scroll_agenda_list = ctk.CTkScrollableFrame(agenda_frame, fg_color="transparent")
        self.scroll_agenda_list.pack(fill="both", expand=True, padx=20, pady=10)
        
        self._load_appointments_into_view()

    def _clear_content(self):
        for widget in self.content_container.winfo_children():
            widget.destroy()

    # ============================================
    # LÓGICA DE DATOS
    # ============================================

    def _load_patient_list(self, query=""):
        """Carga las tarjetas de pacientes en el sidebar."""
        for w in self.scroll_patients.winfo_children(): w.destroy()
        
        patients = self.patient_manager.get_all_patients()
        
        # Filtrar por búsqueda
        if query:
            patients = [p for p in patients if query.lower() in p['code_name'].lower()]

        self.lbl_count.configure(text=f"PACIENTES ({len(patients)})")

        for p in patients:
            self._create_patient_card(p)

    def _create_patient_card(self, p):
        """Crea una tarjeta estilo 'Card' para cada paciente."""
        card = ctk.CTkFrame(self.scroll_patients, fg_color=self.col_card, corner_radius=6, border_width=1, border_color="#ccc")
        card.pack(fill="x", pady=4)
        
        # Contenido Tarjeta
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=8)
        
        # Nombre y ID
        ctk.CTkLabel(inner, text=p['code_name'], font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w")
        ctk.CTkLabel(inner, text=f"ID: {p['id']} | {p['age']} años", font=("Arial", 11), text_color="gray").pack(anchor="w")
        
        # Estado (Simulado)
        ctk.CTkLabel(inner, text="Fase 1: Evaluación", font=("Arial", 10), text_color=self.col_blue).pack(anchor="w", pady=(5,0))
        
        # Al hacer clic en la tarjeta, abrir expediente
        # Truco: Un botón transparente encima de todo o bindear evento click
        btn_open = ctk.CTkButton(card, text="Abrir Expediente", height=25, fg_color="transparent", 
                                 border_width=1, border_color="gray", text_color="gray", hover_color="#e0e0e0",
                                 command=lambda id=p['id']: self._open_clinical_window(id))
        btn_open.pack(fill="x", padx=10, pady=(0, 10))

    def _load_appointments_into_view(self):
        """Carga las citas en la vista de Agenda."""
        apps = self.app_manager.get_upcoming_appointments()
        if not apps:
            ctk.CTkLabel(self.scroll_agenda_list, text="No hay citas programadas.", text_color="gray").pack(pady=20)
            return

        for app in apps:
            row = ctk.CTkFrame(self.scroll_agenda_list, fg_color="#f9f9f9", corner_radius=8, border_width=1, border_color="#ddd")
            row.pack(fill="x", pady=5)
            
            # Fecha (Izquierda destacado)
            left = ctk.CTkFrame(row, fg_color="transparent", width=100)
            left.pack(side="left", padx=15, pady=10)
            
            # Día y Hora separados visualmente
            date_parts = app['date_display'].split(" ") # dd/mm HH:MM
            ctk.CTkLabel(left, text=date_parts[0], font=("Arial", 16, "bold"), text_color=self.col_blue).pack()
            ctk.CTkLabel(left, text=date_parts[1], font=("Arial", 14), text_color="#555").pack()

            # Detalles (Centro)
            center = ctk.CTkFrame(row, fg_color="transparent")
            center.pack(side="left", fill="both", expand=True, padx=10)
            ctk.CTkLabel(center, text=app['patient'], font=("Arial", 16, "bold"), text_color="#333").pack(anchor="w")
            ctk.CTkLabel(center, text=app['note'], font=("Arial", 12), text_color="gray").pack(anchor="w")

            # Acciones (Derecha)
            ctk.CTkButton(row, text="❌", width=40, fg_color="transparent", hover_color="#fee", text_color="red",
                          command=lambda i=app['id']: self._delete_app(i)).pack(side="right", padx=15)

    def _delete_app(self, app_id):
        if messagebox.askyesno("Confirmar", "¿Borrar esta cita?"):
            self.app_manager.delete_appointment(app_id)
            self._load_appointments_into_view()

    # ============================================
    # MODALES Y UTILIDADES
    # ============================================

    def _do_backup(self):
        success, msg = self.backup_manager.create_backup()
        if success: messagebox.showinfo("Respaldo", f"Copia creada:\n{msg}")
        else: messagebox.showerror("Error", msg)

    def _open_clinical_window(self, patient_id):
        ClinicalWindow(patient_id, self)

    def _open_new_patient_modal(self):
        # (Tu código de modal existente, adaptado ligeramente al estilo)
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nuevo Paciente")
        dialog.geometry("500x650")
        dialog.after(100, dialog.lift)
        dialog.grab_set() 
        dialog.configure(fg_color="#f0f0f0")

        ctk.CTkLabel(dialog, text="Crear Nuevo Expediente", font=("Arial", 18, "bold"), text_color="#333").pack(pady=20)

        entries = {}
        fields = [("Nombre / Código:", "code_name"), ("Edad:", "age"), ("Ocupación:", "occupation")]
        for lbl, key in fields:
            f = ctk.CTkFrame(dialog, fg_color="transparent")
            f.pack(fill="x", padx=30, pady=5)
            ctk.CTkLabel(f, text=lbl, width=120, anchor="w", text_color="#333").pack(side="left")
            e = ctk.CTkEntry(f, fg_color="white", border_color="gray", text_color="black")
            e.pack(side="right", fill="x", expand=True)
            entries[key] = e

        # Sexo
        f_sex = ctk.CTkFrame(dialog, fg_color="transparent")
        f_sex.pack(fill="x", padx=30, pady=5)
        ctk.CTkLabel(f_sex, text="Sexo:", width=120, anchor="w", text_color="#333").pack(side="left")
        combo_sex = ctk.CTkComboBox(f_sex, values=["Mujer", "Hombre", "Otro"], fg_color="white", text_color="black")
        combo_sex.pack(side="right", fill="x", expand=True)

        # Textos grandes
        ctk.CTkLabel(dialog, text="Motivo de Consulta:", anchor="w", text_color="#333").pack(fill="x", padx=30, pady=(10,0))
        txt_motive = ctk.CTkTextbox(dialog, height=80, fg_color="white", text_color="black", border_width=1, border_color="gray")
        txt_motive.pack(fill="x", padx=30, pady=5)

        ctk.CTkLabel(dialog, text="Metas y Expectativas:", anchor="w", text_color="#333").pack(fill="x", padx=30, pady=(5,0))
        txt_goals = ctk.CTkEntry(dialog, fg_color="white", text_color="black")
        txt_goals.pack(fill="x", padx=30, pady=5)

        def save():
            data = {k: v.get() for k, v in entries.items()}
            data['sex'] = combo_sex.get()
            data['motive'] = txt_motive.get("1.0", "end-1c")
            data['goals'] = txt_goals.get()
            
            if not data['code_name']: return
            try: int(data['age'])
            except: 
                messagebox.showerror("Error", "Edad inválida")
                return

            success, msg = self.patient_manager.create_patient(data)
            if success:
                self._load_patient_list()
                dialog.destroy()
            else:
                messagebox.showerror("Error", msg)

        ctk.CTkButton(dialog, text="GUARDAR DATOS", fg_color=self.col_blue, height=40, command=save).pack(pady=20, padx=30, fill="x")

    def _open_appointment_modal(self):
        # Lógica de modal de citas (Igual a la anterior pero con estilo)
        patients = self.patient_manager.get_all_patients()
        if not patients:
            messagebox.showwarning("Info", "Crea un paciente primero.")
            return
        p_map = {p['code_name']: p['id'] for p in patients}
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nueva Cita")
        dialog.geometry("400x500")
        dialog.after(100, dialog.lift)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Agendar Cita", font=("Arial", 18, "bold")).pack(pady=20)
        
        ctk.CTkLabel(dialog, text="Paciente:").pack(anchor="w", padx=30)
        c_pat = ctk.CTkComboBox(dialog, values=list(p_map.keys()), width=300)
        c_pat.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Fecha (DD/MM/AAAA):").pack(anchor="w", padx=30)
        e_date = ctk.CTkEntry(dialog, width=300)
        e_date.insert(0, datetime.now().strftime("%d/%m/%Y"))
        e_date.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Hora (HH:MM):").pack(anchor="w", padx=30)
        e_time = ctk.CTkEntry(dialog, width=300)
        e_time.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Nota:").pack(anchor="w", padx=30)
        e_note = ctk.CTkEntry(dialog, width=300)
        e_note.pack(pady=5)
        
        def save_app():
            pid = p_map.get(c_pat.get())
            if not pid: return
            success, msg = self.app_manager.add_appointment(pid, e_date.get(), e_time.get(), e_note.get())
            if success:
                self._show_agenda_screen() # Recargar agenda
                dialog.destroy()
            else:
                messagebox.showerror("Error", msg)
                
        ctk.CTkButton(dialog, text="AGENDAR", fg_color=self.col_blue, command=save_app).pack(pady=30)