import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN ---
# Rutas a tus archivos 
SHP_SECCIONES = "data/raw/secciones_puebla/SECCION.shp"
SHP_MANZANAS = "data/raw/MANZANAS/MANZANAS.shp"  
CSV_MUESTRA = "data/raw/muestra_original.csv"

print("🚀 Iniciando Procesamiento de Planeación Zacatlán...")

# 1. CARGAR DATOS
print("📂 Cargando archivos...")
gdf_secc = gpd.read_file(SHP_SECCIONES)
gdf_manz = gpd.read_file(SHP_MANZANAS)
df_muestra = pd.read_csv(CSV_MUESTRA)

# Asegurar que las claves sean del mismo tipo (String o Int) para cruzar
# Ajusta 'SECCION' al nombre real de tu columna en el SHP si es diferente
gdf_secc['SECCION'] = gdf_secc['SECCION'].astype(int)
df_muestra['seccion'] = df_muestra['seccion'].astype(int)

# 2. FILTRAR SOLO TUS 19 SECCIONES (El "Recorte")
secciones_objetivo = df_muestra['seccion'].unique()

print(f"🎯 Filtrando {len(secciones_objetivo)} secciones objetivo...")

# Filtramos el mapa de secciones
gdf_secc_target = gdf_secc[gdf_secc['SECCION'].isin(secciones_objetivo)].copy()

# Filtramos el mapa de manzanas (Asumiendo que tiene columna SECCION)
# Si el SHP de manzanas no tiene 'SECCION', habría que hacer un sjoin (spatial join)
if 'SECCION' in gdf_manz.columns:
    gdf_manz['SECCION'] = gdf_manz['SECCION'].astype(int)
    gdf_manz_target = gdf_manz[gdf_manz['SECCION'].isin(secciones_objetivo)].copy()
else:
    print("⚠️ El SHP de Manzanas no tiene columna SECCION. Haciendo cruce espacial (esto tarda un poco)...")
    # Aseguramos proyecciones iguales antes del cruce
    gdf_manz = gdf_manz.to_crs(gdf_secc_target.crs)
    gdf_manz_target = gpd.sjoin(gdf_manz, gdf_secc_target, how="inner", predicate="within")

# 3. PEGAR DATOS DE LA MUESTRA AL MAPA
# Unimos para saber cuántas encuestas tocan en cada sección
gdf_final = gdf_secc_target.merge(df_muestra, left_on='SECCION', right_on='seccion', how='left')

# 4. REPROYECCIÓN A LAT/LON (OBLIGATORIO PARA MAPAS WEB/STREAMLIT)
print("🌍 Convirtiendo a coordenadas GPS (WGS84)...")
gdf_final = gdf_final.to_crs("EPSG:4326")
gdf_manz_target = gdf_manz_target.to_crs("EPSG:4326")

# 5. GUARDAR ARCHIVOS OPTIMIZADOS
print("💾 Guardando archivos listos para la App...")
gdf_final.to_file("zacatlan_secciones_opt.geojson", driver="GeoJSON")
gdf_manz_target.to_file("zacatlan_manzanas_opt.geojson", driver="GeoJSON")

print("✅ ¡LISTO! Ahora tienes dos archivos .geojson ligeros para subir a tu carpeta de proyecto.")