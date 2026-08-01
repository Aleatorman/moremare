import sqlite3
import csv
import os

class InterventionManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path
        self._upgrade_db() # Actualizador automático de la Base de Datos

    def _upgrade_db(self):
        """Agrega la columna rubro_funcional si no existe, sin borrar datos."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute("ALTER TABLE library_techniques ADD COLUMN rubro_funcional TEXT DEFAULT 'Sin asignar'")
                conn.commit()
        except sqlite3.OperationalError:
            pass # Si da error, significa que la columna ya existe. Todo bien.

    def get_available_micros(self, patient_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, label FROM microcontingencies WHERE patient_id = ?", (patient_id,))
                return cursor.fetchall()
        except sqlite3.Error:
            return []

    def get_plan_by_micro(self, micro_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM intervention_plans WHERE microcontingency_id = ?", (micro_id,))
                plan_row = cursor.fetchone()
                
                if not plan_row: return None
                    
                data = dict(plan_row)
                cursor.execute("SELECT * FROM deprofessionalization_analysis WHERE intervention_plan_id = ?", (data['id'],))
                data['deprofessionalization'] = [dict(r) for r in cursor.fetchall()]
                
                return data
        except sqlite3.Error: 
            return None

    def save_plan(self, patient_id, micro_id, plan_data, deprof_data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
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

    def get_all_techniques(self, category_filter=None, rubro_filter=None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                
                query = "SELECT * FROM library_techniques WHERE 1=1"
                params = []
                
                if category_filter and category_filter != "Todas":
                    query += " AND category LIKE ?"
                    params.append(f"%{category_filter.strip()}%")
                    
                if rubro_filter and rubro_filter != "Todos los rubros":
                    query += " AND rubro_funcional LIKE ?"
                    params.append(f"%{rubro_filter.strip()}%")
                    
                c.execute(query, params)
                return [dict(r) for r in c.fetchall()]
        except Exception as e: 
            print(f"Error cargando técnicas: {e}")
            return []

    def add_technique(self, data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM library_techniques WHERE name = ?", (data['name'],))
                if cursor.fetchone():
                    return False, "Ya existe una técnica con ese nombre en la base de datos."
                
                cursor.execute('''
                    INSERT INTO library_techniques (category, name, objective, method, pros, cons, rubro_funcional)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (data['category'], data['name'], data['objective'], data['method'], data['pros'], data['cons'], data['rubro_funcional']))
                conn.commit()

            csv_path = "tecnicas.csv"
            delimiter = ','
            if os.path.exists(csv_path):
                with open(csv_path, mode='r', encoding='utf-8-sig') as f:
                    first_line = f.readline()
                    if ';' in first_line: delimiter = ';'

            with open(csv_path, mode='a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, delimiter=delimiter)
                writer.writerow([data['name'], data['category'], data['objective'], data['method'], data['pros'], data['cons'], data['rubro_funcional']])
                
            return True, "Técnica agregada a la Biblioteca y al archivo CSV correctamente."
        except Exception as e: 
            return False, str(e)