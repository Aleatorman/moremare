from fpdf import FPDF
import datetime
from src.clinical.patient_manager import PatientManager
from src.clinical.micro.micro_manager import MicroManager
from src.clinical.macro.macro_manager import MacroManager
from src.clinical.genesis.genesis_manager import GenesisManager
from src.clinical.intervention.intervention_manager import InterventionManager

class ReportManager:
    def __init__(self):
        self.patient_mgr = PatientManager()
        self.micro_mgr = MicroManager()
        self.macro_mgr = MacroManager()
        self.genesis_mgr = GenesisManager()
        self.interv_mgr = InterventionManager()

    def generate_preview_text(self, patient_id, sections):
        """Genera un texto plano para mostrar en la pantalla antes del PDF."""
        text = ""
        p = self.patient_mgr.get_patient_by_id(patient_id)
        
        if not p: return "Error: Paciente no encontrado."

        # 1. ENCABEZADO
        text += f"INFORME CLÍNICO DE ANÁLISIS CONTINGENCIAL\n"
        text += f"Fecha: {datetime.date.today()}\n"
        text += "="*60 + "\n\n"

        # 2. DATOS GENERALES
        if sections.get('datos', True):
            text += "[1. DATOS DE IDENTIFICACIÓN]\n"
            text += f"Nombre/Código: {p['code_name']}\n"
            text += f"Edad: {p['age']} | Sexo: {p['sex']} | Ocupación: {p['occupation']}\n"
            text += f"Motivo de Consulta: {p['motive']}\n"
            goals = p.get('goals', 'No especificadas') 
            text += f"Metas y Expectativas: {goals}\n\n"

        # 3. MICROCONTINGENCIAS
        if sections.get('micro', True):
            micros = self.micro_mgr.get_list_by_patient(patient_id)
            text += "[2. ANÁLISIS MICROCONTINGENCIAL]\n"
            if not micros:
                text += "No hay microcontingencias registradas.\n"
            else:
                for m_tuple in micros:
                    m_id = m_tuple[0]
                    full_m = self.micro_mgr.get_full_microcontingency(m_id)
                    text += f"--- Microcontingencia #{m_id} ---\n"
                    text += f"Problema: {full_m['problem_desc']}\n"
                    text += f"Morfología: {full_m['morphology_type']} ({full_m['morphology_metrics']})\n"
                    text += f"Contexto: {full_m['social_context']}\n"
                    text += f"Consecuencia: {full_m['consequence_desc']}\n\n"
            text += "\n"

        # 4. MACROCONTINGENCIAS
        if sections.get('macro', True):
            macros = self.macro_mgr.get_all_macros(patient_id)
            text += "[3. SISTEMA MACROCONTINGENCIAL]\n"
            if not macros:
                text += "No hay análisis macro registrado.\n"
            else:
                for mac in macros:
                    text += f"- {mac['category']} ({mac['valuative_function']}): {mac['analysis']}\n"
            text += "\n"

        # 5. GÉNESIS
        if sections.get('genesis', True):
            # Usamos el método corregido que añadimos anteriormente
            gen_list = self.genesis_mgr.get_genesis_history_list(patient_id)
            text += "[4. GÉNESIS DEL PROBLEMA]\n"
            if not gen_list:
                text += "No hay historia registrada.\n"
            else:
                for g in gen_list:
                    origin = g['origin_history']
                    text += f"Historial de '{g['problem_desc']}':\n"
                    text += f"Inicio: {origin.get('circunstancia', '')}\n"
                    text += f"Narrativa: {origin.get('narrativa_origen', '')}\n\n"
            text += "\n"

        # 6. INTERVENCIÓN
        if sections.get('interv', True):
            text += "[5. PLAN DE INTERVENCIÓN]\n"
            micros = self.micro_mgr.get_list_by_patient(patient_id)
            found_plan = False
            if micros:
                for m in micros:
                    m_id = m[0]
                    plan = self.interv_mgr.get_plan_by_micro(m_id)
                    if plan:
                        found_plan = True
                        text += f"Plan para Micro #{m_id}:\n"
                        text += f"Objetivo: {plan['goal_description']}\n"
                        text += f"Técnicas: {plan['techniques_text']}\n"
                        text += "-"*30 + "\n"
            
            if not found_plan: text += "No hay planes de intervención definidos.\n"

        return text

    def create_pdf(self, patient_id, sections, filename):
        """Genera el archivo PDF real de forma robusta."""
        text_content = self.generate_preview_text(patient_id, sections)
        
        # 1. Configuración explícita: A4 Vertical, Unidades en mm
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        
        # 2. Establecer márgenes de 2 cm (20mm) para evitar el error de espacio
        pdf.set_margins(20, 20, 20)
        pdf.add_page()
        
        # 3. Calcular ancho efectivo de escritura (Ancho Hoja - Márgenes)
        # A4 width es 210mm. 210 - 20(izq) - 20(der) = 170mm
        epw = pdf.w - 2*pdf.l_margin 
        
        # Configuración de fuente estándar
        pdf.set_font("Arial", size=12)
        
        # Título
        pdf.set_font("Arial", "B", 16)
        pdf.cell(w=epw, h=10, txt="Informe Clínico", ln=True, align='C')
        pdf.ln(10)
        
        # Cuerpo
        pdf.set_font("Arial", size=11)
        
        # Procesar línea por línea
        for line in text_content.split('\n'):
            # Limpieza de caracteres: Arial solo soporta Latin-1.
            # 'replace' pondrá un '?' en caracteres raros para evitar errores.
            safe_line = line.encode('latin-1', 'replace').decode('latin-1')
            
            if not safe_line.strip():
                # Si es línea vacía, solo salto de línea
                pdf.ln(6) 
            else:
                # Multi_cell con ancho EXPLÍCITO (w=epw) para evitar el error
                try:
                    pdf.multi_cell(w=epw, h=6, txt=safe_line, align='L')
                except Exception as e:
                    print(f"Advertencia PDF: No se pudo imprimir una línea: {e}")
                    # Intento de recuperación simple
                    pdf.cell(w=epw, h=6, txt="[Texto no renderizable]", ln=True)

        pdf.output(filename)
        return True