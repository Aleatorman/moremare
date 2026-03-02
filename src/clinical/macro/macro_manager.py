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
        """Recupera toda la macrocontingencia: datos, funciones normativas y matriz"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Datos principales
                cursor.execute("SELECT * FROM macrocontingencies WHERE id = ?", (macro_id,))
                row = cursor.fetchone()
                if not row: return None
                data = dict(row)
                
                # Lista de Funciones Normativas
                cursor.execute("SELECT * FROM macro_normative_functions WHERE macro_id = ?", (macro_id,))
                data['normative_functions'] = [dict(r) for r in cursor.fetchall()]

                # Puntos de la Matriz
                cursor.execute("SELECT row_idx, col_idx FROM macro_matrix_states WHERE macro_id = ? AND active = 1", (macro_id,))
                data['matrix_points'] = [(r['row_idx'], r['col_idx']) for r in cursor.fetchall()]
                
                return data
        except: return None

    def save_macro(self, patient_id, macro_id, data, matrix_points):
        """Guarda la nueva estructura clínica"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 1. Guardar Datos Principales
                if macro_id:
                    cursor.execute("""
                        UPDATE macrocontingencies SET 
                            group_type=?, group_name=?, beliefs_values=?,
                            customs_lifestyles=?, intra_analysis=?, inter_analysis=?
                        WHERE id=?
                    """, (data['group_type'], data['group_name'], data['beliefs_values'], 
                          data['customs_lifestyles'], data['intra_analysis'], data['inter_analysis'], macro_id))
                    mid = macro_id
                    # Limpiar listas para reescribir
                    cursor.execute("DELETE FROM macro_normative_functions WHERE macro_id=?", (mid,))
                    cursor.execute("DELETE FROM macro_matrix_states WHERE macro_id=?", (mid,))
                else:
                    cursor.execute("""
                        INSERT INTO macrocontingencies 
                        (patient_id, group_type, group_name, beliefs_values, customs_lifestyles, intra_analysis, inter_analysis)
                        VALUES (?,?,?,?,?,?,?)
                    """, (patient_id, data['group_type'], data['group_name'], data['beliefs_values'], 
                          data['customs_lifestyles'], data['intra_analysis'], data['inter_analysis']))
                    mid = cursor.lastrowid
                
                # 2. Guardar Funciones Normativas
                for nf in data.get('normative_functions', []):
                    cursor.execute("""
                        INSERT INTO macro_normative_functions (macro_id, function_type, exercised_by, description)
                        VALUES (?,?,?,?)
                    """, (mid, nf['function_type'], nf['exercised_by'], nf['description']))

                # 3. Guardar Matriz
                for (r, c) in matrix_points:
                    cursor.execute("INSERT INTO macro_matrix_states (macro_id, row_idx, col_idx, active) VALUES (?,?,?,1)", (mid, r, c))
                
                conn.commit()
                return True, "Análisis Macrocontingencial guardado correctamente."
        except sqlite3.Error as e:
            return False, str(e)
            
    def delete_macro(self, macro_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM macrocontingencies WHERE id = ?", (macro_id,))
                conn.commit()
                return True, "Análisis eliminado."
        except sqlite3.Error as e:
            return False, str(e)