from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Función para extraer solo las columnas específicas de la tabla de Creación de goles y tiros
def extraer_datos_gca_seleccionados(driver, url, temporada):
    driver.get(url)
    time.sleep(5)  # Espera inicial para cargar la página
    
    # Intentar cambiar a formato por 90 minutos
    try:
        boton_por_90 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "stats_squads_gca_for_per_match_toggle"))
        )
        driver.execute_script("arguments[0].click();", boton_por_90)
        print(f"Formato cambiado a 'por 90' para la temporada {temporada}.")
    except Exception as e:
        print(f"No se pudo cambiar al formato 'por 90' para la temporada {temporada}: {e}")
        return []

    # Esperar a que la tabla se actualice con el formato 'por 90'
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table#stats_squads_gca_for tbody tr"))
        )
    except Exception as e:
        print(f"No se pudo localizar la tabla de estadísticas para la temporada {temporada}: {e}")
        return []
    
    # Obtener el HTML actualizado
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tabla = soup.find('table', {'id': 'stats_squads_gca_for'})

    if not tabla:
        print(f"No se encontró la tabla de Creación de goles y tiros para la temporada {temporada}.")
        return []

    print(f"Tabla de Creación de goles y tiros encontrada para la temporada {temporada}, comenzando a extraer datos...")

    # Definir las columnas necesarias con los encabezados especificados
    columnas_abreviadas = {
        'team': 'Equipo',
        'sca': 'ACT',
        'sca_passes_live': 'PassLive_SCA',
        'sca_passes_dead': 'PassDead_SCA',
        'sca_take_ons': 'HASTA_SCA',
        'sca_shots': 'Dis_SCA',
        'sca_fouled': 'FR_SCA',
        'sca_defense': 'Def_SCA',
        'gca': 'ACG',
        'gca_passes_live': 'PassLive_GCA',
        'gca_passes_dead': 'PassDead_GCA',
        'gca_take_ons': 'HASTA_GCA',
        'gca_shots': 'Dis_GCA',
        'gca_fouled': 'FR_GCA',
        'gca_defense': 'Def_GCA'
    }

    # Extraer todas las filas
    filas = tabla.find('tbody').find_all('tr')  # type: ignore
    estadisticas_temporada = []

    for fila in filas:
        estadisticas = {'Temporada': temporada}

        # Extraer solo las columnas especificadas
        for stat, abreviacion in columnas_abreviadas.items():
            celda = fila.find(['th', 'td'], {'data-stat': stat})
            estadisticas[abreviacion] = celda.text.strip() if celda else "N/A"

        # Agregar solo las filas con datos completos
        if estadisticas.get('Equipo', 'N/A') != "N/A":
            estadisticas_temporada.append(estadisticas)

    return estadisticas_temporada

# Función para guardar los datos en un archivo .txt
def guardar_en_txt_gca(datos, nombre_archivo):
    if not datos:
        print("No hay datos para guardar.")
        return

    # Definir el orden de los encabezados solicitados
    headers = [
        'Equipo', 'ACT', 'PassLive_SCA', 'PassDead_SCA', 'HASTA_SCA', 'Dis_SCA', 'FR_SCA', 'Def_SCA',
        'ACG', 'PassLive_GCA', 'PassDead_GCA', 'HASTA_GCA', 'Dis_GCA', 'FR_GCA', 'Def_GCA', 'Temporada'
    ]

    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        # Escribir encabezados
        archivo.write(','.join(headers) + '\n')

        # Escribir cada fila de datos en el orden especificado
        for estadistica in datos:
            fila = []
            for header in headers:
                # Agregar cada columna en el orden correcto
                fila.append(estadistica.get(header, 'N/A'))
            archivo.write(','.join(fila) + '\n')

# URL base para las temporadas de estadísticas de Creación de goles y tiros
url_base_gca = 'https://fbref.com/es/comps/12/{anio}-{anio_siguiente}/gca/Estadisticas-{anio}-{anio_siguiente}-La-Liga'

# Configuración de Selenium
driver = webdriver.Chrome()
driver.implicitly_wait(10)

# Lista para almacenar todas las estadísticas de Creación de goles y tiros
estadisticas_gca_totales = []

# Iteramos sobre los años de la temporada desde 2017-2018 hasta 2023-2024
for anio in range(2017, 2024):
    anio_siguiente = anio + 1
    temporada = f"{anio}-{anio_siguiente}"
    url_temporada = url_base_gca.format(anio=anio, anio_siguiente=anio_siguiente)

    print(f"Extrayendo datos de Creación de goles y tiros de la temporada: {temporada}")
    
    # Extraemos los datos de la temporada actual
    estadisticas_temporada_gca = extraer_datos_gca_seleccionados(driver, url_temporada, temporada)
    
    # Añadimos las estadísticas de esta temporada a la lista total
    estadisticas_gca_totales.extend(estadisticas_temporada_gca)

# Guardamos todos los datos en un solo archivo
guardar_en_txt_gca(estadisticas_gca_totales, "estadisticas_gca_2017_2024.txt")
print("Datos de Creación de goles y tiros de todas las temporadas guardados en estadisticas_gca_2017_2024.txt")

# Cerramos el navegador
driver.quit()
