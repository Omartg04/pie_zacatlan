import pandas as pd
import geopandas as gpd
import os

# --- RUTAS DE ARCHIVOS ---
# Ajusta el nombre exacto de tu archivo .shp aquí
PATH_SHP_DIR = "data/raw/secciones_puebla"
# Buscamos automáticamente el primer archivo .shp que encontremos en la carpeta
shp_files = [f for f in os.listdir(PATH_SHP_DIR) if f.endswith('.shp')]

if not shp_files:
    raise FileNotFoundError("❌ No se encontró ningún archivo .shp en data/raw/secciones_puebla/")

PATH_SHP = os.path.join(PATH_SHP_DIR, shp_files[0])
PATH_CSV = "data/raw/muestra_original.csv"

print("--- INICIANDO DIAGNÓSTICO DE DATOS ---")
print(f"📂 Leyendo Shapefile: {shp_files[0]}")
print(f"📂 Leyendo CSV: muestra.csv")

# 1. CARGA DE DATOS
try:
    gdf = gpd.read_file(PATH_SHP)
    df = pd.read_csv(PATH_CSV)
    print("\n✅ Archivos cargados correctamente.")
except Exception as e:
    print(f"\n❌ Error cargando archivos: {e}")
    exit()

# 2. INSPECCIÓN DE COLUMNAS
print("\n--- 1. INSPECCIÓN DE COLUMNAS ---")
print(f"Columnas en Shapefile (Primeras 5): {list(gdf.columns[:5])} ...")
print(f"Columnas en CSV: {list(df.columns)}")

# 3. NORMALIZACIÓN Y BÚSQUEDA DE LA LLAVE 'SECCION'
# Intentamos adivinar la columna de sección en el Shapefile
col_seccion_shp = next((c for c in gdf.columns if 'seccion' in c.lower()), None)

# Si no la encuentra por nombre, suele ser la primera o segunda, pero esperemos que tenga nombre
if not col_seccion_shp:
    print("\n⚠️ ALERTA: No encontré una columna que diga 'seccion' en el Shapefile.")
    print("Por favor revisa los nombres de columnas impresos arriba.")
    col_seccion_shp = input("Escribe el nombre exacto de la columna de SECCIÓN en el Shapefile: ")
else:
    print(f"\nℹ️ Columna detectada en Shapefile para sección: '{col_seccion_shp}'")

col_seccion_csv = 'seccion' # Asumimos este nombre por tu descripción previa

# 4. ANÁLISIS DE TIPOS DE DATOS
print("\n--- 2. VERIFICACIÓN DE TIPOS ---")
val_shp = gdf[col_seccion_shp].iloc[0]
val_csv = df[col_seccion_csv].iloc[0]

print(f"Ejemplo valor Shapefile: '{val_shp}' (Tipo: {type(val_shp)})")
print(f"Ejemplo valor CSV:       '{val_csv}' (Tipo: {type(val_csv)})")

# Estandarizamos ambos a string para comparar
gdf['KEY_SECCION'] = gdf[col_seccion_shp].astype(str).astype(int).astype(str) # Forzamos entero para quitar ceros izq (0052 -> 52)
df['KEY_SECCION'] = df[col_seccion_csv].astype(str).astype(int).astype(str)

# 5. PRUEBA DE CRUCE (MATCH)
print("\n--- 3. PRUEBA DE COBERTURA ---")
secciones_objetivo = df['KEY_SECCION'].unique()
secciones_encontradas = gdf[gdf['KEY_SECCION'].isin(secciones_objetivo)]

num_objetivo = len(secciones_objetivo)
num_encontradas = len(secciones_encontradas)

print(f"Total de secciones únicas en tu CSV (Objetivo): {num_objetivo}")
print(f"Total de secciones encontradas en el Mapa:      {num_encontradas}")

if num_objetivo == num_encontradas:
    print("\n🎉 ¡ÉXITO TOTAL! Todas las secciones del CSV tienen su mapa correspondiente.")
else:
    print(f"\n⚠️ FALTAN DATOS: Hay {num_objetivo - num_encontradas} secciones del CSV que NO aparecen en el mapa.")
    faltantes = set(secciones_objetivo) - set(secciones_encontradas['KEY_SECCION'])
    print(f"IDs de secciones faltantes (primeras 10): {list(faltantes)[:10]}")

# 6. VERIFICACIÓN DE MUNICIPIOS
print("\n--- 4. MUNICIPIOS EN EL CSV ---")
print(df['Nombre_municipio'].unique())

print("\n--- FIN DEL DIAGNÓSTICO ---")