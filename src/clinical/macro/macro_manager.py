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
        except sqlite3.Error: 
            return []

    def get_full_macro(self, macro_id):
        """Recupera toda la macrocontingencia y evalúa su estado funcional"""
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

                # Matriz de Correspondencias (Solo traemos donde NO hay correspondencia, es decir, las "X")
                cursor.execute("SELECT axis_1, axis_2 FROM macro_correspondences WHERE macro_id = ? AND has_correspondence = 0", (macro_id,))
                data['matrix_points'] = [(r['axis_1'], r['axis_2']) for r in cursor.fetchall()]
                
                # Generar diagnóstico funcional automático
                data['clinical_hypothesis'] = self.analyze_correspondences(data['matrix_points'])
                
                return data
        except sqlite3.Error: 
            return None

    def save_macro(self, patient_id, macro_id, data, non_correspondences):
        """
        Guarda la estructura clínica. 
        'non_correspondences' es una lista de tuplas con los ejes que chocan, ej: [('UES', 'OSS'), ('USE', 'UEE')]
        """
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
                    cursor.execute("DELETE FROM macro_normative_functions WHERE macro_id=?", (mid,))
                    cursor.execute("DELETE FROM macro_correspondences WHERE macro_id=?", (mid,))
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

                # 3. Guardar Matriz (Guardamos explícitamente las faltas de correspondencia)
                for (axis_1, axis_2) in non_correspondences:
                    cursor.execute("""
                        INSERT INTO macro_correspondences (macro_id, axis_1, axis_2, has_correspondence) 
                        VALUES (?,?,?,0)
                    """, (mid, axis_1, axis_2))
                
                conn.commit()
                return True, "Análisis Macrocontingencial guardado correctamente.", mid
        except sqlite3.Error as e:
            return False, str(e), None

    def analyze_correspondences(self, non_correspondences):
        """
        Motor de diagnóstico: Analiza las faltas de correspondencia para orientar al clínico.
        """
        if not non_correspondences:
            return "No se han detectado faltas de correspondencia. Valore si la problemática recae exclusivamente en deficiencias morfológicas."

        conflict_situational = False # Conflicto puramente micro (situacional vs situacional)
        conflict_normative = False   # Conflicto macro (ejemplar vs situacional)

        situational_axes = ['USS', 'UES', 'OSS', 'OES']
        exemplary_axes = ['USE', 'UEE', 'OSE', 'OEE']

        for (a1, a2) in non_correspondences:
            # Si ambos ejes pertenecen a la situación problema
            if a1 in situational_axes and a2 in situational_axes:
                conflict_situational = True
            # Si un eje es ejemplar (normativo) y el otro es situacional
            elif (a1 in exemplary_axes and a2 in situational_axes) or (a2 in exemplary_axes and a1 in situational_axes):
                conflict_normative = True

        if conflict_normative and conflict_situational:
            return ("HIPÓTESIS MIXTA: Existe un choque directo con las prácticas valorativas del grupo (Macrocontingencia), "
                    "aunado a contradicciones internas en la situación problema (Microcontingencia). "
                    "Se sugiere priorizar el análisis de las creencias (Sustitutivas) frente a la falta de habilidades (Efectivas).")
        
        elif conflict_normative:
            return ("HIPÓTESIS MACROCONTINGENCIAL: El comportamiento problema es producto de un choque directo con las "
                    "prácticas ejemplares/normativas del grupo. La intervención debe enfocarse en alterar prácticas macrocontingenciales, "
                    "desligar al usuario del grupo normativo, o alterar su correspondencia valorativa.")
            
        elif conflict_situational:
            return ("HIPÓTESIS MICROCONTINGENCIAL: La falta de correspondencia es estrictamente intracontingencial. "
                    "El problema radica en que lo que se 'cree' y lo que se 'hace' en la situación problemática no coinciden. "
                    "Sugiere déficit de competencias (precisión), problemas de oportunidad o tendencias incompatibles. "
                    "Revise las estrategias de interacción en el módulo de Génesis.")
            
        return "Requiere más datos en la matriz para formular una hipótesis."

    def delete_macro(self, macro_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM macrocontingencies WHERE id = ?", (macro_id,))
                conn.commit()
                return True, "Análisis eliminado."
        except sqlite3.Error as e:
            return False, str(e)