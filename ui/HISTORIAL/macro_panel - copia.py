import customtkinter as ctk
from tkinter import messagebox
from src.clinical.macro.macro_manager import MacroManager

class MacroPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = MacroManager()
        self.editing_id = None # Para controlar si estamos editando

        self._setup_ui()

    def _setup_ui(self):
        # Encabezado con referencias al documento
        ctk.CTkLabel(self, text="3. Sistema Macrocontingencial", font=("Roboto", 22, "bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self, text="Contexto de valores y correspondencia con prácticas sociales dominantes.", 
                     text_color="gray").pack(anchor="w", pady=(0, 15))

        # --- TABS (Igual que Módulo 2) ---
        self.tabview = ctk.CTkTabview(self, width=900, height=600)
        self.tabview.pack(fill="both", expand=True)

        self.tab_new = self.tabview.add("Nuevo Análisis")
        self.tab_history = self.tabview.add("Tabla de Análisis (Historial)")

        self._setup_form_tab()
        self._setup_history_tab()

    def _setup_form_tab(self):
        self.scroll_form = ctk.CTkScrollableFrame(self.tab_new, fg_color="transparent")
        self.scroll_form.pack(fill="both", expand=True)

        # --- SECCIÓN 1: CONTEXTO DE VALORES (Pág. 58) ---
        self._create_section_title(self.scroll_form, "A. Categoría y Función Valorativa")
        
        frame_top = ctk.CTkFrame(self.scroll_form)
        frame_top.pack(fill="x", pady=5)

        # Categoría
        ctk.CTkLabel(frame_top, text="Categoría (Contexto):", font=("Roboto", 12, "bold")).grid(row=0, column=0, padx=10, pady=10)
        # Valores basados en Pág. 58
        self.combo_cat = ctk.CTkComboBox(frame_top, values=["Creencias", "Costumbres", "Prácticas de Grupo", "Forma de Vida"], width=200)
        self.combo_cat.grid(row=0, column=1, padx=10)

        # Función Valorativa
        ctk.CTkLabel(frame_top, text="Función Valorativa:", font=("Roboto", 12, "bold")).grid(row=0, column=2, padx=10)
        # Valores basados en Pág. 43 y 58
        funcs = ["Prescripción", "Indicación", "Facilitación", "Justificación", 
                 "Sanción", "Advertencia", "Comparación", "Condicionamiento", 
                 "Prohibición", "Expectativa"]
        self.combo_func = ctk.CTkComboBox(frame_top, values=funcs, width=200)
        self.combo_func.grid(row=0, column=3, padx=10)

        # --- SECCIÓN 2: ANÁLISIS DE CORRESPONDENCIA (Pág. 43) ---
        self._create_section_title(self.scroll_form, "B. Análisis de Correspondencia")
        
        frame_mid = ctk.CTkFrame(self.scroll_form, fg_color="transparent")
        frame_mid.pack(fill="x")

        ctk.CTkLabel(frame_mid, text="Tipo de Correspondencia:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=10)
        self.combo_corr = ctk.CTkComboBox(frame_mid, values=["Intracontingencial", "Intercontingencial", "Ninguna"], width=200)
        self.combo_corr.pack(anchor="w", padx=10, pady=5)
        
        ctk.CTkLabel(self.scroll_form, text="Análisis Comparativo (Conducta Usuario vs. Práctica Dominante):", anchor="w").pack(fill="x", pady=(10,0))
        self.txt_analysis = ctk.CTkTextbox(self.scroll_form, height=100)
        self.txt_analysis.pack(fill="x", pady=5)

        # --- SECCIÓN 3: DETALLES ---
        ctk.CTkLabel(self.scroll_form, text="Notas / Detalles Adicionales:", anchor="w").pack(fill="x", pady=(10,0))
        self.txt_detail = ctk.CTkEntry(self.scroll_form, placeholder_text="Observaciones extra...")
        self.txt_detail.pack(fill="x", pady=5)

        # --- BOTONERA ---
        self.btn_frame = ctk.CTkFrame(self.scroll_form, fg_color="transparent")
        self.btn_frame.pack(fill="x", pady=20)

        self.btn_cancel = ctk.CTkButton(self.btn_frame, text="Cancelar Edición", fg_color="gray", command=self._cancel_edit)
        # Se oculta al inicio

        self.btn_save = ctk.CTkButton(self.btn_frame, text="AGREGAR FILA A LA TABLA", height=40, fg_color="green", command=self._save_data)
        self.btn_save.pack(fill="x")

    def _setup_history_tab(self):
        # Botón refrescar
        ctk.CTkButton(self.tab_history, text="🔄 Actualizar Tabla", width=120, height=30,
                     command=self._load_history).pack(anchor="e", pady=10)
        
        self.history_scroll = ctk.CTkScrollableFrame(self.tab_history, fg_color="transparent")
        self.history_scroll.pack(fill="both", expand=True)
        self._load_history()

    def _load_history(self):
        for widget in self.history_scroll.winfo_children(): widget.destroy()
        
        rows = self.manager.get_all_macros(self.patient_id)
        
        if not rows:
            ctk.CTkLabel(self.history_scroll, text="No hay análisis registrado en este módulo.", text_color="gray").pack(pady=20)
            return

        for row in rows:
            self._create_row_card(row)

    def _create_row_card(self, row):
        card = ctk.CTkFrame(self.history_scroll, border_width=1, border_color="gray")
        card.pack(fill="x", pady=5, padx=5)

        # Encabezado: Categoría | Correspondencia | Función
        header = ctk.CTkFrame(card, fg_color="transparent", height=25)
        header.pack(fill="x", padx=10, pady=5)
        
        # Badges (Etiquetas de colores simuladas)
        ctk.CTkLabel(header, text=f"📂 {row['category']}", font=("Roboto", 12, "bold")).pack(side="left", padx=(0,10))
        
        color_corr = "orange" if row['correspondence'] == "Ninguna" else "#2ecc71" # Verde si hay correspondencia
        ctk.CTkLabel(header, text=f"[{row['correspondence']}]", text_color=color_corr, font=("Roboto", 12, "bold")).pack(side="left", padx=10)
        
        ctk.CTkLabel(header, text=f"Función: {row['valuative_function']}", text_color="lightblue").pack(side="left", padx=10)

        # Contenido
        ctk.CTkLabel(card, text=row['analysis'], wraplength=750, justify="left").pack(fill="x", padx=10, pady=5)
        
        if row['detail']:
            ctk.CTkLabel(card, text=f"Nota: {row['detail']}", text_color="gray", font=("Roboto", 11)).pack(fill="x", padx=10, pady=(0,5))

        # Botonera Acciones
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(actions, text="Eliminar", fg_color="#c9302c", width=80, height=25,
                      command=lambda r=row['id']: self._delete_row(r)).pack(side="right", padx=5)
        
        ctk.CTkButton(actions, text="Editar", fg_color="#1f618d", width=80, height=25,
                      command=lambda r=row['id']: self._load_for_edit(r)).pack(side="right", padx=5)

    def _save_data(self):
        data = {
            'category': self.combo_cat.get(),
            'analysis': self.txt_analysis.get("1.0", "end-1c"),
            'correspondence': self.combo_corr.get(),
            'function': self.combo_func.get(),
            'detail': self.txt_detail.get()
        }

        if not data['analysis'].strip():
            messagebox.showwarning("Faltan datos", "El análisis comparativo es obligatorio.")
            return

        if self.editing_id:
            success, msg = self.manager.update_macro_row(self.editing_id, data)
        else:
            success, msg = self.manager.add_macro_row(self.patient_id, data)

        if success:
            messagebox.showinfo("Éxito", msg)
            self._cancel_edit() # Limpia UI
            self._load_history()
            self.tabview.set("Tabla de Análisis (Historial)")
        else:
            messagebox.showerror("Error", msg)

    def _load_for_edit(self, macro_id):
        row = self.manager.get_macro_by_id(macro_id)
        if not row: return

        self.editing_id = macro_id
        
        # Llenar campos
        self.combo_cat.set(row['category'])
        self.combo_func.set(row['valuative_function'])
        self.combo_corr.set(row['correspondence'])
        self.txt_analysis.delete("1.0", "end")
        self.txt_analysis.insert("0.0", row['analysis'])
        self.txt_detail.delete(0, "end")
        self.txt_detail.insert(0, row['detail'])

        # Cambiar UI
        self.btn_save.configure(text="ACTUALIZAR ANÁLISIS", fg_color="#d35400")
        self.btn_cancel.pack(side="left", fill="x", expand=True, padx=5)
        self.btn_save.pack(side="right", fill="x", expand=True, padx=5)
        self.tabview.set("Nuevo Análisis")

    def _cancel_edit(self):
        self.editing_id = None
        self.txt_analysis.delete("1.0", "end")
        self.txt_detail.delete(0, "end")
        
        self.btn_cancel.pack_forget()
        self.btn_save.pack(fill="x")
        self.btn_save.configure(text="AGREGAR FILA A LA TABLA", fg_color="green")

    def _delete_row(self, macro_id):
        if messagebox.askyesno("Confirmar", "¿Eliminar este análisis?"):
            self.manager.delete_macro_row(macro_id)
            self._load_history()

    def _create_section_title(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Roboto", 14, "bold"), text_color=("blue", "lightblue")).pack(anchor="w", pady=(15, 5))