import customtkinter as ctk
from tkinter import messagebox
import sqlite3

class ReportPanel(ctk.CTkFrame):
    def __init__(self, parent, patient_id):
        super().__init__(parent, fg_color="transparent")
        self.patient_id = patient_id
        self.db_path = "database/clinical_app.db"
        self._setup_ui()

    def _setup_ui(self):
        # Título y Botón de Generar
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(header, text="Generador de Informe Clínico", font=("Roboto", 24, "bold")).pack(side="left")
        
        ctk.CTkButton(header, text="🔄 Actualizar/Generar Informe", fg_color="#27ae60", 
                      command=self.generate_report).pack(side="right")

        # Área de visualización del informe
        self.report_area = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=10, border_width=1, border_color="#ccc")
        self.report_area.pack(fill="both", expand=True)
        
        self.txt_report = ctk.CTkTextbox(self.report_area, font=("Consolas", 12), fg_color="transparent", text_color="black")
        self.txt_report.pack(fill="both", expand=True, padx=10, pady=10)

    def generate_report(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # 1. Datos del Paciente
                cursor.execute("SELECT * FROM patients WHERE id = ?", (self.patient_id,))
                p = cursor.fetchone()
                
                report = f"{'='*60}\n"
                report += f"INFORME PSICOLÓGICO: ANÁLISIS CONTINGENCIAL\n"
                report += f"{'='*60}\n\n"
                report += f"PACIENTE: {p['code_name']}\nEDAD: {p['age']} años\nOCUPACIÓN: {p['occupation']}\n"
                report += f"MOTIVO DE CONSULTA: {p['motive']}\n"
                report += f"METAS DEL USUARIO: {p['goals']}\n\n"

                # 2. Análisis Macrocontingencial
                report += f"{'-'*60}\n1. ANÁLISIS MACROCONTINGENCIAL\n{'-'*60}\n"
                cursor.execute("SELECT * FROM macrocontingencies WHERE patient_id = ?", (self.patient_id,))
                macros = cursor.fetchall()
                for m in macros:
                    report += f"GRUPO: {m['group_type']} ({m['group_name']})\n"
                    report += f"CREENCIAS: {m['beliefs_values']}\n"
                    report += f"ANÁLISIS INTRA: {m['intra_analysis']}\n"
                    report += f"ANÁLISIS INTER: {m['inter_analysis']}\n\n"

                # 3. Génesis e Historia
                report += f"{'-'*60}\n2. GÉNESIS DEL PROBLEMA\n{'-'*60}\n"
                cursor.execute("SELECT * FROM genesis_history WHERE patient_id = ?", (self.patient_id,))
                g = cursor.fetchone()
                if g:
                    report += f"HISTORIA DE ORIGEN: {g['origin_history']}\n"
                    report += f"HISTORIA FUNCIONAL: {g['functional_history']}\n\n"

                # 4. Plan de Intervención y Soluciones
                report += f"{'-'*60}\n3. PLAN DE INTERVENCIÓN\n{'-'*60}\n"
                cursor.execute("SELECT * FROM intervention_plans WHERE patient_id = ?", (self.patient_id,))
                plans = cursor.fetchall()
                for pl in plans:
                    report += f"OBJETIVOS TERAPÉUTICOS: {pl['therapeutic_objectives']}\n"
                    report += f"ESTRATEGIA MORFOLÓGICA: {pl['strategy_morphology']}\n"
                    report += f"TÉCNICAS SELECCIONADAS: {pl['techniques_text']}\n\n"

                # 5. Evaluación del Proceso (Matriz)
                report += f"{'-'*60}\n4. EVALUACIÓN DEL PROCESO (Última sesión)\n{'-'*60}\n"
                cursor.execute("SELECT id, date_eval, notes FROM evaluations WHERE patient_id = ? ORDER BY date_eval DESC LIMIT 1", (self.patient_id,))
                ev = cursor.fetchone()
                if ev:
                    report += f"FECHA EVALUACIÓN: {ev['date_eval']}\n"
                    cursor.execute("SELECT * FROM evaluation_matrix WHERE evaluation_id = ?", (ev['id'],))
                    matrix = cursor.fetchall()
                    report += f"{'PARÁMETRO':<20} | {'TERAPIA':<10} | {'TERAPEUTA':<10}\n"
                    for row in matrix:
                        report += f"{row['parameter']:<20} | {row['terapia_val']:<10} | {row['terapeuta_val']:<10}\n"
                    report += f"\nNOTAS DE SEGUIMIENTO: {ev['notes']}\n"

                self.txt_report.delete("1.0", "end")
                self.txt_report.insert("1.0", report)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {e}")