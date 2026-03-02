import sqlite3

class InterventionManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def get_available_micros(self, patient_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, label FROM microcontingencies WHERE patient_id = ?", (patient_id,))
                return cursor.fetchall()
        except sqlite3.Error:
            return []

    def get_plan_by_micro(self, micro_id):
        """Obtiene el plan de intervención y la evaluación de desprofesionalización"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 1. Obtener el plan principal
                cursor.execute("SELECT * FROM intervention_plans WHERE microcontingency_id = ?", (micro_id,))
                plan_row = cursor.fetchone()
                
                if not plan_row:
                    return None
                    
                data = dict(plan_row)
                
                # 2. Obtener el análisis de desprofesionalización
                cursor.execute("SELECT * FROM deprofessionalization_analysis WHERE intervention_plan_id = ?", (data['id'],))
                data['deprofessionalization'] = [dict(r) for r in cursor.fetchall()]
                
                return data
        except sqlite3.Error: 
            return None

    def save_plan(self, patient_id, micro_id, plan_data, deprof_data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Buscar si ya existe el plan
                cursor.execute("SELECT id FROM intervention_plans WHERE microcontingency_id = ?", (micro_id,))
                row = cursor.fetchone()

                if row:
                    plan_id = row[0]
                    cursor.execute('''
                        UPDATE intervention_plans 
                        SET therapeutic_objectives=?, strategy_adquisition=?, strategy_precision=?, 
                            strategy_opportunity=?, strategy_tendency=?, strategy_effect=?, techniques_text=?
                        WHERE id=?
                    ''', (
                        plan_data['objs'], plan_data['adq'], plan_data['prec'], 
                        plan_data['opp'], plan_data['tend'], plan_data['eff'], plan_data['techs'], plan_id
                    ))
                    # Limpiar desprofesionalización vieja
                    cursor.execute("DELETE FROM deprofessionalization_analysis WHERE intervention_plan_id=?", (plan_id,))
                    msg = "Plan de intervención actualizado correctamente."
                else:
                    cursor.execute('''
                        INSERT INTO intervention_plans (
                            patient_id, microcontingency_id, therapeutic_objectives, 
                            strategy_adquisition, strategy_precision, strategy_opportunity, 
                            strategy_tendency, strategy_effect, techniques_text)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        patient_id, micro_id, plan_data['objs'], plan_data['adq'], plan_data['prec'], 
                        plan_data['opp'], plan_data['tend'], plan_data['eff'], plan_data['techs']
                    ))
                    plan_id = cursor.lastrowid
                    msg = "Plan de intervención creado correctamente."
                
                # Guardar el análisis de desprofesionalización (las opciones evaluadas por el paciente)
                for dep in deprof_data:
                    cursor.execute('''
                        INSERT INTO deprofessionalization_analysis 
                        (intervention_plan_id, solution_option, user_motivation, emotional_cost, available_resources, short_long_term_effects, is_selected)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        plan_id, dep['option'], dep['motivation'], dep['cost'], dep['resources'], dep['effects'], dep['selected']
                    ))

                conn.commit()
                return True, msg
        except sqlite3.Error as e: 
            return False, str(e)

    def get_all_techniques(self, category_filter=None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                if category_filter and category_filter != "Todas": 
                    c.execute("SELECT * FROM library_techniques WHERE category = ?", (category_filter,))
                else: 
                    c.execute("SELECT * FROM library_techniques")
                return [dict(r) for r in c.fetchall()]
        except: 
            return []