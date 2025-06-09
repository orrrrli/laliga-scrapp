import pandas as pd

# Function to load and prepare data for merging
def load_and_prepare_data(file_path, team, suffix):
    df = pd.read_csv(file_path)
    # Drop 'Temporada' column if it exists
    if 'Temporada' in df.columns:
        df = df.drop(columns=['Temporada'])
    # Filter by team
    df_team = df[df['Equipo'] == team].copy()
    # Add suffix to columns except 'Equipo'
    df_team = df_team.add_suffix(f"_{suffix}")
    df_team.rename(columns={f'Equipo_{suffix}': 'Equipo'}, inplace=True)
    return df_team

# Function to merge datasets based on local and visitor teams
def merge_team_data(team_local, team_visitor, datasets):
    merged_data = pd.DataFrame()

    # Initialize columns for EquipoLocal and EquipoVisitante
    merged_data['EquipoLocal'] = [team_local]
    merged_data['EquipoVisitante'] = [team_visitor]

    # Load each dataset with appropriate suffix
    for dataset in datasets:
        file_path, local_suffix, visitor_suffix = dataset
        local_data = load_and_prepare_data(file_path, team_local, local_suffix)
        visitor_data = load_and_prepare_data(file_path, team_visitor, visitor_suffix)

        # Drop 'Equipo' column after using it for suffixing to avoid redundancy
        local_data = local_data.drop(columns=['Equipo'])
        visitor_data = visitor_data.drop(columns=['Equipo'])

        # Concatenate local and visitor data side-by-side
        merged_data = pd.concat([merged_data, local_data.reset_index(drop=True), visitor_data.reset_index(drop=True)], axis=1)

    return merged_data

# List of datasets with suffixes for local and visitor teams
datasets = [
    ("C:/UABC/Topicos selectos de la investigacion/MatchesDataSet/current_season_data/estadisticas_defensivas_2024_2025.txt", "defensivas_local", "defensivas_visitante"),
    ("C:/UABC/Topicos selectos de la investigacion/MatchesDataSet/current_season_data/estadisticas_gca_2024_2025.txt", "gca_local", "gca_visitante"),
    ("C:/UABC/Topicos selectos de la investigacion/MatchesDataSet/current_season_data/estadisticas_pases_2024_2025.txt", "pases_local", "pases_visitante"),
    ("C:/UABC/Topicos selectos de la investigacion/MatchesDataSet/current_season_data/estadisticas_porteria_avanzada_2024_2025.txt", "porteria_avanzada_local", "porteria_avanzada_visitante"),
    ("C:/UABC/Topicos selectos de la investigacion/MatchesDataSet/current_season_data/estadisticas_porteros_2024_2025.txt", "porteros_local", "porteros_visitante"),
    ("C:/UABC/Topicos selectos de la investigacion/MatchesDataSet/current_season_data/estadisticas_posesion_2024_2025.txt", "posesion_local", "posesion_visitante"),
    ("C:/UABC/Topicos selectos de la investigacion/MatchesDataSet/current_season_data/estadisticas_salarios_2024_2025.txt", "sueldos_local", "sueldos_visitante"),
    ("C:/UABC/Topicos selectos de la investigacion/MatchesDataSet/current_season_data/estadisticas_tipos_pases_2024_2025.txt", "tipos_pases_local", "tipos_pases_visitante"),
    ("C:/UABC/Topicos selectos de la investigacion/MatchesDataSet/current_season_data/estadisticas_tiros_2024_2025.txt", "tiros_local", "tiros_visitante")
]

# Example usage for merging Barcelona (local) and Osasuna (visitor)
team_local = "Las Palmas"
team_visitor = "Villarreal"
merged_dataset = merge_team_data(team_local, team_visitor, datasets)

# Save the final merged dataset to a CSV file
merged_dataset.to_csv("C:/UABC/Topicos selectos de la investigacion/MatchesDataSet/current_season_data/j24/palmas_villarreal.csv", index=False)