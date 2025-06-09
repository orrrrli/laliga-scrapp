from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os

# List of desired columns updated
columnas_deseadas = [
    ("team", "Equipo"),
    ("touches", "Toques"),
    ("touches_def_pen_area", "Def. pen."),
    ("touches_def_3rd", "3.º def."),
    ("touches_mid_3rd", "3.º cent."),
    ("touches_att_3rd", "3.º ataq."),
    ("touches_att_pen_area", "Ataq. pen."),
    ("take_ons", "Att"),
    ("take_ons_won", "Succ"),
    ("take_ons_tackled", "Tkld"),
    ("carries", "Transportes"),
    ("carries_distance", "Dist. tot."),
    ("carries_progressive_distance", "Dist. prg."),
    ("progressive_carries", "PrgC"),
    ("carries_into_final_third", "1/3"),
    ("carries_into_penalty_area", "TAP"),
    ("miscontrols", "Errores de control"),
    ("dispossessed", "Des"),
    ("passes_received", "Rec"),
    ("progressive_passes_received", "PrgR")
]
headers = [nombre for _, nombre in columnas_deseadas] + ["Temporada"]

# Function to extract possession data from the current season's page
def extraer_datos_posesion(driver, url, temporada="2024-2025"):
    driver.get(url)
    time.sleep(5)  # Initial wait to load the page

    # Switch to 'per 90' format
    try:
        boton_por_90 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "stats_squads_possession_for_per_match_toggle"))
        )
        driver.execute_script("arguments[0].click();", boton_por_90)
        print(f"Formato cambiado a 'por 90' para la temporada {temporada}.")
    except Exception as e:
        print(f"No se pudo cambiar al formato 'por 90' para la temporada {temporada}: {e}")
        return []

    # Wait for the table to update
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table#stats_squads_possession_for tbody tr"))
        )
    except Exception as e:
        print(f"No se pudo localizar la tabla de estadísticas para la temporada {temporada}: {e}")
        return []

    # Get updated HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tabla = soup.find('table', {'id': 'stats_squads_possession_for'})

    if not tabla:
        print(f"No se encontró la tabla de Posesión de Balón para la temporada {temporada}.")
        return []

    print(f"Tabla de Posesión de Balón encontrada para la temporada {temporada}, comenzando a extraer datos...")

    # Extract each row of data
    filas = tabla.find('tbody').find_all('tr') # type: ignore
    estadisticas_temporada = []

    for fila in filas:
        estadisticas = {"Temporada": temporada}
        
        # Extract each desired column
        for data_stat, nombre_columna in columnas_deseadas:
            celda = fila.find("td", {"data-stat": data_stat}) or fila.find("th", {"data-stat": data_stat})
            estadisticas[nombre_columna] = celda.text.strip() if celda else "N/A"

        # Verify that the row contains team data
        if estadisticas.get("Equipo", "N/A") != "N/A":
            estadisticas_temporada.append(estadisticas)

    return estadisticas_temporada

# Function to save data in .txt format
def guardar_en_txt(datos, nombre_archivo):
    if not datos:
        print("No hay datos para guardar.")
        return

    # Ensure the folder exists
    os.makedirs(os.path.dirname(nombre_archivo), exist_ok=True)

    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        # Write headers
        archivo.write(','.join(headers) + '\n')

        # Write each row of data
        for estadistica in datos:
            fila = [estadistica.get(header, 'N/A') for header in headers]
            archivo.write(','.join(fila) + '\n')

# URL for the current season's possession statistics
url_posesion_actual = 'https://fbref.com/es/comps/12/possession/Estadisticas-de-La-Liga'

# Selenium configuration
driver = webdriver.Chrome()
driver.implicitly_wait(10)

# Extract and save data for the current season
print("Extrayendo datos de Posesión de Balón de la temporada actual (2024-2025)")
estadisticas_posesion_actual = extraer_datos_posesion(driver, url_posesion_actual, "2024-2025")

# Save data to the specified file in DataSetCurrentSeason
nombre_archivo = "current_season_data/estadisticas_posesion_2024_2025.txt"
guardar_en_txt(estadisticas_posesion_actual, nombre_archivo)
print(f"Datos de Posesión de Balón guardados en {nombre_archivo}")

# Close the browser
driver.quit()
