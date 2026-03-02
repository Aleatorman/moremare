import customtkinter as ctk
from tkinter import messagebox
import webbrowser
from src.clinical.intervention.intervention_manager import InterventionManager
from src.clinical.genesis.genesis_manager import GenesisManager

class InterventionPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = InterventionManager()
        self.genesis_manager = GenesisManager() 
        
        self.current_micro_id = None
        self.micro_map = {}

        self._setup_ui()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="5. Plan de Intervención y Técnicas", font=("Roboto", 22, "bold")).pack(anchor="w", pady=(0, 10))

        self.tabview = ctk.CTkTabview(self, width=900, height=600)
        self.tabview.pack(fill="both", expand=True)

        self.tab_plan = self.tabview.add("Plan por Microcontingencia")
        self.tab_lib = self.tabview.add("Biblioteca de Técnicas")

        self._setup_plan_tab()
        self._setup_library_tab()

    def _setup_plan_tab(self):
        selector_frame = ctk.CTkFrame(self.tab_plan, fg_color=("gray90", "gray20"))
        selector_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(selector_frame, text="Seleccionar Microcontingencia:", font=("Roboto", 12, "bold")).pack(side="left", padx=10, pady=10)
        self.combo_micros = ctk.CTkComboBox(selector_frame, width=300, command=self._on_micro_selected)
        self.combo_micros.pack(side="left", padx=10)
        
        self.status_lbl = ctk.CTkLabel(selector_frame, text="⚪ Selecciona una opción", font=("Roboto", 12, "bold"), text_color="gray")
        self.status_lbl.pack(side="left", padx=10)

        self.scroll_plan = ctk.CTkScrollableFrame(self.tab_plan, fg_color="transparent")
        self.scroll_plan.pack(fill="both", expand=True, padx=5, pady=5)

        self.txt_goal = self._add_field(self.scroll_plan, "1. Objetivo General de la Intervención:")
        self.txt_morph = self._add_field(self.scroll_plan, "2. Estrategia sobre la Morfología (Conducta del usuario):")
        self.txt_actors = self._add_field(self.scroll_plan, "3. Estrategia sobre los Actores (Mediadores/Otros):")
        self.txt_context = self._add_field(self.scroll_plan, "4. Estrategia sobre el Contexto Físico/Situacional:")
        
        ctk.CTkLabel(self.scroll_plan, text="5. Técnicas Específicas a Utilizar:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        self.txt_techs = ctk.CTkTextbox(self.scroll_plan, height=80)
        self.txt_techs.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(self.scroll_plan, text="(Consulta la pestaña 'Biblioteca' para ideas)", text_color="gray", font=("Roboto", 10)).pack(anchor="w", padx=10)

        self.btn_save_plan = ctk.CTkButton(self.scroll_plan, text="GUARDAR PLAN", height=40, fg_color="darkblue", command=self._save_plan)
        self.btn_save_plan.pack(fill="x", pady=20, padx=10)

        self._load_micros()

    def _add_field(self, parent, label):
        ctk.CTkLabel(parent, text=label, font=("Roboto", 12, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        txt = ctk.CTkTextbox(parent, height=60)
        txt.pack(fill="x", padx=10, pady=5)
        return txt

    def _load_micros(self):
        micros = self.genesis_manager.get_available_micros(self.patient_id)
        if not micros:
            self.combo_micros.set("Sin microcontingencias")
            self.combo_micros.configure(state="disabled")
            return

        self.micro_map = {}
        values = []
        for m in micros:
            desc = m[1][:40] + "..."
            label = f"#{m[0]}: {desc}"
            self.micro_map[label] = m[0]
            values.append(label)
        
        self.combo_micros.configure(values=values)
        if values: 
            self.combo_micros.set(values[0])
            self._on_micro_selected(values[0])

    def _on_micro_selected(self, choice):
        micro_id = self.micro_map.get(choice)
        if not micro_id: return
        self.current_micro_id = micro_id
        
        plan = self.manager.get_plan_by_micro(micro_id)
        
        for t in [self.txt_goal, self.txt_morph, self.txt_actors, self.txt_context, self.txt_techs]:
            t.delete("1.0", "end")

        if plan:
            self.status_lbl.configure(text="✅ Plan Definido", text_color="green")
            self.btn_save_plan.configure(text="ACTUALIZAR PLAN", fg_color="#d35400")
            
            self.txt_goal.insert("0.0", plan['goal_description'])
            self.txt_morph.insert("0.0", plan['strategy_morphology'])
            self.txt_actors.insert("0.0", plan['strategy_actors'])
            self.txt_context.insert("0.0", plan['strategy_context'])
            self.txt_techs.insert("0.0", plan['techniques_text'])
        else:
            self.status_lbl.configure(text="⚪ Sin Plan", text_color="gray")
            self.btn_save_plan.configure(text="GUARDAR PLAN", fg_color="darkblue")

    def _save_plan(self):
        if not self.current_micro_id: return
        data = {
            'goal': self.txt_goal.get("1.0", "end-1c"),
            'morph': self.txt_morph.get("1.0", "end-1c"),
            'actors': self.txt_actors.get("1.0", "end-1c"),
            'context': self.txt_context.get("1.0", "end-1c"),
            'techs': self.txt_techs.get("1.0", "end-1c")
        }
        success, msg = self.manager.save_plan(self.patient_id, self.current_micro_id, data)
        if success:
            messagebox.showinfo("Éxito", msg)
            self._on_micro_selected(self.combo_micros.get())
        else:
            messagebox.showerror("Error", msg)

    def _setup_library_tab(self):
        header = ctk.CTkFrame(self.tab_lib)
        header.pack(fill="x", pady=10)
        
        ctk.CTkLabel(header, text="Filtrar por Categoría:").pack(side="left", padx=10)
        self.combo_cat = ctk.CTkComboBox(header, width=200, values=["Todas", "Cognitivo-Conductual", "ABA", "Contextual/ACT", "Regulación Emocional", "Exposición", "Habilidades", "Mindfulness", "Auto-Manejo", "Estímulos", "Motivación", "Mantenimiento", "Compasión"], command=self._refresh_library)
        self.combo_cat.pack(side="left", padx=10)
        
        ctk.CTkButton(header, text="🌐 Checar Fuentes", fg_color="gray", width=120, command=self._show_sources).pack(side="right", padx=10)
        ctk.CTkButton(header, text="+ Nueva Técnica", fg_color="green", width=120, command=self._add_technique_dialog).pack(side="right", padx=10)

        self.scroll_lib = ctk.CTkScrollableFrame(self.tab_lib, fg_color="transparent")
        self.scroll_lib.pack(fill="both", expand=True, padx=5, pady=5)
        
        self._refresh_library()

    def _refresh_library(self, _=None):
        for w in self.scroll_lib.winfo_children(): w.destroy()
        
        cat = self.combo_cat.get()
        techs = self.manager.get_all_techniques(cat)
        
        if not techs:
            ctk.CTkLabel(self.scroll_lib, text="No hay técnicas en esta categoría.", text_color="gray").pack(pady=20)
            return

        for t in techs:
            self._create_tech_card(t)

    def _create_tech_card(self, tech):
        card = ctk.CTkFrame(self.scroll_lib, border_width=1, border_color="gray")
        card.pack(fill="x", pady=5, padx=5)
        
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(header, text=tech['name'], font=("Roboto", 14, "bold")).pack(side="left")
        ctk.CTkLabel(header, text=f"[{tech['category']}]", text_color="lightblue", font=("Roboto", 11)).pack(side="right")
        
        ctk.CTkLabel(card, text=f"Objetivo: {tech['objective']}", anchor="w", font=("Roboto", 12, "bold")).pack(fill="x", padx=10)
        
        # Método
        ctk.CTkLabel(card, text=tech['method'], wraplength=800, justify="left").pack(fill="x", padx=10, pady=5)
        
        # Pros/Cons
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(footer, text=f"✅ {tech['pros']}", text_color="green", font=("Roboto", 11), wraplength=350, justify="left").pack(side="left", padx=(0,10), anchor="n")
        ctk.CTkLabel(footer, text=f"⚠️ {tech['cons']}", text_color="orange", font=("Roboto", 11), wraplength=350, justify="left").pack(side="left", anchor="n")

    def _show_sources(self):
        # --- AQUÍ ESTÁ LA CORRECCIÓN DE LA VENTANA ---
        win = ctk.CTkToplevel(self)
        win.title("Fuentes Bibliográficas")
        win.geometry("700x500")
        
        win.after(100, win.lift) # Levantar
        win.focus_force()        # Forzar foco
        win.grab_set()           # Bloquear ventana de atrás
        
        ctk.CTkLabel(win, text="Fuentes Bibliográficas Cargadas", font=("Roboto", 16, "bold")).pack(pady=10)
        
        scroll = ctk.CTkScrollableFrame(win)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        urls = self.manager.get_sources()
        if not urls:
            ctk.CTkLabel(scroll, text="No se encontraron fuentes cargadas.").pack()
            
        for i, u in enumerate(urls, 1):
            # Botón tipo enlace
            btn = ctk.CTkButton(scroll, text=f"{i}. {u}", anchor="w", fg_color="transparent", 
                                text_color="blue", hover_color="lightgray",
                                command=lambda url=u: webbrowser.open(url))
            btn.pack(fill="x", padx=5, pady=2)

    def _add_technique_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nueva Técnica")
        dialog.geometry("400x550")
        
        dialog.after(100, dialog.lift)
        dialog.focus_force()
        dialog.grab_set()
        
        fields = {}
        labels = ["Nombre", "Categoría", "Objetivo", "Método", "Pros", "Contras"]
        
        for lbl in labels:
            ctk.CTkLabel(dialog, text=lbl).pack(anchor="w", padx=20)
            entry = ctk.CTkEntry(dialog)
            entry.pack(fill="x", padx=20, pady=5)
            fields[lbl] = entry
            
        def save():
            data = {
                'name': fields['Nombre'].get(),
                'cat': fields['Categoría'].get(),
                'obj': fields['Objetivo'].get(),
                'method': fields['Método'].get(),
                'pros': fields['Pros'].get(),
                'cons': fields['Contras'].get()
            }
            if not data['name']: return
            self.manager.add_technique(data)
            self._refresh_library()
            dialog.destroy()
            
        ctk.CTkButton(dialog, text="Guardar", command=save, fg_color="green").pack(pady=20)