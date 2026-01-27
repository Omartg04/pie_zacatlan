import geopandas as gpd
import pandas as pd

# --- RUTAS (Ajusta si es necesario) ---
SHP_SECCIONES = "data/raw/secciones_puebla/SECCION.shp"
SHP_MANZANAS = "data/raw/MANZANAS/MANZANAS.shp"
CSV_MUESTRA = "data/raw/muestra_original.csv"

OUT_SECCIONES = "zacatlan_secciones_opt.geojson"
OUT_MANZANAS = "zacatlan_manzanas_opt.geojson"

print("🔧 REPARANDO DATOS ESPACIALES ZACATLÁN...")

# 1. CARGAR DATOS
print("📂 Leyendo archivos originales...")
gdf_sec = gpd.read_file(SHP_SECCIONES)
df_muestra = pd.read_csv(CSV_MUESTRA)

# 2. LIMPIEZA DE SECCIONES
# Detectamos columna de sección
col_sec_mapa = next((c for c in gdf_sec.columns if "SECCION" in c.upper()), "SECCION")
# Convertimos a int para cruzar
gdf_sec['SECCION_INT'] = gdf_sec[col_sec_mapa].astype(int)

# Filtramos solo las 19 secciones de la muestra
secciones_target = df_muestra['seccion'].unique()
gdf_sec_final = gdf_sec[gdf_sec['SECCION_INT'].isin(secciones_target)].copy()

# Reproyectamos
gdf_sec_final = gdf_sec_final.to_crs("EPSG:4326")

# 3. CRUCE SEGURO DE DATOS (Muestra -> Mapa)
# Aquí aseguramos que 'encuestas_totales' pase al mapa
print("📊 Cruzando datos de encuestas...")
df_muestra['seccion'] = df_muestra['seccion'].astype(int)
# Solo nos quedamos con columnas útiles del CSV
cols_csv = ['seccion', 'encuestas_totales', 'lista_nom']
# Merge
gdf_sec_final = gdf_sec_final.merge(df_muestra[cols_csv], left_on='SECCION_INT', right_on='seccion', how='left')

# 4. PROCESAMIENTO DE MANZANAS (Recuperando CVE_MZA)
print("🍎 Procesando Manzanas (Masking)...")
try:
    mascara = gdf_sec_final.unary_union
    gdf_manz = gpd.read_file(SHP_MANZANAS, mask=mascara)
    gdf_manz = gdf_manz.to_crs("EPSG:4326")
    
    # IMPORTANTE: Aseguramos que CVE_MZA exista.
    # A veces se llama CVE_MZA, otras CVEGEO, otras ID.
    cols_m = gdf_manz.columns
    col_id_manzana = 'CVE_MZA' if 'CVE_MZA' in cols_m else cols_m[0] # Fallback al primero si no existe
    
    print(f"ℹ️ Usando '{col_id_manzana}' como ID de manzana.")
    
    # Renombramos para estandarizar
    gdf_manz['MANZANA_ID'] = gdf_manz[col_id_manzana]
    
    # Guardamos solo lo necesario
    gdf_manz_final = gdf_manz[['MANZANA_ID', 'geometry']]

except Exception as e:
    print(f"❌ Error en manzanas: {e}")
    exit()

# 5. GUARDAR
print("💾 Guardando archivos corregidos...")
gdf_sec_final.to_file(OUT_SECCIONES, driver="GeoJSON")
gdf_manz_final.to_file(OUT_MANZANAS, driver="GeoJSON")

print("✅ ¡LISTO! Ejecuta ahora la aplicación.")