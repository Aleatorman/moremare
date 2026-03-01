import customtkinter as ctk
from src.clinical.patient_manager import PatientManager
from ui.micro_panel import MicroPanel
from ui.macro_panel import MacroPanel

class ClinicalWindow(ctk.CTkToplevel):
    def __init__(self, patient_id, parent_dashboard):
        super().__init__()

        self.after(100, self.lift) # Levanta la ventana sobre las demás
        self.focus_force() # Fuerza el foco del teclado en esta ventana
        self.grab_set() #        

        self.patient_id = patient_id
        self.parent_dashboard = parent_dashboard # Para refrescar si cambiamos algo
        self.patient_manager = PatientManager()
        
        # Cargar datos del paciente
        self.patient_data = self.patient_manager.get_patient_by_id(patient_id)
        
        # Configuración de ventana
        title_name = self.patient_data['code_name'] if self.patient_data else "Desconocido"
        self.title(f"Expediente Clínico: {title_name}")
        self.geometry("1100x700")
        
        # Layout Principal: Menú Lateral (izq) + Contenido (der)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._setup_sidebar()
        self._setup_content_area()
        
        # Iniciar en la primera pantalla
        self.show_module("datos")

    def _setup_sidebar(self):
        """Crea el menú lateral con navegación."""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Título del menú
        lbl_title = ctk.CTkLabel(self.sidebar, text="Módulos", font=("Roboto", 20, "bold"))
        lbl_title.pack(pady=20)
        
        # Botones de Navegación
        # Guardamos referencias para cambiar colores (Semáforo) luego
        self.btn_datos = self._create_nav_btn("1. Datos Generales", "datos")
        self.btn_micro = self._create_nav_btn("2. Microcontingencias", "micro")
        self.btn_macro = self._create_nav_btn("3. Macrocontingencias", "macro")
        self.btn_genesis = self._create_nav_btn("4. Génesis e Historia", "genesis")
        self.btn_interv = self._create_nav_btn("5. Intervención", "interv")
        self.btn_report = self._create_nav_btn("📄 Generar Informe", "reporte", fg_color="green")

    def _create_nav_btn(self, text, module_name, fg_color="transparent"):
        """Ayudante para crear botones estandarizados."""
        btn = ctk.CTkButton(self.sidebar, text=text, fg_color=fg_color, anchor="w",
                            command=lambda: self.show_module(module_name))
        btn.pack(pady=5, padx=10, fill="x")
        return btn

    def _setup_content_area(self):
        """El área derecha donde cambiaremos las pantallas."""
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_module(self, module_name):
        """Cambia el contenido del panel derecho."""
        # 1. Limpiar lo que haya antes
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # 2. Cargar el módulo nuevo
        if module_name == "datos":
            self._render_datos_generales()
            
        elif module_name == "micro":
            # Aquí es donde estaba el error. Fíjate en el espacio a la izquierda:
            panel = MicroPanel(self.content_frame, self.patient_id)
            panel.pack(fill="both", expand=True)
            
        elif module_name == "macro":
            self._render_placeholder("Sistema Macrocontingencial")
            
        elif module_name == "genesis":
            self._render_placeholder("Génesis del Problema")
            
        elif module_name == "interv":
            self._render_placeholder("Plan de Intervención")
            
        elif module_name == "reporte":
            self._render_placeholder("Generador de Reportes")
        # 1. Limpiar lo que haya antes
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # 2. Cargar el módulo nuevo
        if module_name == "datos":
            self._render_datos_generales()
            
        elif module_name == "micro":
            # ---> AQUÍ ESTABA EL ERROR: Asegúrate de que estas líneas estén indentadas
            panel = MicroPanel(self.content_frame, self.patient_id)
            panel.pack(fill="both", expand=True)
            
        elif module_name == "macro":
            panel = MacroPanel(self.content_frame, self.patient_id)
            panel.pack(fill="both", expand=True)
            
        elif module_name == "genesis":
            self._render_placeholder("Génesis del Problema")
            
        elif module_name == "interv":
            self._render_placeholder("Plan de Intervención")
            
        elif module_name == "reporte":
            self._render_placeholder("Generador de Reportes")

    def _render_placeholder(self, title):
        """Muestra un aviso de construcción (temporal)."""
        ctk.CTkLabel(self.content_frame, text=title, font=("Roboto", 24, "bold")).pack(pady=20)
        ctk.CTkLabel(self.content_frame, text="Módulo en desarrollo...", text_color="gray").pack()

    def _render_datos_generales(self):
        """Muestra los datos del Módulo 1 (Solo lectura por ahora)."""
        ctk.CTkLabel(self.content_frame, text="1. Datos Generales", font=("Roboto", 24, "bold")).pack(anchor="w", pady=(0, 20))
        
        # Grid simple para mostrar info
        info_frame = ctk.CTkFrame(self.content_frame)
        info_frame.pack(fill="x", anchor="n")
        
        # Helper para filas
        def add_row(parent, label, value, r):
            ctk.CTkLabel(parent, text=label, font=("Roboto", 12, "bold")).grid(row=r, column=0, sticky="w", padx=10, pady=5)
            ctk.CTkLabel(parent, text=value).grid(row=r, column=1, sticky="w", padx=10, pady=5)

        p = self.patient_data
        if p:
            add_row(info_frame, "Nombre / Código:", p['code_name'], 0)
            add_row(info_frame, "Edad:", str(p['age']), 1)
            add_row(info_frame, "Sexo:", p['sex'], 2)
            add_row(info_frame, "Ocupación:", p['occupation'], 3)
            
            ctk.CTkLabel(self.content_frame, text="Motivo de Consulta:", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(20, 5))
            
            motive_box = ctk.CTkTextbox(self.content_frame, height=100)
            motive_box.pack(fill="x")
            motive_box.insert("0.0", p['motive'])
            motive_box.configure(state="disabled") # Solo lectura