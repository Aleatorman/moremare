import customtkinter as ctk

class SplashWindow(ctk.CTk):
    def __init__(self, on_complete_callback):
        super().__init__()
        self.on_complete = on_complete_callback
        
        # Configuración de ventana sin bordes
        self.overrideredirect(True)
        self.geometry("500x300")
        
        # Centrar en la pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (500 / 2)
        y = (screen_height / 2) - (300 / 2)
        self.geometry(f'+{int(x)}+{int(y)}')
        
        self.configure(fg_color="#1e1e1e") # Fondo oscuro

        # Diseño del Splash
        ctk.CTkLabel(self, text=" 🐘", font=("Arial", 50)).pack(pady=(40, 10))
        ctk.CTkLabel(self, text="Sistema CONTINGENCIAL", font=("Roboto", 28, "bold"), text_color="white").pack()
        ctk.CTkLabel(self, text="Hecho por El Aris - INTERCONDUCTEAMS", font=("Roboto", 12), text_color="gray").pack(pady=(5, 20))
        
        self.progress = ctk.CTkProgressBar(self, width=300, progress_color="#3498db")
        self.progress.pack(pady=10)
        self.progress.set(0)

        # Iniciar simulación de carga
        self.after(100, self._simulate_load)

    def _simulate_load(self):
        # Simula el avance de la barra (puedes ajustar la velocidad)
        step = 0
        while step <= 100:
            self.progress.set(step / 100)
            self.update_idletasks() # Fuerza la actualización visual
            self.after(30) # Espera 30ms
            step += 1
            
        self.destroy() # Cierra el splash
        self.on_complete() # Llama al inicio real de la app