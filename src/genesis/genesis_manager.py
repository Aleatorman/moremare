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

    def get_genesis_history_list(self, patient_id):
        """Recupera todos los análisis de génesis con el nombre de la microcontingencia asociada."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                # Hacemos un JOIN para traer el nombre del problema desde la otra tabla
                query = """
                    SELECT g.*, m.problem_desc 
                    FROM genesis_history g
                    LEFT JOIN microcontingencies m ON g.microcontingency_id = m.id
                    WHERE g.patient_id = ?
                    ORDER BY g.id DESC
                """
                cursor.execute(query, (patient_id,))
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    data = dict(row)
                    # Desempaquetar JSONs para usarlos si se necesita editar
                    try: data['origin_history'] = json.loads(data['origin_history'])
                    except: data['origin_history'] = {}
                    try: data['functional_history'] = json.loads(data['functional_history'])
                    except: data['functional_history'] = {}
                    results.append(data)
                return results
        except sqlite3.Error as e:
            print(f"Error lista génesis: {e}")
            return []

    def get_genesis_by_id(self, genesis_id):
        """Recupera un análisis específico para editar."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM genesis_history WHERE id = ?", (genesis_id,))
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

    def save_genesis(self, patient_id, micro_id, origin_data, func_data, genesis_id=None):
        """Guarda (Insert) o Actualiza (Update) un análisis."""
        origin_json = json.dumps(origin_data, ensure_ascii=False)
        func_json = json.dumps(func_data, ensure_ascii=False)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if genesis_id:
                    # ACTUALIZAR EXISTENTE
                    cursor.execute('''
                        UPDATE genesis_history 
                        SET microcontingency_id = ?, origin_history = ?, functional_history = ?
                        WHERE id = ?
                    ''', (micro_id, origin_json, func_json, genesis_id))
                    msg = "Análisis actualizado."
                else:
                    # CREAR NUEVO
                    # Verificar si ya existe uno para esa microcontingencia (opcional, pero recomendado)
                    cursor.execute("SELECT id FROM genesis_history WHERE microcontingency_id = ?", (micro_id,))
                    exists = cursor.fetchone()
                    if exists:
                        return False, "Ya existe un análisis de génesis para esta Microcontingencia. Edítalo en el historial."

                    cursor.execute('''
                        INSERT INTO genesis_history (patient_id, microcontingency_id, origin_history, functional_history)
                        VALUES (?, ?, ?, ?)
                    ''', (patient_id, micro_id, origin_json, func_json))
                    msg = "Análisis guardado."
                
                conn.commit()
                return True, msg
        except sqlite3.Error as e:
            return False, str(e)

    def delete_genesis(self, genesis_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM genesis_history WHERE id = ?", (genesis_id,))
                conn.commit()
                return True, "Eliminado."
        except sqlite3.Error as e:
            return False, str(e)