import sqlite3

class MacroManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def get_macros(self, patient_id):
        """Obtiene la lista de análisis previos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, group_name FROM macrocontingencies WHERE patient_id = ?", (patient_id,))
                return cursor.fetchall()
        except: return []

    def get_full_macro(self, macro_id):
        """Recupera textos y los puntos verdes de la matriz"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Datos de texto
                cursor.execute("SELECT * FROM macrocontingencies WHERE id = ?", (macro_id,))
                row = cursor.fetchone()
                if not row: return None
                data = dict(row)
                
                # Coordenadas de la Matriz
                cursor.execute("SELECT row_idx, col_idx FROM macro_matrix_states WHERE macro_id = ? AND active = 1", (macro_id,))
                data['matrix_points'] = [(r['row_idx'], r['col_idx']) for r in cursor.fetchall()]
                
                return data
        except: return None

    def save_macro(self, patient_id, macro_id, data, matrix_points):
        """Guarda textos y reescribe los puntos verdes"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 1. Guardar Textos
                if macro_id:
                    cursor.execute("""
                        UPDATE macrocontingencies SET 
                            group_name=?, user_effective=?, user_substitutive=?,
                            other_effective=?, other_substitutive=?, analysis_notes=?
                        WHERE id=?
                    """, (data['group_name'], data['u_eff'], data['u_sub'], 
                          data['o_eff'], data['o_sub'], data['notes'], macro_id))
                    mid = macro_id
                else:
                    cursor.execute("""
                        INSERT INTO macrocontingencies (patient_id, group_name, user_effective, user_substitutive, other_effective, other_substitutive, analysis_notes)
                        VALUES (?,?,?,?,?,?,?)
                    """, (patient_id, data['group_name'], data['u_eff'], data['u_sub'], 
                          data['o_eff'], data['o_sub'], data['notes']))
                    mid = cursor.lastrowid
                
                # 2. Guardar Puntos (Borrar viejos -> Insertar nuevos)
                cursor.execute("DELETE FROM macro_matrix_states WHERE macro_id=?", (mid,))
                for (r, c) in matrix_points:
                    cursor.execute("INSERT INTO macro_matrix_states (macro_id, row_idx, col_idx, active) VALUES (?,?,?,1)", (mid, r, c))
                
                conn.commit()
                return True, "Análisis guardado correctamente."
        except sqlite3.Error as e:
            return False, str(e)