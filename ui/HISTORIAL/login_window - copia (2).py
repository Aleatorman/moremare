import customtkinter as ctk
from tkinter import messagebox
from src.auth.auth_manager import AuthManager

class LoginWindow(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.auth = AuthManager()

        self.title("Acceso Seguro")
        self.geometry("400x550")
        self.resizable(False, False)
        
        # Contenedor principal que cambiará de contenido
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Decidir qué pantalla mostrar
        if self.auth.is_system_setup():
            self._show_login_screen()
        else:
            self._show_setup_screen()

    # ==========================================
    # PANTALLA 1: CONFIGURACIÓN INICIAL
    # ==========================================
    def _show_setup_screen(self):
        self._clear_frame()
        
        ctk.CTkLabel(self.main_frame, text="👋 ¡Bienvenido!", font=("Arial", 26, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self.main_frame, text="Configuremos tu seguridad por única vez.", text_color="gray").pack(pady=(0, 20))

        ctk.CTkLabel(self.main_frame, text="Crea tu Contraseña Maestra:", anchor="w").pack(fill="x", pady=(10, 0))
        self.entry_new_pass = ctk.CTkEntry(self.main_frame, show="*", width=300)
        self.entry_new_pass.pack(pady=5)

        ctk.CTkLabel(self.main_frame, text="Pregunta de Seguridad (para recuperar):", anchor="w").pack(fill="x", pady=(15, 0))
        self.entry_question = ctk.CTkEntry(self.main_frame, placeholder_text="Ej: Nombre de mi primera mascota", width=300)
        self.entry_question.pack(pady=5)

        ctk.CTkLabel(self.main_frame, text="Respuesta Secreta:", anchor="w").pack(fill="x", pady=(10, 0))
        self.entry_answer = ctk.CTkEntry(self.main_frame, show="*", width=300)
        self.entry_answer.pack(pady=5)

        ctk.CTkButton(self.main_frame, text="GUARDAR Y ENTRAR", fg_color="#27ae60", height=40, 
                      command=self._do_setup).pack(pady=30, fill="x")

    def _do_setup(self):
        pwd = self.entry_new_pass.get()
        ques = self.entry_question.get()
        ans = self.entry_answer.get()

        if not pwd or not ques or not ans:
            messagebox.showwarning("Faltan datos", "Por favor llena todos los campos.")
            return

        success, msg = self.auth.setup_first_time(pwd, ques, ans)
        if success:
            messagebox.showinfo("¡Listo!", "Sistema configurado correctamente.")
            self._show_login_screen()
        else:
            messagebox.showerror("Error", msg)

    # ==========================================
    # PANTALLA 2: LOGIN DIARIO
    # ==========================================
    def _show_login_screen(self):
        self._clear_frame()
        
        ctk.CTkLabel(self.main_frame, text="🔒", font=("Arial", 60)).pack(pady=(40, 10))
        ctk.CTkLabel(self.main_frame, text="Hola de nuevo", font=("Arial", 22, "bold")).pack(pady=5)

        self.entry_pass = ctk.CTkEntry(self.main_frame, placeholder_text="Contraseña", show="*", width=280, height=40)
        self.entry_pass.pack(pady=20)
        self.entry_pass.bind("<Return>", lambda e: self._do_login()) # Enter para entrar

        ctk.CTkButton(self.main_frame, text="Desbloquear", height=45, width=280, 
                      command=self._do_login).pack(pady=10)

        ctk.CTkButton(self.main_frame, text="¿Olvidaste tu contraseña?", fg_color="transparent", text_color="gray", 
                      hover_color="#f0f0f0", command=self._show_recovery_screen).pack(pady=20)

    def _do_login(self):
        pwd = self.entry_pass.get()
        success, uid = self.auth.login(pwd)
        
        if success:
            self.destroy()
            self.on_login_success(uid)
        else:
            self.entry_pass.configure(border_color="red")
            messagebox.showerror("Error", "Contraseña incorrecta")

    # ==========================================
    # PANTALLA 3: RECUPERACIÓN
    # ==========================================
    def _show_recovery_screen(self):
        self._clear_frame()
        question = self.auth.get_security_question()

        ctk.CTkLabel(self.main_frame, text="Recuperar Acceso", font=("Arial", 20, "bold")).pack(pady=20)
        
        ctk.CTkLabel(self.main_frame, text="Responde a tu pregunta de seguridad:", text_color="gray").pack(pady=5)
        ctk.CTkLabel(self.main_frame, text=f"¿{question}?", font=("Arial", 14, "bold"), text_color="#3498db").pack(pady=10)

        self.entry_rec_ans = ctk.CTkEntry(self.main_frame, placeholder_text="Tu respuesta...", width=280)
        self.entry_rec_ans.pack(pady=10)

        ctk.CTkLabel(self.main_frame, text="Nueva Contraseña:", anchor="w").pack(pady=(20,0))
        self.entry_rec_new_pass = ctk.CTkEntry(self.main_frame, show="*", width=280)
        self.entry_rec_new_pass.pack(pady=5)

        ctk.CTkButton(self.main_frame, text="RESTABLECER", fg_color="#e67e22", height=40, width=280,
                      command=self._do_reset).pack(pady=20)
        
        ctk.CTkButton(self.main_frame, text="Cancelar", fg_color="transparent", text_color="gray", 
                      command=self._show_login_screen).pack()

    def _do_reset(self):
        ans = self.entry_rec_ans.get()
        new_pwd = self.entry_rec_new_pass.get()
        
        if not ans or not new_pwd:
            return

        success, msg = self.auth.reset_password(ans, new_pwd)
        if success:
            messagebox.showinfo("Éxito", "Contraseña actualizada. Inicia sesión.")
            self._show_login_screen()
        else:
            messagebox.showerror("Error", msg)

    def _clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()