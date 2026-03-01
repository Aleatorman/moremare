import sqlite3
import hashlib

class AuthManager:
    def __init__(self, db_path="database/clinical_app.db"):
        self.db_path = db_path
        self.fixed_user = "admin" # El usuario interno siempre será 'admin'

    def _hash(self, text):
        """Encripta texto (para contraseña y respuesta de seguridad)."""
        return hashlib.sha256(text.lower().strip().encode()).hexdigest()

    def is_system_setup(self):
        """Verifica si ya existe el usuario configurado."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE username = ?", (self.fixed_user,))
                return cursor.fetchone() is not None
        except:
            return False

    def setup_first_time(self, password, question, answer):
        """Configura el sistema por primera vez."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                pwd_hash = self._hash(password)
                ans_hash = self._hash(answer) # Encriptamos también la respuesta
                
                cursor.execute("""
                    INSERT INTO users (username, password_hash, security_question, security_answer_hash)
                    VALUES (?, ?, ?, ?)
                """, (self.fixed_user, pwd_hash, question, ans_hash))
                conn.commit()
                return True, "Configuración exitosa"
        except sqlite3.Error as e:
            return False, str(e)

    def login(self, password):
        """Intenta entrar con la contraseña."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                pwd_hash = self._hash(password)
                
                cursor.execute("SELECT id FROM users WHERE username = ? AND password_hash = ?", 
                             (self.fixed_user, pwd_hash))
                user = cursor.fetchone()
                
                if user:
                    return True, user[0]
                return False, "Contraseña incorrecta"
        except sqlite3.Error as e:
            return False, str(e)

    def get_security_question(self):
        """Obtiene la pregunta de seguridad para mostrarla."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT security_question FROM users WHERE username = ?", (self.fixed_user,))
                row = cursor.fetchone()
                return row[0] if row else None
        except: return None

    def reset_password(self, answer, new_password):
        """Resetea la contraseña si la respuesta de seguridad es correcta."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 1. Verificar respuesta
                ans_hash = self._hash(answer)
                cursor.execute("SELECT id FROM users WHERE username = ? AND security_answer_hash = ?", 
                             (self.fixed_user, ans_hash))
                if not cursor.fetchone():
                    return False, "Respuesta de seguridad incorrecta"
                
                # 2. Actualizar contraseña
                new_pwd_hash = self._hash(new_password)
                cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", 
                             (new_pwd_hash, self.fixed_user))
                conn.commit()
                return True, "Contraseña actualizada exitosamente"
        except sqlite3.Error as e:
            return False, str(e)