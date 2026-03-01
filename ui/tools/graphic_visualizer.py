import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphicVisualizer(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Datos en memoria
        # Formato: [{'session': 1, 'value': 10}, ...]
        self.data_points = []
        
        # Fases (Líneas verticales)
        self.phases = {}

        self._setup_ui()

    def _setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=10)
        ctk.CTkLabel(header, text="Visualizador Gráfico de Progreso", font=("Arial", 20, "bold")).pack(side="left")

        # Layout Principal (Izquierda: Controles / Derecha: Gráfico)
        main_layout = ctk.CTkFrame(self, fg_color="transparent")
        main_layout.pack(fill="both", expand=True)

        # --- PANEL IZQUIERDO: DATOS ---
        left_col = ctk.CTkFrame(main_layout, width=300, fg_color=("white", "gray25"), corner_radius=10)
        left_col.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(left_col, text="Ingreso de Datos", font=("Arial", 14, "bold")).pack(pady=10)

        # Entrada de Puntos
        input_frame = ctk.CTkFrame(left_col, fg_color="transparent")
        input_frame.pack(fill="x", padx=10)
        
        self.entry_val = ctk.CTkEntry(input_frame, placeholder_text="Valor (ej: 5)", width=100)
        self.entry_val.pack(side="left", padx=5)
        
        ctk.CTkButton(input_frame, text="+ Punto", width=80, fg_color="#3498db", command=self._add_point).pack(side="left", padx=5)

        # Entrada de Fases
        ctk.CTkLabel(left_col, text="Configurar Fases", font=("Arial", 14, "bold")).pack(pady=(20, 10))
        
        phase_frame = ctk.CTkFrame(left_col, fg_color="transparent")
        phase_frame.pack(fill="x", padx=10)
        
        self.combo_phase = ctk.CTkComboBox(phase_frame, values=["Línea Base", "Intervención", "Mantenimiento"], width=140)
        self.combo_phase.pack(side="left", padx=5)
        
        # Botón para marcar inicio de fase
        ctk.CTkButton(phase_frame, text="Marcar Inicio", width=100, fg_color="#e67e22", command=self._set_phase).pack(side="left", padx=5)

        # Lista de Datos
        ctk.CTkLabel(left_col, text="Historial:", text_color="gray").pack(anchor="w", padx=15, pady=(20, 5))
        self.txt_history = ctk.CTkTextbox(left_col, height=200)
        self.txt_history.pack(fill="x", padx=10, pady=5)
        
        # Botón Limpiar (CORREGIDO)
        ctk.CTkButton(left_col, text="🗑️ Borrar Todo", fg_color="transparent", border_width=1, border_color="red", text_color="red", hover_color="#fee", command=self._clear_all).pack(side="bottom", pady=20)

        # --- PANEL DERECHO: GRÁFICO ---
        self.right_col = ctk.CTkFrame(main_layout, fg_color="white", corner_radius=10)
        self.right_col.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Inicializar gráfico vacío
        self._init_plot()

    def _init_plot(self):
        # Crear Figura de Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.ax.set_title("Gráfico de Análisis Conductual")
        self.ax.set_xlabel("Sesiones")
        self.ax.set_ylabel("Frecuencia / Medida")
        self.ax.grid(True, linestyle='--', alpha=0.6)

        # Canvas de Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_col)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _update_plot(self):
        self.ax.clear()
        self.ax.set_title("Gráfico de Análisis Conductual")
        self.ax.set_xlabel("Sesiones")
        self.ax.set_ylabel("Frecuencia / Medida")
        self.ax.grid(True, linestyle='--', alpha=0.6)

        if not self.data_points:
            self.canvas.draw()
            return

        # Extraer coordenadas
        x_vals = [p['session'] for p in self.data_points]
        y_vals = [p['value'] for p in self.data_points]

        # Dibujar línea principal
        self.ax.plot(x_vals, y_vals, marker='o', color='black', linestyle='-', linewidth=1.5, markersize=6)

        # Dibujar Líneas de Cambio de Fase
        for session_num, phase_name in self.phases.items():
            line_pos = session_num - 0.5 
            self.ax.axvline(x=line_pos, color='red', linestyle='--', linewidth=2)
            
            y_max = max(y_vals) if y_vals else 10
            self.ax.text(line_pos + 0.1, y_max, phase_name, color='red', fontsize=9, fontweight='bold', rotation=0)

        self.canvas.draw()

    def _add_point(self):
        try:
            val = float(self.entry_val.get())
            session_num = len(self.data_points) + 1
            
            self.data_points.append({'session': session_num, 'value': val})
            
            self.txt_history.insert("end", f"Sesión {session_num}: {val}\n")
            self.entry_val.delete(0, "end")
            
            self._update_plot()
            
        except ValueError:
            messagebox.showerror("Error", "Ingresa un número válido")

    def _set_phase(self):
        if not self.data_points:
            messagebox.showwarning("Atención", "Agrega al menos un punto de datos primero.")
            return
            
        next_session = len(self.data_points) + 1
        name = self.combo_phase.get()
        
        self.phases[next_session] = name
        messagebox.showinfo("Fase Configurada", f"La próxima sesión ({next_session}) iniciará la fase: {name}")

    def _clear_all(self):
        if messagebox.askyesno("Borrar", "¿Reiniciar el gráfico?"):
            self.data_points = []
            self.phases = {}
            self.txt_history.delete("1.0", "end")
            self._update_plot()