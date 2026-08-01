import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

class GraphicVisualizer(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Datos en memoria. Formato: [{'session': 1, 'val_a': 10, 'val_b': 2}, ...]
        self.data_points = []
        self.phases = {}

        self._setup_ui()

    def _setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=10)
        ctk.CTkLabel(header, text="Visualizador Gráfico de Progreso (Diseño N=1)", font=("Arial", 20, "bold")).pack(side="left")

        main_layout = ctk.CTkFrame(self, fg_color="transparent")
        main_layout.pack(fill="both", expand=True)

        # --- PANEL IZQUIERDO: DATOS ---
        left_col = ctk.CTkFrame(main_layout, width=320, fg_color=("white", "gray25"), corner_radius=10)
        left_col.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(left_col, text="Ingreso de Datos por Sesión", font=("Arial", 14, "bold")).pack(pady=10)

        input_frame = ctk.CTkFrame(left_col, fg_color="transparent")
        input_frame.pack(fill="x", padx=10)
        
        # VARIABLE A (Conducta Problema)
        ctk.CTkLabel(input_frame, text="Variable A (Ej. Conducta a reducir):", text_color="#c0392b", font=("Arial", 11, "bold")).pack(anchor="w", pady=(5,0))
        self.entry_val_a = ctk.CTkEntry(input_frame, placeholder_text="Valor A", width=120)
        self.entry_val_a.pack(anchor="w", pady=5)

        # VARIABLE B (Conducta Alternativa)
        ctk.CTkLabel(input_frame, text="Variable B (Ej. Conducta a aumentar):", text_color="#27ae60", font=("Arial", 11, "bold")).pack(anchor="w", pady=(5,0))
        self.entry_val_b = ctk.CTkEntry(input_frame, placeholder_text="Valor B", width=120)
        self.entry_val_b.pack(anchor="w", pady=5)
        
        ctk.CTkButton(input_frame, text="+ Añadir Punto a la Gráfica", fg_color="#3498db", command=self._add_point).pack(fill="x", pady=15)

        # FASES
        ctk.CTkLabel(left_col, text="Configurar Fases (Línea Base, etc.)", font=("Arial", 14, "bold")).pack(pady=(20, 10))
        
        phase_frame = ctk.CTkFrame(left_col, fg_color="transparent")
        phase_frame.pack(fill="x", padx=10)
        
        self.combo_phase = ctk.CTkComboBox(phase_frame, values=["Línea Base", "Intervención", "Mantenimiento"], width=140)
        self.combo_phase.pack(side="left", padx=5)
        
        ctk.CTkButton(phase_frame, text="Marcar Inicio", width=100, fg_color="#e67e22", command=self._set_phase).pack(side="left", padx=5)

        # HISTORIAL
        ctk.CTkLabel(left_col, text="Historial de Registros:", text_color="gray").pack(anchor="w", padx=15, pady=(20, 5))
        self.txt_history = ctk.CTkTextbox(left_col, height=150)
        self.txt_history.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(left_col, text="🗑️ Borrar Todo", fg_color="transparent", border_width=1, border_color="red", text_color="red", hover_color="#fee", command=self._clear_all).pack(side="bottom", pady=20)

        # --- PANEL DERECHO: GRÁFICO ---
        self.right_col = ctk.CTkFrame(main_layout, fg_color="white", corner_radius=10)
        self.right_col.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self._init_plot()

    def _init_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        self._format_axes()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_col)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _format_axes(self):
        self.ax.set_title("Gráfico de Análisis Conductual (Multivariable)")
        self.ax.set_xlabel("Sesiones")
        self.ax.set_ylabel("Frecuencia / Magnitud")
        self.ax.grid(True, linestyle='--', alpha=0.6)

    def _update_plot(self):
        self.ax.clear()
        self._format_axes()

        if not self.data_points:
            self.canvas.draw()
            return

        x_vals = [p['session'] for p in self.data_points]
        y_a_vals = [p['val_a'] for p in self.data_points]
        y_b_vals = [p['val_b'] for p in self.data_points]

        # Trazar Línea A (Roja - Problema) si hay datos
        if any(not math.isnan(v) for v in y_a_vals):
            self.ax.plot(x_vals, y_a_vals, marker='o', color='#c0392b', linestyle='-', linewidth=2, markersize=6, label="Variable A")

        # Trazar Línea B (Verde - Alternativa) si hay datos
        if any(not math.isnan(v) for v in y_b_vals):
            self.ax.plot(x_vals, y_b_vals, marker='s', color='#27ae60', linestyle='--', linewidth=2, markersize=6, label="Variable B")

        # Leyenda
        if any(not math.isnan(v) for v in y_a_vals) or any(not math.isnan(v) for v in y_b_vals):
            self.ax.legend(loc="upper right")

        # Dibujar Líneas de Cambio de Fase
        for session_num, phase_name in self.phases.items():
            line_pos = session_num - 0.5 
            self.ax.axvline(x=line_pos, color='#34495e', linestyle='-.', linewidth=1.5)
            
            # Colocar el texto de la fase en la parte superior del gráfico
            y_max = self.ax.get_ylim()[1]
            self.ax.text(line_pos + 0.1, y_max * 0.95, phase_name, color='#34495e', fontsize=9, fontweight='bold', rotation=0)

        self.canvas.draw()

    def _add_point(self):
        val_a_str = self.entry_val_a.get().strip()
        val_b_str = self.entry_val_b.get().strip()

        if not val_a_str and not val_b_str:
            messagebox.showwarning("Aviso", "Ingresa al menos un valor en la Variable A o B.")
            return

        try:
            val_a = float(val_a_str) if val_a_str else float('nan')
            val_b = float(val_b_str) if val_b_str else float('nan')
            
            session_num = len(self.data_points) + 1
            self.data_points.append({'session': session_num, 'val_a': val_a, 'val_b': val_b})
            
            # Registrar en el historial
            txt_a = str(val_a) if not math.isnan(val_a) else "-"
            txt_b = str(val_b) if not math.isnan(val_b) else "-"
            self.txt_history.insert("end", f"Sesión {session_num} -> A: {txt_a} | B: {txt_b}\n")
            
            self.entry_val_a.delete(0, "end")
            self.entry_val_b.delete(0, "end")
            self._update_plot()
            
        except ValueError:
            messagebox.showerror("Error", "Ingresa números válidos.")

    def _set_phase(self):
        if not self.data_points:
            messagebox.showwarning("Atención", "Agrega al menos un punto de datos primero antes de marcar una fase.")
            return
            
        next_session = len(self.data_points) + 1
        name = self.combo_phase.get()
        
        self.phases[next_session] = name
        messagebox.showinfo("Fase Configurada", f"La sesión {next_session} iniciará la fase: {name}")

    def _clear_all(self):
        if messagebox.askyesno("Borrar", "¿Estás seguro de reiniciar el gráfico? Se perderán los puntos no guardados."):
            self.data_points = []
            self.phases = {}
            self.txt_history.delete("1.0", "end")
            self._update_plot()