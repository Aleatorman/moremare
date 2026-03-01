import sqlite3

class MicroManager:
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

    def get_full_microcontingency(self, micro_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM microcontingencies WHERE id = ?", (micro_id,))
                row = cursor.fetchone()
                if not row: return None
                data = dict(row)
                
                # Cargar las 8 listas
                tables = {
                    'morphologies': 'micro_morphologies',
                    'social_contexts': 'micro_contexts_social',
                    'physical_contexts': 'micro_contexts_physical',
                    'interactions': 'micro_interactions',
                    'inclinations': 'micro_inclinations',
                    'actors': 'micro_actors',
                    'effects': 'micro_effects',
                    'noproblems': 'micro_noproblem'
                }
                
                for key, table in tables.items():
                    cursor.execute(f"SELECT * FROM {table} WHERE micro_id = ?", (micro_id,))
                    data[key] = [dict(r) for r in cursor.fetchall()]
                
                return data
        except sqlite3.Error:
            return None

    def create_micro(self, patient_id, data):
        return self._save_transaction(patient_id, None, data)

    def update_micro(self, micro_id, data):
        return self._save_transaction(None, micro_id, data)

    def _save_transaction(self, patient_id, micro_id, data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if micro_id: # UPDATE
                    cursor.execute("UPDATE microcontingencies SET label=? WHERE id=?", (data['label'], micro_id))
                    # Borrar hijos viejos para reinsertar
                    tables = ['micro_morphologies', 'micro_contexts_social', 'micro_contexts_physical', 
                              'micro_interactions', 'micro_inclinations', 'micro_actors', 
                              'micro_effects', 'micro_noproblem']
                    for t in tables:
                        cursor.execute(f"DELETE FROM {t} WHERE micro_id=?", (micro_id,))
                else: # CREATE
                    cursor.execute("INSERT INTO microcontingencies (patient_id, label) VALUES (?, ?)", (patient_id, data['label']))
                    micro_id = cursor.lastrowid

                # Insertar Listas
                for i in data.get('morphologies', []):
                    cursor.execute("INSERT INTO micro_morphologies (micro_id, type, class, metrics, description) VALUES (?,?,?,?,?)",
                                   (micro_id, i['type'], i['class'], i['metrics'], i['description']))
                
                for i in data.get('social_contexts', []):
                    cursor.execute("INSERT INTO micro_contexts_social (micro_id, type, description) VALUES (?,?,?)",
                                   (micro_id, i['type'], i['description']))

                for i in data.get('physical_contexts', []):
                    cursor.execute("INSERT INTO micro_contexts_physical (micro_id, element, description) VALUES (?,?,?)",
                                   (micro_id, i['element'], i['description']))

                for i in data.get('interactions', []):
                    cursor.execute("INSERT INTO micro_interactions (micro_id, expected, competence) VALUES (?,?,?)",
                                   (micro_id, i['expected'], i['competence']))

                for i in data.get('inclinations', []):
                    cursor.execute("INSERT INTO micro_inclinations (micro_id, category, description) VALUES (?,?,?)",
                                   (micro_id, i['category'], i['description']))

                for i in data.get('actors', []):
                    cursor.execute("INSERT INTO micro_actors (micro_id, name, role, response) VALUES (?,?,?,?)",
                                   (micro_id, i['name'], i['role'], i['response']))

                for i in data.get('effects', []):
                    cursor.execute("INSERT INTO micro_effects (micro_id, type, description) VALUES (?,?,?)",
                                   (micro_id, i['type'], i['description']))

                for i in data.get('noproblems', []):
                    cursor.execute("INSERT INTO micro_noproblem (micro_id, situation, description) VALUES (?,?,?)",
                                   (micro_id, i['situation'], i['description']))

                conn.commit()
                return True, "Microcontingencia guardada."
        except sqlite3.Error as e:
            return False, str(e)
            
    # Compatibilidad Reporte
    def get_list_by_patient(self, patient_id):
        # Esta función simple se usa en el reporte. Devolvemos el Label como 'problem_desc'
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, label as problem_desc, 'Múltiple' as morphology_type FROM microcontingencies WHERE patient_id = ?", (patient_id,))
                return cursor.fetchall()
        except: return []