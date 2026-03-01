import customtkinter as ctk
from tkinter import filedialog, messagebox
from src.clinical.report.report_manager import ReportManager

class ReportPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.manager = ReportManager()
        
        self._setup_ui()
        self._refresh_preview() # Cargar vista inicial

    def _setup_ui(self):
        # Título
        ctk.CTkLabel(self, text="6. Generador de Informes", font=("Roboto", 22, "bold")).pack(anchor="w", pady=(0, 10))

        # Layout Principal (2 Columnas)
        main_layout = ctk.CTkFrame(self, fg_color="transparent")
        main_layout.pack(fill="both", expand=True)
        
        # --- COLUMNA IZQUIERDA: CONFIGURACIÓN ---
        left_col = ctk.CTkFrame(main_layout, width=250)
        left_col.pack(side="left", fill="y", padx=(0, 10))
        
        ctk.CTkLabel(left_col, text="Secciones a Incluir:", font=("Roboto", 14, "bold")).pack(pady=10)
        
        self.chk_datos = ctk.CTkCheckBox(left_col, text="1. Datos Generales", command=self._refresh_preview)
        self.chk_datos.select()
        self.chk_datos.pack(anchor="w", padx=20, pady=5)
        
        self.chk_micro = ctk.CTkCheckBox(left_col, text="2. Microcontingencias", command=self._refresh_preview)
        self.chk_micro.select()
        self.chk_micro.pack(anchor="w", padx=20, pady=5)
        
        self.chk_macro = ctk.CTkCheckBox(left_col, text="3. Macrocontingencias", command=self._refresh_preview)
        self.chk_macro.select()
        self.chk_macro.pack(anchor="w", padx=20, pady=5)
        
        self.chk_genesis = ctk.CTkCheckBox(left_col, text="4. Génesis e Historia", command=self._refresh_preview)
        self.chk_genesis.select()
        self.chk_genesis.pack(anchor="w", padx=20, pady=5)
        
        self.chk_interv = ctk.CTkCheckBox(left_col, text="5. Intervención", command=self._refresh_preview)
        self.chk_interv.select()
        self.chk_interv.pack(anchor="w", padx=20, pady=5)
        
        ctk.CTkFrame(left_col, height=2, fg_color="gray").pack(fill="x", pady=20, padx=10)
        
        self.btn_export = ctk.CTkButton(left_col, text="📄 GUARDAR PDF", height=50, fg_color="green", command=self._export_pdf)
        self.btn_export.pack(padx=20, pady=10, fill="x")

        # --- COLUMNA DERECHA: VISTA PREVIA ---
        right_col = ctk.CTkFrame(main_layout)
        right_col.pack(side="right", fill="both", expand=True)
        
        ctk.CTkLabel(right_col, text="Vista Previa del Documento:", font=("Roboto", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.txt_preview = ctk.CTkTextbox(right_col, font=("Consolas", 12)) # Fuente monoespaciada para ver mejor
        self.txt_preview.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _get_sections(self):
        return {
            'datos': self.chk_datos.get(),
            'micro': self.chk_micro.get(),
            'macro': self.chk_macro.get(),
            'genesis': self.chk_genesis.get(),
            'interv': self.chk_interv.get()
        }

    def _refresh_preview(self):
        """Actualiza el texto de la derecha según los checkboxes."""
        sections = self._get_sections()
        text = self.manager.generate_preview_text(self.patient_id, sections)
        
        self.txt_preview.configure(state="normal")
        self.txt_preview.delete("1.0", "end")
        self.txt_preview.insert("0.0", text)
        self.txt_preview.configure(state="disabled") # Solo lectura

    def _export_pdf(self):
        sections = self._get_sections()
        
        # Pedir dónde guardar
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar Informe Clínico"
        )
        
        if not filename: return # Usuario canceló
        
        try:
            self.manager.create_pdf(self.patient_id, sections, filename)
            messagebox.showinfo("Éxito", f"Informe guardado correctamente en:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el PDF:\n{str(e)}")