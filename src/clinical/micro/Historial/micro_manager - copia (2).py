import sqlite3

class MicroManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def get_available_micros(self, patient_id):
        """
        Para el dropdown del panel visual: devuelve ID y Descripción.
        Corrige: AttributeError 'get_available_micros'
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, problem_desc FROM microcontingencies WHERE patient_id = ?", (patient_id,))
                return cursor.fetchall()
        except sqlite3.Error:
            return []

    def get_list_by_patient(self, patient_id):
        """
        Para el ReportManager (compatibilidad): devuelve ID, Problema, Morfología.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, problem_desc, morphology_type FROM microcontingencies WHERE patient_id = ?", (patient_id,))
                return cursor.fetchall()
        except sqlite3.Error:
            return []

    def get_full_microcontingency(self, micro_id):
        """
        Recupera TODOS los datos de una micro específica + sus actores.
        Necesario para llenar el formulario al seleccionar una opción.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # 1. Datos base de la microcontingencia
                cursor.execute("SELECT * FROM microcontingencies WHERE id = ?", (micro_id,))
                row = cursor.fetchone()
                if not row: return None
                
                data = dict(row)
                
                # 2. Actores asociados
                cursor.execute("SELECT name, role, response FROM micro_actors WHERE microcontingency_id = ?", (micro_id,))
                actors_rows = cursor.fetchall()
                data['actors'] = [dict(a) for a in actors_rows]
                
                return data
        except sqlite3.Error:
            return None

    def create_micro(self, patient_id, data):
        """Crea una nueva microcontingencia y sus actores."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insertar Micro
                cursor.execute("""
                    INSERT INTO microcontingencies (
                        patient_id, morphology_type, morphology_metrics, problem_desc, 
                        social_context, physical_context, dispositions, 
                        consequence_type, consequence_desc, non_problematic_desc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    patient_id, data['morphology_type'], data['morphology_metrics'], data['problem_desc'],
                    data['social_context'], data['physical_context'], data['dispositions'],
                    data['consequence_type'], data['consequence_desc'], data['non_problematic_desc']
                ))
                
                micro_id = cursor.lastrowid
                
                # Insertar Actores
                for actor in data.get('actors', []):
                    cursor.execute("INSERT INTO micro_actors (microcontingency_id, name, role, response) VALUES (?, ?, ?, ?)",
                                   (micro_id, actor['name'], actor['role'], actor['response']))
                
                conn.commit()
                return True, "Microcontingencia creada correctamente."
        except sqlite3.Error as e:
            return False, str(e)

    def update_micro(self, micro_id, data):
        """Actualiza una micro existente y regenera sus actores."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Actualizar campos base
                cursor.execute("""
                    UPDATE microcontingencies SET
                        morphology_type=?, morphology_metrics=?, problem_desc=?, 
                        social_context=?, physical_context=?, dispositions=?, 
                        consequence_type=?, consequence_desc=?, non_problematic_desc=?
                    WHERE id=?
                """, (
                    data['morphology_type'], data['morphology_metrics'], data['problem_desc'],
                    data['social_context'], data['physical_context'], data['dispositions'],
                    data['consequence_type'], data['consequence_desc'], data['non_problematic_desc'],
                    micro_id
                ))
                
                # Actualizar Actores (Estrategia limpia: Borrar todos y reinsertar)
                cursor.execute("DELETE FROM micro_actors WHERE microcontingency_id = ?", (micro_id,))
                
                for actor in data.get('actors', []):
                    cursor.execute("INSERT INTO micro_actors (microcontingency_id, name, role, response) VALUES (?, ?, ?, ?)",
                                   (micro_id, actor['name'], actor['role'], actor['response']))
                
                conn.commit()
                return True, "Microcontingencia actualizada."
        except sqlite3.Error as e:
            return False, str(e)