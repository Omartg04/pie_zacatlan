import geopandas as gpd
import os

# Usaremos el de Zacatlan como ejemplo (que es el más crítico)
archivo = "data/processed/manzanas_optimizadas/manzanas_acapulco_opt.shp"

print(f"🔬 Inspeccionando: {archivo}")

if os.path.exists(archivo):
    gdf = gpd.read_file(archivo)
    
    print(f"\n📋 Columnas disponibles: {list(gdf.columns)}")
    
    if 'CVEGEO' in gdf.columns:
        print("\n🔍 MUESTRA DE CLAVES (Primeras 5 filas):")
        print(gdf['CVEGEO'].head(5))
        
        # Verificación de tipo de dato
        tipo_dato = gdf['CVEGEO'].dtype
        print(f"\nℹ️ Tipo de dato: {tipo_dato}")
        
        # Simulación de extracción
        ejemplo = gdf['CVEGEO'].iloc[0]
        # INEGI Estándar: Los últimos 3 dígitos son la manzana
        manzana_id = str(ejemplo)[-3:] 
        
        print("\n--- PRUEBA DE LÓGICA ---")
        print(f"Clave Completa (Shape): '{ejemplo}'")
        print(f"Manzana extraída (-3):  '{manzana_id}'")
        
        if len(manzana_id) == 3 and manzana_id.isdigit():
            print("✅ La lógica de tomar los últimos 3 dígitos funcionará.")
        else:
            print("⚠️ CUIDADO: La extracción no parece devolver 3 dígitos numéricos.")
            
    else:
        print("❌ NO se encontró la columna 'CVEGEO'. Revisa los nombres impresos arriba.")
else:
    print("❌ El archivo no existe. Verifica la ruta.")
