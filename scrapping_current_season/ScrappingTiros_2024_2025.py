from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os

# Function to extract specific columns from the shooting table with abbreviations
def extraer_datos_actual_tiros_seleccionados(driver, url, temporada="2024-2025"):
    driver.get(url)
    time.sleep(5)  # Initial wait to load the page
    
    # Attempt to switch to 'per 90' format
    try:
        boton_por_90 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "stats_squads_shooting_for_per_match_toggle"))
        )
        driver.execute_script("arguments[0].click();", boton_por_90)
        print(f"Formato cambiado a 'por 90' para la temporada {temporada}.")
    except Exception as e:
        print(f"No se pudo cambiar al formato 'por 90' para la temporada {temporada}: {e}")
        return []

    # Wait for the table to update
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table#stats_squads_shooting_for tbody tr"))
        )
    except Exception as e:
        print(f"No se pudo localizar la tabla de estadísticas para la temporada {temporada}: {e}")
        return []
    
    # Retrieve updated HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tabla = soup.find('table', {'id': 'stats_squads_shooting_for'})

    if not tabla:
        print(f"No se encontró la tabla de tiros para la temporada {temporada}.")
        return []

    print(f"Tabla de tiros encontrada para la temporada {temporada}, comenzando a extraer datos...")

    # Define only the necessary columns with abbreviations
    columnas_abreviadas = {
        'team': 'Equipo',
        'goals': 'Gls.',
        'shots': 'Dis',
        'shots_on_target': 'DaP',
        'shots_free_kicks': 'FK',
        'pens_made': 'TP',
        'pens_att': 'TPint',
        'xg': 'xG',
        'npxg': 'npxG',
    }

    filas = tabla.find('tbody').find_all('tr') # type: ignore
    estadisticas_temporada = []

    for fila in filas:
        estadisticas = {'Temporada': temporada}

        # Extract only the specified columns
        for stat, abreviacion in columnas_abreviadas.items():
            celda = fila.find(['th', 'td'], {'data-stat': stat})
            estadisticas[abreviacion] = celda.text.strip() if celda else "N/A"

        # Add rows with complete data
        if estadisticas.get('Equipo', 'N/A') != "N/A":
            estadisticas_temporada.append(estadisticas)

    return estadisticas_temporada

# Function to save data in .txt format
def guardar_en_txt_tiros(datos, nombre_archivo):
    if not datos:
        print("No hay datos para guardar.")
        return

    # Ensure the folder exists
    os.makedirs(os.path.dirname(nombre_archivo), exist_ok=True)

    # Define headers with abbreviations
    headers = [
        'Equipo', 'Gls.', 'Dis', 'DaP', 'FK', 'TP', 'TPint', 'xG', 'npxG', 'Temporada'
    ]

    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        # Write headers
        archivo.write(','.join(headers) + '\n')

        # Write each row of data in the specified order
        for estadistica in datos:
            archivo.write(','.join(estadistica.get(header, '') for header in headers) + '\n')

# URL for the current season's shooting statistics
url_tiros_actual = 'https://fbref.com/es/comps/12/shooting/Estadisticas-de-La-Liga'

# Selenium configuration
driver = webdriver.Chrome()
driver.implicitly_wait(10)

# Extract and save data for the current season
print("Extrayendo datos de tiros para la temporada actual (2024-2025)")
estadisticas_tiros_actual = extraer_datos_actual_tiros_seleccionados(driver, url_tiros_actual, "2024-2025")

# Save data to the specified file in DataSetCurrentSeason
nombre_archivo = "current_season_data/estadisticas_tiros_2024_2025.txt"
guardar_en_txt_tiros(estadisticas_tiros_actual, nombre_archivo)
print(f"Datos de tiros guardados en {nombre_archivo}")

# Close the browser
driver.quit()
