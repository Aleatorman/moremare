import customtkinter as ctk
from src.auth.auth_manager import AuthManager

class LoginWindow(ctk.CTk):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success

        # Configuración básica de la ventana
        self.title("Acceso - Análisis Contingencial")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Conexión con la lógica
        self.auth = AuthManager()

        # Diseño de la interfaz
        self._setup_ui()

    def _setup_ui(self):
        # Título
        self.label_title = ctk.CTkLabel(self, text="Bienvenido", font=("Roboto", 24))
        self.label_title.pack(pady=(50, 20))

        # Campo Usuario
        self.entry_user = ctk.CTkEntry(self, placeholder_text="Usuario", width=250)
        self.entry_user.pack(pady=10)

        # Campo Contraseña
        self.entry_pass = ctk.CTkEntry(self, placeholder_text="Contraseña", show="*", width=250)
        self.entry_pass.pack(pady=10)

        # Botón Iniciar Sesión
        self.btn_login = ctk.CTkButton(self, text="Iniciar Sesión", command=self._handle_login, width=250)
        self.btn_login.pack(pady=(20, 10))

        # Sección de Registro (Pequeña, para el primer usuario)
        self.label_register = ctk.CTkLabel(self, text="¿Es tu primera vez?", text_color="gray")
        self.label_register.pack(pady=(30, 5))
        
        self.btn_register = ctk.CTkButton(self, text="Registrar Nuevo Usuario", 
                                        command=self._handle_register, 
                                        fg_color="transparent", border_width=1, width=250)
        self.btn_register.pack(pady=5)

    def _handle_login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        
        success, data = self.auth.login(user, pwd)
        
        if success:
            print(f"Login correcto. ID Usuario: {data}")
            self.destroy() # Cierra la ventana de login
            self.on_login_success(data)
            # AQUI SE ABRIRÍA LA VENTANA PRINCIPAL (DASHBOARD)
            # Por ahora, simularemos esto en el main.py
        else:
            # Mostrar error visualmente
            self.label_title.configure(text="Error de credenciales", text_color="red")
            self.after(2000, lambda: self.label_title.configure(text="Bienvenido", text_color=("black", "white")))

    def _handle_register(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        
        success, message = self.auth.register_user(user, pwd)
        
        if success:
            self.label_title.configure(text="Usuario Creado", text_color="green")
        else:
            self.label_title.configure(text=f"Error: {message}", text_color="red")
        
        # Regresar color normal después de 2 segundos
        self.after(2000, lambda: self.label_title.configure(text="Bienvenido", text_color=("black", "white")))