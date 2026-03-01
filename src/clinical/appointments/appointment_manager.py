import sqlite3
from datetime import datetime

class AppointmentManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path

    def add_appointment(self, patient_id, date_str, time_str, note):
        """
        Guarda una cita. 
        date_str: DD/MM/YYYY
        time_str: HH:MM
        """
        try:
            # Convertir a formato ordenable (ISO) YYYY-MM-DD HH:MM
            dt_obj = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
            iso_format = dt_obj.strftime("%Y-%m-%d %H:%M")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO appointments (patient_id, date_time, note) VALUES (?, ?, ?)", 
                               (patient_id, iso_format, note))
                conn.commit()
                return True, "Cita agendada."
        except ValueError:
            return False, "Formato de fecha/hora inválido (Use DD/MM/AAAA y HH:MM)"
        except sqlite3.Error as e:
            return False, str(e)

    def get_upcoming_appointments(self):
        """Obtiene citas futuras ordenadas cronológicamente."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Traemos el nombre del paciente con un JOIN
                # Filtramos para mostrar solo las pendientes o futuras (opcionalmente)
                query = """
                    SELECT a.id, a.date_time, a.note, p.code_name 
                    FROM appointments a
                    JOIN patients p ON a.patient_id = p.id
                    ORDER BY a.date_time ASC
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    # Convertir de vuelta a formato legible
                    dt_obj = datetime.strptime(row['date_time'], "%Y-%m-%d %H:%M")
                    friendly_date = dt_obj.strftime("%d/%m %H:%M")
                    
                    results.append({
                        'id': row['id'],
                        'patient': row['code_name'],
                        'date_display': friendly_date,
                        'note': row['note'],
                        'raw_date': dt_obj # Para lógica interna si se necesita
                    })
                return results
        except sqlite3.Error:
            return []

    def delete_appointment(self, app_id):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM appointments WHERE id = ?", (app_id,))
                conn.commit()
                return True
        except sqlite3.Error:
            return False