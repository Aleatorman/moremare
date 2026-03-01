import sqlite3

class PatientManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def create_patient(self, data):
        """
        Crea un nuevo paciente recibiendo un diccionario de datos.
        Corrige el error: TypeError... missing arguments
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Aseguramos que 'goals' exista, si no, cadena vacía
                goals = data.get('goals', '')

                cursor.execute("""
                    INSERT INTO patients (code_name, age, sex, occupation, motive, goals)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (data['code_name'], data['age'], data['sex'], 
                      data['occupation'], data['motive'], goals))
                
                conn.commit()
                return True, "Paciente creado exitosamente."
        except sqlite3.Error as e:
            return False, str(e)

    def get_all_patients(self):
        """
        Devuelve la lista de pacientes como Diccionarios.
        Corrige el error: TypeError: tuple indices must be integers...
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Esto es clave: permite acceder a las columnas por nombre ['nombre']
                conn.row_factory = sqlite3.Row 
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients ORDER BY id DESC")
                rows = cursor.fetchall()
                
                # Convertimos las filas (Rows) a diccionarios reales de Python
                return [dict(row) for row in rows]
        except sqlite3.Error:
            return []

    def get_patient_by_id(self, patient_id):
        """Obtiene un paciente específico por ID como diccionario."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
                row = cursor.fetchone()
                
                return dict(row) if row else None
        except sqlite3.Error:
            return None