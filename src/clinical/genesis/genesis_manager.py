import sqlite3
import json

class GenesisManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def get_available_micros(self, patient_id):
        """Obtiene lista de micros (ID y Nombre) para el selector."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, problem_desc FROM microcontingencies WHERE patient_id = ?", (patient_id,))
                return cursor.fetchall()
        except sqlite3.Error:
            return []

    def get_genesis_by_micro_id(self, micro_id):
        """Busca si existe un análisis para esta microcontingencia específica."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM genesis_history WHERE microcontingency_id = ?", (micro_id,))
                row = cursor.fetchone()
                
                if row:
                    data = dict(row)
                    try: data['origin_history'] = json.loads(data['origin_history'])
                    except: data['origin_history'] = {}
                    try: data['functional_history'] = json.loads(data['functional_history'])
                    except: data['functional_history'] = {}
                    return data
                return None
        except sqlite3.Error:
            return None

    def get_genesis_history_list(self, patient_id):
        """
        Recupera TODOS los análisis de génesis del paciente.
        (Esta es la función que necesita el Report Manager)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                # Hacemos JOIN para obtener el nombre del problema asociado
                query = """
                    SELECT g.*, m.problem_desc 
                    FROM genesis_history g
                    LEFT JOIN microcontingencies m ON g.microcontingency_id = m.id
                    WHERE g.patient_id = ?
                """
                cursor.execute(query, (patient_id,))
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    data = dict(row)
                    # Desempaquetar JSON
                    try: data['origin_history'] = json.loads(data['origin_history'])
                    except: data['origin_history'] = {}
                    # (Opcional) Desempaquetar funcional si lo necesitaras en el reporte
                    try: data['functional_history'] = json.loads(data['functional_history'])
                    except: data['functional_history'] = {}
                    
                    results.append(data)
                return results
        except sqlite3.Error as e:
            print(f"Error recuperando historial génesis: {e}")
            return []

    def save_genesis(self, patient_id, micro_id, origin_data, func_data):
        """Guarda (Insert) o Actualiza (Update) automáticamente."""
        origin_json = json.dumps(origin_data, ensure_ascii=False)
        func_json = json.dumps(func_data, ensure_ascii=False)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificamos si ya existe para decidir si hacemos UPDATE o INSERT
                cursor.execute("SELECT id FROM genesis_history WHERE microcontingency_id = ?", (micro_id,))
                row = cursor.fetchone()

                if row:
                    # ACTUALIZAR
                    cursor.execute('''
                        UPDATE genesis_history 
                        SET origin_history = ?, functional_history = ?
                        WHERE id = ?
                    ''', (origin_json, func_json, row[0]))
                    msg = "Análisis actualizado correctamente."
                else:
                    # CREAR
                    cursor.execute('''
                        INSERT INTO genesis_history (patient_id, microcontingency_id, origin_history, functional_history)
                        VALUES (?, ?, ?, ?)
                    ''', (patient_id, micro_id, origin_json, func_json))
                    msg = "Análisis guardado correctamente."
                
                conn.commit()
                return True, msg
        except sqlite3.Error as e:
            return False, str(e)