import customtkinter as ctk
from ui.login_window import LoginWindow
from ui.dashboard_window import DashboardWindow

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def launch_dashboard(user_id):
    """Función que arranca la ventana principal."""
    app = DashboardWindow(user_id)
    app.mainloop()

def main():
    # Pasamos 'launch_dashboard' como función a ejecutar si el login es bueno
    login_app = LoginWindow(on_login_success=launch_dashboard)
    login_app.mainloop()

if __name__ == "__main__":
    main()