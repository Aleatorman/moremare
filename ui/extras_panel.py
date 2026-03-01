import customtkinter as ctk
from ui.tools.aba_calculator import ABACalculator
from ui.tools.graphic_visualizer import GraphicVisualizer

class ExtrasPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        
        self._setup_ui()

    def _setup_ui(self):
        # Contenedor principal
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(fill="both", expand=True)
        
        # --- PANTALLA DE MENÚ (GRID DE BOTONES) ---
        self.menu_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.menu_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.menu_frame, text="Herramientas Adicionales", font=("Arial", 22, "bold")).pack(anchor="w", pady=(0, 20))
        ctk.CTkLabel(self.menu_frame, text="Selecciona una utilidad para complementar el proceso:", text_color="gray").pack(anchor="w", pady=(0, 20))

        # Grid de Botones
        grid = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        grid.pack(fill="both", expand=True)

        # HERRAMIENTA 1: ABA
        self._create_tool_card(grid, 0, 0, "📈", "Registro Conductual (ABA)", 
                               "Calculadora de Tasa, Frecuencia y Duración en tiempo real.", 
                               self._open_aba)

        # HERRAMIENTA 2: GRÁFICO
        self._create_tool_card(grid, 0, 1, "📊", "Visualizador Gráfico", 
                               "Gráficos de línea base, intervención y mantenimiento.", 
                               self._open_graphic)


    def _create_tool_card(self, parent, r, c, icon, title, desc, command):
        card = ctk.CTkButton(parent, text="", fg_color=("white", "gray25"), 
                             corner_radius=15, border_width=1, border_color="gray",
                             hover_color=("gray90", "gray30"),
                             height=150, width=250, command=command)
        card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
        
        # Truco para poner contenido dentro del botón (usando un frame transparente encima no clickeable o labels dentro)
        # CustomTkinter no deja poner widgets DENTRO de un botón fácilmente.
        # Así que mejor hacemos un Frame que actúe como botón o usamos el texto del botón.
        
        # Opción simple: Texto del botón con saltos de línea
        full_text = f"{icon}\n\n{title}\n\n{desc}"
        card.configure(text=full_text, font=("Arial", 14), anchor="center")

    def _open_aba(self):
        # Limpiar y mostrar herramienta
        for w in self.main_content.winfo_children(): w.pack_forget()
        
        tool_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        tool_frame.pack(fill="both", expand=True)
        
        # Botón volver
        ctk.CTkButton(tool_frame, text="← Volver al Menú", fg_color="transparent", text_color="gray", anchor="w",
                      command=lambda: self._back_to_menu(tool_frame)).pack(fill="x", pady=10)
        
        # Cargar la calculadora
        ABACalculator(tool_frame).pack(fill="both", expand=True)

    def _back_to_menu(self, current_frame):
        current_frame.destroy()
        self.menu_frame.pack(fill="both", expand=True)

    def _open_graphic(self):
        for w in self.main_content.winfo_children(): w.pack_forget()

        tool_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        tool_frame.pack(fill="both", expand=True)

        ctk.CTkButton(tool_frame, text="← Volver al Menú", fg_color="transparent", text_color="gray", anchor="w",
                  command=lambda: self._back_to_menu(tool_frame)).pack(fill="x", pady=10)

        GraphicVisualizer(tool_frame).pack(fill="both", expand=True)