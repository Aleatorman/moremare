import sqlite3
import json

class MicroManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def get_list_by_patient(self, patient_id):
        """Obtiene lista resumen para el historial."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, problem_desc, morphology_type 
                    FROM microcontingencies 
                    WHERE patient_id = ? ORDER BY id DESC
                """, (patient_id,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error cargando lista: {e}")
            return []

    def get_full_microcontingency(self, micro_id):
        """Recupera TODA la información."""
        data = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM microcontingencies WHERE id = ?", (micro_id,))
                row = cursor.fetchone()
                if row:
                    data = dict(row)
                else:
                    return None

                cursor.execute("SELECT * FROM micro_actors WHERE microcontingency_id = ?", (micro_id,))
                actors = [dict(act) for act in cursor.fetchall()]
                data['actors'] = actors
                
                return data
        except sqlite3.Error as e:
            print(f"Error recuperando detalle: {e}")
            return None

    def save_microcontingency(self, patient_id, form_data, actors_list):
        """Guarda un registro NUEVO."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO microcontingencies (
                        patient_id, morphology_type, morphology_metrics, 
                        problem_desc, social_context, physical_context, 
                        dispositions, consequence_type, consequence_desc, 
                        non_problematic_desc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    patient_id, form_data['type'], form_data['metrics'], 
                    form_data['problem'], form_data['social'], form_data['physical'],
                    form_data['dispositions'], form_data['conseq_type'], 
                    form_data['conseq_desc'], form_data['non_prob']
                ))
                
                new_micro_id = cursor.lastrowid
                
                for actor in actors_list:
                    cursor.execute('''
                        INSERT INTO micro_actors (microcontingency_id, name, role, response)
                        VALUES (?, ?, ?, ?)
                    ''', (new_micro_id, actor['name'], actor['role'], actor['response']))
                
                conn.commit()
                return True, "Guardado exitosamente"
        except sqlite3.Error as e:
            return False, str(e)

    def delete_microcontingency(self, micro_id):
        """ELIMINA un registro y sus actores."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Primero borramos los actores dependientes
                cursor.execute("DELETE FROM micro_actors WHERE microcontingency_id = ?", (micro_id,))
                # Luego borramos la ficha principal
                cursor.execute("DELETE FROM microcontingencies WHERE id = ?", (micro_id,))
                conn.commit()
                return True, "Eliminado correctamente"
        except sqlite3.Error as e:
            return False, str(e)

    def update_microcontingency(self, micro_id, form_data, actors_list):
        """ACTUALIZA un registro existente."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 1. Actualizar datos principales
                cursor.execute('''
                    UPDATE microcontingencies SET
                        morphology_type = ?, morphology_metrics = ?, 
                        problem_desc = ?, social_context = ?, physical_context = ?, 
                        dispositions = ?, consequence_type = ?, consequence_desc = ?, 
                        non_problematic_desc = ?
                    WHERE id = ?
                ''', (
                    form_data['type'], form_data['metrics'], form_data['problem'],
                    form_data['social'], form_data['physical'], form_data['dispositions'],
                    form_data['conseq_type'], form_data['conseq_desc'], form_data['non_prob'],
                    micro_id
                ))

                # 2. Actualizar Actores: Borramos los viejos e insertamos los nuevos
                cursor.execute("DELETE FROM micro_actors WHERE microcontingency_id = ?", (micro_id,))
                
                for actor in actors_list:
                    cursor.execute('''
                        INSERT INTO micro_actors (microcontingency_id, name, role, response)
                        VALUES (?, ?, ?, ?)
                    ''', (micro_id, actor['name'], actor['role'], actor['response']))
                
                conn.commit()
                return True, "Actualizado correctamente"
        except sqlite3.Error as e:
            return False, str(e)