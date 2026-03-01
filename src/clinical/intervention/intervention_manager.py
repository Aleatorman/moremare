import sqlite3

class InterventionManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path
        # Al iniciar, verificamos y llenamos la biblioteca
        self._check_and_populate_library()

    # ==========================================
    # LÓGICA DEL PLAN DE INTERVENCIÓN
    # ==========================================

    def get_plan_by_micro(self, micro_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM intervention_plans WHERE microcontingency_id = ?", (micro_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error:
            return None

    def save_plan(self, patient_id, micro_id, data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM intervention_plans WHERE microcontingency_id = ?", (micro_id,))
                row = cursor.fetchone()

                if row:
                    cursor.execute('''
                        UPDATE intervention_plans 
                        SET goal_description=?, strategy_morphology=?, strategy_actors=?, strategy_context=?, techniques_text=?
                        WHERE id=?
                    ''', (data['goal'], data['morph'], data['actors'], data['context'], data['techs'], row[0]))
                    msg = "Plan actualizado."
                else:
                    cursor.execute('''
                        INSERT INTO intervention_plans (patient_id, microcontingency_id, goal_description, strategy_morphology, strategy_actors, strategy_context, techniques_text)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (patient_id, micro_id, data['goal'], data['morph'], data['actors'], data['context'], data['techs']))
                    msg = "Plan creado."
                
                conn.commit()
                return True, msg
        except sqlite3.Error as e:
            return False, str(e)

    # ==========================================
    # LÓGICA DE LA BIBLIOTECA
    # ==========================================

    def get_all_techniques(self, category_filter=None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if category_filter and category_filter != "Todas":
                    cursor.execute("SELECT * FROM library_techniques WHERE category = ?", (category_filter,))
                else:
                    cursor.execute("SELECT * FROM library_techniques")
                return [dict(r) for r in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def add_technique(self, data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO library_techniques (category, name, objective, method, pros, cons)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (data['cat'], data['name'], data['obj'], data['method'], data['pros'], data['cons']))
                conn.commit()
                return True, "Técnica agregada."
        except sqlite3.Error as e:
            return False, str(e)

    def get_sources(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT url FROM library_sources")
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    # ==========================================
    # CARGA MASIVA DE DATOS (52 TÉCNICAS + 150+ URLs)
    # ==========================================
    def _check_and_populate_library(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificamos si necesitamos recargar (Si hay menos de 100 fuentes, asumimos que es la versión vieja)
                cursor.execute("SELECT count(*) FROM library_sources")
                source_count = cursor.fetchone()[0]
                
                if source_count < 100: 
                    print("Actualizando Biblioteca con listado extendido...")
                    # Limpiamos tablas de biblioteca para evitar duplicados
                    cursor.execute("DELETE FROM library_techniques")
                    cursor.execute("DELETE FROM library_sources")
                    # Reiniciamos los autoincrementales
                    cursor.execute("DELETE FROM sqlite_sequence WHERE name='library_techniques'")
                    cursor.execute("DELETE FROM sqlite_sequence WHERE name='library_sources'")
                    
                    self._insert_full_data(cursor)
                    conn.commit()
                    print("Biblioteca actualizada: 52 técnicas y listado completo de fuentes.")
        except Exception as e:
            print(f"Error poblando biblioteca: {e}")

    def _insert_full_data(self, cursor):
        # 1. LISTADO COMPLETO DE FUENTES (Extraído del archivo 'fuentes-completas-urls')
        urls = [
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC10440210/",
            "https://dialecticalbehaviortherapy.com/cbt/cognitive-restructuring/",
            "https://www.science.org/doi/10.1126/sciadv.adk3222",
            "https://journal.staihubbulwathan.id/index.php/alishlah/article/view/7085",
            "https://e-journals.unmul.ac.id/index.php/psikoneo/article/view/13125",
            "https://www.ncbi.nlm.nih.gov/books/NBK279297/",
            "https://www.apa.org/ptsd-guideline/patients-and-families/cognitive-behavioral",
            "https://www.nature.com/articles/s41591-025-03639-1",
            "https://mental.jmir.org/2024/1/e56691",
            "https://pdm.pensoft.net/article/34286/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC3584580/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC4992341/",
            "https://seattleanxiety.com/exposure-and-response-prevention-erp",
            "https://beyondthestormkc.com/erp-therapy-comprehensive-clinical-report/",
            "https://tapclinicnc.com/home/how-we-treat/exposure-response-prevention-erp/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC11176611/",
            "https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2024.1331155/pdf",
            "https://doi.apa.org/doi/10.1037/cps0000131",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC11332086/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC9728040/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC9642026/",
            "https://apsijournal.com/index.php/psyjournal/article/view/1664",
            "https://www.gratefulcareaba.com/blog/the-role-of-self-monitoring-techniques-in-aba-therapy",
            "https://www.sciencedirect.com/topics/psychology/self-monitoring",
            "http://openaccesspub.org/article/386/pdf",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC5007662/",
            "https://www.psychologytools.com/professional/techniques/self-monitoring",
            "https://www.interventioncentral.org/self_management_self_monitoring",
            "https://howtoaba.com/implement-self-monitoring-system/",
            "https://www.scirp.org/journal/paperinformation?paperid=72442",
            "https://happyshypeople.com/p/social-skills-training-for-adults",
            "https://www.cci.health.wa.gov.au/~/media/CCI/Mental-Health-Professionals/Therapist-Manuals/Social-Skills-Training/Social-Skills-Training---Therapist-Manual.pdf",
            "https://www.verywellmind.com/social-skills-4157216",
            "https://www.mdpi.com/2076-328X/14/1/46",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC10243415/",
            "https://onlinelibrary.wiley.com/doi/10.1002/cpp.1956",
            "https://www.simplypsychology.org/operant-conditioning.html",
            "https://www.tanagerplace.org/operant-conditioning-aba-an-introduction-to-autism-awareness-month/",
            "https://www.ebsco.com/research-starters/health-and-medicine/operant-conditioning-therapies",
            "http://link.springer.com/10.1007/s40617-016-0117-0",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC9163266/",
            "https://www.stepaheadaba.com/blog/understanding-reinforcement-strategies-in-aba-therapy",
            "https://eagleswill.com/what-is-operant-extinction-in-aba/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC10524675/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC10204583/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC1284010/",
            "https://howtoaba.com/extinction/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC2861874/",
            "https://www.magnetaba.com/blog/what-is-differential-reinforcement-and-how-is-it-used",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC11608818/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC5048277/",
            "https://www.handscenter.com/understanding-shaping-and-chaining-in-aba-therapy",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC10050503/",
            "https://howtoaba.com/shaping-behavior/",
            "https://link.springer.com/10.1007/978-1-4419-8065-6_23",
            "https://www.semanticscholar.org/paper/296a4d0fe77def1de0fef02b95376dfc1d3ada18",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC4383256/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC1702338/",
            "https://www.sciencedirect.com/topics/psychology/stimulus-fading",
            "https://rainbowtherapy.org/aba-prompt-fading/",
            "https://masteraba.academy/post/behavioral-skills-training-bst-step-by-step-guide",
            "https://www.youtube.com/watch?v=sdbP7AKLJF8",
            "https://paloaltou.edu/resources/business-of-practice-blog/behavior-you-dont-like",
            "https://www.besteveraba.com/blog/response-cost-in-aba-therapy",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC1224409/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC7720655/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC11957246/",
            "https://alz-journals.onlinelibrary.wiley.com/doi/10.1002/alz.088248",
            "https://washingtoncenterforcognitivetherapy.com/cognitive-defusion/",
            "https://cogbtherapy.com/cbt-blog/cognitive-defusion-techniques-and-exercises",
            "https://www.sciencedirect.com/science/article/abs/pii/S1750946718301880",
            "https://www.therapistaid.com/therapy-worksheet/thought-defusion-techniques",
            "https://www.mdpi.com/2076-3425/12/9/1215/pdf",
            "https://bayareacbtcenter.com/values-domains-and-values-based-actions-in-act-therapy/",
            "https://psychotherapyacademy.org/act-worksheets-for-values-clarification-the-magic-wand/",
            "https://positivepsychology.com/values-clarification/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC3635495/",
            "https://contextualscience.org/publications/acceptance_commitment_therapy_functional_contextualism_clinical_social_work",
            "https://thehappinesstrap.com/upimages/the_house_of_ACT.pdf",
            "https://quenza.com/blog/act-therapy-exercises/",
            "https://rainbowtherapy.org/acceptance-and-commitment-therapy-act/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC5103165/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC6706318/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC7459352/",
            "https://arxiv.org/pdf/2409.15289.pdf",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC5021701/",
            "https://www.frontiersin.org/articles/10.3389/fpsyg.2016.01373/pdf",
            "https://mindfulnessdbt.com/techniques-for-distress-tolerance-in-dbt/",
            "https://centerforcbt.org/2023/04/26/dbt-tipp-skills/",
            "https://www.frontiersin.org/articles/10.3389/fpsyg.2020.611156/pdf",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC7772151/",
            "https://www.lilaccenter.org/blog/2025/11/26/understanding-the-four-dbt-skills-mindfulness-distress-tolerance-emotion-regulation-interpersonal-effectiveness",
            "https://mindfulnessdbt.com/applying-dbt-self-soothing-techniques/",
            "https://elizablooms.com/2024/01/24/what-is-dbt-distress-tolerance-skills-guide/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC3215612/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC6884337/",
            "https://www.sunshinecarenetwork.com/blog/addressing-anxiety-with-aba-therapy-techniques",
            "https://www.sciencedirect.com/topics/psychology/behavioral-modeling",
            "https://educationoftheheartdialogue.org/mindfulness-and-training-of-attention-awareness/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC11127867/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC7307795/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC12460839/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC5292405/",
            "https://www.youtube.com/watch?v=OB5X8wZLpas",
            "https://www.sleepfoundation.org/sleep-hygiene/relaxation-exercises-to-help-fall-asleep",
            "https://www.ncbi.nlm.nih.gov/books/NBK513238/",
            "https://www.sleepandtmjcenter.com/breathing-techniques-for-better-sleep",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC4564346/",
            "https://academic.oup.com/abm/article/doi/10.1093/abm/kaaf088/8323187",
            "https://kyocare.com/classroom-series-using-a-contingency-contract-to-support-positive-student-behavior/",
            "https://abastudyguide.com/what-is-contingency-contracting-and-how-can-it-boost-behavior-change/",
            "https://www.youtube.com/watch?v=MwuIuIovGrE",
            "https://sweetinstitute.com/the-role-of-contingency-management-contracts-in-behavioral-therapy/",
            "https://www.soaringhighaba.com/post/the-role-of-contingency-plans-in-aba-therapy",
            "https://www.psychologytools.com/professional/techniques/functional-analysis",
            "https://linksaba.com/applied-behavior-analysis-101/",
            "https://behaviorprep.com/glossary/contingency-analysis/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC1284458/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC2591753/",
            "https://www.jennifervonk.com/uploads/7/7/3/2/7732985/herrnstein_1990.pdf",
            "https://faculty.fiu.edu/~pelaeznm/wp-content/uploads/2016/10/31.-The-context-of-stimulus-control-in-behavior-analysis.pdf",
            "https://selfdeterminationtheory.org/SDT/documents/2005_MarklandRyanTobinRollnick_MotivationalInterviewing.pdf",
            "https://www.child-focus.org/news/what-is-motivational-interviewing-and-how-can-it-empower-change-in-people/",
            "https://www.sciencedirect.com/science/article/abs/pii/S0167876015300258",
            "https://www.mdpi.com/2076-328X/16/1/24",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC1389770/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC11295203/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC11403187/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC5538309/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC5982936/",
            "https://self-compassion.org/wp-content/uploads/2019/08/Haukaas2018.pdf",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC5021701/",
            "https://www.ncbi.nlm.nih.gov/books/",
            "https://www.apa.org/",
            "https://www.psychologytools.com/",
            "https://www.frontiersin.org/",
            "https://www.nature.com/",
            "https://www.science.org/",
            "https://www.jmir.org/",
            "https://www.mdpi.com/",
            "https://www.sciencedirect.com/",
            "https://link.springer.com/",
            "https://onlinelibrary.wiley.com/"
        ]

        # 2. TÉCNICAS (52 TÉCNICAS con descripciones completas)
        techs = [
            ("Cognitivo-Conductual", "Reestructuración Cognitiva", "Identificar y cambiar patrones de pensamiento distorsionado.", "Identificar pensamientos automáticos, cuestionar con evidencia, buscar alternativas realistas.", "Aborda la raíz, empodera al individuo.", "Requiere capacidad metacognitiva, puede parecer forzada."),
            ("Cognitivo-Conductual", "Activación Conductual", "Aumentar conductas que generan placer y logro.", "Cronograma de actividades programadas independientemente del estado emocional.", "Rompe el ciclo de la depresión.", "Puede encontrar resistencia inicial por falta de motivación."),
            ("Cognitivo-Conductual", "Exposición y Prevención de Respuesta (ERP)", "Reducir miedo y evitación.", "Jerarquía de exposición a estímulos temidos evitando compulsiones.", "Gold standard para TOC y fobias.", "Altamente ansiógena inicialmente."),
            ("Cognitivo-Conductual", "Entrenamiento en Resolución de Problemas", "Resolver problemas sistemáticamente.", "Definir problema, metas, generar soluciones, elegir e implementar.", "Transferible a contextos, reduce rumiación.", "Lenta para crisis inmediatas."),
            ("Cognitivo-Conductual", "Autorregistro y Automonitoreo", "Aumentar conciencia de patrones.", "Registrar conductas, pensamientos y emociones en formatos estructurados.", "Genera datos objetivos, promueve metacognición.", "Puede ser tedioso, requiere consistencia."),
            ("Cognitivo-Conductual", "Entrenamiento de Habilidades Sociales", "Desarrollar habilidades de interacción.", "Psicoeducación, modelado, role-play de contacto visual, escucha, asertividad.", "Mejora relaciones y reduce aislamiento.", "Generalización no automática."),
            ("Cognitivo-Conductual", "Entrenamiento en Control de Ira", "Reducir respuestas de ira desadaptativas.", "Identificar triggers, señales físicas, técnicas de relajación y reformulación.", "Previene agresión, mejora salud.", "Puede no abordar causas profundas."),
            ("ABA", "Reforzamiento Positivo", "Aumentar conductas deseadas.", "Presentar estímulo reforzante inmediatamente después de la conducta.", "Científicamente validado, robusto.", "Dependencia de recompensas externas."),
            ("ABA", "Extinción Operante", "Reducir conductas indeseadas.", "Suprimir consistentemente la consecuencia que mantiene la conducta.", "Efectivo a largo plazo, no es castigo.", "Explosión de extinción inicial."),
            ("ABA", "Reforzamiento Diferencial", "Aumentar deseadas/Reducir indeseadas.", "Reforzar conductas alternativas (DRA) o incompatibles mientras se extinguen otras.", "Menos adverso que el castigo.", "Requiere identificación precisa de conductas."),
            ("ABA", "Moldeamiento (Shaping)", "Enseñar conductas complejas nuevas.", "Reforzar aproximaciones sucesivas hacia la conducta meta.", "Permite enseñar conductas desde cero.", "Lento, requiere mucha observación."),
            ("ABA", "Encadenamiento", "Enseñar secuencias de conducta.", "Desglosar en pasos (eslabones) y enseñar secuencialmente.", "Útil para autonomía en vida diaria.", "Tedioso, errores requieren retroceso."),
            ("ABA", "Desvanecimiento de Estímulos", "Transferir control a estímulos naturales.", "Reducir gradualmente la ayuda o prompt inicial.", "Promueve independencia.", "Requiere precisión en el timing."),
            ("ABA", "Tiempo Fuera", "Reducir conducta problemática.", "Remoción breve del ambiente reforzante.", "Rápido, no físico.", "Requiere que el ambiente normal sea rico en refuerzos."),
            ("ABA", "Costo de Respuesta", "Reducir conducta mediante penalización.", "Retirar un reforzador ganado previamente (fichas, tiempo).", "Claro vínculo conducta-consecuencia.", "Genera frustración."),
            ("Contextual/ACT", "Desusión Cognitiva", "Ver pensamientos como eventos mentales.", "Metáforas (nubes), repetición de palabras, etiquetar 'tengo el pensamiento'.", "Reduce poder emocional de pensamientos.", "Puede parecer extraña al inicio."),
            ("Contextual/ACT", "Clarificación de Valores", "Identificar dirección vital.", "Reflexión, ejercicios (funeral), distinguir valores de metas.", "Proporciona motivación profunda.", "Puede generar angustia al ver discrepancias."),
            ("Contextual/ACT", "Acción Comprometida", "Actuar según valores.", "Metas SMART alineadas a valores a pesar de barreras internas.", "Genera movimiento y resiliencia.", "Dificultad ante barreras emocionales."),
            ("Contextual/ACT", "Decentering y Perspectiva de Observador", "Observar experiencias sin identificarse.", "Meditación, observar fenómenos como testigo.", "Reduce identificación con lo negativo.", "Requiere práctica extendida."),
            ("Contextual/ACT", "Aceptación Radical", "Tolerar experiencias sin evitación.", "Permitir experiencias desagradables sin intentar cambiarlas.", "Ahorra energía, rompe ciclos de lucha.", "Contraintuitiva, puede confundirse con resignación."),
            ("Regulación Emocional", "Habilidades TIPP", "Regular crisis fisiológica.", "Temperatura (hielo), Ejercicio intenso, Respiración pautada, Relajación.", "Rápidamente efectiva en crisis.", "Efectos temporales."),
            ("Regulación Emocional", "Habilidades ACCEPTS", "Distracción de angustia inmediata.", "Actividades, Contribución, Comparaciones, Emociones opuestas.", "Interrumpe rumiación en crisis.", "Es una estrategia temporal, no resuelve."),
            ("Regulación Emocional", "Auto-Calma (Self-Soothing)", "Calmar sistema nervioso.", "Estimulación deliberada de los 5 sentidos (vista, oído, tacto...).", "Accesible y placentera.", "Puede generar habituación."),
            ("Regulación Emocional", "IMPROVE the Moment", "Mejorar tolerancia al momento.", "Imaginería, Significado, Oración, Relajación, Una cosa a la vez.", "Flexible, refuerza resiliencia.", "Requiere creatividad cognitiva."),
            ("Exposición", "Desensibilización Sistemática", "Reducir ansiedad a estímulos.", "Relajación profunda + exposición imaginal gradual en jerarquía.", "Menos traumática que en vivo.", "Lenta, requiere entrenamiento en relajación."),
            ("Exposición", "Exposición Gradual en Vivo", "Reducir miedo por habituación.", "Exposición real escalonada sin escape.", "Aprendizaje conductual fuerte.", "Altamente ansiógena inicialmente."),
            ("Exposición", "Exposición Imaginal", "Procesar trauma.", "Relatar memoria traumática en detalle repetidamente.", "Efectiva para TEPT.", "Muy angustiante, requiere cuidado."),
            ("Habilidades", "Entrenamiento de Habilidades Conductuales (BST)", "Adquirir habilidades complejas.", "Instrucción, Modelado, Ensayo, Retroalimentación.", "Altamente efectiva, componentes múltiples.", "Intensiva en tiempo."),
            ("Habilidades", "Modelado Conductual", "Enseñar por imitación.", "Demostración clara de la conducta deseada.", "Aprendizaje vicario rápido.", "Requiere un buen modelo."),
            ("Habilidades", "Ensayo de Rol (Role-Play)", "Practicar en ambiente seguro.", "Actuar situaciones desafiantes con terapeuta.", "Feedback inmediato sin riesgos.", "Puede dar vergüenza."),
            ("Mindfulness", "Entrenamiento de Atención (ATT)", "Control atencional voluntario.", "Escuchar sonidos selectivos y cambiar foco.", "Reduce rumiación y ansiedad.", "Tedioso, requiere consistencia."),
            ("Mindfulness", "Mindfulness/Meditación", "Conciencia presente no juzgadora.", "Atención a la respiración, retorno suave tras distracción.", "Neuroplasticidad, regulación emocional.", "Requiere práctica prolongada."),
            ("Mindfulness", "Body Scan", "Conexión mente-cuerpo.", "Recorrido atencional por sensaciones corporales.", "Reconocimiento emocional somático.", "Lento, puede activar traumas."),
            ("Mindfulness", "Respiración Diafragmática", "Activar sistema parasimpático.", "Respiración lenta controlada con el vientre.", "Reduce activación fisiológica.", "Insuficiente en crisis de pánico severo."),
            ("Auto-Manejo", "Autorregistro (Self-Monitoring)", "Conciencia de patrones.", "Registro sistemático propio de conductas/emociones.", "Efecto reactivo positivo.", "Requiere disciplina."),
            ("Auto-Manejo", "Establecimiento de Metas", "Definir progreso.", "Metas SMART colaborativas.", "Claridad y motivación.", "Riesgo de frustración si son irreales."),
            ("Auto-Manejo", "Autorrefuerzo", "Auto-motivación.", "Administrarse premios tras cumplir metas.", "Empodera agencia.", "Posible 'trampa'."),
            ("Auto-Manejo", "Contratos de Contingencia", "Acuerdo explícito.", "Contrato escrito de conducta-consecuencia.", "Claridad de expectativas.", "Puede sentirse rígido o coercitivo."),
            ("Estímulos", "Análisis ABC", "Identificar relaciones funcionales.", "Analizar Antecedente-Conducta-Consecuencia.", "Base de intervención.", "Puede ser complejo."),
            ("Estímulos", "Análisis Funcional", "Comprender el propósito de la conducta.", "Identificar función (atención, escape, tangible, sensorial).", "Crucial para eficacia.", "Requiere entrenamiento experto."),
            ("Estímulos", "Mapeo de Contingencia", "Organizar visualmente relaciones.", "Diagramas visuales de desencadenantes y consecuencias.", "Útil para procesamiento visual.", "Puede simplificar demasiado."),
            ("Estímulos", "Control de Estímulos", "Modificar ambiente.", "Alterar entorno para facilitar/prevenir conductas.", "Preventivo, bajo costo.", "No siempre es posible modificar el entorno."),
            ("Motivación", "Entrevista Motivacional", "Resolver ambivalencia.", "Preguntas abiertas, escucha, evocar charla de cambio.", "Aumenta motivación intrínseca.", "Requiere habilidades específicas."),
            ("Motivación", "Apoyo a la Autonomía", "Fomentar elección.", "Ofrecer opciones y justificaciones.", "Mejora adherencia y satisfacción.", "Puede parecer permisivo."),
            ("Motivación", "Teoría de la Autodeterminación", "Satisfacer necesidades básicas.", "Promover autonomía, competencia y relación.", "Cambio sostenible.", "Requiere visión sistémica."),
            ("Mantenimiento", "Desvanecimiento del Refuerzo", "Reducir dependencia.", "Pasar a refuerzo intermitente gradualmente.", "Resistencia a extinción.", "Riesgo si es muy rápido."),
            ("Mantenimiento", "Generalización de Conducta", "Transferir a vida real.", "Entrenar en múltiples contextos con variaciones.", "Asegura utilidad real.", "Requiere planificación costosa."),
            ("Mantenimiento", "Planeamiento de Mantenimiento", "Prevenir recaídas.", "Identificar riesgos futuros y planes de acción.", "Empodera post-terapia.", "El paciente puede olvidar el plan."),
            ("Mantenimiento", "ABC Renewal Prevention", "Prevenir resurgimiento por contexto.", "Entrenar y reforzar en contextos originales.", "Científicamente robusto.", "Complejo de implementar."),
            ("Compasión", "Auto-Compasión", "Amabilidad ante la dificultad.", "Tratarse con calidez en lugar de crítica.", "Mejora resiliencia, reduce vergüenza.", "Puede confundirse con auto-indulgencia."),
            ("Compasión", "Meditación de Bondad Amorosa", "Generar afecto positivo.", "Frases de deseo de bienestar a uno mismo y otros.", "Aumenta conexión social.", "Puede parecer artificial."),
            ("Compasión", "Terapia Enfocada en Compasión", "Regular sistemas emocionales.", "Activar sistema de calma y seguridad.", "Efectiva para vergüenza y trauma.", "Puede ser intensa emocionalmente.")
        ]

        for t in techs:
            cursor.execute("INSERT INTO library_techniques (category, name, objective, method, pros, cons) VALUES (?, ?, ?, ?, ?, ?)", t)
        
        for u in urls:
            cursor.execute("INSERT INTO library_sources (url) VALUES (?)", (u,))