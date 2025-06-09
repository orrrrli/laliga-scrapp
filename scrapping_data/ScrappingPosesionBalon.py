from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Lista de columnas deseadas actualizada
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

# Función para extraer datos específicos de la tabla de Posesión de Balón
def extraer_datos_posesion(driver, url, temporada):
    driver.get(url)
    time.sleep(5)  # Espera inicial para cargar la página

    # Cambiar a formato 'por 90'
    try:
        boton_por_90 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "stats_squads_possession_for_per_match_toggle"))
        )
        driver.execute_script("arguments[0].click();", boton_por_90)
        print(f"Formato cambiado a 'por 90' para la temporada {temporada}.")
    except Exception as e:
        print(f"No se pudo cambiar al formato 'por 90' para la temporada {temporada}: {e}")
        return []

    # Esperar a que la tabla se actualice
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table#stats_squads_possession_for tbody tr"))
        )
    except Exception as e:
        print(f"No se pudo localizar la tabla de estadísticas para la temporada {temporada}: {e}")
        return []

    # Obtener el HTML actualizado
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tabla = soup.find('table', {'id': 'stats_squads_possession_for'})

    if not tabla:
        print(f"No se encontró la tabla de Posesión de Balón para la temporada {temporada}.")
        return []

    print(f"Tabla de Posesión de Balón encontrada para la temporada {temporada}, comenzando a extraer datos...")

    # Extraer datos de cada fila
    filas = tabla.find('tbody').find_all('tr') # type: ignore
    estadisticas_temporada = []

    for fila in filas:
        estadisticas = {"Temporada": temporada}
        
        # Extraer cada columna de acuerdo al orden deseado
        for data_stat, nombre_columna in columnas_deseadas:
            celda = fila.find("td", {"data-stat": data_stat}) or fila.find("th", {"data-stat": data_stat})
            estadisticas[nombre_columna] = celda.text.strip() if celda else "N/A"

        # Verificar si hay datos del equipo en la fila
        if estadisticas.get("Equipo", "N/A") != "N/A":
            estadisticas_temporada.append(estadisticas)

    return estadisticas_temporada

# Función para guardar datos en formato .txt
def guardar_en_txt_posesion(datos, nombre_archivo):
    if not datos:
        print("No hay datos para guardar.")
        return

    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        # Escribir encabezados
        archivo.write(','.join(headers) + '\n')

        # Escribir cada fila de datos en el orden especificado
        for estadistica in datos:
            fila = [estadistica.get(header, 'N/A') for header in headers]
            archivo.write(','.join(fila) + '\n')

# URL base para las temporadas de estadísticas de Posesión de Balón
url_base_posesion = 'https://fbref.com/es/comps/12/{anio}-{anio_siguiente}/possession/Estadisticas-{anio}-{anio_siguiente}-La-Liga'

# Configuración de Selenium
driver = webdriver.Chrome()
driver.implicitly_wait(10)

# Lista para almacenar todas las estadísticas de Posesión de Balón
estadisticas_posesion_totales = []

# Iteramos sobre los años de la temporada desde 2017-2018 hasta 2023-2024
for anio in range(2017, 2024):
    anio_siguiente = anio + 1
    temporada = f"{anio}-{anio_siguiente}"
    url_temporada = url_base_posesion.format(anio=anio, anio_siguiente=anio_siguiente)

    print(f"Extrayendo datos de Posesión de Balón de la temporada: {temporada}")
    
    # Extraemos los datos de la temporada actual
    estadisticas_temporada_posesion = extraer_datos_posesion(driver, url_temporada, temporada)
    
    # Añadimos las estadísticas de esta temporada a la lista total
    estadisticas_posesion_totales.extend(estadisticas_temporada_posesion)

# Guardamos todos los datos en un solo archivo
guardar_en_txt_posesion(estadisticas_posesion_totales, "estadisticas_posesion_2017_2024.txt")
print("Datos de Posesión de Balón de todas las temporadas guardados en estadisticas_posesion_2017_2024.txt")

# Cerramos el navegador
driver.quit()
