import customtkinter as ctk
import time
from datetime import datetime

class ABACalculator(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.count = 0
        self.start_time = None
        self.is_running = False
        
        self._setup_ui()

    def _setup_ui(self):
        # Header
        ctk.CTkLabel(self, text="Calculadora de Tasa y Frecuencia (ABA)", font=("Arial", 20, "bold")).pack(pady=10)
        ctk.CTkLabel(self, text="Herramienta basada en medición continua", text_color="gray").pack()

        # Panel Principal
        main_panel = ctk.CTkFrame(self, fg_color=("white", "gray20"), corner_radius=15)
        main_panel.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. Cronómetro
        self.lbl_timer = ctk.CTkLabel(main_panel, text="00:00:00", font=("Consolas", 40, "bold"), text_color="#3498db")
        self.lbl_timer.pack(pady=(30, 10))
        
        btn_frame = ctk.CTkFrame(main_panel, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        self.btn_start = ctk.CTkButton(btn_frame, text="▶ Iniciar Sesión", fg_color="green", command=self._toggle_timer)
        self.btn_start.pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="⏹ Reiniciar", fg_color="red", command=self._reset).pack(side="left", padx=5)

        # 2. Contador de Conducta
        ctk.CTkLabel(main_panel, text="Frecuencia (Conteo)", font=("Arial", 16, "bold")).pack(pady=(30, 10))
        
        counter_frame = ctk.CTkFrame(main_panel, fg_color="transparent")
        counter_frame.pack()
        
        ctk.CTkButton(counter_frame, text="-", width=50, height=50, font=("Arial", 20), fg_color="gray", command=self._decrement).pack(side="left", padx=10)
        self.lbl_count = ctk.CTkLabel(counter_frame, text="0", font=("Arial", 50, "bold"))
        self.lbl_count.pack(side="left", padx=20)
        ctk.CTkButton(counter_frame, text="+", width=50, height=50, font=("Arial", 20), fg_color="#e67e22", command=self._increment).pack(side="left", padx=10)

        # 3. Resultados en Tiempo Real
        results_frame = ctk.CTkFrame(main_panel, fg_color=("gray90", "gray30"), corner_radius=10)
        results_frame.pack(fill="x", padx=20, pady=30)
        
        self.lbl_rate = ctk.CTkLabel(results_frame, text="Tasa Actual: 0.00 respuestas / minuto", font=("Arial", 16))
        self.lbl_rate.pack(pady=15)

    def _toggle_timer(self):
        if not self.is_running:
            self.is_running = True
            self.start_time = time.time() if self.start_time is None else time.time() - self.elapsed
            self.btn_start.configure(text="⏸ Pausar", fg_color="orange")
            self._update_timer()
        else:
            self.is_running = False
            self.elapsed = time.time() - self.start_time
            self.btn_start.configure(text="▶ Continuar", fg_color="green")

    def _update_timer(self):
        if self.is_running:
            self.elapsed = time.time() - self.start_time
            minutes = int(self.elapsed // 60)
            seconds = int(self.elapsed % 60)
            centis = int((self.elapsed * 100) % 100)
            self.lbl_timer.configure(text=f"{minutes:02}:{seconds:02}:{centis:02}")
            self._calc_rate()
            self.after(50, self._update_timer)

    def _increment(self):
        self.count += 1
        self.lbl_count.configure(text=str(self.count))
        self._calc_rate()

    def _decrement(self):
        if self.count > 0:
            self.count -= 1
            self.lbl_count.configure(text=str(self.count))
            self._calc_rate()

    def _calc_rate(self):
        # Tasa = Frecuencia / Tiempo (en minutos)
        if hasattr(self, 'elapsed') and self.elapsed > 0:
            minutes = self.elapsed / 60
            rate = self.count / minutes
            self.lbl_rate.configure(text=f"Tasa Actual: {rate:.2f} respuestas / minuto")

    def _reset(self):
        self.is_running = False
        self.start_time = None
        self.elapsed = 0
        self.count = 0
        self.lbl_timer.configure(text="00:00:00")
        self.lbl_count.configure(text="0")
        self.lbl_rate.configure(text="Tasa Actual: 0.00 respuestas / minuto")
        self.btn_start.configure(text="▶ Iniciar Sesión", fg_color="green")