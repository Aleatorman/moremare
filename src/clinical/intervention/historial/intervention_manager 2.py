import sqlite3

class InterventionManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def get_plan_by_micro(self, micro_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM intervention_plans WHERE microcontingency_id = ?", (micro_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error: return None

    def save_plan(self, patient_id, micro_id, data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM intervention_plans WHERE microcontingency_id = ?", (micro_id,))
                row = cursor.fetchone()

                if row:
                    cursor.execute('''
                        UPDATE intervention_plans 
                        SET therapeutic_objectives=?, sol_cambio_macro=?, sol_mant_macro=?, sol_mant_micro=?, 
                            sol_cambio_otros=?, sol_cambio_propia=?, sol_nuevas_micro=?, sol_opciones_func=?,
                            strategy_morphology=?, strategy_actors=?, strategy_context=?, techniques_text=?
                        WHERE id=?
                    ''', (
                        data['objs'], data['s1'], data['s2'], data['s3'], data['s4'], data['s5'], data['s6'], data['s7'],
                        data['morph'], data['actors'], data['context'], data['techs'], row[0]
                    ))
                    msg = "Plan actualizado."
                else:
                    cursor.execute('''
                        INSERT INTO intervention_plans (
                            patient_id, microcontingency_id, therapeutic_objectives, 
                            sol_cambio_macro, sol_mant_macro, sol_mant_micro, sol_cambio_otros, sol_cambio_propia, sol_nuevas_micro, sol_opciones_func,
                            strategy_morphology, strategy_actors, strategy_context, techniques_text)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        patient_id, micro_id, data['objs'], data['s1'], data['s2'], data['s3'], data['s4'], data['s5'], data['s6'], data['s7'],
                        data['morph'], data['actors'], data['context'], data['techs']
                    ))
                    msg = "Plan creado."
                
                conn.commit()
                return True, msg
        except sqlite3.Error as e: return False, str(e)

    # Funciones de biblioteca (sin cambios, resumidas)
    def get_all_techniques(self, category_filter=None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                if category_filter and category_filter != "Todas": c.execute("SELECT * FROM library_techniques WHERE category = ?", (category_filter,))
                else: c.execute("SELECT * FROM library_techniques")
                return [dict(r) for r in c.fetchall()]
        except: return []