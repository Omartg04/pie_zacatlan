# -*- coding: utf-8 -*-
import pandas as pd
import geopandas as gpd
import numpy as np
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment

def balanced_cluster_optimization(gdf, n_clusters):
    """
    Algoritmo Híbrido Avanzado (Adaptado para Zacatlán):
    Divide las secciones en 'n_clusters' (brigadas) asegurando que todas
    tengan la misma cantidad de secciones (+/- 1).
    """
    
    # Validación básica
    if n_clusters < 1: n_clusters = 1
    if len(gdf) <= n_clusters:
        gdf = gdf.copy()
        gdf['Grupo_ID'] = range(1, len(gdf) + 1)
        return gdf

    # --- MODO EJECUCIÓN (ASIGNACIÓN FIJA) ---
    # Si ya tienes una columna 'Grupo_Fijo' en tu CSV, la respeta.
    if 'Grupo_Fijo' in gdf.columns:
        try:
            gdf = gdf.copy()
            gdf['Grupo_ID'] = gdf['Grupo_Fijo'].fillna(0).astype(int)
            return gdf
        except:
            pass # Si falla, calculamos

    # --- MODO PLANEACIÓN (CÁLCULO MATEMÁTICO) ---
    
    # 1. Proyección temporal a UTM Zona 14N (Metros) para calcular distancias reales
    # Zacatlán está en la zona 14N, igual que Guerrero, así que EPSG:32614 funciona perfecto.
    gdf_utm = gdf.to_crs("EPSG:32614")
    
    # 2. Obtenemos coordenadas X, Y
    coords = np.column_stack((gdf_utm.geometry.centroid.x, gdf_utm.geometry.centroid.y))
    n_points = len(coords)

    # 3. Definir cuántas secciones le tocan a cada brigada
    base_size = n_points // n_clusters
    remainder = n_points % n_clusters
    
    # Crear los "huecos" (slots) disponibles.
    # Ej: Brigada 1, Brigada 1, Brigada 2, Brigada 2...
    cluster_slots = []
    for i in range(n_clusters):
        size = base_size + (1 if i < remainder else 0)
        cluster_slots.extend([i] * size)
    
    # 4. K-MEANS para encontrar los Centros Ideales
    # Primero buscamos dónde están los centros de gravedad geográficos
    kmeans = KMeans(n_clusters=n_clusters, n_init=20, random_state=42)
    kmeans.fit(coords)
    centroids = kmeans.cluster_centers_

    # 5. ASIGNACIÓN LINEAL (La Magia de Balanceo)
    # Calculamos la distancia de TODAS las secciones a TODOS los centroides
    target_coords = centroids[cluster_slots]
    cost_matrix = cdist(coords, target_coords)
    
    # El algoritmo húngaro asigna cada sección al mejor hueco disponible
    # minimizando la distancia total recorrida.
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    # Recuperamos el ID de la brigada original
    assigned_supervisors = [cluster_slots[c] + 1 for c in col_ind]
    final_assignment = pd.Series(data=assigned_supervisors, index=row_ind).sort_index()
    
    # 6. Guardamos el resultado
    gdf_out = gdf.copy()
    gdf_out['Grupo_ID'] = final_assignment.values
    
    return gdf_out