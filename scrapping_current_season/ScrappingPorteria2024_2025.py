from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os

# Function to extract goalkeeper data for the current season
def extraer_datos_actual_porteros(driver, url, temporada="2024-2025"):
    driver.get(url)
    time.sleep(5)  # Initial wait to load the page
    
    # Attempt to switch to 'per 90' format
    try:
        boton_por_90 = driver.find_element(By.ID, "stats_squads_keeper_for_per_match_toggle")
        driver.execute_script("arguments[0].click();", boton_por_90)
        print(f"Formato cambiado a 'por 90' para la temporada {temporada}.")
    except Exception as e:
        print(f"No se pudo cambiar al formato 'por 90' para la temporada {temporada}: {e}")
        return []

    # Wait for the table to update to the 'per 90' format
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "td.modified"))
    )
    
    # Retrieve updated HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tabla = soup.find('table', {'id': 'stats_squads_keeper_for'})

    if not tabla:
        print(f"No se encontró la tabla de porteros para la temporada {temporada}")
        return []

    print(f"Tabla de porteros encontrada para la temporada {temporada}, comenzando a extraer datos...")

    # Define expected data structure
    columnas_esperadas = {
        'team': 'Equipo',
        'gk_goals_against': 'GC',
        'gk_shots_on_target_against': 'DaPC',
        'gk_saves': 'Salvadas',
        'gk_wins': 'PG',
        'gk_ties': 'PE',
        'gk_losses': 'PP',
        'gk_clean_sheets': 'PaC',
        'gk_pens_att': 'TPint',
        'gk_pens_allowed': 'PD'
    }

    filas = tabla.find('tbody').find_all('tr') # type: ignore
    estadisticas_temporada = []

    for fila in filas:
        estadisticas = {'Temporada': temporada}

        # Extract team name
        equipo_celda = fila.find('th', {'data-stat': 'team'})
        estadisticas['Equipo'] = equipo_celda.text.strip() if equipo_celda else "N/A"

        # Extract data using `data-stat`
        columnas = fila.find_all('td')
        for columna in columnas:
            data_stat = columna.get('data-stat')
            if data_stat in columnas_esperadas:
                estadisticas[columnas_esperadas[data_stat]] = columna.text.strip()

        # Add row only if the team data is complete
        if estadisticas['Equipo'] != "N/A":
            estadisticas_temporada.append(estadisticas)

    return estadisticas_temporada

# Function to save data in .txt format
def guardar_en_txt_porteros(datos, nombre_archivo):
    # Ensure the folder exists
    os.makedirs(os.path.dirname(nombre_archivo), exist_ok=True)

    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        # Write headers
        archivo.write(','.join([
            'Equipo', 'GC', 'DaPC', 'Salvadas', 'PG', 'PE', 'PP', 'PaC', 'TPint', 'PD', 'Temporada'
        ]) + '\n')

        for estadistica in datos:
            archivo.write(','.join([
                estadistica.get('Equipo', ''),
                estadistica.get('GC', ''),
                estadistica.get('DaPC', ''),
                estadistica.get('Salvadas', ''),
                estadistica.get('PG', ''),
                estadistica.get('PE', ''),
                estadistica.get('PP', ''),
                estadistica.get('PaC', ''),
                estadistica.get('TPint', ''),
                estadistica.get('PD', ''),
                estadistica.get('Temporada', '')
            ]) + '\n')

# URL for the current season's goalkeeper statistics
url_porteros_actual = 'https://fbref.com/es/comps/12/keepers/Estadisticas-de-La-Liga'

# Selenium configuration
driver = webdriver.Chrome()
driver.implicitly_wait(10)

# Extract and save data for the current season
print("Extrayendo datos de porteros para la temporada actual (2024-2025)")
estadisticas_porteros_actual = extraer_datos_actual_porteros(driver, url_porteros_actual, "2024-2025")

# Save data to the specified file within DataSetCurrentSeason
nombre_archivo = "current_season_data/estadisticas_porteros_2024_2025.txt"
guardar_en_txt_porteros(estadisticas_porteros_actual, nombre_archivo)
print(f"Datos de porteros guardados en {nombre_archivo}")

# Close the browser
driver.quit()
