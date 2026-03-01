import sqlite3
import os

# Nombre del archivo de la base de datos
DB_NAME = "database/clinical_app.db"

def create_connection():
    """Crea una conexión a la base de datos SQLite."""
    # Asegurarnos de que la carpeta existe
    if not os.path.exists('database'):
        os.makedirs('database')
        
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except sqlite3.Error as e:
        print(f"Error conectando a la base de datos: {e}")
    return conn

def create_tables(conn):
    """Crea las tablas necesarias si no existen."""
    try:
        cursor = conn.cursor()

        # ---------------------------------------------------------
        # 1. TABLAS DE SISTEMA (Usuarios y Glosario)
        # ---------------------------------------------------------
        
        # Usuarios (Login simple)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            );
        ''')

        # Glosario (Para el sistema de ayuda contextual - Pág. 56 y definiciones)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS glossary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term TEXT NOT NULL UNIQUE,
                definition TEXT NOT NULL,
                source_page TEXT
            );
        ''')

        # Agenda (Híbrida/Opcional)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agenda_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                start_datetime TEXT NOT NULL,
                end_datetime TEXT NOT NULL,
                description TEXT,
                patient_id INTEGER,
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            );
        ''')

        # ---------------------------------------------------------
        # 2. TABLAS CLÍNICAS (El Expediente)
        # ---------------------------------------------------------

        # Pacientes (Módulo 1 - Datos Generales - Pág. 40, 57)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code_name TEXT NOT NULL, -- Nombre o Siglas
                age INTEGER,
                sex TEXT,
                occupation TEXT,
                motive TEXT, -- Motivo de consulta
                goals TEXT, -- Metas del consultante
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')

        # Microcontingencias (Módulo 2 - Encabezado - Pág. 41)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS microcontingencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                morphology_type TEXT, -- "Efectiva" o "Afectiva"
                morphology_metrics TEXT, -- JSON o Texto: Frecuencia, Intensidad, Duración
                problem_desc TEXT, -- Descripción narrativa
                social_context TEXT, -- Circunstancia social
                physical_context TEXT, -- Acontecimientos físicos
                dispositions TEXT, -- Inclinaciones y tendencias
                consequence_type TEXT, -- "Otros", "Sí mismo", "Sin efecto"
                consequence_desc TEXT, -- Descripción del efecto
                non_problematic_desc TEXT, -- Ejercicio no problemático
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            );
        ''')

        # Actores de la Microcontingencia (Módulo 2 - Detalle "Otros" - Pág. 41)
        # Esta tabla permite agregar N personas a una situación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS micro_actors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                microcontingency_id INTEGER NOT NULL,
                name TEXT, -- Ej: "Madre", "Jefe"
                role TEXT, -- Ej: "Auspiciador", "Mediador" (Lista desplegable)
                response TEXT, -- Qué hace exactamente
                FOREIGN KEY (microcontingency_id) REFERENCES microcontingencies (id)
            );
        ''')

        # Macrocontingencias (Módulo 3 - Valores y Prácticas - Pág. 42-43)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS macrocontingencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                category TEXT, -- "Creencia", "Costumbre", "Práctica", "Forma de vida"
                analysis TEXT, -- Conducta Usuario vs Práctica Dominante
                correspondence TEXT, -- "Intra", "Inter", "Ninguna"
                valuative_function TEXT, -- "Sanción", "Facilitación", etc.
                detail TEXT, -- Texto libre
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            );
        ''')

        # Génesis e Historia (Módulo 4 - Pág. 44)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genesis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                origin_history TEXT, -- Historia del inicio del problema
                functional_history TEXT, -- Funcionalidad en otros contextos
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            );
        ''')

        # Planes de Intervención (Módulo 5 - Pág. 45, 60)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS intervention_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                macro_axis TEXT, -- Cambio / Mantenimiento
                micro_axis TEXT, -- Estrategia seleccionada
                therapist_tactics TEXT, -- Detalles de la intervención
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            );
        ''')

        print("--- Tablas creadas exitosamente ---")
        
    except sqlite3.Error as e:
        print(f"Error creando tablas: {e}")

def seed_glossary(conn):
    """Carga los datos iniciales del glosario basados en el PDF (Pág 56 y definiciones)."""
    # Lista de tuplas (Término, Definición, Fuente)
    initial_terms = [
        ("Auspiciador", "Quien propicia o facilita las condiciones para que se presente la conducta considerada problemática, sin participar directamente.", "Pág. 41"),
        ("Regulador de inclinaciones", "Quien modula estados de ánimo y regula disposiciones que afectan indirectamente la presentación de la conducta.", "Pág. 41"),
        ("Mediador de la contingencia", "Quien con su conducta estructura y regula la relación que se está dando, para que los demás se articulen contingencialmente.", "Pág. 41"),
        ("Mediado", "Aquel cuya conducta es regulada por el mediador de la microcontingencia.", "Pág. 42"),
        ("Regulador de la tendencia", "Quien ajusta la tendencia sea porque ha estado presente en situaciones similares en el pasado o tiene dicha capacidad actual.", "Pág. 42"),
        ("Microcontingencia ejemplar", "Interacciones explícitamente valoradas, en las que el otro significativo define la relación contingencial particular.", "Pág. 56"),
        ("Correspondencia intracontingencial", "Aquella que se da entre la conducta y las prácticas sustitutivas o no sustitutivas en un mismo individuo.", "Pág. 56"),
        ("Correspondencia intercontingencial", "Aquella que se presenta entre las prácticas de los individuos, ya sea con respecto a su conducta, sus prácticas sustitutivas o ambas.", "Pág. 56")
    ]
    
    cursor = conn.cursor()
    try:
        for term in initial_terms:
            # INSERT OR IGNORE evita errores si corres el script dos veces
            cursor.execute('''
                INSERT OR IGNORE INTO glossary (term, definition, source_page)
                VALUES (?, ?, ?)
            ''', term)
        conn.commit()
        print("--- Glosario inicial cargado ---")
    except sqlite3.Error as e:
        print(f"Error cargando glosario: {e}")

def main():
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        seed_glossary(conn)
        conn.close()
    else:
        print("No se pudo establecer conexión con la base de datos.")

if __name__ == '__main__':
    main()