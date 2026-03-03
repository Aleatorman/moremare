import sqlite3
import os

DB_NAME = "database/clinical_app.db"

def create_connection():
    if not os.path.exists('database'):
        os.makedirs('database')
    try:
        conn = sqlite3.connect(DB_NAME)
        # Activar Foreign Keys para que funcione el CASCADE
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        print(f"Error conectando a BD: {e}")
        return None

def create_tables(conn):
    try:
        cursor = conn.cursor()

        # 1. SISTEMA
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT, security_question TEXT, security_answer_hash TEXT);''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS glossary (id INTEGER PRIMARY KEY AUTOINCREMENT, term TEXT UNIQUE, definition TEXT, source_page TEXT);''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS agenda_events (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, start_datetime TEXT, end_datetime TEXT, description TEXT, patient_id INTEGER);''')

        # 2. PACIENTES
        cursor.execute('''CREATE TABLE IF NOT EXISTS patients (id INTEGER PRIMARY KEY AUTOINCREMENT, code_name TEXT, age INTEGER, sex TEXT, occupation TEXT, motive TEXT, goals TEXT, status TEXT DEFAULT 'Activo', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);''')

        # 3. MICROCONTINGENCIAS
        cursor.execute('''CREATE TABLE IF NOT EXISTS microcontingencies (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER, label TEXT, FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE);''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS micro_morphologies (id INTEGER PRIMARY KEY AUTOINCREMENT, micro_id INTEGER, type TEXT, class TEXT, molar TEXT, molecular TEXT, description TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS micro_contexts_social (id INTEGER PRIMARY KEY AUTOINCREMENT, micro_id INTEGER, type TEXT, description TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS micro_contexts_physical (id INTEGER PRIMARY KEY AUTOINCREMENT, micro_id INTEGER, element TEXT, description TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS micro_interactions (id INTEGER PRIMARY KEY AUTOINCREMENT, micro_id INTEGER, expected TEXT, competence TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS micro_inclinations (id INTEGER PRIMARY KEY AUTOINCREMENT, micro_id INTEGER, category TEXT, description TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS micro_tendencies (id INTEGER PRIMARY KEY AUTOINCREMENT, micro_id INTEGER, category TEXT, description TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS micro_actors (id INTEGER PRIMARY KEY AUTOINCREMENT, micro_id INTEGER, name TEXT, role TEXT, response TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS micro_effects (id INTEGER PRIMARY KEY AUTOINCREMENT, micro_id INTEGER, type TEXT, description TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS micro_noproblem (id INTEGER PRIMARY KEY AUTOINCREMENT, micro_id INTEGER, situation TEXT, description TEXT)''')

        # 4. MACROCONTINGENCIAS
        cursor.execute('''CREATE TABLE IF NOT EXISTS macrocontingencies (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER, group_type TEXT, group_name TEXT, beliefs_values TEXT, customs_lifestyles TEXT, intra_analysis TEXT, inter_analysis TEXT, FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE);''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS macro_normative_functions (id INTEGER PRIMARY KEY AUTOINCREMENT, macro_id INTEGER, function_type TEXT, exercised_by TEXT, description TEXT);''')
        
        # ---> MATRIZ DE CORRESPONDENCIAS CON PUENTE MICROCONTINGENCIAL <---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS macro_correspondences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                macro_id INTEGER NOT NULL,
                micro_id INTEGER NOT NULL,
                axis_1 TEXT NOT NULL, 
                axis_2 TEXT NOT NULL, 
                has_correspondence BOOLEAN NOT NULL DEFAULT 1,
                FOREIGN KEY (macro_id) REFERENCES macrocontingencies (id) ON DELETE CASCADE,
                FOREIGN KEY (micro_id) REFERENCES microcontingencies (id) ON DELETE CASCADE
            );
        ''')

        # 5. GÉNESIS
        cursor.execute('''CREATE TABLE IF NOT EXISTS genesis_history (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id INTEGER, microcontingency_id INTEGER, origin_history TEXT, functional_history TEXT, FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE);''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genesis_interactive_styles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                genesis_id INTEGER NOT NULL,
                arrangement_type TEXT NOT NULL, 
                response_style TEXT,
                FOREIGN KEY (genesis_id) REFERENCES genesis_history (id) ON DELETE CASCADE
            );
        ''')

        # 6. INTERVENCIÓN
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS intervention_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                microcontingency_id INTEGER NOT NULL,
                therapeutic_objectives TEXT,
                sol_cambio_macro INTEGER DEFAULT 0,
                sol_mant_macro INTEGER DEFAULT 0,
                sol_mant_micro INTEGER DEFAULT 0,
                sol_cambio_otros INTEGER DEFAULT 0,
                sol_cambio_propia INTEGER DEFAULT 0,
                sol_nuevas_micro INTEGER DEFAULT 0,
                sol_opciones_func INTEGER DEFAULT 0,
                strategy_adquisition TEXT,
                strategy_precision TEXT,
                strategy_opportunity TEXT,
                strategy_tendency TEXT,
                strategy_effect TEXT,
                techniques_text TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE
            );
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deprofessionalization_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intervention_plan_id INTEGER NOT NULL,
                solution_option TEXT NOT NULL, 
                user_motivation TEXT,          
                emotional_cost TEXT,           
                available_resources TEXT,      
                short_long_term_effects TEXT,  
                is_selected BOOLEAN DEFAULT 0, 
                FOREIGN KEY (intervention_plan_id) REFERENCES intervention_plans (id) ON DELETE CASCADE
            );
        ''')

        # Se corrigió añadiendo UNIQUE al nombre de la técnica
        cursor.execute('''CREATE TABLE IF NOT EXISTS library_techniques (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, name TEXT UNIQUE, objective TEXT, method TEXT, pros TEXT, cons TEXT);''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS library_sources (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT);''')

        # 7. EVALUACIÓN 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                date_eval TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evaluation_matrix (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evaluation_id INTEGER NOT NULL,
                target TEXT, 
                parameter TEXT, 
                terapia_val TEXT,
                terapeuta_val TEXT,
                FOREIGN KEY (evaluation_id) REFERENCES evaluations (id) ON DELETE CASCADE
            );
        ''')

        conn.commit()
        print("--- Tablas creadas exitosamente ---")
    except sqlite3.Error as e: print(f"Error creando tablas: {e}")

def seed_library(conn):
    """Inserta automáticamente las 52 técnicas de tu lista cada vez que se crea la BD."""
    tecnicas = [
        ('Cognitivo-Conductual','Reestructuración Cognitiva','Identificar y cambiar patrones de pensamiento distorsionado','Identificar pensamientos automáticos, cuestionar con evidencia, buscar alternativas realistas.','Aborda la raíz, empodera al individuo.','Requiere capacidad metacognitiva, puede parecer forzada.'),
        ('Cognitivo-Conductual','Activación Conductual','Aumentar conductas que generan placer y logro.','Cronograma de actividades programadas independientemente del estado emocional.','Rompe el ciclo de la depresión.','Puede encontrar resistencia inicial por falta de motivación.'),
        ('Cognitivo-Conductual','Exposición y Prevención de Respuesta (ERP)','Reducir miedo y evitación.','Jerarquía de exposición a estímulos temidos evitando compulsiones.','Gold standard para TOC y fobias.','Altamente ansiógena inicialmente.'),
        ('Cognitivo-Conductual','Entrenamiento en Resolución de Problemas','Resolver problemas sistemáticamente.','Definir problema, metas, generar soluciones, elegir e implementar.','Transferible a contextos, reduce rumiación.','Lenta para crisis inmediatas.'),
        ('Cognitivo-Conductual','Autorregistro y Automonitoreo','Aumentar conciencia de patrones.','Registrar conductas, pensamientos y emociones en formatos estructurados.','Genera datos objetivos, promueve metacognición.','Puede ser tedioso, requiere consistencia.'),
        ('Cognitivo-Conductual','Entrenamiento de Habilidades Sociales','Desarrollar habilidades de interacción.','Psicoeducación, modelado, role-play de contacto visual, escucha, asertividad.','Mejora relaciones y reduce aislamiento.','Generalización no automática.'),
        ('Cognitivo-Conductual','Entrenamiento en Control de Ira','Reducir respuestas de ira desadaptativas.','Identificar triggers, señales físicas, técnicas de relajación y reformulación.','Previene agresión, mejora salud.','Puede no abordar causas profundas.'),
        ('ABA','Reforzamiento Positivo','Aumentar conductas deseadas.','Presentar estímulo reforzante inmediatamente después de la conducta.','Científicamente validado, robusto.','Dependencia de recompensas externas.'),
        ('ABA','Extinción Operante','Reducir conductas indeseadas.','Suprimir consistentemente la consecuencia que mantiene la conducta.','Efectivo a largo plazo, no es castigo.','Explosión de extinción inicial.'),
        ('ABA','Reforzamiento Diferencial','Aumentar deseadas/Reducir indeseadas.','Reforzar conductas alternativas (DRA) o incompatibles mientras se extinguen otras.','Menos adverso que el castigo.','Requiere identificación precisa de conductas.'),
        ('ABA','Moldeamiento (Shaping)','Enseñar conductas complejas nuevas.','Reforzar aproximaciones sucesivas hacia la conducta meta.','Permite enseñar conductas desde cero.','Lento, requiere mucha observación.'),
        ('ABA','Encadenamiento','Enseñar secuencias de conducta.','Desglosar en pasos (eslabones) y enseñar secuencialmente.','Útil para autonomía en vida diaria.','Tedioso, errores requieren retroceso.'),
        ('ABA','Desvanecimiento de Estímulos','Transferir control a estímulos naturales.','Reducir gradualmente la ayuda o prompt inicial.','Promueve independencia.','Requiere precisión en el timing.'),
        ('ABA','Tiempo Fuera','Reducir conducta problemática.','Remoción breve del ambiente reforzante.','Rápido, no físico.','Requiere que el ambiente normal sea rico en refuerzos.'),
        ('ABA','Costo de Respuesta','Reducir conducta mediante penalización.','Retirar un reforzador ganado previamente (fichas, tiempo).','Claro vínculo conducta-consecuencia.','Genera frustración.'),
        ('Contextual/ACT','Desusión Cognitiva','Ver pensamientos como eventos mentales.','Metáforas (nubes), repetición de palabras, etiquetar "tengo el pensamiento".','Reduce poder emocional de pensamientos.','Puede parecer extraña al inicio.'),
        ('Contextual/ACT','Clarificación de Valores','Identificar dirección vital.','Reflexión, ejercicios (funeral), distinguir valores de metas.','Proporciona motivación profunda.','Puede generar angustia al ver discrepancias.'),
        ('Contextual/ACT','Acción Comprometida','Actuar según valores.','Metas SMART alineadas a valores a pesar de barreras internas.','Genera movimiento y resiliencia.','Dificultad ante barreras emocionales.'),
        ('Contextual/ACT','Decentering y Perspectiva de Observador','Observar experiencias sin identificarse.','Meditación, observar fenómenos como testigo.','Reduce identificación con lo negativo.','Requiere práctica extendida.'),
        ('Contextual/ACT','Aceptación Radical','Tolerar experiencias sin evitación.','Permitir experiencias desagradables sin intentar cambiarlas.','Ahorra energía, rompe ciclos de lucha.','Contraintuitiva, puede confundirse con resignación.'),
        ('Regulación Emocional','Habilidades TIPP','Regular crisis fisiológica.','Temperatura (hielo), Ejercicio intenso, Respiración pautada, Relajación.','Rápidamente efectiva en crisis.','Efectos temporales.'),
        ('Regulación Emocional','Habilidades ACCEPTS','Distracción de angustia inmediata.','Actividades, Contribución, Comparaciones, Emociones opuestas.','Interrumpe rumiación en crisis.','Es una estrategia temporal, no resuelve.'),
        ('Regulación Emocional','Auto-Calma (Self-Soothing)','Calmar sistema nervioso.','Estimulación deliberada de los 5 sentidos (vista, oído, tacto...).','Accesible y placentera.','Puede generar habituación.'),
        ('Regulación Emocional','IMPROVE the Moment','Mejorar tolerancia al momento.','Imaginería, Significado, Oración, Relajación, Una cosa a la vez.','Flexible, refuerza resiliencia.','Requiere creatividad cognitiva.'),
        ('Exposición','Desensibilización Sistemática','Reducir ansiedad a estímulos.','Relajación profunda + exposición imaginal gradual en jerarquía.','Menos traumática que en vivo.','Lenta, requiere entrenamiento en relajación.'),
        ('Exposición','Exposición Gradual en Vivo','Reducir miedo por habituación.','Exposición real escalonada sin escape.','Aprendizaje conductual fuerte.','Altamente ansiógena inicialmente.'),
        ('Exposición','Exposición Imaginal','Procesar trauma.','Relatar memoria traumática en detalle repetidamente.','Efectiva para TEPT.','Muy angustiante, requiere cuidado.'),
        ('Habilidades','Entrenamiento de Habilidades Conductuales (BST)','Adquirir habilidades complejas.','Instrucción, Modelado, Ensayo, Retroalimentación.','Altamente efectiva, componentes múltiples.','Intensiva en tiempo.'),
        ('Habilidades','Modelado Conductual','Enseñar por imitación.','Demostración clara de la conducta deseada.','Aprendizaje vicario rápido.','Requiere un buen modelo.'),
        ('Habilidades','Ensayo de Rol (Role-Play)','Practicar en ambiente seguro.','Actuar situaciones desafiantes con terapeuta.','Feedback inmediato sin riesgos.','Puede dar vergüenza.'),
        ('Mindfulness','Entrenamiento de Atención (ATT)','Control atencional voluntario.','Escuchar sonidos selectivos y cambiar foco.','Reduce rumiación y ansiedad.','Tedioso, requiere consistencia.'),
        ('Mindfulness','Mindfulness/Meditación','Conciencia presente no juzgadora.','Atención a la respiración, retorno suave tras distracción.','Neuroplasticidad, regulación emocional.','Requiere práctica prolongada.'),
        ('Mindfulness','Body Scan','Conexión mente-cuerpo.','Recorrido atencional por sensaciones corporales.','Reconocimiento emocional somático.','Lento, puede activar traumas.'),
        ('Mindfulness','Respiración Diafragmática','Activar sistema parasimpático.','Respiración lenta controlada con el vientre.','Reduce activación fisiológica.','Insuficiente en crisis de pánico severo.'),
        ('Auto-Manejo','Autorregistro (Self-Monitoring)','Conciencia de patrones.','Registro sistemático propio de conductas/emociones.','Efecto reactivo positivo.','Requiere disciplina.'),
        ('Auto-Manejo','Establecimiento de Metas','Definir progreso.','Metas SMART colaborativas.','Claridad y motivación.','Riesgo de frustración si son irreales.'),
        ('Auto-Manejo','Autorrefuerzo','Auto-motivación.','Administrarse premios tras cumplir metas.','Empodera agencia.','Posible "trampa".'),
        ('Auto-Manejo','Contratos de Contingencia','Acuerdo explícito.','Contrato escrito de conducta-consecuencia.','Claridad de expectativas.','Puede sentirse rígido o coercitivo.'),
        ('Estímulos','Análisis ABC','Identificar relaciones funcionales.','Analizar Antecedente-Conducta-Consecuencia.','Base de intervención.','Puede ser complejo.'),
        ('Estímulos','Análisis Funcional','Comprender el propósito de la conducta.','Identificar función (atención, escape, tangible, sensorial).','Crucial para eficacia.','Requiere entrenamiento experto.'),
        ('Estímulos','Mapeo de Contingencia','Organizar visualmente relaciones.','Diagramas visuales de desencadenantes y consecuencias.','Útil para procesamiento visual.','Puede simplificar demasiado.'),
        ('Estímulos','Control de Estímulos','Modificar ambiente.','Alterar entorno para facilitar/prevenir conductas.','Preventivo, bajo costo.','No siempre es posible modificar el entorno.'),
        ('Motivación','Entrevista Motivacional','Resolver ambivalencia.','Preguntas abiertas, escucha, evocar charla de cambio.','Aumenta motivación intrínseca.','Requiere habilidades específicas.'),
        ('Motivación','Apoyo a la Autonomía','Fomentar elección.','Ofrecer opciones y justificaciones.','Mejora adherencia y satisfacción.','Puede parecer permisivo.'),
        ('Motivación','Teoría de la Autodeterminación','Satisfacer necesidades básicas.','Promover autonomía, competencia y relación.','Cambio sostenible.','Requiere visión sistémica.'),
        ('Mantenimiento','Desvanecimiento del Refuerzo','Reducir dependencia.','Pasar a refuerzo intermitente gradualmente.','Resistencia a extinción.','Riesgo si es muy rápido.'),
        ('Mantenimiento','Generalización de Conducta','Transferir a vida real.','Entrenar en múltiples contextos con variaciones.','Asegura utilidad real.','Requiere planificación costosa.'),
        ('Mantenimiento','Planeamiento de Mantenimiento','Prevenir recaídas.','Identificar riesgos futuros y planes de acción.','Empodera post-terapia.','El paciente puede olvidar el plan.'),
        ('Mantenimiento','ABC Renewal Prevention','Prevenir resurgimiento por contexto.','Entrenar y reforzar en contextos originales.','Científicamente robusto.','Complejo de implementar.'),
        ('Compasión','Auto-Compasión','Amabilidad ante la dificultad.','Tratarse con calidez en lugar de crítica.','Mejora resiliencia, reduce vergüenza.','Puede confundirse con auto-indulgencia.'),
        ('Compasión','Meditación de Bondad Amorosa','Generar afecto positivo.','Frases de deseo de bienestar a uno mismo y otros.','Aumenta conexión social.','Puede parecer artificial.'),
        ('Compasión','Terapia Enfocada en Compasión','Regular sistemas emocionales.','Activar sistema de calma y seguridad.','Efectiva para vergüenza y trauma.','Puede ser intensa emocionalmente.')
    ]
    cursor = conn.cursor()
    try:
        cursor.executemany('''
            INSERT OR IGNORE INTO library_techniques 
            (category, name, objective, method, pros, cons) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', tecnicas)
        conn.commit()
        print(f"--- {len(tecnicas)} técnicas sembradas en la biblioteca ---")
    except sqlite3.Error as e: print(f"Error sembrando biblioteca: {e}")

def main():
    conn = create_connection()
    if conn:
        create_tables(conn)
        seed_library(conn)
        conn.close()

if __name__ == '__main__':
    main()