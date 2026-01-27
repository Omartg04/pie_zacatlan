import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Search, Fullscreen
import geopandas as gpd
import pandas as pd
import numpy as np
import io
import re
import random
from src.logic import balanced_cluster_optimization

# Configuración de página
st.set_page_config(page_title="Logística Zacatlán", layout="wide")

COLORS = ['#E74C3C', '#8E44AD', '#3498DB', '#1ABC9C', '#F1C40F', '#E67E22', '#34495E', '#95A5A6']

# ==============================================================================
# FUNCION MAESTRA: LIMPIEZA DE COORDENADAS
# ==============================================================================
def limpiar_y_convertir_universal(coord):
    if pd.isna(coord): return 0
    if isinstance(coord, (int, float)): return float(coord)
    s = str(coord).upper().strip()
    signo = -1 if 'W' in s or 'S' in s or s.startswith('-') else 1
    numeros = re.findall(r"(\d+(?:\.\d+)?)", s)
    try:
        if len(numeros) >= 3:
            return (float(numeros[0]) + (float(numeros[1]) / 60) + (float(numeros[2]) / 3600)) * signo
        elif len(numeros) >= 1:
            return float(numeros[0]) * signo
    except: return 0
    return 0

# ==============================================================================
# 1. CARGA DE DATOS (AHORA GENERA df_pines SEPARADO)
# ==============================================================================
@st.cache_data
def cargar_datos_zacatlan():
    secc_path = "zacatlan_secciones_opt.geojson"
    manz_path = "zacatlan_manzanas_opt.geojson" 
    csv_path  = "data/raw/muestra_original.csv"
    loc_coords_path = "data/raw/catalogo_localidades.csv" 
    shp_raw_path = "data/raw/secciones_puebla/SECCION.shp" 
    
    # 1. CARGA GEOGRÁFICA
    gdf_s = gpd.read_file(secc_path)
    col_mapa = next((c for c in gdf_s.columns if 'seccion' in c.lower()), None)
    if not col_mapa: st.stop()
    
    gdf_clean = gdf_s[[col_mapa, 'geometry']].copy()
    gdf_clean = gdf_clean.rename(columns={col_mapa: 'seccion'})
    gdf_clean['seccion'] = gdf_clean['seccion'].astype(int)
    gdf_clean = gdf_clean.loc[:, ~gdf_clean.columns.duplicated()]

    gdf_m = gpd.read_file(manz_path)
    gdf_m = gdf_m.loc[:, ~gdf_m.columns.duplicated()]

    # 2. PROCESAMIENTO CSV MUESTRA
    df_csv = pd.read_csv(csv_path)
    df_csv.columns = [c.lower().strip() for c in df_csv.columns]
    
    col_enc = next((c for c in df_csv.columns if 'encuestas_totales' in c), 'encuestas_totales')
    col_mza = next((c for c in df_csv.columns if 'manzanas_meta' in c), None)
    col_sec = next((c for c in df_csv.columns if 'seccion' in c), 'seccion')
    col_loc = next((c for c in df_csv.columns if 'localidad' in c or 'nom_loc' in c), None)

    if not col_mza: df_csv['manzanas_meta'] = 1; col_mza = 'manzanas_meta'
    if not col_loc: df_csv['nom_localidad'] = "Sin Dato"; col_loc = 'nom_localidad'

    df_csv[col_enc] = pd.to_numeric(df_csv[col_enc], errors='coerce').fillna(0)
    df_csv[col_mza] = pd.to_numeric(df_csv[col_mza], errors='coerce').fillna(0)
    df_csv[col_loc] = df_csv[col_loc].fillna("").astype(str)

    # -------------------------------------------------------------------------
    # NUEVO: PREPARAR EL DATAFRAME DE PINES (ANTES DE AGRUPAR)
    # -------------------------------------------------------------------------
    # Copiamos el CSV original para tener el detalle por localidad
    df_pines = df_csv[[col_sec, col_loc, col_enc]].copy()
    df_pines.columns = ['seccion', 'Localidad', 'Encuestas']
    df_pines['KEY_LOC'] = df_pines['Localidad'].astype(str).str.upper().str.strip()

    # -------------------------------------------------------------------------
    # PROCESAMIENTO CATÁLOGO Y CRUCE DE PINES
    # -------------------------------------------------------------------------
    try:
        try: df_coords = pd.read_csv(loc_coords_path, encoding='utf-8')
        except: df_coords = pd.read_csv(loc_coords_path, encoding='latin-1')
        
        df_coords.columns = [c.lower().strip() for c in df_coords.columns]
        c_lat = next((c for c in df_coords.columns if 'lat' in c), None)
        c_lon = next((c for c in df_coords.columns if 'lon' in c), None)
        c_nom = next((c for c in df_coords.columns if 'nom' in c or 'loc' in c), None)
        
        if c_lat and c_lon and c_nom:
            df_coords['CAT_LAT'] = df_coords[c_lat].apply(limpiar_y_convertir_universal)
            df_coords['CAT_LON'] = df_coords[c_lon].apply(limpiar_y_convertir_universal)
            df_coords['KEY_LOC'] = df_coords[c_nom].astype(str).str.upper().str.strip()
            
            df_coords_clean = df_coords[(df_coords['CAT_LAT'] != 0) & (df_coords['CAT_LON'] != 0)].copy()
            df_coords_clean = df_coords_clean[['KEY_LOC', 'CAT_LAT', 'CAT_LON']].drop_duplicates(subset=['KEY_LOC'])
            
            # Cruzamos los PINES individuales con el catálogo
            df_pines = df_pines.merge(df_coords_clean, on='KEY_LOC', how='left')
        
    except Exception as e:
        print(f"Error coords: {e}")

    # -------------------------------------------------------------------------
    # AGRUPAMIENTO (PARA EL MAPA DE POLIGONOS)
    # -------------------------------------------------------------------------
    # Concatenamos nombres para el tooltip del polígono
    agg_rules = {
        col_enc: 'sum',
        col_mza: 'sum',
        col_loc: lambda x: ', '.join(sorted(set(x.unique())))
    }
    df_agrupado = df_csv.groupby(col_sec).agg(agg_rules).reset_index()
    df_agrupado.columns = ['seccion', 'Meta', 'Manzanas_Obj', 'Localidad_Full']

    # Unión Final
    gdf_final = gdf_clean.merge(df_agrupado, on='seccion', how='left')
    gdf_final['Meta'] = gdf_final['Meta'].fillna(0).astype(int)
    gdf_final['Manzanas_Obj'] = gdf_final['Manzanas_Obj'].fillna(0).astype(int)

    # 4. CONTEXTO
    try:
        gdf_raw = gpd.read_file(shp_raw_path)
        col_mun = next((c for c in gdf_raw.columns if 'MUN' in c.upper()), None)
        if col_mun:
            mask = gdf_raw[col_mun].astype(str).str.upper().str.contains("ZACATLAN") | (gdf_raw[col_mun] == 208)
            gdf_contexto = gdf_raw[mask].copy()
        else:
            gdf_contexto = gpd.GeoDataFrame()
        
        if not gdf_contexto.empty:
            gdf_contexto = gdf_contexto.to_crs("EPSG:4326")
            ids_muestra = gdf_final['seccion'].unique()
            col_sec_raw = next((c for c in gdf_contexto.columns if 'SECC' in c.upper()), None)
            if col_sec_raw:
                gdf_contexto = gdf_contexto[~gdf_contexto[col_sec_raw].astype(int).isin(ids_muestra)]
            gdf_contexto = gdf_contexto[[col_sec_raw, 'geometry']]
    except:
        gdf_contexto = gpd.GeoDataFrame()

    return gdf_final, gdf_m, gdf_contexto, df_pines # <--- RETORNAMOS LOS PINES APARTE

