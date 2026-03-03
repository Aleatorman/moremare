import customtkinter as ctk
from tkinter import messagebox
from src.clinical.evaluation.evaluation_manager import EvaluationManager

class EvaluationPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = EvaluationManager()
        self.matrix_data = [] # Lista de diccionarios con las filas de la tabla
        self._setup_ui()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="6. Evaluación del Proceso", font=("Arial", 22, "bold"), text_color="#333").pack(anchor="w", pady=(0, 10))

        leyenda = "📌 NOTA: Este apartado evalúa exclusivamente la eficacia de las estrategias y el desempeño del psicólogo, NO evalúa al paciente."
        ctk.CTkLabel(self, text=leyenda, font=("Roboto", 12, "italic"), text_color="#c0392b").pack(anchor="w", pady=(0, 10))

        self.tabview = ctk.CTkTabview(self, width=900, height=600)
        self.tabview.pack(fill="both", expand=True)
        self.tabview.add("Nueva Evaluación")
        self.tabview.add("Historial de Evaluaciones")

        self._setup_tab_capture(self.tabview.tab("Nueva Evaluación"))
        self._setup_tab_history(self.tabview.tab("Historial de Evaluaciones"))

    def _setup_tab_capture(self, parent):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="Matriz de Evaluación del Proceso Terapéutico", font=("Arial", 14, "bold"), text_color="#2c3e50").pack(anchor="w", pady=10)
        
        # --- Formulario de Entrada para la Matriz ---
        input_frame = ctk.CTkFrame(scroll, fg_color="#F8F9F9", border_width=1, border_color="#ccc")
        input_frame.pack(fill="x", padx=10, pady=5)

        # Fila 1: Target y Parámetro
        r1 = ctk.CTkFrame(input_frame, fg_color="transparent")
        r1.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(r1, text="Objetivo de cambio:").pack(side="left", padx=5)
        self.entry_target = ctk.CTkEntry(r1, width=250, placeholder_text="Ej: Alterar conducta de evitación")
        self.entry_target.pack(side="left", padx=5)

        ctk.CTkLabel(r1, text="Parámetro:").pack(side="left", padx=(15, 5))
        params = ["Adquisición", "Precisión", "Oportunidad", "Relación de efecto", "Tendencia"]
        self.combo_param = ctk.CTkComboBox(r1, values=params, width=180)
        self.combo_param.pack(side="left", padx=5)

        # Fila 2: Calificaciones
        r2 = ctk.CTkFrame(input_frame, fg_color="transparent")
        r2.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(r2, text="Valoración Terapia (0-10):").pack(side="left", padx=5)
        self.entry_val_terapia = ctk.CTkEntry(r2, width=80)
        self.entry_val_terapia.pack(side="left", padx=5)

        ctk.CTkLabel(r2, text="Valoración Terapeuta (0-10):").pack(side="left", padx=(15, 5))
        self.entry_val_terapeuta = ctk.CTkEntry(r2, width=80)
        self.entry_val_terapeuta.pack(side="left", padx=5)

        ctk.CTkButton(r2, text="➕ Agregar a Matriz", fg_color="#3498db", command=self._add_to_matrix).pack(side="right", padx=10)

        # --- Contenedor de la Tabla Visual ---
        self.table_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self.table_container.pack(fill="x", padx=10, pady=15)
        self._render_table()

        # Notas finales
        ctk.CTkLabel(scroll, text="Notas y Observaciones Clínicas:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(20, 0))
        self.txt_notes = ctk.CTkTextbox(scroll, height=100)
        self.txt_notes.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(scroll, text="💾 GUARDAR EVALUACIÓN COMPLETA", fg_color="#27ae60", height=45, command=self._save_all).pack(pady=20)

    def _render_table(self):
        for w in self.table_container.winfo_children(): w.destroy()
        
        if not self.matrix_data:
            ctk.CTkLabel(self.table_container, text="No hay datos en la matriz aún.", text_color="gray").pack()
            return

        # Encabezados
        h = ctk.CTkFrame(self.table_container, fg_color="#34495e")
        h.pack(fill="x")
        ctk.CTkLabel(h, text="Objetivo", width=250, text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(h, text="Parámetro", width=150, text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(h, text="Terapia", width=80, text_color="white").pack(side="left", padx=5)
        ctk.CTkLabel(h, text="Terapeuta", width=80, text_color="white").pack(side="left", padx=5)

        for i, row in enumerate(self.matrix_data):
            f = ctk.CTkFrame(self.table_container, fg_color="white", border_width=1, border_color="#ddd")
            f.pack(fill="x", pady=1)
            ctk.CTkLabel(f, text=row['target'], width=250, anchor="w", text_color="black").pack(side="left", padx=5)
            ctk.CTkLabel(f, text=row['parameter'], width=150, text_color="black").pack(side="left", padx=5)
            ctk.CTkLabel(f, text=row['terapia'], width=80, text_color="black").pack(side="left", padx=5)
            ctk.CTkLabel(f, text=row['terapeuta'], width=80, text_color="black").pack(side="left", padx=5)
            ctk.CTkButton(f, text="x", width=30, fg_color="transparent", text_color="red", command=lambda idx=i: self._remove_row(idx)).pack(side="right")

    def _add_to_matrix(self):
        target = self.entry_target.get()
        terapia = self.entry_val_terapia.get()
        terapeuta = self.entry_val_terapeuta.get()
        
        if not target or not terapia or not terapeuta:
            return messagebox.showwarning("Aviso", "Completa todos los campos de la matriz.")
        
        self.matrix_data.append({
            'target': target,
            'parameter': self.combo_param.get(),
            'terapia': terapia,
            'terapeuta': terapeuta
        })
        self._render_table()
        self.entry_target.delete(0, "end")

    def _remove_row(self, idx):
        self.matrix_data.pop(idx)
        self._render_table()

    def _save_all(self):
        if not self.matrix_data:
            return messagebox.showwarning("Error", "La matriz de evaluación está vacía.")
        
        notes = self.txt_notes.get("1.0", "end-1c")
        success, msg = self.manager.save_evaluation(self.patient_id, notes, self.matrix_data)
        
        if success:
            messagebox.showinfo("Éxito", msg)
            self.matrix_data = []
            self.txt_notes.delete("1.0", "end")
            self._render_table()
            self._setup_tab_history(self.tabview.tab("Historial de Evaluaciones"))
        else:
            messagebox.showerror("Error", msg)

    def _setup_tab_history(self, parent):
        for w in parent.winfo_children(): w.destroy()
        evals = self.manager.get_evaluations(self.patient_id)
        
        hist_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        hist_scroll.pack(fill="both", expand=True)

        for ev in evals:
            frame = ctk.CTkFrame(hist_scroll, fg_color="white", border_width=1, border_color="#ccc")
            frame.pack(fill="x", pady=5, padx=5)
            
            ctk.CTkLabel(frame, text=f"📅 Fecha: {ev['date_eval']}", font=("Arial", 12, "bold"), text_color="black").pack(side="left", padx=15, pady=10)
            ctk.CTkButton(frame, text="Ver Detalle", width=100, command=lambda e=ev: self._show_details(e)).pack(side="right", padx=10)

    def _show_details(self, ev):
        details = self.manager.get_evaluation_details(ev['id'])
        win = ctk.CTkToplevel(self)
        win.title(f"Detalle de Evaluación - {ev['date_eval']}")
        win.geometry("700x500")
        win.grab_set()

        ctk.CTkLabel(win, text="Notas:", font=("Arial", 12, "bold")).pack(pady=(10,0))
        txt = ctk.CTkTextbox(win, height=80)
        txt.insert("0.0", ev['notes'])
        txt.configure(state="disabled")
        txt.pack(fill="x", padx=20, pady=5)

        table = ctk.CTkScrollableFrame(win)
        table.pack(fill="both", expand=True, padx=20, pady=10)

        for d in details:
            r = ctk.CTkFrame(table, fg_color="#f1f1f1")
            r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=f"🎯 {d['target']} | {d['parameter']}\nVal. Terapia: {d['terapia_val']} | Val. Terapeuta: {d['terapeuta_val']}", justify="left", text_color="black").pack(padx=10, pady=5)