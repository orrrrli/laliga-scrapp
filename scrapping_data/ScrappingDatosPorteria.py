from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Función para extraer datos de la tabla de porteros para una temporada dada
def extraer_datos_temporada_porteros(driver, url, temporada):
    driver.get(url)
    time.sleep(5)  # Espera inicial para cargar la página
    
    # Intentar cambiar a formato por 90 minutos
    try:
        boton_por_90 = driver.find_element(By.ID, "stats_squads_keeper_for_per_match_toggle")
        driver.execute_script("arguments[0].click();", boton_por_90)
        print(f"Formato cambiado a 'por 90' para la temporada {temporada}.")
    except Exception as e:
        print(f"No se pudo cambiar al formato 'por 90' para la temporada {temporada}: {e}")
        return []

    # Esperar a que la tabla se actualice con el formato 'por 90'
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "td.modified"))
    )
    
    # Obtener el HTML actualizado
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tabla = soup.find('table', {'id': 'stats_squads_keeper_for'})

    if not tabla:
        print(f"No se encontró la tabla de porteros para la temporada {temporada}")
        return []

    print(f"Tabla de porteros encontrada para la temporada {temporada}, comenzando a extraer datos...")

    # Estructura de los datos esperados
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

        # Extraer el nombre del equipo
        equipo_celda = fila.find('th', {'data-stat': 'team'})
        estadisticas['Equipo'] = equipo_celda.text.strip() if equipo_celda else "N/A"

        # Extraer los datos con `data-stat`
        columnas = fila.find_all('td')
        for columna in columnas:
            data_stat = columna.get('data-stat')
            if data_stat in columnas_esperadas:
                estadisticas[columnas_esperadas[data_stat]] = columna.text.strip()

        # Agregar solo las filas con datos completos
        if estadisticas['Equipo'] != "N/A":
            estadisticas_temporada.append(estadisticas)

    return estadisticas_temporada

# Función para guardar los datos en un archivo .txt
def guardar_en_txt_porteros(datos, nombre_archivo):
    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        # Escribir encabezados
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

# URL base para las temporadas de estadísticas avanzadas de porteros
url_base_porteros = 'https://fbref.com/es/comps/12/{anio}-{anio_siguiente}/keepers/Estadisticas-{anio}-{anio_siguiente}-La-Liga'

# Configuración de Selenium
driver = webdriver.Chrome()
driver.implicitly_wait(10)

# Lista para almacenar todas las estadísticas de porteros
estadisticas_porteros_totales = []

# Iteramos sobre los años de la temporada desde 2017-2018 hasta 2023-2024
for anio in range(2017, 2024):
    anio_siguiente = anio + 1
    temporada = f"{anio}-{anio_siguiente}"
    url_temporada = url_base_porteros.format(anio=anio, anio_siguiente=anio_siguiente)

    print(f"Extrayendo datos de porteros de la temporada: {temporada}")
    
    # Extraemos los datos de la temporada actual
    estadisticas_temporada_porteros = extraer_datos_temporada_porteros(driver, url_temporada, temporada)
    
    # Añadimos las estadísticas de esta temporada a la lista total
    estadisticas_porteros_totales.extend(estadisticas_temporada_porteros)

# Guardamos todos los datos en un solo archivo
guardar_en_txt_porteros(estadisticas_porteros_totales, "estadisticas_porteros_2017_2024.txt")
print("Datos de porteros de todas las temporadas guardados en estadisticas_porteros_2017_2024.txt")

# Cerramos el navegador
driver.quit()
