import tkinter as tk

class ToolTip:
    """Crea una ventana flotante de ayuda al pasar el ratón sobre un widget."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tw = None
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        # Calculamos la posición del ratón para abrir el cuadro justo a un lado
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 20
        
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True) # Oculta la barra de título de la ventana
        self.tw.wm_geometry(f"+{x}+{y}")
        
        # Diseño del cuadro emergente (oscuro, moderno y con borde)
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#2b2b2b", foreground="white", relief='solid', borderwidth=1,
                         font=("Roboto", 11, "normal"), padx=10, pady=8, wraplength=350)
        label.pack(ipadx=1)

    def leave(self, event=None):
        if self.tw:
            self.tw.destroy()
            self.tw = None