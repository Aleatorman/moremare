import customtkinter as ctk
from tkinter import messagebox
from src.clinical.macro.macro_manager import MacroManager

class LegendWindow(ctk.CTkToplevel):
    """Ventana de ayuda con definiciones y UN CASO PRÁCTICO"""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Guía de Referencia y Ejemplo Práctico")
        self.geometry("800x700")
        self.transient(parent)
        self.grab_set()
        
        self._setup_ui()

    def _setup_ui(self):
        # Título
        ctk.CTkLabel(self, text="Guía de Códigos: Ejemplo 'El Estudiante'", font=("Arial", 18, "bold"), text_color="#2c3e50").pack(pady=(15, 5))
        ctk.CTkLabel(self, text="Caso: Pedro dice querer graduarse, pero sale de fiesta y reprueba.", font=("Arial", 12), text_color="#7f8c8d").pack(pady=(0, 10))
        
        # Scroll Principal
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=5)
        
        # --- SECCIÓN 1: EL SUJETO (PEDRO) ---
        self._add_section_header(scroll, "👤 EL SUJETO (Pedro)", "#3498db")
        
        self._add_card(scroll, "SsE", "Sustitutiva Ejemplar (Creer/Decir en contexto ideal)",
                       "Pedro dice en casa: 'Debo estudiar mucho para ser un profesional exitoso'.")
        
        self._add_card(scroll, "SꞩE", "No Sustitutiva Ejemplar (Hacer en contexto ideal)",
                       "Pedro asiste a clases, compra libros y se inscribe a tiempo.")
        
        self._add_card(scroll, "SsɆ", "Sustitutiva NO Ejemplar (Creer/Decir en situación problema)",
                       "Pedro dice en la fiesta: 'La vida es corta, una falta no me afecta'.")
        
        self._add_card(scroll, "SꞩɆ", "No Sustitutiva NO Ejemplar (Hacer en situación problema)",
                       "Pedro falta los lunes, no entrega tareas y se embriaga.")

        # --- SECCIÓN 2: LOS OTROS (LA FAMILIA) ---
        self._add_section_header(scroll, "👥 LOS OTROS (Familia)", "#e67e22")

        self._add_card(scroll, "OsE", "Sustitutiva Ejemplar (Valores explícitos del grupo)",
                       "La familia dice: 'Aquí lo más importante es la responsabilidad'.")
        
        self._add_card(scroll, "OꞩE", "No Sustitutiva Ejemplar (Exigencias formales)",
                       "Pagan la colegiatura puntual y revisan sus boletas de calificaciones.")
        
        self._add_card(scroll, "OsɆ", "Sustitutiva NO Ejemplar (Lo que dicen en el conflicto)",
                       "Dicen: 'Pobrecito, está estresado, déjenlo divertirse un poco'.")
        
        self._add_card(scroll, "OꞩɆ", "No Sustitutiva NO Ejemplar (Lo que permiten en la práctica)",
                       "Le dan dinero extra para alcohol y le perdonan llegar tarde.")

        # Botón Cerrar
        ctk.CTkButton(self, text="Entendido, volver a la matriz", fg_color="#3498db", height=40, command=self.destroy).pack(pady=15)

    def _add_section_header(self, parent, text, color):
        ctk.CTkLabel(parent, text=text, font=("Arial", 14, "bold"), text_color=color).pack(anchor="w", pady=(15, 5))

    def _add_card(self, parent, code, title, example):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=6, border_width=1, border_color="#ddd")
        card.pack(fill="x", pady=4)
        
        # Columna Izq: Código
        left = ctk.CTkFrame(card, fg_color="transparent", width=60)
        left.pack(side="left", padx=10, pady=5)
        ctk.CTkLabel(left, text=code, font=("Arial", 16, "bold"), text_color="#2c3e50").pack()

        # Columna Der: Info
        right = ctk.CTkFrame(card, fg_color="transparent")
        right.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(right, text=title, font=("Arial", 11, "bold"), text_color="gray").pack(anchor="w")
        ctk.CTkLabel(right, text=f'"{example}"', font=("Arial", 12), text_color="#333", wraplength=550, justify="left").pack(anchor="w")


