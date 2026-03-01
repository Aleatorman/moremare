import sqlite3

class MicroManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def get_available_micros(self, patient_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, problem_desc FROM microcontingencies WHERE patient_id = ?", (patient_id,))
                return cursor.fetchall()
        except sqlite3.Error:
            return []

    def get_full_microcontingency(self, micro_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 1. Datos Principales
                cursor.execute("SELECT * FROM microcontingencies WHERE id = ?", (micro_id,))
                row = cursor.fetchone()
                if not row: return None
                data = dict(row)
                
                # 2. Listas
                # Actores
                cursor.execute("SELECT name, role, response FROM micro_actors WHERE microcontingency_id = ?", (micro_id,))
                data['actors'] = [dict(r) for r in cursor.fetchall()]
                
                # Inclinaciones
                cursor.execute("SELECT category, description FROM micro_inclinations WHERE microcontingency_id = ?", (micro_id,))
                data['inclinations'] = [dict(r) for r in cursor.fetchall()]
                
                # Efectos
                cursor.execute("SELECT effect_type, description FROM micro_effects WHERE microcontingency_id = ?", (micro_id,))
                data['effects'] = [dict(r) for r in cursor.fetchall()]
                
                return data
        except sqlite3.Error:
            return None

    def create_micro(self, patient_id, data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insertar Principal
                cursor.execute("""
                    INSERT INTO microcontingencies (
                        patient_id, morphology_type, morphology_class, morphology_metrics, problem_desc, 
                        social_type, social_context, physical_context, 
                        expected_behaviors, social_competence, non_problematic_desc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    patient_id, data['morphology_type'], data['morphology_class'], data['morphology_metrics'], data['problem_desc'],
                    data['social_type'], data['social_context'], data['physical_context'],
                    data['expected_behaviors'], data['social_competence'], data['non_problematic_desc']
                ))
                micro_id = cursor.lastrowid
                
                self._insert_children(cursor, micro_id, data)
                
                conn.commit()
                return True, "Microcontingencia creada correctamente."
        except sqlite3.Error as e:
            return False, str(e)

    def update_micro(self, micro_id, data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE microcontingencies SET
                        morphology_type=?, morphology_class=?, morphology_metrics=?, problem_desc=?, 
                        social_type=?, social_context=?, physical_context=?, 
                        expected_behaviors=?, social_competence=?, non_problematic_desc=?
                    WHERE id=?
                """, (
                    data['morphology_type'], data['morphology_class'], data['morphology_metrics'], data['problem_desc'],
                    data['social_type'], data['social_context'], data['physical_context'],
                    data['expected_behaviors'], data['social_competence'], data['non_problematic_desc'],
                    micro_id
                ))
                
                # Borrar hijos viejos y reinsertar
                cursor.execute("DELETE FROM micro_actors WHERE microcontingency_id=?", (micro_id,))
                cursor.execute("DELETE FROM micro_inclinations WHERE microcontingency_id=?", (micro_id,))
                cursor.execute("DELETE FROM micro_effects WHERE microcontingency_id=?", (micro_id,))
                
                self._insert_children(cursor, micro_id, data)
                
                conn.commit()
                return True, "Microcontingencia actualizada."
        except sqlite3.Error as e:
            return False, str(e)

    def _insert_children(self, cursor, micro_id, data):
        # Actores
        for x in data.get('actors', []):
            cursor.execute("INSERT INTO micro_actors (microcontingency_id, name, role, response) VALUES (?, ?, ?, ?)",
                           (micro_id, x['name'], x['role'], x['response']))
        # Inclinaciones
        for x in data.get('inclinations', []):
            cursor.execute("INSERT INTO micro_inclinations (microcontingency_id, category, description) VALUES (?, ?, ?)",
                           (micro_id, x['category'], x['description']))
        # Efectos
        for x in data.get('effects', []):
            cursor.execute("INSERT INTO micro_effects (microcontingency_id, effect_type, description) VALUES (?, ?, ?)",
                           (micro_id, x['effect_type'], x['description']))
    
    # Compatibilidad para reportes (evita errores con código viejo)
    def get_list_by_patient(self, patient_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, problem_desc, morphology_type FROM microcontingencies WHERE patient_id = ?", (patient_id,))
                return cursor.fetchall()
        except sqlite3.Error:
            return []