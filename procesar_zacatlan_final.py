import geopandas as gpd
import pandas as pd
import os

# --- RUTAS DE TUS ARCHIVOS ---
SHP_SECCIONES = "data/raw/secciones_puebla/SECCION.shp"
SHP_MANZANAS = "data/raw/MANZANAS/MANZANAS.shp"
CSV_MUESTRA = "data/raw/muestra_original.csv"

# --- RUTAS DE SALIDA ---
OUT_SECCIONES = "zacatlan_secciones_opt.geojson"
OUT_MANZANAS = "zacatlan_manzanas_opt.geojson"

print("🚀 INICIANDO RECORTE QUIRÚRGICO DE ZACATLÁN (VERSIÓN 2)...")

# 1. CARGAR MUESTRA Y SECCIONES
print("📂 Cargando secciones y muestra...")
df_muestra = pd.read_csv(CSV_MUESTRA)
gdf_secciones = gpd.read_file(SHP_SECCIONES)

# --- CORRECCIÓN DEL ERROR DE GEOMETRÍA ---
# Buscamos cuál es la columna de geometría real (geometry, GEOMETRY, shape, etc.)
try:
    # Intentamos obtener la geometría activa. Si falla, la buscamos manualmente.
    _ = gdf_secciones.geometry.name
except AttributeError:
    # Si falla, buscamos columnas tipo geometría
    geo_cols = gdf_secciones.select_dtypes(include=['geometry']).columns
    if len(geo_cols) > 0:
        print(f"🔧 Geometría detectada en columna: {geo_cols[0]}. Activando...")
        gdf_secciones = gdf_secciones.set_geometry(geo_cols[0])
    else:
        # Fallback: a veces se carga como objeto pero se llama GEOMETRY
        if 'GEOMETRY' in gdf_secciones.columns:
            gdf_secciones = gdf_secciones.set_geometry('GEOMETRY')
        else:
            raise ValueError("❌ No se encontró columna de geometría en el Shapefile de Secciones.")

# --- BÚSQUEDA INTELIGENTE DE LA COLUMNA 'SECCION' ---
# No forzamos mayúsculas a todo para no romper nada más.
# Buscamos la columna que se parezca a "SECCION"
cols_disponibles = gdf_secciones.columns
col_seccion_shp = next((c for c in cols_disponibles if "SECCION" in c.upper()), None)

if not col_seccion_shp:
    raise ValueError(f"❌ No encontré la columna SECCION. Columnas disponibles: {cols_disponibles}")

print(f"ℹ️ Usando columna de sección del mapa: '{col_seccion_shp}'")

# Estandarizamos CSV a minúsculas para facilitar
df_muestra.columns = [c.lower() for c in df_muestra.columns]

# 2. FILTRADO
secciones_target = df_muestra['seccion'].unique()
print(f"🎯 Objetivo: {len(secciones_target)} secciones.")

# Filtrar usando la columna detectada
gdf_secc_final = gdf_secciones[gdf_secciones[col_seccion_shp].astype(int).isin(secciones_target)].copy()

# Reproyectar a WGS84 (Lat/Lon)
if gdf_secc_final.crs != "EPSG:4326":
    print("🌍 Reproyectando Secciones a WGS84...")
    gdf_secc_final = gdf_secc_final.to_crs("EPSG:4326")

print("✅ Mapa de Secciones listo.")

# 3. MASKING DE MANZANAS
print("🍎 Cargando Manzanas (esto puede tardar unos segundos)...")

mascara = gdf_secc_final.unary_union

try:
    gdf_manz_final = gpd.read_file(SHP_MANZANAS, mask=mascara)
    
    # Arreglo de geometría para Manzanas (igual que arriba, por si acaso)
    try:
        _ = gdf_manz_final.geometry.name
    except AttributeError:
        geo_cols_m = gdf_manz_final.select_dtypes(include=['geometry']).columns
        if len(geo_cols_m) > 0:
            gdf_manz_final = gdf_manz_final.set_geometry(geo_cols_m[0])
        elif 'GEOMETRY' in gdf_manz_final.columns:
            gdf_manz_final = gdf_manz_final.set_geometry('GEOMETRY')

    if gdf_manz_final.crs != "EPSG:4326":
        gdf_manz_final = gdf_manz_final.to_crs("EPSG:4326")
        
    print(f"✅ ¡Éxito! Se cargaron {len(gdf_manz_final)} manzanas.")

except Exception as e:
    print(f"❌ Error al cargar manzanas: {e}")
    exit()

# 4. VINCULACIÓN (SPATIAL JOIN)
print("🔗 Vinculando Manzanas a Secciones...")

# Nos aseguramos de quedarnos solo con lo necesario
gdf_manz_con_datos = gpd.sjoin(
    gdf_manz_final, 
    gdf_secc_final[[col_seccion_shp, 'geometry']], 
    how="inner", 
    predicate="intersects"
)

# Renombrar columna de sección para que sea estándar en el output
gdf_manz_con_datos = gdf_manz_con_datos.rename(columns={col_seccion_shp: 'SECCION'})
gdf_secc_final = gdf_secc_final.rename(columns={col_seccion_shp: 'SECCION'})

# 5. GUARDAR
print("💾 Guardando GeoJSONs...")
gdf_secc_final.to_file(OUT_SECCIONES, driver="GeoJSON")
gdf_manz_con_datos[['SECCION', 'geometry']].to_file(OUT_MANZANAS, driver="GeoJSON") # Solo guardamos lo útil

print(f"""
🎉 PROCESO COMPLETADO
---------------------
Archivos generados:
1. {OUT_SECCIONES}
2. {OUT_MANZANAS}
""")