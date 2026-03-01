import sqlite3

class PatientManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def create_patient(self, data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                goals = data.get('goals', '')
                # Guardamos siempre como 'Activo' al crear
                cursor.execute("""
                    INSERT INTO patients (code_name, age, sex, occupation, motive, goals, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'Activo')
                """, (data['code_name'], data['age'], data['sex'], 
                      data['occupation'], data['motive'], goals))
                conn.commit()
                return True, "Paciente creado exitosamente."
        except sqlite3.Error as e:
            return False, str(e)

    def get_all_patients(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row 
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients ORDER BY id DESC")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error:
            return []

    def get_patient_by_id(self, patient_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error:
            return None

    def toggle_status(self, patient_id, new_status):
        """Cambia el estado del paciente (Activo <-> Inactivo)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE patients SET status = ? WHERE id = ?", (new_status, patient_id))
                conn.commit()
                return True
        except sqlite3.Error:
            return False