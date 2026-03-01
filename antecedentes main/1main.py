import customtkinter as ctk
from ui.login_window import LoginWindow

# Configuración global de apariencia (Modo oscuro por defecto)
ctk.set_appearance_mode("System")  # "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Tema de color

def main():
    # 1. Iniciar con la pantalla de Login
    app = LoginWindow()
    app.mainloop()
    
    # NOTA: Cuando cerremos el login exitosamente, 
    # aquí lanzaremos el Dashboard más adelante.
    print("El programa ha finalizado.")

if __name__ == "__main__":
    main()