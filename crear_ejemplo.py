import sqlite3
import os

DB_PATH = "database/clinical_app.db"

def sembrar_paciente_ejemplo():
    if not os.path.exists(DB_PATH):
        print("❌ No se encontró la base de datos. Ejecuta primero setup_db.py")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Crear el Paciente
        cursor.execute('''
            INSERT INTO patients (code_name, age, sex, occupation, motive, goals, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ("PACIENTE-DEMO-01", 28, "Hombre", "Ingeniero de Software", 
              "Ansiedad intensa al presentar proyectos ante supervisores y evitación de reuniones sociales.", 
              "Lograr exponer mis ideas sin bloqueos y dejar de cancelar salidas con amigos.", "Activo"))
        
        patient_id = cursor.lastrowid

        # 2. Macrocontingencia (Grupos de referencia) 
        cursor.execute('''
            INSERT INTO macrocontingencies (patient_id, group_type, group_name, beliefs_values, customs_lifestyles, intra_analysis, inter_analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, "Laboral", "Equipo de Desarrollo", 
              "Valor absoluto en la perfección técnica; error es igual a incompetencia.", 
              "Jornadas extendidas, poca interacción personal.", 
              "El usuario acepta la creencia de perfección como propia.", 
              "El grupo sanciona el error con críticas pasivas, reforzando la evitación."))

        # 3. Génesis (Historia) 
        cursor.execute('''
            INSERT INTO genesis_history (patient_id, origin_history, functional_history)
            VALUES (?, ?, ?)
        ''', (patient_id, 
              "Padre altamente crítico en el ámbito académico durante la infancia.", 
              "La conducta de evitación es reforzada por el alivio inmediato de la ansiedad (Reforzamiento Negativo)."))

        # 4. Intervención (Metas vs Objetivos) 
        cursor.execute('''
            INSERT INTO intervention_plans (patient_id, microcontingency_id, therapeutic_objectives, strategy_morphology, techniques_text)
            VALUES (?, ?, ?, ?, ?)
        ''', (patient_id, 1, 
              "Entrenar habilidades de exposición gradual y reestructuración de creencias de perfección.", 
              "Modificar la respuesta de huida por una de permanencia con respiración diafragmática.", 
              "Reestructuración Cognitiva, Exposición Gradual, Respiración Diafragmática"))

        # 5. Evaluación (Matriz de parámetros) 
        cursor.execute("INSERT INTO evaluations (patient_id, notes) VALUES (?, ?)", 
                       (patient_id, "El paciente logró permanecer en la reunión aunque con niveles medios de ansiedad."))
        eval_id = cursor.lastrowid

        matrix_data = [
            ("Exposición", "Adquisición", "8", "7"),
            ("Exposición", "Precisión", "7", "6"),
            ("Exposición", "Oportunidad", "9", "8"),
            ("Habilidades", "Tendencia", "6", "7")
        ]
        cursor.executemany('''
            INSERT INTO evaluation_matrix (evaluation_id, target, parameter, terapia_val, terapeuta_val)
            VALUES (?, ?, ?, ?, ?)
        ''', [(eval_id, t, p, v1, v2) for t, p, v1, v2 in matrix_data])

        conn.commit()
        print("✅ Paciente de ejemplo 'PACIENTE-DEMO-01' creado con éxito.")
        print("Ahora puedes abrir el programa y ver cómo se ve el protocolo completo.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    sembrar_paciente_ejemplo()