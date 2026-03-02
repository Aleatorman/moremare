import customtkinter as ctk
from src.clinical.patient_manager import PatientManager
from ui.micro_panel import MicroPanel
from ui.macro_panel import MacroPanel
from ui.genesis_panel import GenesisPanel
from ui.intervention_panel import InterventionPanel
from ui.report_panel import ReportPanel
from ui.extras_panel import ExtrasPanel

class ClinicalWindow(ctk.CTkToplevel):
    def __init__(self, patient_id, parent_dashboard):
        super().__init__()
        
        # Configuración de Ventana
        self.after(100, self.lift) 
        self.focus_force() 
        self.grab_set() 
        
        self.patient_id = patient_id
        self.parent_dashboard = parent_dashboard 
        self.patient_manager = PatientManager()
        self.patient_data = self.patient_manager.get_patient_by_id(patient_id)
        
        title_name = self.patient_data['code_name'] if self.patient_data else "Desconocido"
        self.title(f"Expediente Clínico: {title_name}")
        self.geometry("1200x750")
        
        # Layout Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Diccionario para guardar referencias a los botones (para cambiarles el color)
        self.nav_buttons = {} 

        self._setup_sidebar()
        self._setup_content_area()
        
        # Iniciar en Datos Generales
        self.show_module("datos")

    def _setup_sidebar(self):
        """Menú lateral moderno y oscuro."""
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#2b2b2b") # Gris oscuro elegante
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Título del Paciente (Arriba)
        p_name = self.patient_data['code_name'] if self.patient_data else "Paciente"
        ctk.CTkLabel(self.sidebar, text=p_name, font=("Roboto", 20, "bold"), text_color="white").pack(pady=(30, 5), padx=10)
        ctk.CTkLabel(self.sidebar, text="EXPEDIENTE ACTIVO", font=("Roboto", 10), text_color="gray").pack(pady=(0, 30))
        
        # Botones de Navegación (Estilo "Drawer")
        # Usamos Emojis como iconos para no cargar imagenes externas y mantenerlo ligero
        self._create_nav_btn("👤  Datos Generales", "datos")
        self._create_nav_btn("🔬  Microcontingencias", "micro")
        self._create_nav_btn("🌐  Macrocontingencias", "macro")
        self._create_nav_btn("📜  Génesis e Historia", "genesis")
        self._create_nav_btn("🛠️  Intervención", "interv")
        self._create_nav_btn("🧩  Herramientas Extra", "extras")
        
        # Espaciador
        ctk.CTkLabel(self.sidebar, text="").pack(expand=True)
        
        # Botón Reporte (Destacado)
        self._create_nav_btn("📄  Generar Informe", "reporte", is_special=True)
        
        # Botón Salir
        ctk.CTkButton(self.sidebar, text="← Volver al Panel", fg_color="transparent", 
                      border_width=1, border_color="gray", text_color="gray",
                      command=self.destroy).pack(pady=20, padx=20, fill="x")

    def _create_nav_btn(self, text, module_name, is_special=False):
        """Crea un botón y lo guarda en el diccionario."""
        
        # Color base: Transparente. Color hover: Gris suave.
        btn = ctk.CTkButton(self.sidebar, 
                            text=text, 
                            height=45,
                            corner_radius=8,
                            anchor="w", # Alinear texto a la izquierda
                            font=("Roboto", 13, "bold"),
                            fg_color="transparent" if not is_special else "#27ae60",
                            text_color="white",
                            hover_color="#404040" if not is_special else "#2ecc71",
                            command=lambda: self.show_module(module_name))
        
        btn.pack(pady=3, padx=10, fill="x")
        self.nav_buttons[module_name] = btn # Guardar referencia

    def _highlight_active_btn(self, active_name):
        """Ilumina el botón activo y apaga los demás."""
        for name, btn in self.nav_buttons.items():
            if name == "reporte": continue # El reporte siempre se queda verde

            if name == active_name:
                btn.configure(fg_color="#3498db", text_color="white") # Azul "Activo"
            else:
                btn.configure(fg_color="transparent", text_color="gray90") # Transparente "Inactivo"

    def _setup_content_area(self):
        """Área blanca derecha."""
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("gray95", "gray15")) # Fondo claro suave
        self.content_frame.grid(row=0, column=1, sticky="nsew")

    def show_module(self, module_name):
        """Cambia el contenido y actualiza el menú."""
        
        # 1. Iluminar el botón correcto
        self._highlight_active_btn(module_name)
        
        # 2. Limpiar contenido anterior
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        # 3. Cargar el módulo nuevo (Con márgenes para que respire el diseño)
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        if module_name == "datos":
            self._render_datos_generales(container)
        elif module_name == "micro":
            MicroPanel(container, self.patient_id).pack(fill="both", expand=True)
        elif module_name == "macro":
            MacroPanel(container, self.patient_id).pack(fill="both", expand=True)
        elif module_name == "genesis":
            GenesisPanel(container, self.patient_id).pack(fill="both", expand=True)
        elif module_name == "interv":
            InterventionPanel(container, self.patient_id).pack(fill="both", expand=True)
        elif module_name == "extras":
            ExtrasPanel(container, self.patient_id).pack(fill="both", expand=True)
        elif module_name == "reporte":
            ReportPanel(container, self.patient_id).pack(fill="both", expand=True)

    def _render_datos_generales(self, parent):
        """Diseño mejorado de la ficha de datos."""
        # Título
        ctk.CTkLabel(parent, text="Resumen del Paciente", font=("Roboto", 28, "bold"), text_color=("gray20", "white")).pack(anchor="w", pady=(0, 20))
        
        # Tarjeta de Datos (Card View)
        card = ctk.CTkFrame(parent, fg_color=("white", "gray25"), corner_radius=15, border_width=1, border_color=("gray80", "gray30"))
        card.pack(fill="x", pady=10, ipady=10)

        # Grid de datos
        p = self.patient_data
        if p:
            self._add_info_row(card, "Nombre / Código:", p['code_name'], 0)
            self._add_info_row(card, "Edad:", str(p['age']) + " años", 1)
            self._add_info_row(card, "Sexo:", p['sex'], 2)
            self._add_info_row(card, "Ocupación:", p['occupation'], 3)
        
        # Motivo y Metas
        ctk.CTkLabel(parent, text="Motivo de Consulta", font=("Roboto", 16, "bold"), text_color="gray").pack(anchor="w", pady=(30, 5))
        
        m_box = ctk.CTkTextbox(parent, height=80, corner_radius=10, fg_color=("white", "gray20"), border_width=1, border_color="gray80")
        m_box.pack(fill="x")
        m_box.insert("0.0", p['motive'])
        m_box.configure(state="disabled")

        ctk.CTkLabel(parent, text="Metas y Expectativas", font=("Roboto", 16, "bold"), text_color="gray").pack(anchor="w", pady=(20, 5))
        
        g_box = ctk.CTkTextbox(parent, height=80, corner_radius=10, fg_color=("white", "gray20"), border_width=1, border_color="gray80")
        g_box.pack(fill="x")
        goals = p.get('goals', 'Sin especificar')
        g_box.insert("0.0", goals)
        g_box.configure(state="disabled")

    def _add_info_row(self, parent, label, value, row_idx):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(f, text=label, font=("Roboto", 12, "bold"), width=150, anchor="w", text_color="gray").pack(side="left")
        ctk.CTkLabel(f, text=value, font=("Roboto", 14), anchor="w").pack(side="left")