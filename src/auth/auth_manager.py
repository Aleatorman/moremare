import sqlite3
import hashlib
import os
import sys
import secrets

class AuthManager:
    def __init__(self, db_path="database/clinical_app.db"):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.getcwd()

        self.db_path = os.path.join(base_path, db_path)
        directorio_bd = os.path.dirname(self.db_path)
        os.makedirs(directorio_bd, exist_ok=True)
        
        self.fixed_user = "admin"

    def _hash_new_password(self, text):
        """Genera un hash seguro con una sal aleatoria."""
        salt = secrets.token_hex(16)
        # 100,000 iteraciones lo hace muy seguro contra fuerza bruta
        hash_obj = hashlib.pbkdf2_hmac('sha256', text.encode(), salt.encode(), 100000)
        # Guardamos la sal junto al hash, separados por un punto
        return f"{salt}.{hash_obj.hex()}"

    def _verify_password(self, text, stored_hash_string):
        """Verifica si el texto coincide con el hash guardado."""
        try:
            salt, stored_hash = stored_hash_string.split('.')
            hash_obj = hashlib.pbkdf2_hmac('sha256', text.encode(), salt.encode(), 100000)
            return hash_obj.hex() == stored_hash
        except ValueError:
            # Compatibilidad con el formato viejo de sha256 puro si ya tenías datos guardados
            legacy_hash = hashlib.sha256(text.lower().strip().encode()).hexdigest()
            return legacy_hash == stored_hash_string

    def is_system_setup(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE username = ?", (self.fixed_user,))
                return cursor.fetchone() is not None
        except:
            return False

    def setup_first_time(self, password, question, answer):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                pwd_hash = self._hash_new_password(password)
                ans_hash = self._hash_new_password(answer.lower().strip()) 
                
                cursor.execute("""
                    INSERT INTO users (username, password_hash, security_question, security_answer_hash)
                    VALUES (?, ?, ?, ?)
                """, (self.fixed_user, pwd_hash, question, ans_hash))
                conn.commit()
                return True, "Configuración exitosa"
        except sqlite3.Error as e:
            return False, str(e)

    def login(self, password):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (self.fixed_user,))
                user = cursor.fetchone()
                
                if user and self._verify_password(password, user[1]):
                    return True, user[0]
                return False, "Contraseña incorrecta"
        except sqlite3.Error as e:
            return False, str(e)

    def get_security_question(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT security_question FROM users WHERE username = ?", (self.fixed_user,))
                row = cursor.fetchone()
                return row[0] if row else None
        except: return None

    def reset_password(self, answer, new_password):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, security_answer_hash FROM users WHERE username = ?", (self.fixed_user,))
                user = cursor.fetchone()
                
                if not user or not self._verify_password(answer.lower().strip(), user[1]):
                    return False, "Respuesta de seguridad incorrecta"
                
                new_pwd_hash = self._hash_new_password(new_password)
                cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", 
                             (new_pwd_hash, self.fixed_user))
                conn.commit()
                return True, "Contraseña actualizada exitosamente"
        except sqlite3.Error as e:
            return False, str(e)