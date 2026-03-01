import customtkinter as ctk
from tkinter import messagebox
from src.clinical.micro.micro_manager import MicroManager

class MicroPanel(ctk.CTkFrame): # Cambiamos a Frame normal, el scroll estará dentro de las tabs
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = MicroManager()
        
        self.actors_temp = [] 

        self._setup_ui()

    def _setup_ui(self):
        # Título Principal
        ctk.CTkLabel(self, text="2. Análisis Microcontingencial", font=("Roboto", 22, "bold")).pack(anchor="w", pady=(0, 10))

        # --- SISTEMA DE PESTAÑAS ---
        self.tabview = ctk.CTkTabview(self, width=900, height=600)
        self.tabview.pack(fill="both", expand=True)

        # Crear las dos pestañas
        self.tab_new = self.tabview.add("Nueva Microcontingencia")
        self.tab_history = self.tabview.add("Historial Guardado")

        # Configurar contenido de cada pestaña
        self._setup_form_tab()
        self._setup_history_tab()

    def _setup_form_tab(self):
        """Mueve todo el formulario anterior aquí, dentro de un ScrollableFrame."""
        self.scroll_form = ctk.CTkScrollableFrame(self.tab_new, fg_color="transparent")
        self.scroll_form.pack(fill="both", expand=True)

        # ===================================================
        # (AQUÍ PEGAMOS EL FORMULARIO QUE YA TENÍAMOS)
        # ===================================================
        
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

        # Lista visual de actores TEMPORAL
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

        # BOTÓN GUARDAR
        ctk.CTkButton(self.scroll_form, text="GUARDAR TODO", height=40, fg_color="darkblue", 
                      command=self._save_all).pack(fill="x", pady=20)

    def _setup_history_tab(self):
        """Pestaña 2: Muestra la lista de lo guardado."""
        # Botón refrescar
        ctk.CTkButton(self.tab_history, text="🔄 Actualizar Lista", width=120, height=30,
                     command=self._load_history).pack(anchor="e", pady=10)
        
        # Área con scroll para las tarjetas
        self.history_scroll = ctk.CTkScrollableFrame(self.tab_history, fg_color="transparent")
        self.history_scroll.pack(fill="both", expand=True)
        
        # Cargar datos iniciales
        self._load_history()

    def _load_history(self):
        """Consulta la BD y crea tarjetas."""
        for widget in self.history_scroll.winfo_children():
            widget.destroy()
            
        # Obtenemos lista simplificada (ID, Titulo, Tipo)
        items = self.manager.get_list_by_patient(self.patient_id)
        
        if not items:
            ctk.CTkLabel(self.history_scroll, text="No hay registros guardados.", text_color="gray").pack(pady=20)
            return

        for item in items:
            # item = (id, problem_desc, morphology_type)
            self._create_history_card(item)

    def _create_history_card(self, item):
        card = ctk.CTkFrame(self.history_scroll, border_width=1, border_color="gray")
        card.pack(fill="x", pady=5, padx=5)
        
        # Título (truncado)
        desc = item[1]
        if len(desc) > 50: desc = desc[:50] + "..."
        
        ctk.CTkLabel(card, text=f"ID {item[0]} | {item[2]}", font=("Roboto", 11, "bold"), text_color="lightblue").pack(anchor="w", padx=10, pady=(5,0))
        ctk.CTkLabel(card, text=desc, font=("Roboto", 14)).pack(anchor="w", padx=10, pady=(0,10))
        
        # Botón Ver Detalles
        ctk.CTkButton(card, text="Ver Detalles", width=100, height=25, 
                     command=lambda i=item[0]: self._show_details(i)).pack(anchor="e", padx=10, pady=5)

    def _show_details(self, micro_id):
        """Abre una ventana emergente con toda la info."""
        data = self.manager.get_full_microcontingency(micro_id)
        if not data: return

        # Ventana emergente (Toplevel)
        detail_win = ctk.CTkToplevel(self)
        detail_win.title(f"Detalle Microcontingencia #{micro_id}")
        detail_win.geometry("600x500")
        
        # Truco para que aparezca al frente
        detail_win.after(100, detail_win.lift)
        detail_win.grab_set()

        scroll = ctk.CTkScrollableFrame(detail_win)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # Helper para mostrar texto
        def show_field(label, value):
            ctk.CTkLabel(scroll, text=label, font=("Roboto", 12, "bold"), text_color="gray").pack(anchor="w")
            ctk.CTkLabel(scroll, text=value, wraplength=500, justify="left").pack(anchor="w", pady=(0, 10))

        show_field("Morfología:", f"{data['morphology_type']} - {data['morphology_metrics']}")
        show_field("Problema:", data['problem_desc'])
        show_field("Contexto Social/Físico:", data['social_context'])
        show_field("Disposiciones:", data['dispositions'])
        
        ctk.CTkLabel(scroll, text="--- ACTORES ---", font=("Roboto", 12, "bold"), text_color="lightblue").pack(anchor="w", pady=5)
        if 'actors' in data and data['actors']:
            for act in data['actors']:
                txt = f"• {act['name']} ({act['role']}): {act['response']}"
                ctk.CTkLabel(scroll, text=txt, wraplength=500, justify="left").pack(anchor="w")
        else:
            ctk.CTkLabel(scroll, text="(Sin actores registrados)").pack(anchor="w")

        ctk.CTkLabel(scroll, text="--- EFECTOS ---", font=("Roboto", 12, "bold"), text_color="lightblue").pack(anchor="w", pady=(10,5))
        show_field(f"Consecuencia ({data['consequence_type']}):", data['consequence_desc'])
        show_field("Ejercicio No Problemático:", data['non_problematic_desc'])

    # --- MÉTODOS DE SOPORTE (Idénticos a antes, solo ajustados al scroll_form) ---
    
    def _create_section_title(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Roboto", 14, "bold"), text_color=("blue", "lightblue")).pack(anchor="w", pady=(15, 5))

    def _add_actor_to_list(self):
        name = self.entry_actor_name.get()
        role = self.combo_actor_role.get()
        resp = self.entry_actor_response.get()
        if not name or not resp:
            messagebox.showwarning("Faltan datos", "Nombre y respuesta requeridos")
            return
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

    def _save_all(self):
        # Recolectar datos (igual que antes)
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

        success, msg = self.manager.save_microcontingency(self.patient_id, data, self.actors_temp)

        if success:
            messagebox.showinfo("Éxito", "Guardado correctamente.")
            self.actors_temp = []
            self._refresh_actors_ui()
            # Limpiar campos de texto
            self.txt_problem.delete("1.0", "end")
            self.txt_context.delete("1.0", "end")
            self.txt_dispositions.delete("1.0", "end")
            self.txt_conseq.delete("1.0", "end")
            self.txt_non_prob.delete("1.0", "end")
            self.entry_metrics.delete(0, "end")
            
            # AUTOMÁTICAMENTE CARGAR HISTORIAL Y CAMBIAR DE PESTAÑA
            self._load_history()
            self.tabview.set("Historial Guardado") # Cambia el foco a la pestaña 2
        else:
            messagebox.showerror("Error", msg)