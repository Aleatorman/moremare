import customtkinter as ctk
from ui.login_window import LoginWindow
from ui.dashboard_window import DashboardWindow

def main():
    # Variables para controlar el flujo fuera del login
    login_successful = False
    current_user_id = None

    def handle_login_success(uid):
        nonlocal login_successful, current_user_id
        login_successful = True
        current_user_id = uid
        # Esto cierra la ventana de login y ROMPE su mainloop limpiamente
        login_app.destroy() 

    # Iniciar la aplicación de Login
    login_app = LoginWindow(on_login_success=handle_login_success)
    login_app.mainloop()

    # --- EL CÓDIGO SOLO LLEGA AQUÍ CUANDO LA VENTANA DE LOGIN SE HA CERRADO ---
    
    # Si el login fue exitoso, arrancamos el Dashboard con su propio mainloop independiente
    if login_successful and current_user_id:
        app = DashboardWindow(current_user_id)
        app.mainloop()

if __name__ == "__main__":
    main()