import requests
from bs4 import BeautifulSoup
import unicodedata
import re
import os

# Function to normalize text and remove accents
def normalize_text(text):
    normalized = unicodedata.normalize('NFKD', text)
    return normalized.encode('ASCII', 'ignore').decode('utf-8')

# Function to extract only the numerical salary amount
def extraer_salario_dolares(texto_salario):
    match = re.search(r'\$([\d,]+)', texto_salario)
    if match:
        # Remove commas and convert to integer
        return int(match.group(1).replace(',', ''))
    return None

# Function to get salaries for the current season
def obtener_salarios_actuales():
    url = "https://fbref.com/es/comps/12/wages/La-Liga-Salarios"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error al obtener datos para la temporada actual: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'squad_wages'})

    sueldos_temporada = []

    if table:
        tbody = table.find('tbody')
        for row in tbody.find_all('tr'): # type: ignore
            cols = row.find_all('td')
            if len(cols) > 0:
                equipo = normalize_text(cols[0].text.strip())
                jugadores = cols[1].text.strip()
                salario_semanal = extraer_salario_dolares(cols[2].text.strip())
                salario_anual = extraer_salario_dolares(cols[3].text.strip())

                # Add row data to list
                sueldos_temporada.append({
                    'Equipo': equipo,
                    'Jugadores': jugadores,
                    'Salario Semanal': salario_semanal,
                    'Salario Anual': salario_anual,
                    'Temporada': "2024-2025"
                })

    return sueldos_temporada

# Get salaries for the current season
print("Procesando salarios para la temporada actual (2024-2025)...")
dataset_sueldos = obtener_salarios_actuales()

# Function to save data to a .txt file
def guardar_en_txt(datos, nombre_archivo):
    # Ensure the folder exists
    os.makedirs(os.path.dirname(nombre_archivo), exist_ok=True)

    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        # Write header
        archivo.write("Equipo,Jugadores,Salario Semanal,Salario Anual,Temporada\n")
        # Write data
        for sueldo in datos:
            archivo.write(f"{sueldo['Equipo']},{sueldo['Jugadores']},{sueldo['Salario Semanal']},{sueldo['Salario Anual']},{sueldo['Temporada']}\n")
    print(f"Datos guardados en {nombre_archivo}")

# Save the data in the specified file within DataSetCurrentSeason
nombre_archivo = "current_season_data/estadisticas_salarios_2024_2025.txt"
guardar_en_txt(dataset_sueldos, nombre_archivo)