try:
    gdf_secciones, gdf_manzanas, gdf_contexto, df_pines_raw = cargar_datos_zacatlan()
except Exception as e:
    st.error(f"⚠️ Error cargando datos: {e}")
    st.stop()

# ==============================================================================
# UI
# ==============================================================================
st.title("🗺️ Planeación Logística: Zacatlán")
with st.expander("ℹ️ Ficha Técnica", expanded=False):
    st.markdown("**Metodología:** Muestreo Aleatorio Estratificado | **Confianza:** 95% | **Error:** +/- 5%")
st.divider()

with st.sidebar:
    st.header("⚙️ Configuración")
    total_personal = st.number_input("Encuestadores:", min_value=1, value=30)
    n_rutas = st.slider("Brigadas/Rutas:", 1, 8, 4)
    
    with st.spinner(f"Optimizando..."):
        gdf_view = balanced_cluster_optimization(gdf_secciones.copy(), n_rutas)
        gdf_view = gdf_view.loc[:, ~gdf_view.columns.duplicated()]
    
    st.success("✅ Rutas Listas")
    st.divider()
    
    grupos_disp = sorted(gdf_view['Grupo_ID'].unique())
    filtro_grupo = st.selectbox("🔍 Filtrar:", ["Todas"] + list(grupos_disp))
    
    # FILTRADO DE CAPAS
    if filtro_grupo != "Todas":
        gdf_view = gdf_view[gdf_view['Grupo_ID'] == filtro_grupo]
        
        # Filtramos manzanas
        gdf_manzanas_view = gpd.sjoin(gdf_manzanas, gdf_view[['geometry']], how='inner', predicate='intersects')
        gdf_manzanas_view = gdf_manzanas_view.loc[:, ~gdf_manzanas_view.columns.duplicated()]
        
        # FILTRAMOS PINES (Solo los de las secciones visibles)
        secciones_visibles = gdf_view['seccion'].unique()
        df_pines_view = df_pines_raw[df_pines_raw['seccion'].isin(secciones_visibles)]
        
        zoom_start = 14
        stroke_weight = 3
    else:
        gdf_manzanas_view = gdf_manzanas
        df_pines_view = df_pines_raw # Todos los pines
        zoom_start = 12
        stroke_weight = 1

