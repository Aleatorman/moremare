import csv

def clasificar_rubro(nombre_tecnica):
    nombre = nombre_tecnica.lower()
    
    # 1. Alterar Prácticas Macrocontingenciales
    # Técnicas enfocadas en valores, compasión, resignificación y normatividad.
    macro = ['valor', 'compasión', 'motivacional', 'autodeterminación', 'autonomía', 'improve', 'bondad']
    if any(palabra in nombre for palabra in macro):
        return "Alterar Prácticas Macrocontingenciales"
        
    # 2. Alterar Conducta de Otros
    # Técnicas enfocadas en mediadores, contingencias interpersonales y operantes directas.
    otros = ['reforzamiento', 'extinción', 'moldeamiento', 'encadenamiento', 
             'tiempo fuera', 'costo de respuesta', 'castigo', 'habilidades sociales', 
             'ira', 'role-play', 'ensayo de rol']
    if any(palabra in nombre for palabra in otros):
        return "Alterar Conducta de Otros"
        
    # 3. Alterar Disposiciones
    # Técnicas enfocadas en el ambiente físico o estados de activación biológica.
    disposiciones = ['estímulo', 'abc', 'mapeo', 'desensibilización', 
                     'relajación', 'respiración', 'tipp', 'mindfulness', 
                     'body scan', 'calma']
    if any(palabra in nombre for palabra in disposiciones):
        return "Alterar Disposiciones"
        
    # 4. Alterar Conducta Propia (Por defecto y explícitas)
    # Reestructuración, activación, ERP, solución de problemas, defusión, aceptación...
    return "Alterar Conducta Propia"

# Nombres de los archivos
archivo_original = 'tecnicas.csv'
archivo_actualizado = 'tecnicas_actualizado.csv'

try:
    # Asegúrate de usar encoding utf-8 para preservar los acentos de tu archivo
    with open(archivo_original, mode='r', encoding='utf-8') as infile, \
         open(archivo_actualizado, mode='w', encoding='utf-8', newline='') as outfile:
        
        lector = csv.DictReader(infile)
        
        # Agregamos la nueva columna al final de las ya existentes
        nuevos_campos = lector.fieldnames + ['rubro_funcional']
        escritor = csv.DictWriter(outfile, fieldnames=nuevos_campos)
        
        escritor.writeheader()
        
        for fila in lector:
            # Mandamos el nombre de la técnica a clasificar
            fila['rubro_funcional'] = clasificar_rubro(fila['name'])
            escritor.writerow(fila)
            
    print(f"¡Éxito! Se ha generado el archivo '{archivo_actualizado}' con todos tus datos intactos y la nueva columna.")

except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{archivo_original}'. Asegúrate de ejecutar este script en la misma carpeta.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")