import shutil
import os
from datetime import datetime

class BackupManager:
    def __init__(self, db_path="database/clinical_app.db", backup_dir="backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        
        # Crear carpeta de respaldos si no existe
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def create_backup(self):
        """Crea una copia de seguridad con fecha y hora."""
        if not os.path.exists(self.db_path):
            return False, "No se encontró la base de datos."

        try:
            # Generar nombre único: backup_2023-10-25_14-30-05.db
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_filename = f"backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)

            # Copiar archivo
            shutil.copy2(self.db_path, backup_path)
            
            return True, f"Respaldo creado: {backup_filename}"
        except Exception as e:
            return False, str(e)

    def get_last_backup_info(self):
        """Devuelve la fecha del último respaldo."""
        try:
            files = [os.path.join(self.backup_dir, f) for f in os.listdir(self.backup_dir) if f.endswith(".db")]
            if not files:
                return "Nunca"
            latest_file = max(files, key=os.path.getctime)
            timestamp = os.path.getctime(latest_file)
            return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")
        except:
            return "Error leyendo"