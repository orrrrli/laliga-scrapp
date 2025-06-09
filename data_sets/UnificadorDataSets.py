import pandas as pd

# Cargar los archivos de datos
df_partidos = pd.read_csv("DataSetPartidos.txt")
df_estadisticas_defensivas = pd.read_csv("estadisticas_defensivas_2017_2024.txt")
df_estadisticas_gca = pd.read_csv("estadisticas_gca_2017_2024.txt")
df_estadisticas_pases = pd.read_csv("estadisticas_pases_2017_2024.txt")
df_estadisticas_porteria_avanzada = pd.read_csv("estadisticas_porteria_avanzada_2017_2024.txt")
df_estadisticas_porteros = pd.read_csv("estadisticas_porteros_2017_2024.txt")
df_estadisticas_posesion = pd.read_csv("estadisticas_posesion_2017_2024.txt")
df_estadisticas_sueldos = pd.read_csv("estadisticas_sueldos_equipos.txt")
df_estadisticas_tipos_pases = pd.read_csv("estadisticas_tipos_pases_2017_2024.txt")
df_estadisticas_tiros = pd.read_csv("estadisticas_tiros_2017_2024.txt")

# Asegurar que las temporadas tengan un formato consistente
df_partidos['Temporada'] = df_partidos['Temporada'].str.replace("2017-18", "2017-2018")

# Realizar merge de todos los datasets, primero para el equipo local, luego para el visitante
datasets = [
    (df_estadisticas_defensivas, 'defensivas'),
    (df_estadisticas_gca, 'gca'),
    (df_estadisticas_pases, 'pases'),
    (df_estadisticas_porteria_avanzada, 'porteria_avanzada'),
    (df_estadisticas_porteros, 'porteros'),
    (df_estadisticas_posesion, 'posesion'),
    (df_estadisticas_sueldos, 'sueldos'),
    (df_estadisticas_tipos_pases, 'tipos_pases'),
    (df_estadisticas_tiros, 'tiros')
]

merged_df = df_partidos.copy()

for dataset, name in datasets:
    # Ajustar nombres de columna para que coincidan en los merges
    dataset['Temporada'] = dataset['Temporada'].str.replace("2017-18", "2017-2018")
    
    # Merge para el equipo local
    merged_df = merged_df.merge(
        dataset.add_suffix(f'_{name}_local'),
        how="left",
        left_on=["EquipoLocal", "Temporada"],
        right_on=[f"Equipo_{name}_local", f"Temporada_{name}_local"]
    ).drop(columns=[f"Equipo_{name}_local", f"Temporada_{name}_local"])
    
    # Merge para el equipo visitante
    merged_df = merged_df.merge(
        dataset.add_suffix(f'_{name}_visitante'),
        how="left",
        left_on=["EquipoVisitante", "Temporada"],
        right_on=[f"Equipo_{name}_visitante", f"Temporada_{name}_visitante"]
    ).drop(columns=[f"Equipo_{name}_visitante", f"Temporada_{name}_visitante"])

# Guardar el resultado en un archivo .txt separado por comas
output_path = 'merged_all_statistics.txt'
merged_df.to_csv(output_path, index=False, sep=",")

print(f"Archivo guardado en {output_path}")
