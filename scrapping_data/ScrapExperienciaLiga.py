import requests
from bs4 import BeautifulSoup
import re
import unicodedata

# Lista de temporadas que queremos analizar
TEMPORADAS = ["2010-11", "2011-12", "2012-13", "2013-14", "2014-15", "2015-16", 
              "2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24"]  

# Diccionario para guardar la participación de los equipos
equipos_participacion = {}

# Función para normalizar los nombres de los equipos
def normalize_text(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')

# Función para extraer equipos de una temporada
def find_equipos(str_resultados, temporada):
    equipos_encontrados = re.findall(r'SE\[\d+\]=\"(\d+)\|(.*?)\";', str_resultados)
    for equipo in equipos_encontrados:
        nombre_normalizado = normalize_text(equipo[1])

        # Registrar la participación del equipo en la temporada actual
        if nombre_normalizado not in equipos_participacion:
            equipos_participacion[nombre_normalizado] = []
        equipos_participacion[nombre_normalizado].append(temporada)

# Scraping de los equipos por temporada
def get_equipos_por_temporada():
    for temporada in TEMPORADAS:
        print(f"****  PROCESANDO TEMPORADA {temporada} ****")
        url = f"https://www.bdfutbol.com/en/t/t{temporada}.html"
        
        req = requests.get(url)
        if req.status_code != 200:
            print(f"Error al obtener datos para la temporada {temporada}: {req.status_code}")
            continue
        
        soup = BeautifulSoup(req.text, "html.parser")
        datos_temporada = str(soup)
        
        # Obtener los equipos de esa temporada
        find_equipos(datos_temporada, temporada)

# Función para calcular la experiencia de los equipos
def calcular_experiencia_equipos():
    total_temporadas = len(TEMPORADAS)
    experiencia_equipos = {}

    for equipo, temporadas_jugadas in equipos_participacion.items():
        temporadas_jugadas_count = len(temporadas_jugadas)
        puntaje_experiencia = temporadas_jugadas_count / total_temporadas
        experiencia_equipos[equipo] = puntaje_experiencia

    return experiencia_equipos

# Función para escribir la información en un archivo .txt
def escribir_experiencia_en_txt(experiencia_equipos, nombre_archivo):
    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        archivo.write("Equipo, Puntaje de experiencia\n")
        for equipo, puntaje in experiencia_equipos.items():
            archivo.write(f"{equipo}, {puntaje:.2f}\n")
    print(f"Información guardada en el archivo {nombre_archivo}")

# Obtener la participación de los equipos en cada temporada
get_equipos_por_temporada()

# Calcular la experiencia de los equipos
experiencia_equipos = calcular_experiencia_equipos()

# Guardar la experiencia de los equipos en un archivo de texto
escribir_experiencia_en_txt(experiencia_equipos, "experiencia_equipos.txt")
