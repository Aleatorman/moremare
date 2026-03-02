import sqlite3
import csv
import os

DB_PATH = "database/clinical_app.db"
CSV_PATH = "tecnicas.csv" 

def importar_tecnicas():
    if not os.path.exists(DB_PATH):
        print("❌ No se encuentra la base de datos en", DB_PATH)
        return
    
    if not os.path.exists(CSV_PATH):
        print(f"❌ No se encuentra el archivo: {CSV_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Averiguar qué formato tiene tu archivo antes de procesarlo
        codificacion = 'utf-8-sig'
        try:
            with open(CSV_PATH, mode='r', encoding='utf-8-sig') as test_f:
                test_f.read()
        except UnicodeDecodeError:
            codificacion = 'latin-1' # Si falla, usamos el formato clásico de Excel Windows

        # 2. Abrir el archivo con el formato correcto y respetando los "Enters" (newline='')
        with open(CSV_PATH, mode='r', encoding=codificacion, newline='') as file:
            
            # Detectar si Excel usó comas o puntos y comas
            primera_linea = file.readline()
            delimitador = ';' if ';' in primera_linea else ','
            file.seek(0)
            
            reader = csv.DictReader(file, delimiter=delimitador)
            
            # Limpiar los títulos de las columnas
            if reader.fieldnames:
                reader.fieldnames = [str(col).strip().upper() for col in reader.fieldnames]
            
            count = 0
            for row in reader:
                name = row.get('NAME')
                if not name: 
                    continue # Saltar filas en blanco
                
                category = row.get('CATEGORY', '')
                objective = row.get('OBJECTIVE', '')
                method = row.get('METHOD', '')
                pros = row.get('PROS', '')
                cons = row.get('CONS', '')

                # Verificar duplicados e insertar
                cursor.execute("SELECT id FROM library_techniques WHERE name = ?", (name,))
                if not cursor.fetchone():
                    cursor.execute('''
                        INSERT INTO library_techniques (category, name, objective, method, pros, cons)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (category, name, objective, method, pros, cons))
                    count += 1
        
        conn.commit()
        print(f"✅ ¡Éxito! Se han importado {count} técnicas a tu biblioteca.")
        print("Ya puedes abrir tu programa y revisar la pestaña de Biblioteca de Técnicas.")
        
    except Exception as e:
        print(f"❌ Error durante la importación: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    importar_tecnicas()