k1, k2, k3, k4 = st.columns(4)
total_meta = gdf_secciones['Meta'].sum()
with k1: st.metric("🎯 Meta Encuestas", f"{total_meta}")
with k2: st.metric("🍎 Manzanas Obj.", f"{gdf_secciones['Manzanas_Obj'].sum()}")
with k3: st.metric("📍 Secciones", f"{len(gdf_secciones)}")
with k4: st.metric("🏃 Carga x Persona", f"{total_meta / total_personal:.1f}")
st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# MAPA VISUAL
# ==============================================================================
if not gdf_contexto.empty and filtro_grupo == "Todas":
    lat = gdf_contexto.geometry.centroid.y.mean()
    lon = gdf_contexto.geometry.centroid.x.mean()
else:
    lat = gdf_view.geometry.centroid.y.mean()
    lon = gdf_view.geometry.centroid.x.mean()

m = folium.Map([lat, lon], zoom_start=zoom_start, tiles="CartoDB positron")

# 1. CONTEXTO
if not gdf_contexto.empty:
    gdf_contexto_simple = gdf_contexto.simplify(tolerance=0.0001)
    folium.GeoJson(
        gdf_contexto_simple,
        name="Contexto",
        style_function=lambda x: {'fillColor':'#F0F0F0', 'color':'#aaaaaa', 'weight':0.8, 'fillOpacity':0.3},
        tooltip="Fuera de Muestra"
    ).add_to(m)

# 2. RUTAS (POLIGONOS)
def get_style(feature):
    gid = feature['properties']['Grupo_ID']
    return {'fillColor': COLORS[(gid - 1) % len(COLORS)], 'color': 'black', 'weight': stroke_weight, 'fillOpacity': 0.6}

