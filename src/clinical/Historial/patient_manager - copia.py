import sqlite3

class PatientManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def get_all_patients(self):
        """Obtiene una lista resumida de todos los pacientes."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Traemos solo lo necesario para la lista
                cursor.execute("SELECT id, code_name, motive FROM patients ORDER BY created_at DESC")
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error recuperando pacientes: {e}")
            return []

    def create_patient(self, code_name, age, sex, occupation, motive, goals):
        """Crea un nuevo expediente."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO patients (code_name, age, sex, occupation, motive, goals)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (code_name, age, sex, occupation, motive, goals))
                conn.commit()
                return True, "Paciente creado correctamente"
        except sqlite3.Error as e:
            return False, str(e)

    def get_patient_by_id(self, patient_id):
        """Recupera todos los datos de un paciente específico."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row # Esto permite acceder a columnas por nombre
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row) # Convertimos a diccionario para usarlo fácil
                return None
        except sqlite3.Error as e:
            print(f"Error recuperando paciente: {e}")
            return None