class MatrixWindow(ctk.CTkToplevel):
    """Ventana flotante con la Tabla Teórica de 8x8"""
    def __init__(self, parent, current_points, on_close_callback):
        super().__init__(parent)
        self.title("Matriz de Interacciones Macrocontingenciales")
        self.geometry("980x780") 
        self.transient(parent)
        self.grab_set()
        
        self.active_points = set(current_points)
        self.on_close_callback = on_close_callback
        self.buttons = {} 

        self.headers = ["SsE", "SꞩE", "SsɆ", "SꞩɆ", "OsE", "OꞩE", "OsɆ", "OꞩɆ"]

        self._setup_ui()

    def _setup_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(pady=10, fill="x")
        
        ctk.CTkLabel(top_frame, text="Matriz de Interacción (8x8)", font=("Arial", 18, "bold")).pack()
        
        # BOTÓN DE AYUDA DESTACADO
        ctk.CTkButton(top_frame, text="📖 Ver Ejemplo y Simbología", fg_color="#8e44ad", hover_color="#9b59b6", 
                      width=220, command=self._open_legend).pack(pady=5)
        
        ctk.CTkLabel(top_frame, text="Haz clic en las intersecciones (Triángulo Inferior) para marcar.", text_color="gray").pack()

        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(expand=True, padx=20, pady=5)

        header_font = ("Arial", 11, "bold") 
        text_col = "#2c3e50"

        # Encabezados Columnas
        for col, text in enumerate(self.headers):
            lbl = ctk.CTkLabel(grid_frame, text=text, font=header_font, width=60, text_color=text_col)
            lbl.grid(row=0, column=col+1, padx=2, pady=5)

        # Encabezados Filas
        for row, text in enumerate(self.headers):
            lbl = ctk.CTkLabel(grid_frame, text=text, font=header_font, width=60, text_color=text_col)
            lbl.grid(row=row+1, column=0, padx=5, pady=2)

        # GENERACIÓN MATRIZ 8x8 (Con Bloqueo Diagonal Principal + Superior)
        for r in range(8):
            for c in range(8):
                key = (r, c)
                
                # Bloquear si Columna >= Fila
                if c >= r:
                    btn = ctk.CTkButton(grid_frame, text="", width=60, height=45, 
                                        fg_color="#444444", state="disabled", border_width=0)
                else:
                    is_active = key in self.active_points
                    bg_color = "#2ecc71" if is_active else "#ecf0f1"
                    hover_color = "#27ae60" if is_active else "#bdc3c7"

                    btn = ctk.CTkButton(grid_frame, text="", width=60, height=45, 
                                        fg_color=bg_color, hover_color=hover_color,
                                        border_width=1, border_color="#dcdcdc",
                                        command=lambda k=key: self._toggle_point(k))
                    self.buttons[key] = btn 
                
                btn.grid(row=r+1, column=c+1, padx=2, pady=2)

        ctk.CTkButton(self, text="Listo / Terminar Selección", height=40, font=("Arial", 12, "bold"),
                      fg_color="#3498db", command=self._close).pack(pady=15)

    def _open_legend(self):
        LegendWindow(self)

    def _toggle_point(self, key):
        if key in self.active_points:
            self.active_points.remove(key)
            self.buttons[key].configure(fg_color="#ecf0f1", hover_color="#bdc3c7")
        else:
            self.active_points.add(key)
            self.buttons[key].configure(fg_color="#2ecc71", hover_color="#27ae60")

    def _close(self):
        self.on_close_callback(list(self.active_points))
        self.destroy()


class MacroPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = MacroManager()
        self.current_macro_id = None
        self.matrix_points = [] 

        self._setup_ui()
        self._refresh_history()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="3. Análisis Macrocontingencial", font=("Arial", 22, "bold"), text_color="#333").pack(anchor="w", pady=(0, 10))

        self.tabview = ctk.CTkTabview(self, width=900, height=600)
        self.tabview.pack(fill="both", expand=True)

        self.tabview.add("Nueva Macrocontingencia")
        self.tabview.add("Historial Guardado")
        
        self._setup_tab_capture(self.tabview.tab("Nueva Macrocontingencia"))
        self._setup_tab_history(self.tabview.tab("Historial Guardado"))

    def _setup_tab_capture(self, parent_frame):
        scroll = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # 1. Datos del Grupo
        ctk.CTkLabel(scroll, text="1. Grupo de Referencia:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        self.entry_group = ctk.CTkEntry(scroll, placeholder_text="Ej: Familia, Trabajo...", height=35)
        self.entry_group.pack(fill="x", padx=10, pady=5)

        # 2. Prácticas
        self._section_header(scroll, "A. Prácticas del USUARIO")
        self.txt_u_eff = self._area_input(scroll, "Práctica Efectiva (Hacer):")
        self.txt_u_sub = self._area_input(scroll, "Práctica Sustitutiva (Decir/Creer):")

        self._section_header(scroll, "B. Prácticas del GRUPO")
        self.txt_o_eff = self._area_input(scroll, "Práctica Efectiva (Exigencias/Costumbres):")
        self.txt_o_sub = self._area_input(scroll, "Práctica Sustitutiva (Valores/Normas):")

        # 3. Matriz
        self._section_header(scroll, "C. Matriz de Interacción")
        
        self.btn_open_matrix = ctk.CTkButton(scroll, text="📊 ABRIR MATRIZ (0 marcados)", 
                                             height=45, fg_color="#8e44ad", hover_color="#9b59b6", font=("Arial", 12, "bold"),
                                             command=self._open_matrix_window)
        self.btn_open_matrix.pack(fill="x", padx=20, pady=10)

        # Notas
        ctk.CTkLabel(scroll, text="Conclusión / Notas:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
        self.txt_notes = ctk.CTkTextbox(scroll, height=80)
        self.txt_notes.pack(fill="x", padx=10, pady=5)

        # Botones
        action_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        action_frame.pack(fill="x", pady=20)
        ctk.CTkButton(action_frame, text="Nueva / Limpiar", fg_color="gray", width=120, command=self._reset_form).pack(side="left", padx=10)
        ctk.CTkButton(action_frame, text="💾 GUARDAR ANÁLISIS", fg_color="#27ae60", width=180, command=self._save).pack(side="right", padx=10)

    def _setup_tab_history(self, parent_frame):
        ctk.CTkButton(parent_frame, text="🔄 Actualizar Lista", command=self._refresh_history, fg_color="gray").pack(anchor="e", pady=5)
        self.scroll_hist = ctk.CTkScrollableFrame(parent_frame, fg_color="transparent")
        self.scroll_hist.pack(fill="both", expand=True)

    def _section_header(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Arial", 13, "bold"), text_color="#2c3e50").pack(anchor="w", padx=10, pady=(15, 5))

    def _area_input(self, parent, label):
        ctk.CTkLabel(parent, text=label, font=("Arial", 11), text_color="gray").pack(anchor="w", padx=15)
        entry = ctk.CTkEntry(parent, height=30) 
        entry.pack(fill="x", padx=15, pady=(0, 5))
        return entry

    def _open_matrix_window(self):
        MatrixWindow(self, self.matrix_points, self._on_matrix_closed)

    def _on_matrix_closed(self, new_points):
        self.matrix_points = new_points
        count = len(self.matrix_points)
        self.btn_open_matrix.configure(text=f"📊 ABRIR MATRIZ ({count} marcados)")

    def _save(self):
        name = self.entry_group.get()
        if not name: return messagebox.showwarning("Error", "Falta el nombre del grupo.")
        
        data = {
            'group_name': name,
            'u_eff': self.txt_u_eff.get(), 'u_sub': self.txt_u_sub.get(),
            'o_eff': self.txt_o_eff.get(), 'o_sub': self.txt_o_sub.get(),
            'notes': self.txt_notes.get("1.0", "end-1c")
        }
        
        s, m = self.manager.save_macro(self.patient_id, self.current_macro_id, data, self.matrix_points)
        if s:
            messagebox.showinfo("Éxito", m)
            self._refresh_history()
            self._reset_form() 
        else:
            messagebox.showerror("Error", m)

    def _refresh_history(self):
        for w in self.scroll_hist.winfo_children(): w.destroy()
        macros = self.manager.get_macros(self.patient_id)
        if not macros:
            ctk.CTkLabel(self.scroll_hist, text="No hay registros guardados.", text_color="gray").pack(pady=20)
            return

        for m in macros:
            row = ctk.CTkFrame(self.scroll_hist, fg_color="white", corner_radius=6)
            row.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(row, text=f"📂 {m[1]}", font=("Arial", 14, "bold"), text_color="#333").pack(side="left", padx=15, pady=10)
            ctk.CTkButton(row, text="Editar / Ver", width=100, fg_color="#3498db", 
                          command=lambda i=m[0]: self._load_macro(i)).pack(side="right", padx=10)

    def _load_macro(self, mid):
        data = self.manager.get_full_macro(mid)
        if not data: return
        self.current_macro_id = data['id']
        self.entry_group.delete(0, "end"); self.entry_group.insert(0, data['group_name'])
        self.txt_u_eff.delete(0, "end"); self.txt_u_eff.insert(0, data['user_effective'])
        self.txt_u_sub.delete(0, "end"); self.txt_u_sub.insert(0, data['user_substitutive'])
        self.txt_o_eff.delete(0, "end"); self.txt_o_eff.insert(0, data['other_effective'])
        self.txt_o_sub.delete(0, "end"); self.txt_o_sub.insert(0, data['other_substitutive'])
        self.txt_notes.delete("1.0", "end"); self.txt_notes.insert("0.0", data['analysis_notes'])
        self.matrix_points = data.get('matrix_points', [])
        self.btn_open_matrix.configure(text=f"📊 ABRIR MATRIZ ({len(self.matrix_points)} marcados)")
        self.tabview.set("Nueva Macrocontingencia")

    def _reset_form(self):
        self.current_macro_id = None
        self.entry_group.delete(0, "end")
        self.txt_u_eff.delete(0, "end"); self.txt_u_sub.delete(0, "end")
        self.txt_o_eff.delete(0, "end"); self.txt_o_sub.delete(0, "end")
        self.txt_notes.delete("1.0", "end")
        self.matrix_points = []
        self.btn_open_matrix.configure(text="📊 ABRIR MATRIZ (0 marcados)")