import customtkinter as ctk
from tkinter import messagebox
from src.clinical.micro.micro_manager import MicroManager

class MicroPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = MicroManager()
        
        self.actors_temp = [] 
        self.editing_id = None # Variable para saber si estamos editando (ID) o creando (None)

        self._setup_ui()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="2. Análisis Microcontingencial", font=("Roboto", 22, "bold")).pack(anchor="w", pady=(0, 10))

        # --- TABS ---
        self.tabview = ctk.CTkTabview(self, width=900, height=600)
        self.tabview.pack(fill="both", expand=True)

        self.tab_new = self.tabview.add("Nueva Microcontingencia")
        self.tab_history = self.tabview.add("Historial Guardado")

        self._setup_form_tab()
        self._setup_history_tab()

    def _setup_form_tab(self):
        self.scroll_form = ctk.CTkScrollableFrame(self.tab_new, fg_color="transparent")
        self.scroll_form.pack(fill="both", expand=True)

        # SECCIÓN A
        self._create_section_title(self.scroll_form, "A. Definición del Problema (Morfología)")
        frame_a = ctk.CTkFrame(self.scroll_form)
        frame_a.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_a, text="Tipo:", font=("Roboto", 12, "bold")).grid(row=0, column=0, padx=10, pady=10)
        self.var_type = ctk.StringVar(value="Efectiva")
        ctk.CTkRadioButton(frame_a, text="Efectiva", variable=self.var_type, value="Efectiva").grid(row=0, column=1, padx=10)
        ctk.CTkRadioButton(frame_a, text="Afectiva", variable=self.var_type, value="Afectiva").grid(row=0, column=2, padx=10)

        ctk.CTkLabel(frame_a, text="Métricas:", font=("Roboto", 12, "bold")).grid(row=1, column=0, padx=10, pady=10)
        self.entry_metrics = ctk.CTkEntry(frame_a, placeholder_text="Frecuencia/Intensidad", width=300)
        self.entry_metrics.grid(row=1, column=1, columnspan=2, sticky="w", padx=10)

        ctk.CTkLabel(self.scroll_form, text="Descripción concreta:", anchor="w").pack(fill="x", pady=(10,0))
        self.txt_problem = ctk.CTkTextbox(self.scroll_form, height=60)
        self.txt_problem.pack(fill="x", pady=5)

        # SECCIÓN B
        self._create_section_title(self.scroll_form, "B. Contexto Situacional")
        self.txt_context = ctk.CTkTextbox(self.scroll_form, height=50)
        self.txt_context.pack(fill="x", pady=5)
        
        ctk.CTkLabel(self.scroll_form, text="Disposiciones (Historia/Gustos):", anchor="w").pack(fill="x")
        self.txt_dispositions = ctk.CTkTextbox(self.scroll_form, height=50)
        self.txt_dispositions.pack(fill="x", pady=5)

        # SECCIÓN C (ACTORES)
        self._create_section_title(self.scroll_form, "C. Actores (Los Otros)")
        add_frame = ctk.CTkFrame(self.scroll_form)
        add_frame.pack(fill="x", pady=5)
        
        self.entry_actor_name = ctk.CTkEntry(add_frame, placeholder_text="Nombre", width=120)
        self.entry_actor_name.pack(side="left", padx=5, pady=5)
        
        roles = ["Auspiciador", "Regulador de inclinaciones", "Mediador de la contingencia", "Mediado", "Regulador de la tendencia"]
        self.combo_actor_role = ctk.CTkComboBox(add_frame, values=roles, width=180)
        self.combo_actor_role.pack(side="left", padx=5)
        
        self.entry_actor_response = ctk.CTkEntry(add_frame, placeholder_text="Respuesta", width=180)
        self.entry_actor_response.pack(side="left", padx=5)
        
        ctk.CTkButton(add_frame, text="+", width=40, fg_color="green", command=self._add_actor_to_list).pack(side="left", padx=10)

        self.actors_list_frame = ctk.CTkFrame(self.scroll_form, fg_color="gray20")
        self.actors_list_frame.pack(fill="x", pady=5)

        # SECCIÓN D
        self._create_section_title(self.scroll_form, "D. Consecuencias")
        frame_d = ctk.CTkFrame(self.scroll_form)
        frame_d.pack(fill="x", pady=5)
        self.var_conseq = ctk.StringVar(value="Otros")
        ctk.CTkComboBox(frame_d, values=["Sobre Otros", "Sobre Sí Mismo", "Sin Efecto"], variable=self.var_conseq).pack(side="left", padx=10, pady=5)
        self.txt_conseq = ctk.CTkTextbox(self.scroll_form, height=50)
        self.txt_conseq.pack(fill="x", pady=5)

        # SECCIÓN E
        self._create_section_title(self.scroll_form, "E. Ejercicio NO Problemático")
        self.txt_non_prob = ctk.CTkTextbox(self.scroll_form, height=50)
        self.txt_non_prob.pack(fill="x", pady=5)

        # --- BOTONERA INFERIOR ---
        self.btn_frame = ctk.CTkFrame(self.scroll_form, fg_color="transparent")
        self.btn_frame.pack(fill="x", pady=20)

        # Botón Cancelar (Solo visible al editar)
        self.btn_cancel = ctk.CTkButton(self.btn_frame, text="Cancelar Edición", fg_color="gray", command=self._cancel_edit)
        # No lo mostramos (pack) al inicio

        # Botón Guardar
        self.btn_save = ctk.CTkButton(self.btn_frame, text="GUARDAR TODO", height=40, fg_color="darkblue", command=self._save_all)
        self.btn_save.pack(fill="x")

    def _setup_history_tab(self):
        ctk.CTkButton(self.tab_history, text="🔄 Actualizar Lista", width=120, height=30,
                     command=self._load_history).pack(anchor="e", pady=10)
        
        self.history_scroll = ctk.CTkScrollableFrame(self.tab_history, fg_color="transparent")
        self.history_scroll.pack(fill="both", expand=True)
        self._load_history()

    def _load_history(self):
        for widget in self.history_scroll.winfo_children(): widget.destroy()
        items = self.manager.get_list_by_patient(self.patient_id)
        if not items:
            ctk.CTkLabel(self.history_scroll, text="No hay registros guardados.", text_color="gray").pack(pady=20)
            return
        for item in items:
            self._create_history_card(item)

    def _create_history_card(self, item):
        card = ctk.CTkFrame(self.history_scroll, border_width=1, border_color="gray")
        card.pack(fill="x", pady=5, padx=5)
        
        desc = item[1]
        if len(desc) > 60: desc = desc[:60] + "..."
        
        # Info
        ctk.CTkLabel(card, text=f"ID {item[0]} | {item[2]}", font=("Roboto", 11, "bold"), text_color="lightblue").pack(anchor="w", padx=10, pady=(5,0))
        ctk.CTkLabel(card, text=desc, font=("Roboto", 14)).pack(anchor="w", padx=10, pady=(0,5))
        
        # Botonera de la tarjeta
        btn_box = ctk.CTkFrame(card, fg_color="transparent", height=30)
        btn_box.pack(fill="x", padx=5, pady=5)

        # Botón Eliminar (Rojo)
        ctk.CTkButton(btn_box, text="Eliminar", width=80, fg_color="#c9302c", hover_color="#992320",
                     command=lambda i=item[0]: self._delete_item(i)).pack(side="left", padx=5)

        # Botón Editar (Azul)
        ctk.CTkButton(btn_box, text="Editar", width=80, fg_color="#1f618d", 
                     command=lambda i=item[0]: self._load_for_editing(i)).pack(side="left", padx=5)

        # Botón Ver Detalles (Gris/Normal)
        ctk.CTkButton(btn_box, text="Ver Detalles", width=100, 
                     command=lambda i=item[0]: self._show_details(i)).pack(side="right", padx=5)

    # --- ACCIONES DE EDICIÓN Y BORRADO ---

    def _delete_item(self, micro_id):
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este registro?\nEsta acción es permanente."):
            success, msg = self.manager.delete_microcontingency(micro_id)
            if success:
                self._load_history()
            else:
                messagebox.showerror("Error", msg)

    def _load_for_editing(self, micro_id):
        """Carga los datos en el formulario y cambia el modo a EDICIÓN."""
        data = self.manager.get_full_microcontingency(micro_id)
        if not data: return

        # 1. Limpiar formulario actual
        self._cancel_edit(reset_ui=False) 

        # 2. Llenar campos
        self.editing_id = micro_id
        self.var_type.set(data['morphology_type'])
        self.entry_metrics.insert(0, data['morphology_metrics'])
        self.txt_problem.insert("0.0", data['problem_desc'])
        self.txt_context.insert("0.0", data['social_context'])
        self.txt_dispositions.insert("0.0", data['dispositions'])
        self.var_conseq.set(data['consequence_type'])
        self.txt_conseq.insert("0.0", data['consequence_desc'])
        self.txt_non_prob.insert("0.0", data['non_problematic_desc'])

        # 3. Llenar actores
        if 'actors' in data:
            self.actors_temp = data['actors']
            self._refresh_actors_ui()

        # 4. Cambiar UI a modo edición
        self.btn_save.configure(text="ACTUALIZAR DATOS", fg_color="#d35400", hover_color="#a04000") # Naranja
        self.btn_cancel.pack(side="left", fill="x", expand=True, padx=5) # Mostrar botón cancelar
        self.btn_save.pack(side="right", fill="x", expand=True, padx=5)
        
        self.tabview.set("Nueva Microcontingencia") # Cambiar tab

    def _cancel_edit(self, reset_ui=True):
        """Limpia el formulario y sale del modo edición."""
        self.editing_id = None
        self.actors_temp = []
        self._refresh_actors_ui()
        
        # Limpiar Textos
        widgets = [self.txt_problem, self.txt_context, self.txt_dispositions, self.txt_conseq, self.txt_non_prob]
        for w in widgets: w.delete("1.0", "end")
        self.entry_metrics.delete(0, "end")
        
        # Restaurar UI
        if reset_ui:
            self.btn_cancel.pack_forget() # Ocultar cancelar
            self.btn_save.pack(fill="x") # Botón guardar full width
            self.btn_save.configure(text="GUARDAR TODO", fg_color="darkblue", hover_color="#3a7ebf")

    def _save_all(self):
        # Recolectar datos
        data = {
            'type': self.var_type.get(),
            'metrics': self.entry_metrics.get(),
            'problem': self.txt_problem.get("1.0", "end-1c"),
            'social': self.txt_context.get("1.0", "end-1c"),
            'physical': "Ver contexto",
            'dispositions': self.txt_dispositions.get("1.0", "end-1c"),
            'conseq_type': self.var_conseq.get(),
            'conseq_desc': self.txt_conseq.get("1.0", "end-1c"),
            'non_prob': self.txt_non_prob.get("1.0", "end-1c")
        }

        if not data['problem'].strip():
            messagebox.showwarning("Error", "Describe el problema.")
            return

        if self.editing_id:
            # MODO ACTUALIZACIÓN
            success, msg = self.manager.update_microcontingency(self.editing_id, data, self.actors_temp)
            action_msg = "Actualizado correctamente."
        else:
            # MODO CREACIÓN
            success, msg = self.manager.save_microcontingency(self.patient_id, data, self.actors_temp)
            action_msg = "Guardado correctamente."

        if success:
            messagebox.showinfo("Éxito", action_msg)
            self._cancel_edit() # Limpia y resetea UI
            self._load_history() # Recarga la lista
            self.tabview.set("Historial Guardado")
        else:
            messagebox.showerror("Error", msg)

    # --- MÉTODOS DE SOPORTE (Idénticos al anterior) ---
    def _create_section_title(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Roboto", 14, "bold"), text_color=("blue", "lightblue")).pack(anchor="w", pady=(15, 5))
    
    def _add_actor_to_list(self):
        name = self.entry_actor_name.get()
        role = self.combo_actor_role.get()
        resp = self.entry_actor_response.get()
        if not name or not resp: return
        self.actors_temp.append({'name': name, 'role': role, 'response': resp})
        self.entry_actor_name.delete(0, "end")
        self.entry_actor_response.delete(0, "end")
        self._refresh_actors_ui()

    def _refresh_actors_ui(self):
        for widget in self.actors_list_frame.winfo_children(): widget.destroy()
        for idx, actor in enumerate(self.actors_temp):
            row = ctk.CTkFrame(self.actors_list_frame, fg_color="transparent")
            row.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(row, text=f"👤 {actor['name']} ({actor['role']})", anchor="w").pack(side="left")
            ctk.CTkButton(row, text="x", width=30, fg_color="red", command=lambda i=idx: self._remove_actor(i)).pack(side="right")

    def _remove_actor(self, index):
        self.actors_temp.pop(index)
        self._refresh_actors_ui()

def _show_details(self, micro_id):
        """Muestra TODOS los detalles de la microcontingencia en una ventana emergente."""
        data = self.manager.get_full_microcontingency(micro_id)
        if not data: return

        # 1. Configurar ventana
        detail_win = ctk.CTkToplevel(self)
        detail_win.title(f"Detalle de Microcontingencia #{micro_id}")
        detail_win.geometry("700x600")
        
        # Trucos para que la ventana se quede al frente
        detail_win.after(100, detail_win.lift)
        detail_win.grab_set() # Bloquea la ventana de atrás

        # 2. Área de Scroll
        scroll = ctk.CTkScrollableFrame(detail_win, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        # --- HELPER PARA MOSTRAR CAMPOS ---
        def add_field(title, content):
            container = ctk.CTkFrame(scroll, fg_color="transparent")
            container.pack(fill="x", pady=5)
            ctk.CTkLabel(container, text=title, font=("Roboto", 12, "bold"), text_color="gray").pack(anchor="w")
            ctk.CTkLabel(container, text=content if content else "(Sin datos)", 
                         wraplength=600, justify="left", font=("Roboto", 14)).pack(anchor="w")

        def add_separator(text):
            ctk.CTkLabel(scroll, text=text, font=("Roboto", 14, "bold"), text_color=("blue", "lightblue")).pack(anchor="w", pady=(20, 5))
            ctk.CTkFrame(scroll, height=2, fg_color="gray").pack(fill="x", pady=(0, 10))

        # --- SECCIÓN A: MORFOLOGÍA ---
        add_separator("A. Definición del Problema")
        add_field("Tipo de Conducta:", data['morphology_type'])
        add_field("Métricas (Frecuencia/Intensidad):", data['morphology_metrics'])
        add_field("Descripción de la Conducta:", data['problem_desc'])

        # --- SECCIÓN B: CONTEXTO ---
        add_separator("B. Contexto Situacional")
        add_field("Circunstancia Social y Física:", data['social_context'])
        add_field("Disposiciones (Historia/Tendencias):", data['dispositions'])

        # --- SECCIÓN C: ACTORES ---
        add_separator("C. Actores Involucrados")
        if 'actors' in data and data['actors']:
            for act in data['actors']:
                card = ctk.CTkFrame(scroll, border_width=1, border_color="gray")
                card.pack(fill="x", pady=2)
                
                # Título: Nombre y Rol
                ctk.CTkLabel(card, text=f"👤 {act['name']} - {act['role']}", 
                             font=("Roboto", 12, "bold")).pack(anchor="w", padx=10, pady=(5,0))
                
                # Respuesta
                ctk.CTkLabel(card, text=f"Respuesta: {act['response']}", 
                             text_color="gray", wraplength=580).pack(anchor="w", padx=10, pady=(0,5))
        else:
            ctk.CTkLabel(scroll, text="(No hay actores registrados en esta situación)").pack(anchor="w", pady=5)

        # --- SECCIÓN D: CONSECUENCIAS ---
        add_separator("D. Consecuencias")
        add_field(f"Efecto ({data['consequence_type']}):", data['consequence_desc'])

        # --- SECCIÓN E: CONTRASTE ---
        add_separator("E. Ejercicio No Problemático")
        add_field("Descripción:", data['non_problematic_desc'])

        # Botón para cerrar
        ctk.CTkButton(scroll, text="Cerrar", command=detail_win.destroy, fg_color="gray").pack(pady=30)




