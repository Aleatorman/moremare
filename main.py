import customtkinter as ctk
from ui.login_window import LoginWindow
from ui.dashboard_window import DashboardWindow
from ui.splash_window import SplashWindow
from database import setup_db

def main():
    def start_application():
        # 1. Configurar BD en segundo plano una vez que la UI ya está cargando
        setup_db.main() 

        login_successful = False
        current_user_id = None

        def handle_login_success(uid):
            nonlocal login_successful, current_user_id
            login_successful = True
            current_user_id = uid
            login_app.destroy() 

        login_app = LoginWindow(on_login_success=handle_login_success)
        login_app.mainloop()

        if login_successful and current_user_id:
            app = DashboardWindow(current_user_id)
            app.mainloop()

    # Arrancamos el Splash Screen primero
    splash = SplashWindow(on_complete_callback=start_application)
    splash.mainloop()

if __name__ == "__main__":
    main()