folium.GeoJson(
    gdf_view,
    name="Secciones",
    style_function=get_style,
    tooltip=folium.GeoJsonTooltip(fields=['seccion', 'Localidad_Full', 'Grupo_ID', 'Meta'], localize=True),
    popup=folium.GeoJsonPopup(fields=['seccion'])
).add_to(m)

# 3. PINES MULTIPLES POR SECCION (CORREGIDO PARA EVITAR LOOP)
for idx, row in df_pines_view.iterrows():
    loc_name = row['Localidad']
    sec_id = row['seccion']
    
    # ¿Tenemos coordenada real del catálogo?
    if 'CAT_LAT' in row and pd.notnull(row['CAT_LAT']) and row['CAT_LAT'] != 0:
        c_lat = row['CAT_LAT']
        c_lon = row['CAT_LON']
        icon_color = 'green'
        source = "📍 Exacta"
        
        folium.Marker(
            location=[c_lat, c_lon],
            tooltip=f"<b>{loc_name}</b><br>Sección {sec_id}<br>{source}",
            icon=folium.Icon(color=icon_color, icon='pushpin', prefix='glyphicon')
        ).add_to(m)
        
    else:
        # SI NO HAY COORDENADA EXACTA EN CATALOGO:
        geom = gdf_view[gdf_view['seccion'] == sec_id]
        if not geom.empty:
            c_lat = geom.geometry.centroid.y.values[0]
            base_lon = geom.geometry.centroid.x.values[0]
            
            # --- FIX DEL LOOP INFINITO ---
            # Usamos el ID de la sección como "semilla" para el random.
            # Esto garantiza que el "offset" sea siempre el mismo para esta sección.
            random.seed(int(sec_id) + idx) # Sumamos idx para que si hay 2 pines en la misma sección, no caigan encima
            
            offset_lat = random.uniform(-0.0015, 0.0015)
            offset_lon = random.uniform(-0.0015, 0.0015)
            
            final_lat = c_lat + offset_lat
            final_lon = base_lon + offset_lon
            
            folium.Marker(
                location=[final_lat, final_lon],
                tooltip=f"<b>{loc_name}</b><br>Sección {sec_id}<br>📐 Estimada",
                icon=folium.Icon(color='red', icon='info-sign', prefix='glyphicon')
            ).add_to(m)
# 4. MANZANAS
ver_manz = st.sidebar.checkbox("Mostrar Traza Urbana", value=(filtro_grupo != "Todas"))
if ver_manz and not gdf_manzanas_view.empty:
    folium.GeoJson(
        gdf_manzanas_view, name="Manzanas",
        style_function=lambda x: {'fillColor':'transparent', 'color':'#444', 'weight':0.5, 'dashArray':'2,2'},
        tooltip="Manzana"
    ).add_to(m)

Fullscreen().add_to(m)
folium.LayerControl().add_to(m)
st_folium(m, height=600, use_container_width=True)

# TABLA FINAL
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("📋 Detalle por Localidad")
    # Mostramos el detalle fino
    # Unimos con el grupo asignado para que se vea la ruta
    df_detalle = df_pines_view.merge(gdf_view[['seccion', 'Grupo_ID']], on='seccion', how='left')
    df_detalle = df_detalle[['Grupo_ID', 'seccion', 'Localidad', 'Encuestas']].sort_values(['Grupo_ID', 'seccion'])
    st.dataframe(df_detalle, use_container_width=True, hide_index=True)

with col2:
    st.info("📤 Exportar")
    csv = df_detalle.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Descargar CSV", csv, "plan_detallado.csv", "text/csv", type="primary", use_container_width=True)
    map_html = io.BytesIO()
    m.save(map_html, close_file=False)
    st.download_button("🌍 Descargar Mapa HTML", map_html.getvalue(), "mapa_zacatlan.html", "text/html", use_container_width=True)