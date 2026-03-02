import sqlite3

class EvaluationManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def save_evaluation(self, patient_id, notes, matrix_rows):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 1. Insertar cabecera de evaluación
                cursor.execute("INSERT INTO evaluations (patient_id, notes) VALUES (?, ?)", (patient_id, notes))
                eval_id = cursor.lastrowid
                
                # 2. Insertar filas de la matriz
                for row in matrix_rows:
                    cursor.execute('''
                        INSERT INTO evaluation_matrix (evaluation_id, target, parameter, terapia_val, terapeuta_val)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (eval_id, row['target'], row['parameter'], row['terapia'], row['terapeuta']))
                
                conn.commit()
                return True, "Evaluación guardada exitosamente."
        except sqlite3.Error as e:
            return False, str(e)

    def get_evaluations(self, patient_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM evaluations WHERE patient_id = ? ORDER BY date_eval DESC", (patient_id,))
                return [dict(r) for r in cursor.fetchall()]
        except: return []

    def get_evaluation_details(self, eval_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM evaluation_matrix WHERE evaluation_id = ?", (eval_id,))
                return [dict(r) for r in cursor.fetchall()]
        except: return []