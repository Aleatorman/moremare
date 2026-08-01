import customtkinter as ctk
from tkinter import messagebox
from src.clinical.macro.macro_manager import MacroManager
from ui.tools.tooltip import ToolTip

class MatrixWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_points, on_save_callback):
        super().__init__(parent)
        self.title("Matriz de Correspondencias Macrocontingenciales")
        self.geometry("900x650")
        self.transient(parent)
        self.grab_set()
        
        self.on_save_callback = on_save_callback
        self.current_points = current_points
        self.checkboxes = {}
        
        self.axes = ['USE', 'UEE', 'OSE', 'OEE', 'USS', 'UES', 'OSS', 'OES']
        self.axis_labels = {
            'USE': 'Sujeto-Sustitutiva-Ejemplar', 'UEE': 'Sujeto-Efectiva-Ejemplar',
            'OSE': 'Otros-Sustitutiva-Ejemplar', 'OEE': 'Otros-Efectiva-Ejemplar',
            'USS': 'Sujeto-Sustitutiva-Situacional', 'UES': 'Sujeto-Efectiva-Situacional',
            'OSS': 'Otros-Sustitutiva-Situacional', 'OES': 'Otros-Efectiva-Situacional'
        }

        self._setup_ui()

    def _setup_ui(self):
        lbl_info = ctk.CTkLabel(self, text="Marque las intersecciones donde NO HAYA CORRESPONDENCIA (Conflicto)", font=("Arial", 14, "bold"))
        lbl_info.pack(pady=10)

        grid_frame = ctk.CTkFrame(self)
        grid_frame.pack(padx=20, pady=10, fill="both", expand=True)

        for col, axis in enumerate(self.axes):
            ctk.CTkLabel(grid_frame, text=axis, font=("Arial", 12, "bold")).grid(row=0, column=col+1, padx=5, pady=5)

        for row, axis_1 in enumerate(self.axes):
            ctk.CTkLabel(grid_frame, text=f"{axis_1} ({self.axis_labels[axis_1]})", font=("Arial", 11, "bold")).grid(row=row+1, column=0, sticky="w", padx=10, pady=5)
            for col, axis_2 in enumerate(self.axes):
                if col >= row:
                    is_checked = (axis_1, axis_2) in self.current_points or (axis_2, axis_1) in self.current_points
                    var = ctk.IntVar(value=1 if is_checked else 0)
                    cb = ctk.CTkCheckBox(grid_frame, text="", variable=var, width=20)
                    cb.grid(row=row+1, column=col+1, padx=5, pady=5)
                    self.checkboxes[(axis_1, axis_2)] = var

        btn_save = ctk.CTkButton(self, text="Guardar Cambios en Matriz", command=self._save_and_close, fg_color="#27ae60", hover_color="#2ecc71")
        btn_save.pack(pady=20)

    def _save_and_close(self):
        selected_points = []
        for (a1, a2), var in self.checkboxes.items():
            if var.get() == 1:
                selected_points.append((a1, a2))
        self.on_save_callback(selected_points)
        self.destroy()

class MacroPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent)
        self.patient_id = patient_id
        self.manager = MacroManager()
        self.current_macro_id = None
        self.matrix_points = []
        self.normative_functions = []
        self.micro_map = {} 

        self._setup_ui()
        self._load_list()
        self._load_micros()

    def _setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(self, width=280)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(left_frame, text="Historial Macro", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.listbox_macros = ctk.CTkScrollableFrame(left_frame)
        self.listbox_macros.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkButton(left_frame, text="+ Nuevo Análisis", command=self._reset_form, fg_color="#34495e").pack(pady=10, padx=10, fill="x")

        right_frame = ctk.CTkScrollableFrame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(right_frame, text="Análisis de la Macrocontingencia", font=("Arial", 20, "bold")).pack(pady=(0, 20))

        frame_vinculo = ctk.CTkFrame(right_frame, fg_color="#e8f8f5", border_width=1, border_color="#1abc9c")
        frame_vinculo.pack(fill="x", pady=(0, 15), padx=10)
        
        lbl_vinc = ctk.CTkLabel(frame_vinculo, text="1. Vincular a Microcontingencia Situacional ❓", font=("Arial", 12, "bold"), text_color="#16a085", cursor="hand2")
        lbl_vinc.pack(pady=(10, 0))
        ToolTip(lbl_vinc, "Seleccione la conducta problemática específica (Micro) que vamos a comparar contra las normas de este grupo (Macro).")
        
        self.combo_micro = ctk.CTkComboBox(frame_vinculo, values=["Seleccione una microcontingencia..."])
        self.combo_micro.pack(pady=(5, 10), padx=20, fill="x")

        frame_datos = ctk.CTkFrame(right_frame)
        frame_datos.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(frame_datos, text="Tipo de Grupo:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.combo_group_type = ctk.CTkComboBox(frame_datos, values=["Familiar", "Pareja", "Laboral", "Social", "Otro"])
        self.combo_group_type.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(frame_datos, text="Nombre/Id Grupo:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_group_name = ctk.CTkEntry(frame_datos, placeholder_text="Ej: Familia nuclear")
        self.entry_group_name.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # ---> NUEVO: Modos de Regulación Moral <---
        lbl_moral = ctk.CTkLabel(frame_datos, text="Modo de Regulación Moral ❓", cursor="hand2")
        lbl_moral.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        ToolTip(lbl_moral, "¿Cómo exige este grupo que te comportes? \nPrescripción = Debes hacerlo. \nProhibición = No lo hagas. \nExpectativa = Se espera que lo hagas, pero no es explícito.")
        
        self.combo_moral = ctk.CTkComboBox(frame_datos, values=["Prescripción (Deber hacer)", "Expectativa (Se espera que)", "Prohibición (No hacer)", "Comparación", "Facilitación", "Justificación"])
        self.combo_moral.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        lbl_sancion = ctk.CTkLabel(frame_datos, text="Sanción/Consecuencia ❓", cursor="hand2")
        lbl_sancion.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        ToolTip(lbl_sancion, "¿Qué castigo aplica el grupo si el usuario rompe la regla moral que seleccionaste arriba?")
        
        self.entry_sancion = ctk.CTkEntry(frame_datos, placeholder_text="Ej: Exclusión del grupo, regaño...")
        self.entry_sancion.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        frame_datos.grid_columnconfigure(1, weight=1)

        lbl_creencias = ctk.CTkLabel(right_frame, text="Prácticas Sustitutivas (Creencias, Valores, Normas) ❓", font=("Arial", 12, "bold"), cursor="hand2")
        lbl_creencias.pack(anchor="w", padx=10, pady=(15, 0))
        ToolTip(lbl_creencias, "Registre las creencias absolutas y reglas verbales explícitas o implícitas del grupo.")
        self.txt_beliefs = ctk.CTkTextbox(right_frame, height=80)
        self.txt_beliefs.pack(fill="x", padx=10, pady=5)

        lbl_costumbres = ctk.CTkLabel(right_frame, text="Prácticas Efectivas (Costumbres, Estilos de vida) ❓", font=("Arial", 12, "bold"), cursor="hand2")
        lbl_costumbres.pack(anchor="w", padx=10, pady=(15, 0))
        ToolTip(lbl_costumbres, "Registre cómo interactúa realmente el grupo mediante hechos y acciones (independientemente de lo que digan).")
        self.txt_customs = ctk.CTkTextbox(right_frame, height=80)
        self.txt_customs.pack(fill="x", padx=10, pady=5)

        frame_analisis = ctk.CTkFrame(right_frame, fg_color="#f2f4f4", border_width=1)
        frame_analisis.pack(fill="x", pady=20, padx=10)
        
        self.btn_open_matrix = ctk.CTkButton(frame_analisis, text="📊 ABRIR MATRIZ DE CORRESPONDENCIAS", command=self._open_matrix_window, font=("Arial", 14, "bold"), fg_color="#16a085", hover_color="#1abc9c")
        self.btn_open_matrix.pack(pady=15)

        lbl_hipotesis = ctk.CTkLabel(frame_analisis, text="Hipótesis Derivada del Análisis ❓", font=("Arial", 12, "bold"), text_color="#1a5276", cursor="hand2")
        lbl_hipotesis.pack(anchor="w", padx=15)
        ToolTip(lbl_hipotesis, "Se generará automáticamente cuando termine de marcar los cruces en la matriz.")

        self.lbl_hypothesis = ctk.CTkTextbox(frame_analisis, height=80, fg_color="#ffffff", text_color="#7b241c", font=("Arial", 12))
        self.lbl_hypothesis.pack(fill="x", padx=15, pady=(0, 15))
        self.lbl_hypothesis.insert("0.0", "Complete la matriz para generar una conclusión.")
        self.lbl_hypothesis.configure(state="disabled")

        self.btn_save = ctk.CTkButton(right_frame, text="💾 GUARDAR ANÁLISIS COMPLETO", command=self._save_macro, height=45, font=("Arial", 14, "bold"))
        self.btn_save.pack(pady=30, fill="x", padx=10)

    def _load_list(self):
        for widget in self.listbox_macros.winfo_children(): widget.destroy()
        macros = self.manager.get_macros(self.patient_id)
        if not macros:
            ctk.CTkLabel(self.listbox_macros, text="Sin registros", text_color="gray").pack(pady=10)
            return

        for m in macros:
            m_id = m[0]
            display_name = m[1] if m[1] and m[1].strip() else f"Análisis #{m_id}"
            btn = ctk.CTkButton(self.listbox_macros, text=f"📂 {display_name}", command=lambda mid=m_id: self._load_macro(mid), fg_color="transparent", text_color=("gray10", "gray90"), anchor="w")
            btn.pack(fill="x", pady=2)

    def _load_micros(self):
        micros = self.manager.get_patient_micros(self.patient_id)
        self.micro_map.clear()
        
        if not micros:
            self.combo_micro.configure(values=["No hay microcontingencias creadas"])
            self.combo_micro.set("No hay microcontingencias creadas")
        else:
            values = []
            for m_id, label in micros:
                text = f"[{m_id}] - {label}"
                values.append(text)
                self.micro_map[text] = m_id
            self.combo_micro.configure(values=values)
            self.combo_micro.set(values[0])

    def _open_matrix_window(self):
        MatrixWindow(self, self.matrix_points, self._on_matrix_saved)

    def _on_matrix_saved(self, selected_points):
        self.matrix_points = selected_points
        self.btn_open_matrix.configure(text=f"📊 MATRIZ DE CORRESPONDENCIAS ({len(self.matrix_points)} conflictos)")
        
        nueva_hipotesis = self.manager.analyze_correspondences(self.matrix_points)
        self.lbl_hypothesis.configure(state="normal")
        self.lbl_hypothesis.delete("0.0", "end")
        self.lbl_hypothesis.insert("0.0", nueva_hipotesis)
        self.lbl_hypothesis.configure(state="disabled")

    def _save_macro(self):
        if not self.entry_group_name.get().strip():
            messagebox.showwarning("Atención", "Por favor asigne un nombre al grupo para el historial.")
            return

        selected_micro_text = self.combo_micro.get()
        micro_id = self.micro_map.get(selected_micro_text)

        if not micro_id and self.matrix_points:
            messagebox.showwarning("Atención", "Debe registrar y seleccionar una microcontingencia antes de guardar correspondencias en la matriz.")
            return

        data = {
            'group_type': self.combo_group_type.get(),
            'group_name': self.entry_group_name.get(),
            'beliefs_values': self.txt_beliefs.get("0.0", "end").strip(),
            'customs_lifestyles': self.txt_customs.get("0.0", "end").strip(),
            'intra_analysis': self.combo_moral.get(),     # <-- Guardamos la Regulación Moral aquí
            'inter_analysis': self.entry_sancion.get(),   # <-- Guardamos la Sanción aquí
            'normative_functions': self.normative_functions
        }

        success, msg, mid = self.manager.save_macro(self.patient_id, self.current_macro_id, data, self.matrix_points, micro_id)
        
        if success:
            self.current_macro_id = mid
            messagebox.showinfo("Éxito", msg)
            self._load_list() 
            self._load_macro(mid)
        else:
            messagebox.showerror("Error", msg)

    def _load_macro(self, macro_id):
        self._reset_form()
        data = self.manager.get_full_macro(macro_id)
        if not data: return

        self.current_macro_id = data['id']
        self.combo_group_type.set(data['group_type'])
        self.entry_group_name.insert(0, data['group_name'])
        self.txt_beliefs.insert("0.0", data['beliefs_values'])
        self.txt_customs.insert("0.0", data['customs_lifestyles'])
        
        # Cargar los nuevos campos
        self.combo_moral.set(data.get('intra_analysis') or "Prescripción (Deber hacer)")
        self.entry_sancion.insert(0, data.get('inter_analysis') or "")
        
        self.normative_functions = data.get('normative_functions', [])
        self.matrix_points = data.get('matrix_points', [])
        
        saved_micro_id = data.get('micro_id')
        if saved_micro_id:
            for text, m_id in self.micro_map.items():
                if m_id == saved_micro_id:
                    self.combo_micro.set(text)
                    break

        self.btn_open_matrix.configure(text=f"📊 ABRIR MATRIZ DE CORRESPONDENCIAS ({len(self.matrix_points)} conflictos)")
        
        self.lbl_hypothesis.configure(state="normal")
        self.lbl_hypothesis.delete("0.0", "end")
        self.lbl_hypothesis.insert("0.0", data.get('clinical_hypothesis', 'Sin datos suficientes.'))
        self.lbl_hypothesis.configure(state="disabled")

    def _reset_form(self):
        self.current_macro_id = None
        self.matrix_points = []
        self.normative_functions = []
        
        self.entry_group_name.delete(0, "end")
        self.entry_sancion.delete(0, "end")
        self.txt_beliefs.delete("0.0", "end")
        self.txt_customs.delete("0.0", "end")
        
        if self.micro_map:
            self.combo_micro.set(list(self.micro_map.keys())[0])

        self.btn_open_matrix.configure(text="📊 ABRIR MATRIZ INTERCONDUCTUAL")
        self.lbl_hypothesis.configure(state="normal")
        self.lbl_hypothesis.delete("0.0", "end")
        self.lbl_hypothesis.insert("0.0", "Complete la matriz para generar una conclusión.")
        self.lbl_hypothesis.configure(state="disabled")