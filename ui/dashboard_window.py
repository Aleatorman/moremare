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
        
        self.patient_manager = PatientManager()
        self.backup_manager = BackupManager()
        self.app_manager = AppointmentManager()

        self.title("Sistema Clínico - Análisis Contingencial v1.0.0")
        self.geometry("1280x720")
        self.state("zoomed") 
        
        # COLORES
        self.col_sidebar = "#EBEBEB"
        self.col_main = "#D9D9D9"
        self.col_card = "#F5F5F5"
        self.col_blue = "#3498db"
        self.col_red = "#e74c3c"
        self.col_green = "#27ae60" # Para estado activo

        # Layout
        self.grid_columnconfigure(0, weight=0, minsize=320) 
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._setup_sidebar()
        self._setup_main_area()
        self._show_welcome_screen()
        self._load_patient_list() # Carga inicial

    def _setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=self.col_sidebar, corner_radius=0, width=320)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Header
        header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text="🧠 SISTEMA\nCLÍNICO", font=("Arial", 20, "bold"), 
                     text_color="black", justify="left").pack(side="left")

        # Buscador
        self.entry_search = ctk.CTkEntry(self.sidebar, placeholder_text="Buscar paciente...", 
                                         fg_color="white", border_color="gray", border_width=1, text_color="black")
        self.entry_search.pack(fill="x", padx=20, pady=10)
        self.entry_search.bind("<Return>", lambda e: self._load_patient_list())

        # --- FILTROS ACTIVOS ---
        self.filter_var = ctk.StringVar(value="Activo") # Por defecto solo activos
        
        filter_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=5)
        
        radio_style = {"text_color": "#555", "font": ("Arial", 12), "fg_color": self.col_blue}
        
        # Al hacer clic en un radio, recargamos la lista
        ctk.CTkRadioButton(filter_frame, text="Activos", variable=self.filter_var, value="Activo", 
                           command=self._load_patient_list, **radio_style).pack(anchor="w", pady=2)
        ctk.CTkRadioButton(filter_frame, text="Inactivos", variable=self.filter_var, value="Inactivo", 
                           command=self._load_patient_list, **radio_style).pack(anchor="w", pady=2)
        ctk.CTkRadioButton(filter_frame, text="Todos", variable=self.filter_var, value="Todos", 
                           command=self._load_patient_list, **radio_style).pack(anchor="w", pady=2)

        # Contador
        self.lbl_count = ctk.CTkLabel(self.sidebar, text="PACIENTES (0)", font=("Arial", 12, "bold"), text_color="gray")
        self.lbl_count.pack(anchor="w", padx=20, pady=(20, 5))

        # Lista
        self.scroll_patients = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent")
        self.scroll_patients.pack(fill="both", expand=True, padx=10, pady=5)

        # Botonera
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=20, side="bottom")
        
        ctk.CTkButton(bottom_frame, text="+ NUEVO PACIENTE", fg_color=self.col_blue, font=("Arial", 12, "bold"), height=40, command=self._open_new_patient_modal).pack(fill="x", pady=5)
        ctk.CTkButton(bottom_frame, text="🚪 Salir", fg_color=self.col_red, font=("Arial", 12), height=30, command=self.destroy).pack(fill="x", pady=5)

    def _setup_main_area(self):
        self.main_frame = ctk.CTkFrame(self, fg_color=self.col_main, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        
        # Top Bar
        self.top_bar = ctk.CTkFrame(self.main_frame, fg_color="#E0E0E0", height=50, corner_radius=0)
        self.top_bar.pack(fill="x", side="top")
        
        ctk.CTkButton(self.top_bar, text="← Inicio", width=80, fg_color=self.col_blue, command=self._show_welcome_screen).pack(side="left", padx=20, pady=10)
        self.lbl_title_main = ctk.CTkLabel(self.top_bar, text="Inicio", font=("Arial", 16, "bold"), text_color="black")
        self.lbl_title_main.pack(side="left", padx=10)

        # Contenedor
        self.content_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True, padx=40, pady=40)

    # --- LÓGICA DE CARGA DE PACIENTES ---
    def _load_patient_list(self, _=None):
        for w in self.scroll_patients.winfo_children(): w.destroy()
        
        all_patients = self.patient_manager.get_all_patients()
        
        # 1. Filtro de Búsqueda
        query = self.entry_search.get().lower()
        if query:
            all_patients = [p for p in all_patients if query in p['code_name'].lower()]

        # 2. Filtro de Estado
        status_filter = self.filter_var.get()
        if status_filter != "Todos":
            # Si el paciente no tiene campo status (base vieja sin actualizar), asumimos 'Activo'
            all_patients = [p for p in all_patients if p.get('status', 'Activo') == status_filter]

        self.lbl_count.configure(text=f"PACIENTES ({len(all_patients)})")

        for p in all_patients:
            self._create_patient_card(p)

    def _create_patient_card(self, p):
        # Color del borde según estado
        is_active = p.get('status', 'Activo') == 'Activo'
        border_col = self.col_green if is_active else "gray"
        
        card = ctk.CTkFrame(self.scroll_patients, fg_color=self.col_card, corner_radius=6, border_width=2, border_color=border_col)
        card.pack(fill="x", pady=4)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=8)
        
        # Nombre
        ctk.CTkLabel(inner, text=p['code_name'], font=("Arial", 14, "bold"), text_color="#333").pack(anchor="w")
        
        # Subtítulo (Edad | Estado)
        status_icon = "🟢 Activo" if is_active else "⚪ Inactivo"
        ctk.CTkLabel(inner, text=f"{p['age']} años | {status_icon}", font=("Arial", 11), text_color="gray").pack(anchor="w")
        
        # Botonera tarjeta
        btn_frame = ctk.CTkFrame(card, fg_color="transparent", height=30)
        btn_frame.pack(fill="x", padx=5, pady=(0, 5))
        
        # Botón Abrir
        ctk.CTkButton(btn_frame, text="Abrir", width=70, height=25, fg_color=self.col_blue, 
                      command=lambda id=p['id']: self._open_clinical_window(id)).pack(side="right", padx=2)
        
        # Botón Archivar/Reactivar
        action_text = "Archivar" if is_active else "Reactivar"
        action_color = "gray" if is_active else self.col_green
        ctk.CTkButton(btn_frame, text=action_text, width=70, height=25, fg_color=action_color, 
                      command=lambda id=p['id'], st=p.get('status', 'Activo'): self._toggle_patient_status(id, st)).pack(side="left", padx=2)

    def _toggle_patient_status(self, pid, current_status):
        new_status = "Inactivo" if current_status == "Activo" else "Activo"
        if self.patient_manager.toggle_status(pid, new_status):
            self._load_patient_list() # Recargar lista para ver cambios
        else:
            messagebox.showerror("Error", "No se pudo cambiar el estado")

    # --- PANTALLAS ---
    def _show_welcome_screen(self):
        self._clear_content()
        self.lbl_title_main.configure(text="Inicio")
        
        c = ctk.CTkFrame(self.content_container, fg_color="transparent")
        c.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(c, text="🏥", font=("Arial", 80)).pack(pady=10)
        ctk.CTkLabel(c, text="BIENVENIDO", font=("Arial", 30, "bold"), text_color="#333").pack(pady=10)
        ctk.CTkLabel(c, text="Selecciona un paciente o gestiona tu agenda.", font=("Arial", 14), text_color="gray").pack(pady=5)

        ctk.CTkButton(c, text="📅 IR A MI AGENDA", font=("Arial", 14, "bold"), height=50, width=200, fg_color=self.col_blue, command=self._show_agenda_screen).pack(pady=30)
        ctk.CTkButton(c, text="💾 Crear Respaldo", fg_color="gray", width=150, command=self._do_backup).pack(pady=5)

    def _show_agenda_screen(self):
        self._clear_content()
        self.lbl_title_main.configure(text="Agenda Semanal")
        
        frm = ctk.CTkFrame(self.content_container, fg_color="white", corner_radius=10)
        frm.pack(fill="both", expand=True)

        head = ctk.CTkFrame(frm, fg_color="transparent")
        head.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(head, text="Próximas Citas", font=("Arial", 20, "bold"), text_color="black").pack(side="left")
        ctk.CTkButton(head, text="+ Agendar", fg_color=self.col_blue, command=self._open_appointment_modal).pack(side="right")

        self.scroll_agenda_list = ctk.CTkScrollableFrame(frm, fg_color="transparent")
        self.scroll_agenda_list.pack(fill="both", expand=True, padx=20, pady=10)
        
        self._load_appointments_view()

    def _load_appointments_view(self):
        for w in self.scroll_agenda_list.winfo_children(): w.destroy()
        apps = self.app_manager.get_upcoming_appointments()
        
        if not apps:
            ctk.CTkLabel(self.scroll_agenda_list, text="No hay citas.", text_color="gray").pack(pady=20)
            return

        for app in apps:
            row = ctk.CTkFrame(self.scroll_agenda_list, fg_color="#f9f9f9", corner_radius=8, border_width=1, border_color="#ddd")
            row.pack(fill="x", pady=5)
            
            left = ctk.CTkFrame(row, fg_color="transparent", width=80)
            left.pack(side="left", padx=10, pady=10)
            dt = app['date_display'].split(" ")
            ctk.CTkLabel(left, text=dt[0], font=("Arial", 16, "bold"), text_color=self.col_blue).pack()
            ctk.CTkLabel(left, text=dt[1], font=("Arial", 14), text_color="#555").pack()

            center = ctk.CTkFrame(row, fg_color="transparent")
            center.pack(side="left", fill="both", expand=True, padx=10)
            ctk.CTkLabel(center, text=app['patient'], font=("Arial", 16, "bold"), text_color="#333").pack(anchor="w")
            ctk.CTkLabel(center, text=app['note'], font=("Arial", 12), text_color="gray").pack(anchor="w")

            ctk.CTkButton(row, text="🗑️", width=40, fg_color="transparent", hover_color="#fee", text_color="red", command=lambda i=app['id']: self._del_app(i)).pack(side="right", padx=10)

    def _del_app(self, aid):
        if messagebox.askyesno("Borrar", "¿Eliminar cita?"):
            self.app_manager.delete_appointment(aid)
            self._load_appointments_view()

    def _clear_content(self):
        for w in self.content_container.winfo_children(): w.destroy()

    def _do_backup(self):
        s, m = self.backup_manager.create_backup()
        messagebox.showinfo("Respaldo", m if s else f"Error: {m}")

    def _open_clinical_window(self, pid):
        ClinicalWindow(pid, self)

    def _open_new_patient_modal(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nuevo Paciente")
        dialog.geometry("500x650")
        dialog.after(100, dialog.lift)
        dialog.grab_set() 
        dialog.configure(fg_color="#f0f0f0")

        ctk.CTkLabel(dialog, text="Nuevo Expediente", font=("Arial", 18, "bold"), text_color="#333").pack(pady=15)

        entries = {}
        for lbl, k in [("Nombre:", "code_name"), ("Edad:", "age"), ("Ocupación:", "occupation")]:
            f = ctk.CTkFrame(dialog, fg_color="transparent")
            f.pack(fill="x", padx=30, pady=5)
            ctk.CTkLabel(f, text=lbl, width=100, anchor="w", text_color="#333").pack(side="left")
            entries[k] = ctk.CTkEntry(f, fg_color="white", text_color="black")
            entries[k].pack(side="right", fill="x", expand=True)

        f_sex = ctk.CTkFrame(dialog, fg_color="transparent")
        f_sex.pack(fill="x", padx=30, pady=5)
        ctk.CTkLabel(f_sex, text="Sexo:", width=100, anchor="w", text_color="#333").pack(side="left")
        combo_sex = ctk.CTkComboBox(f_sex, values=["Mujer", "Hombre"], fg_color="white", text_color="black")
        combo_sex.pack(side="right", fill="x", expand=True)

        ctk.CTkLabel(dialog, text="Motivo:", anchor="w", text_color="#333").pack(fill="x", padx=30, pady=(10,0))
        txt_motive = ctk.CTkTextbox(dialog, height=60, fg_color="white", text_color="black")
        txt_motive.pack(fill="x", padx=30)

        ctk.CTkLabel(dialog, text="Metas:", anchor="w", text_color="#333").pack(fill="x", padx=30, pady=(5,0))
        txt_goals = ctk.CTkEntry(dialog, fg_color="white", text_color="black")
        txt_goals.pack(fill="x", padx=30)

        def save():
            d = {k: v.get() for k, v in entries.items()}
            d['sex'] = combo_sex.get()
            d['motive'] = txt_motive.get("1.0", "end-1c")
            d['goals'] = txt_goals.get()
            if not d['code_name']: return
            try: int(d['age']) 
            except: 
                messagebox.showerror("Error", "Edad inválida")
                return
            
            s, m = self.patient_manager.create_patient(d)
            if s: 
                self._load_patient_list()
                dialog.destroy()
            else: messagebox.showerror("Error", m)

        ctk.CTkButton(dialog, text="GUARDAR", fg_color=self.col_blue, command=save).pack(pady=20)

    def _open_appointment_modal(self):
        patients = self.patient_manager.get_all_patients()
        if not patients:
            messagebox.showwarning("Info", "Sin pacientes.")
            return
        p_map = {p['code_name']: p['id'] for p in patients}
        
        d = ctk.CTkToplevel(self)
        d.title("Cita")
        d.geometry("400x450")
        d.after(100, d.lift)
        d.grab_set()
        
        ctk.CTkLabel(d, text="Nueva Cita", font=("Arial", 16, "bold")).pack(pady=10)
        
        c_pat = ctk.CTkComboBox(d, values=list(p_map.keys()), width=250)
        c_pat.pack(pady=5)
        e_date = ctk.CTkEntry(d, width=250); e_date.insert(0, datetime.now().strftime("%d/%m/%Y")); e_date.pack(pady=5)
        e_time = ctk.CTkEntry(d, width=250, placeholder_text="HH:MM"); e_time.pack(pady=5)
        e_note = ctk.CTkEntry(d, width=250, placeholder_text="Nota"); e_note.pack(pady=5)
        
        def save():
            pid = p_map.get(c_pat.get())
            if pid:
                self.app_manager.add_appointment(pid, e_date.get(), e_time.get(), e_note.get())
                self._load_appointments_view()
                d.destroy()
        
        ctk.CTkButton(d, text="AGENDAR", fg_color=self.col_blue, command=save).pack(pady=20)