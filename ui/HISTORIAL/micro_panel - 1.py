import customtkinter as ctk
from tkinter import messagebox
from src.clinical.micro.micro_manager import MicroManager

class MicroPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = MicroManager()
        
        # Lista temporal para guardar actores antes de dar click en "Guardar Todo"
        self.actors_temp = [] 

        self._setup_ui()

    def _setup_ui(self):
        # --- TÍTULO ---
        ctk.CTkLabel(self, text="2. Análisis Microcontingencial", font=("Roboto", 22, "bold")).pack(anchor="w", pady=(0, 20))

        # ===================================================
        # SECCIÓN A: MORFOLOGÍA DE LA CONDUCTA
        # ===================================================
        self._create_section_title("A. Definición del Problema (Morfología)")
        
        frame_a = ctk.CTkFrame(self)
        frame_a.pack(fill="x", pady=5)

        # Tipo (Efectiva vs Afectiva)
        ctk.CTkLabel(frame_a, text="Tipo de Conducta:", font=("Roboto", 12, "bold")).grid(row=0, column=0, padx=10, pady=10)
        self.var_type = ctk.StringVar(value="Efectiva")
        ctk.CTkRadioButton(frame_a, text="Efectiva (Afecta a otros)", variable=self.var_type, value="Efectiva").grid(row=0, column=1, padx=10)
        ctk.CTkRadioButton(frame_a, text="Afectiva (Solo a sí mismo)", variable=self.var_type, value="Afectiva").grid(row=0, column=2, padx=10)

        # Métricas (Frecuencia, etc)
        ctk.CTkLabel(frame_a, text="Métricas (Frecuencia/Intensidad):", font=("Roboto", 12, "bold")).grid(row=1, column=0, padx=10, pady=10)
        self.entry_metrics = ctk.CTkEntry(frame_a, placeholder_text="Ej: 3 veces por semana, Intensidad 8/10", width=300)
        self.entry_metrics.grid(row=1, column=1, columnspan=2, sticky="w", padx=10)

        # Descripción Narrativa
        ctk.CTkLabel(self, text="Descripción concreta de la conducta:", anchor="w").pack(fill="x", pady=(10,0))
        self.txt_problem = ctk.CTkTextbox(self, height=80)
        self.txt_problem.pack(fill="x", pady=5)

        # ===================================================
        # SECCIÓN B: CONDICIONES SITUACIONALES
        # ===================================================
        self._create_section_title("B. Condiciones Situacionales (Contexto)")
        
        # Grid para contextos
        frame_b = ctk.CTkFrame(self, fg_color="transparent")
        frame_b.pack(fill="x")
        
        # Columna 1: Social y Físico
        ctk.CTkLabel(frame_b, text="Circunstancia Social y Física:", anchor="w").pack(fill="x")
        self.txt_context = ctk.CTkTextbox(frame_b, height=60)
        self.txt_context.pack(fill="x", pady=5)

        # Columna 2: Disposiciones
        ctk.CTkLabel(frame_b, text="Inclinaciones y Tendencias (Historia/Gustos):", anchor="w").pack(fill="x", pady=(10,0))
        self.txt_dispositions = ctk.CTkTextbox(frame_b, height=60)
        self.txt_dispositions.pack(fill="x", pady=5)

        # ===================================================
        # SECCIÓN C: LOS OTROS (Dinámico)
        # ===================================================
        self._create_section_title("C. Análisis de Actores (Los Otros)")
        
        # 1. Formulario para agregar persona
        add_frame = ctk.CTkFrame(self)
        add_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(add_frame, text="Agregar Persona:", font=("Roboto", 12, "bold")).grid(row=0, column=0, padx=10, pady=10)
        
        self.entry_actor_name = ctk.CTkEntry(add_frame, placeholder_text="Nombre/Rol (Ej: Mamá)", width=150)
        self.entry_actor_name.grid(row=0, column=1, padx=5)

        # Roles estandarizados del PDF
        roles = ["Auspiciador", "Regulador de inclinaciones", "Mediador de la contingencia", "Mediado", "Regulador de la tendencia"]
        self.combo_actor_role = ctk.CTkComboBox(add_frame, values=roles, width=200)
        self.combo_actor_role.grid(row=0, column=2, padx=5)

        # Botón de ayuda (?)
        btn_help = ctk.CTkButton(add_frame, text="?", width=30, fg_color="gray", command=self._show_role_help)
        btn_help.grid(row=0, column=3, padx=2)

        self.entry_actor_response = ctk.CTkEntry(add_frame, placeholder_text="¿Qué hace/dice exactamente?", width=200)
        self.entry_actor_response.grid(row=0, column=4, padx=5)

        btn_add = ctk.CTkButton(add_frame, text="+", width=40, fg_color="green", command=self._add_actor_to_list)
        btn_add.grid(row=0, column=5, padx=10)

        # 2. Lista visual de agregados
        ctk.CTkLabel(self, text="Actores en esta situación:", anchor="w", text_color="gray").pack(fill="x")
        self.actors_list_frame = ctk.CTkFrame(self, fg_color="gray20") # Color oscuro para diferenciar
        self.actors_list_frame.pack(fill="x", pady=5)
        
        self.lbl_no_actors = ctk.CTkLabel(self.actors_list_frame, text="No hay actores agregados aún.")
        self.lbl_no_actors.pack(pady=10)

        # ===================================================
        # SECCIÓN D: CONSECUENCIAS
        # ===================================================
        self._create_section_title("D. Consecuencias y Efectos")
        
        frame_d = ctk.CTkFrame(self)
        frame_d.pack(fill="x", pady=5)

        ctk.CTkLabel(frame_d, text="El efecto recae sobre:", font=("Roboto", 12, "bold")).pack(side="left", padx=10)
        self.var_conseq = ctk.StringVar(value="Otros")
        ctk.CTkComboBox(frame_d, values=["Sobre Otros", "Sobre Sí Mismo", "Sin Efecto"], variable=self.var_conseq).pack(side="left", padx=10)

        ctk.CTkLabel(self, text="Descripción del efecto:", anchor="w").pack(fill="x", pady=(5,0))
        self.txt_conseq = ctk.CTkTextbox(self, height=60)
        self.txt_conseq.pack(fill="x", pady=5)

        # ===================================================
        # SECCIÓN E: EJERCICIO NO PROBLEMÁTICO
        # ===================================================
        self._create_section_title("E. Ejercicio NO Problemático (Contraste)")
        self.txt_non_prob = ctk.CTkTextbox(self, height=60)
        self.txt_non_prob.pack(fill="x", pady=5)

        # --- BOTÓN FINAL ---
        ctk.CTkButton(self, text="GUARDAR MICROCONTINGENCIA", height=50, fg_color="darkblue", 
                      font=("Roboto", 14, "bold"), command=self._save_all).pack(fill="x", pady=30)

    def _create_section_title(self, text):
        ctk.CTkLabel(self, text=text, font=("Roboto", 14, "bold"), text_color=("blue", "lightblue")).pack(anchor="w", pady=(20, 5))

    def _add_actor_to_list(self):
        """Toma los datos de los inputs y los pone en la lista visual."""
        name = self.entry_actor_name.get()
        role = self.combo_actor_role.get()
        resp = self.entry_actor_response.get()

        if not name or not resp:
            messagebox.showwarning("Faltan datos", "Indica el nombre y la respuesta del actor.")
            return

        # Agregar a la memoria
        actor_data = {'name': name, 'role': role, 'response': resp}
        self.actors_temp.append(actor_data)

        # Limpiar inputs
        self.entry_actor_name.delete(0, "end")
        self.entry_actor_response.delete(0, "end")

        # Refrescar visual
        self._refresh_actors_ui()

    def _refresh_actors_ui(self):
        """Redibuja la lista de actores."""
        for widget in self.actors_list_frame.winfo_children():
            widget.destroy()

        if not self.actors_temp:
            ctk.CTkLabel(self.actors_list_frame, text="No hay actores agregados aún.").pack(pady=10)
            return

        # Dibujar cada actor como una "tarjeta" pequeña
        for idx, actor in enumerate(self.actors_temp):
            row = ctk.CTkFrame(self.actors_list_frame, fg_color="transparent")
            row.pack(fill="x", padx=5, pady=2)
            
            txt = f"👤 {actor['name']} ({actor['role']}) ➔ {actor['response']}"
            ctk.CTkLabel(row, text=txt, anchor="w").pack(side="left")
            
            # Botón eliminar pequeño
            ctk.CTkButton(row, text="x", width=30, fg_color="red", 
                          command=lambda i=idx: self._remove_actor(i)).pack(side="right")

    def _remove_actor(self, index):
        self.actors_temp.pop(index)
        self._refresh_actors_ui()

    def _show_role_help(self):
        # Aquí conectaremos con el glosario más adelante
        messagebox.showinfo("Ayuda de Roles", f"Definición de {self.combo_actor_role.get()}:\n\n(Consulta el manual de análisis contingencial para detalle)")

    def _save_all(self):
        # Recolectar Textboxes
        data = {
            'type': self.var_type.get(),
            'metrics': self.entry_metrics.get(),
            'problem': self.txt_problem.get("1.0", "end-1c"),
            'social': self.txt_context.get("1.0", "end-1c"),
            'physical': "Ver contexto", # Simplificación por ahora
            'dispositions': self.txt_dispositions.get("1.0", "end-1c"),
            'conseq_type': self.var_conseq.get(),
            'conseq_desc': self.txt_conseq.get("1.0", "end-1c"),
            'non_prob': self.txt_non_prob.get("1.0", "end-1c")
        }

        # Validar mínimo
        if not data['problem'].strip():
            messagebox.showwarning("Error", "Debes describir la conducta problema.")
            return

        # Enviar al Manager
        success, msg = self.manager.save_microcontingency(self.patient_id, data, self.actors_temp)

        if success:
            messagebox.showinfo("Éxito", "Microcontingencia guardada correctamente.")
            # Limpiar todo para agregar otra? O cerrar? 
            # Por ahora limpiaremos la lista de actores
            self.actors_temp = []
            self._refresh_actors_ui()
            # Aquí podrías recargar la vista si quisieras
        else:
            messagebox.showerror("Error", f"No se pudo guardar: {msg}")