from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os

# Define the desired columns without 'PL' or '90 s'
columnas_deseadas = [
    ("team", "Equipo"),
    ("tackles", "Derribos Tkl"), ("tackles_won", "Derribos TklG"),
    ("tackles_def_3rd", "Derribos 3.º def."), ("tackles_mid_3rd", "Derribos 3.º cent."),
    ("tackles_att_3rd", "Derribos 3.º ataq."),
    ("challenge_tackles", "Desafíos Tkl"), ("challenges", "Desafíos Att"),
    ("challenge_tackles_pct", "Desafíos Tkl%"), ("challenges_lost", "Desafíos Pérdida"),
    ("blocks", "Bloqueos"), ("blocked_shots", "Bloqueos Dis"), ("blocked_passes", "Bloqueos Pases"),
    ("interceptions", "Intercepciones"), ("tackles_interceptions", "Tkl+Int"),
    ("clearances", "Desp."), ("errors", "Err")
]
headers = [nombre for _, nombre in columnas_deseadas] + ["Temporada"]

# Function to extract specific defensive action data
def extraer_datos_actual_defensivos(driver, url, temporada="2024-2025"):
    driver.get(url)
    time.sleep(5)  # Initial wait to load the page

    # Attempt to switch to 'per 90' format
    try:
        boton_por_90 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "stats_squads_defense_for_per_match_toggle"))
        )
        driver.execute_script("arguments[0].click();", boton_por_90)
        print(f"Formato cambiado a 'por 90' para la temporada {temporada}.")
    except Exception as e:
        print(f"No se pudo cambiar al formato 'por 90' para la temporada {temporada}: {e}")
        return []

    # Wait for the table to update
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table#stats_squads_defense_for tbody tr"))
        )
    except Exception as e:
        print(f"No se pudo localizar la tabla de estadísticas para la temporada {temporada}: {e}")
        return []

    # Retrieve updated HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tabla = soup.find('table', {'id': 'stats_squads_defense_for'})

    if not tabla:
        print(f"No se encontró la tabla de Acciones defensivas para la temporada {temporada}.")
        return []

    print(f"Tabla de Acciones defensivas encontrada para la temporada {temporada}, comenzando a extraer datos...")

    # Extract data from each row
    filas = tabla.find('tbody').find_all('tr')  # type: ignore
    estadisticas_temporada = []

    for fila in filas:
        estadisticas = {"Temporada": temporada}
        
        # Extract each column according to the desired order
        for data_stat, nombre_columna in columnas_deseadas:
            celda = fila.find("td", {"data-stat": data_stat}) or fila.find("th", {"data-stat": data_stat})
            estadisticas[nombre_columna] = celda.text.strip() if celda else "N/A"

        # Verify if team data exists in the row
        if estadisticas.get("Equipo", "N/A") != "N/A":
            estadisticas_temporada.append(estadisticas)

    return estadisticas_temporada

# Function to save data in .txt format
def guardar_en_txt_defensivos(datos, nombre_archivo):
    if not datos:
        print("No hay datos para guardar.")
        return

    # Ensure the folder exists
    os.makedirs(os.path.dirname(nombre_archivo), exist_ok=True)

    # Use specified headers for correct format
    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        # Write headers
        archivo.write(','.join(headers) + '\n')

        # Write each row of data in the specified order
        for estadistica in datos:
            archivo.write(','.join(estadistica.get(header, 'N/A') for header in headers) + '\n')

# URL for the current season's defensive action statistics
url_defensiva_actual = 'https://fbref.com/es/comps/12/defense/Estadisticas-de-La-Liga'

# Selenium configuration
driver = webdriver.Chrome()
driver.implicitly_wait(10)

# Extract and save data for the current season
print("Extrayendo datos de Acciones defensivas para la temporada actual (2024-2025)")
estadisticas_defensivas_actual = extraer_datos_actual_defensivos(driver, url_defensiva_actual, "2024-2025")

# Save data to the specified file in DataSetCurrentSeason
nombre_archivo = "current_season_data/estadisticas_defensivas_2024_2025.txt"
guardar_en_txt_defensivos(estadisticas_defensivas_actual, nombre_archivo)
print(f"Datos de Acciones defensivas guardados en {nombre_archivo}")

# Close the browser
driver.quit()
