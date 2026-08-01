import customtkinter as ctk
from tkinter import messagebox
from src.clinical.report_manager import ReportManager

class ReportPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = ReportManager()
        self._setup_ui()

    def _setup_ui(self):
        # Título
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Generador de Informe Clínico Avanzado", font=("Roboto", 24, "bold")).pack(side="left")

        # Área de instrucciones
        instrucciones = ("💡 Este módulo recopila y formatea automáticamente toda la información registrada en los paneles anteriores.\n"
                         "Al hacer clic en exportar, el expediente se abrirá en su navegador web (Chrome, Edge, Safari).\n"
                         "Desde allí, puede leerlo cómodamente o presionar (Ctrl + P) para guardarlo como un PDF perfecto.")
        
        info_frame = ctk.CTkFrame(self, fg_color="#e8f8f5", border_color="#1abc9c", border_width=1)
        info_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(info_frame, text=instrucciones, text_color="#16a085", justify="left").pack(padx=15, pady=15)

        # Botón de Previsualización Rápida
        ctk.CTkButton(self, text="🔄 Cargar Vista Previa Rápida (Texto Plano)", fg_color="gray", 
                      command=self._load_quick_preview).pack(anchor="w", pady=(10, 5))

        # Área de visualización del informe
        self.report_area = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=10, border_width=1, border_color="#ccc")
        self.report_area.pack(fill="both", expand=True)
        
        self.txt_report = ctk.CTkTextbox(self.report_area, font=("Consolas", 12), fg_color="transparent", text_color="black")
        self.txt_report.pack(fill="both", expand=True, padx=10, pady=10)
        self.txt_report.insert("1.0", "Haga clic en 'Cargar Vista Previa Rápida' para leer un resumen aquí,\no utilice el botón morado de abajo para generar el expediente profesional HTML/PDF.")

        # Botón Morado de Exportación Final
        self.btn_export = ctk.CTkButton(self, text="🖨️ EXPORTAR Y ABRIR REPORTE COMPLETO (HTML/PDF)", 
                                        fg_color="#8e44ad", hover_color="#9b59b6", height=45, font=("Roboto", 14, "bold"),
                                        command=self._export_report)
        self.btn_export.pack(fill="x", pady=(15, 10))

    def _load_quick_preview(self):
        """Carga una vista previa rápida extrayendo solo las metas y un resumen."""
        try:
            p = self.manager.patient_mgr.get_patient_by_id(self.patient_id)
            preview = f"--- VISTA PREVIA RÁPIDA ---\n\n"
            preview += f"Paciente: {p['code_name']}\nMotivo: {p['motive']}\n\n"
            preview += "El expediente completo incluirá las Microcontingencias, Macrocontingencias, Génesis, Intervención y Evaluaciones de Proceso.\n"
            preview += "Haga clic en el botón morado inferior para generar el documento formateado."
            
            self.txt_report.delete("1.0", "end")
            self.txt_report.insert("1.0", preview)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la vista previa: {e}")

    def _export_report(self):
        """Llama al manager para generar el HTML y abrirlo en el navegador."""
        success, msg = self.manager.export_and_open(self.patient_id)
        if success:
            # Mostramos el aviso de éxito
            messagebox.showinfo("Reporte Generado", msg)
        else:
            messagebox.showerror("Error", msg)