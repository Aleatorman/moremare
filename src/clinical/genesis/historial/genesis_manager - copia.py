import sqlite3
import json

class GenesisManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def get_genesis_data(self, patient_id):
        """Recupera la historia y desempaqueta el JSON."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM genesis_history WHERE patient_id = ?", (patient_id,))
                row = cursor.fetchone()
                
                if row:
                    # Convertimos la fila a diccionario
                    data = dict(row)
                    # Desempaquetamos los textos JSON a diccionarios reales
                    try: data['origin_history'] = json.loads(data['origin_history'])
                    except: data['origin_history'] = {}
                    
                    try: data['functional_history'] = json.loads(data['functional_history'])
                    except: data['functional_history'] = {}
                    
                    return data
                return None
        except sqlite3.Error as e:
            print(f"Error recuperando génesis: {e}")
            return None

    def save_genesis(self, patient_id, origin_data, func_data):
        """Guarda o actualiza la historia."""
        # 1. Convertir diccionarios a Texto JSON
        origin_json = json.dumps(origin_data, ensure_ascii=False)
        func_json = json.dumps(func_data, ensure_ascii=False)

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificamos si ya existe registro para este paciente
                cursor.execute("SELECT id FROM genesis_history WHERE patient_id = ?", (patient_id,))
                exists = cursor.fetchone()

                if exists:
                    # ACTUALIZAR
                    cursor.execute('''
                        UPDATE genesis_history 
                        SET origin_history = ?, functional_history = ?
                        WHERE patient_id = ?
                    ''', (origin_json, func_json, patient_id))
                else:
                    # CREAR NUEVO
                    cursor.execute('''
                        INSERT INTO genesis_history (patient_id, origin_history, functional_history)
                        VALUES (?, ?, ?)
                    ''', (patient_id, origin_json, func_json))
                
                conn.commit()
                return True, "Historia guardada correctamente."
        except sqlite3.Error as e:
            return False, str(e)