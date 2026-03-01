import sqlite3

class MacroManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def get_all_macros(self, patient_id):
        """Recupera todas las filas del análisis macro para la tabla."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                # Traemos todo ordenado por ID descendente (lo más nuevo arriba)
                cursor.execute("SELECT * FROM macrocontingencies WHERE patient_id = ? ORDER BY id DESC", (patient_id,))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error recuperando macro: {e}")
            return []

    def get_macro_by_id(self, macro_id):
        """Recupera una fila específica para editarla."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM macrocontingencies WHERE id = ?", (macro_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            return None

    def add_macro_row(self, patient_id, data):
        """Crea una nueva fila de análisis."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO macrocontingencies (
                        patient_id, category, analysis, 
                        correspondence, valuative_function, detail
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    patient_id,
                    data['category'],
                    data['analysis'],
                    data['correspondence'],
                    data['function'],
                    data['detail']
                ))
                conn.commit()
                return True, "Análisis agregado correctamente."
        except sqlite3.Error as e:
            return False, str(e)

    def update_macro_row(self, macro_id, data):
        """Actualiza una fila existente."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE macrocontingencies SET
                        category = ?, analysis = ?, 
                        correspondence = ?, valuative_function = ?, detail = ?
                    WHERE id = ?
                ''', (
                    data['category'], data['analysis'], 
                    data['correspondence'], data['function'], 
                    data['detail'], macro_id
                ))
                conn.commit()
                return True, "Actualizado correctamente."
        except sqlite3.Error as e:
            return False, str(e)

    def delete_macro_row(self, macro_id):
        """Borra una fila."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM macrocontingencies WHERE id = ?", (macro_id,))
                conn.commit()
                return True, "Eliminado correctamente."
        except sqlite3.Error as e:
            return False, str(e)