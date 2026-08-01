import datetime
import webbrowser
import os
import sqlite3
from src.clinical.patient_manager import PatientManager
from src.clinical.micro.micro_manager import MicroManager
from src.clinical.macro.macro_manager import MacroManager
from src.clinical.genesis.genesis_manager import GenesisManager
from src.clinical.intervention.intervention_manager import InterventionManager

class ReportManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path
        self.patient_mgr = PatientManager(db_path)
        self.micro_mgr = MicroManager(db_path)
        self.macro_mgr = MacroManager(db_path)
        self.genesis_mgr = GenesisManager(db_path)
        self.interv_mgr = InterventionManager(db_path)

    def generate_html(self, patient_id):
        """Construye un expediente clínico completo en formato HTML con CSS integrado."""
        
        # 1. Recuperar Datos del Paciente
        p = self.patient_mgr.get_patient_by_id(patient_id)
        if not p: return "<h1>Error: Paciente no encontrado</h1>"
        
        date_str = datetime.date.today().strftime("%d/%m/%Y")
        
        # --- INICIO DEL HTML Y CSS ---
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Expediente Clínico - {p['code_name']}</title>
            <style>
                body {{ font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #2c3e50; line-height: 1.6; padding: 20px; max-width: 900px; margin: auto; }}
                h1 {{ text-align: center; color: #2980b9; border-bottom: 2px solid #2980b9; padding-bottom: 10px; }}
                h2 {{ color: #16a085; border-bottom: 1px solid #bdc3c7; margin-top: 30px; padding-bottom: 5px; }}
                h3 {{ color: #34495e; margin-bottom: 5px; }}
                .card {{ background: #fdfefe; border: 1px solid #d5dbdb; border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); page-break-inside: avoid; }}
                .data-row {{ display: flex; margin-bottom: 8px; border-bottom: 1px dashed #ecf0f1; padding-bottom: 5px; }}
                .data-label {{ font-weight: bold; width: 200px; color: #34495e; }}
                .data-value {{ flex: 1; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ border: 1px solid #bdc3c7; padding: 10px; text-align: left; }}
                th {{ background-color: #ecf0f1; color: #2c3e50; }}
                .highlight {{ background-color: #fef9e7; padding: 5px; border-left: 4px solid #f1c40f; }}
            </style>
        </head>
        <body>
            <h1>REPORTE DE ANÁLISIS CONTINGENCIAL</h1>
            <div style="text-align: right; color: #7f8c8d; margin-bottom: 20px;">Fecha de emisión: {date_str}</div>
            
            <h2>1. DATOS DE IDENTIFICACIÓN</h2>
            <div class="card">
                <div class="data-row"><div class="data-label">Nombre/Código:</div><div class="data-value">{p.get('code_name', '')}</div></div>
                <div class="data-row"><div class="data-label">Edad:</div><div class="data-value">{p.get('age', '')} años</div></div>
                <div class="data-row"><div class="data-label">Sexo:</div><div class="data-value">{p.get('sex', '')}</div></div>
                <div class="data-row"><div class="data-label">Ocupación:</div><div class="data-value">{p.get('occupation', '')}</div></div>
                <div class="data-row"><div class="data-label">Motivo de Consulta:</div><div class="data-value"><i>"{p.get('motive', '')}"</i></div></div>
                <div class="data-row"><div class="data-label">Metas y Expectativas:</div><div class="data-value">{p.get('goals', 'No especificadas')}</div></div>
            </div>
        """

        # 2. Análisis Microcontingencial
        html += "<h2>2. ANÁLISIS MICROCONTINGENCIAL (Situacional)</h2>"
        micros = self.micro_mgr.get_list_by_patient(patient_id)
        if not micros:
            html += "<p>No hay microcontingencias registradas.</p>"
        else:
            for m_tuple in micros:
                m_id = m_tuple[0]
                full_m = self.micro_mgr.get_full_microcontingency(m_id)
                html += f"<h3>Situación: {full_m.get('label', 'Sin título')}</h3><div class='card'>"
                
                # Morfologías
                html += "<b>A. Morfología de la Conducta:</b><ul>"
                for i in full_m.get('morphologies', []):
                    html += f"<li>{i.get('type','')} ({i.get('class','')}) - {i.get('molar','')} / {i.get('molecular','')}: {i.get('description','')}</li>"
                html += "</ul>"
                
                # Contextos
                if full_m.get('social_contexts'):
                    html += "<b>B1. Contexto Social:</b> " + ", ".join([f"{i.get('type','')}: {i.get('description','')}" for i in full_m['social_contexts']]) + "<br><br>"
                
                # Competencias (Las nuevas columnas)
                html += "<b>B3. Ajuste Funcional y Competencias:</b><ul>"
                for i in full_m.get('interactions', []):
                    html += f"<li><b>Esperado:</b> {i.get('expected','')}</li>"
                    html += f"<li><b>C. Efectiva:</b> {i.get('competence','')}</li>"
                    html += f"<li><b>C. Afectiva:</b> {i.get('comp_afectiva','')}</li>"
                    html += f"<li><b>C. Valorativa:</b> {i.get('comp_valorativa','')}</li>"
                html += "</ul>"
                
                # Efectos
                if full_m.get('effects'):
                    html += "<b>D. Efectos / Consecuencias:</b><ul>"
                    for i in full_m['effects']:
                        html += f"<li>{i.get('type','')}: {i.get('description','')}</li>"
                    html += "</ul>"
                
                html += "</div>"

        # 3. Análisis Macrocontingencial
        html += "<h2>3. ANÁLISIS MACROCONTINGENCIAL (Grupo de Referencia)</h2>"
        macros = self.macro_mgr.get_macros(patient_id)
        if not macros:
            html += "<p>No hay análisis macro registrado.</p>"
        else:
            for m_info in macros:
                mac = self.macro_mgr.get_full_macro(m_info[0])
                html += f"<div class='card'>"
                html += f"<div class='data-row'><div class='data-label'>Grupo Analizado:</div><div class='data-value'>{mac.get('group_type', '')} - {mac.get('group_name', '')}</div></div>"
                html += f"<div class='data-row'><div class='data-label'>Prácticas Sustitutivas (Creencias):</div><div class='data-value'>{mac.get('beliefs_values', '')}</div></div>"
                html += f"<div class='data-row'><div class='data-label'>Prácticas Efectivas (Costumbres):</div><div class='data-value'>{mac.get('customs_lifestyles', '')}</div></div>"
                
                # Modos de Regulación Moral (Nuevos campos)
                html += f"<div class='data-row'><div class='data-label'>Regulación Moral:</div><div class='data-value'><b>{mac.get('intra_analysis', '')}</b></div></div>"
                if mac.get('inter_analysis'):
                    html += f"<div class='data-row'><div class='data-label'>Sanción del Grupo:</div><div class='data-value'>{mac.get('inter_analysis', '')}</div></div>"
                
                if mac.get('clinical_hypothesis'):
                    html += f"<br><div class='highlight'><b>Hipótesis Clínica:</b><br>{mac.get('clinical_hypothesis')}</div>"
                html += "</div>"

        # 4. Génesis
        html += "<h2>4. GÉNESIS DEL PROBLEMA</h2>"
        gen_list = self.genesis_mgr.get_genesis_history_list(patient_id)
        if not gen_list:
            html += "<p>No hay historia registrada.</p>"
        else:
            for g in gen_list:
                origin = g.get('origin_history', {})
                func = g.get('functional_history', {})
                html += f"<div class='card'>"
                html += f"<b>Origen:</b> {origin.get('circunstancia', '')}<br><br>"
                html += f"<b>Narrativa:</b> {origin.get('narrativa_origen', '')}<br><br>"
                html += f"<b>Función Histórica:</b> {func.get('func_no_prob', '')}<br>"
                html += "</div>"

        # 5. Intervención
        html += "<h2>5. PLAN DE INTERVENCIÓN ESTRATÉGICO</h2>"
        found_plan = False
        if micros:
            for m_tuple in micros:
                m_id = m_tuple[0]
                plan = self.interv_mgr.get_plan_by_micro(m_id)
                if plan:
                    found_plan = True
                    html += f"<div class='card'>"
                    html += f"<h3>Objetivos Terapéuticos:</h3><p>{plan.get('therapeutic_objectives', '')}</p>"
                    html += f"<h3>Estrategias Funcionales:</h3><ul>"
                    if plan.get('strategy_adquisition'): html += f"<li><b>Adquisición:</b> {plan.get('strategy_adquisition')}</li>"
                    if plan.get('strategy_precision'): html += f"<li><b>Precisión:</b> {plan.get('strategy_precision')}</li>"
                    if plan.get('strategy_opportunity'): html += f"<li><b>Oportunidad:</b> {plan.get('strategy_opportunity')}</li>"
                    if plan.get('strategy_tendency'): html += f"<li><b>Tendencia:</b> {plan.get('strategy_tendency')}</li>"
                    html += f"</ul>"
                    html += f"<h3>Técnicas Seleccionadas:</h3><pre style='font-family: inherit;'>{plan.get('techniques_text', '')}</pre>"
                    html += "</div>"
        
        if not found_plan:
            html += "<p>No hay planes de intervención definidos.</p>"

        # 6. Evaluaciones
        html += "<h2>6. EVALUACIÓN DEL PROCESO TERAPÉUTICO</h2>"
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute("SELECT * FROM evaluations WHERE patient_id = ? ORDER BY date_eval DESC", (patient_id,))
                evals = c.fetchall()
                if not evals:
                    html += "<p>No hay evaluaciones registradas.</p>"
                else:
                    for ev in evals:
                        html += f"<div class='card'><b>Fecha:</b> {ev['date_eval']}<br>"
                        html += f"<b>Notas Clínicas:</b> {ev['notes']}<br>"
                        c.execute("SELECT * FROM evaluation_matrix WHERE evaluation_id = ?", (ev['id'],))
                        matrix = c.fetchall()
                        if matrix:
                            html += "<table><tr><th>Objetivo</th><th>Parámetro</th><th>Val. Terapia</th><th>Val. Terapeuta</th></tr>"
                            for row in matrix:
                                html += f"<tr><td>{row['target']}</td><td>{row['parameter']}</td><td>{row['terapia_val']}</td><td>{row['terapeuta_val']}</td></tr>"
                            html += "</table>"
                        html += "</div>"
        except Exception as e:
            html += f"<p>Error cargando evaluaciones: {e}</p>"

        html += "</body></html>"
        return html

    def export_and_open(self, patient_id):
        """Genera el HTML, lo guarda temporalmente y lo abre en el navegador web predeterminado."""
        try:
            html_content = self.generate_html(patient_id)
            
            # Nombre de archivo seguro
            p = self.patient_mgr.get_patient_by_id(patient_id)
            safe_name = "".join([c for c in p['code_name'] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            filename = f"Expediente_{safe_name}.html".replace(" ", "_")
            
            filepath = os.path.abspath(filename)
            
            # Guardamos el HTML con encoding utf-8
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Abrimos el archivo en el navegador por defecto del sistema
            webbrowser.open('file://' + filepath)
            
            return True, f"Reporte generado exitosamente.\nSe ha abierto en su navegador web."
        except Exception as e:
            return False, f"Error al exportar: {e}"