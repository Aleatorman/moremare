import sqlite3
import json

class MicroManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def get_list_by_patient(self, patient_id):
        """Obtiene solo los títulos de las microcontingencias para la lista lateral."""
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
        """Recupera TODA la información (Formulario + Actores)."""
        data = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 1. Datos principales
                cursor.execute("SELECT * FROM microcontingencies WHERE id = ?", (micro_id,))
                row = cursor.fetchone()
                if row:
                    data = dict(row)
                else:
                    return None

                # 2. Actores asociados
                cursor.execute("SELECT * FROM micro_actors WHERE microcontingency_id = ?", (micro_id,))
                actors = [dict(act) for act in cursor.fetchall()]
                data['actors'] = actors
                
                return data
        except sqlite3.Error as e:
            print(f"Error recuperando detalle: {e}")
            return None

    def save_microcontingency(self, patient_id, form_data, actors_list):
        """Guarda una nueva microcontingencia y sus actores en una sola transacción."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 1. Insertar la Microcontingencia Principal
                cursor.execute('''
                    INSERT INTO microcontingencies (
                        patient_id, morphology_type, morphology_metrics, 
                        problem_desc, social_context, physical_context, 
                        dispositions, consequence_type, consequence_desc, 
                        non_problematic_desc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    patient_id,
                    form_data['type'],
                    form_data['metrics'], # Esto vendrá como texto o JSON
                    form_data['problem'],
                    form_data['social'],
                    form_data['physical'],
                    form_data['dispositions'],
                    form_data['conseq_type'],
                    form_data['conseq_desc'],
                    form_data['non_prob']
                ))
                
                # Obtener el ID que se acaba de crear
                new_micro_id = cursor.lastrowid
                
                # 2. Insertar los Actores (Loop)
                for actor in actors_list:
                    # actor es un diccionario: {'name': 'Madre', 'role': 'Mediador', 'response': 'Grita'}
                    cursor.execute('''
                        INSERT INTO micro_actors (microcontingency_id, name, role, response)
                        VALUES (?, ?, ?, ?)
                    ''', (new_micro_id, actor['name'], actor['role'], actor['response']))
                
                conn.commit()
                return True, "Guardado exitosamente"
                
        except sqlite3.Error as e:
            return False, str(e)