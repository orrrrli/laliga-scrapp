# -*- coding: utf-8 -*-
__author__ = 'Orlando Castaneda Sanchez'

from bs4 import BeautifulSoup
import requests
import re
import unicodedata
import Const
import pandas as pd
import json

# Diccionario para almacenar partidos con un ID único
partidos = dict()
# Diccionario para almacenar equipos de fútbol con su ID y nombre normalizado
equipos = dict()
# Contador de partidos
contador = 0

# Función para normalizar los nombres de los equipos y eliminar los acentos
def normalize_text(text):
    normalized = unicodedata.normalize('NFKD', text)
    return normalized.encode('ASCII', 'ignore').decode('utf-8')

# Función para procesar los equipos y normalizarlos
def find_equipos(str_resultados):
    match = re.findall(r'SE\[\d+\]=\"(\d+)\|(.*?)\";', str_resultados)
    print(f"Equipos encontrados: {len(match)}")
    for mat in match:
        id_equipo = mat[0]
        nombre_equipo = mat[1]
        nombre_normalizado = normalize_text(nombre_equipo)
        equipos[id_equipo] = nombre_normalizado
        print(f"Equipo agregado: {nombre_normalizado}")

# Función para procesar los partidos y extraer solo la información relevante
def find_partidos(str_partidos, temporada, division):
    global contador

    # Encontrar todas las entradas de partidos en el array SP
    partidos_encontrados = re.findall(r'SP\[\d+\]\.push\((\{.*?\})\);', str_partidos)
    print(f"Partidos encontrados: {len(partidos_encontrados)}")

    for partido_json in partidos_encontrados:
        # Convertimos el texto a un diccionario usando json.loads si es JSON válido
        partido = json.loads(partido_json.replace("'", '"'))  # Convierte comillas simples a dobles

        # Extraer la información relevante para cada partido
        equipo_local = equipos.get(partido.get('a1'))
        equipo_visitante = equipos.get(partido.get('a2'))
        goles_local = partido.get('g1')
        goles_visitante = partido.get('g2')

        # Incrementar el contador y almacenar los datos del partido en el formato especificado
        contador += 1
        partidos[contador] = {
            "idPartido": contador,
            "EquipoLocal": equipo_local,
            "EquipoVisitante": equipo_visitante,
            "golesLocal": goles_local,
            "golesVisitante": goles_visitante,
            "Temporada": temporada
        }

# Función principal para obtener los datos de partidos de cada temporada
def get_partidos():
    for temporada in Const.TEMPORADAS:
        print(f"**** PROCESANDO TEMPORADA {temporada} ****")
        
        url_primera = f"https://www.bdfutbol.com/en/t/t{temporada}.html"
        print(f"Procesando la URL: {url_primera}")

        req_primera = requests.get(url_primera)
        
        # Verificar si la solicitud fue exitosa
        if req_primera.status_code != 200:
            print(f"Error al obtener datos para la temporada {temporada}: {req_primera.status_code}")
            continue

        # Parsear la respuesta HTML
        soup_primera = BeautifulSoup(req_primera.text, "html.parser")
        datos_primera = str(soup_primera)

        # Procesar equipos y partidos
        find_equipos(datos_primera)
        find_partidos(datos_primera, temporada, 1)

    return partidos

# Función para exportar los partidos a un archivo .txt separado por comas en el formato deseado
def exportar_partidos_txt():
    # Convertir el diccionario de partidos a un DataFrame
    partidos_df = pd.DataFrame.from_dict(partidos, orient='index')
    # Reordenar columnas según el formato especificado
    partidos_df = partidos_df[["idPartido", "EquipoLocal", "EquipoVisitante", "golesLocal", "golesVisitante", "Temporada"]]
    # Exportar a un archivo .txt con datos separados por comas
    partidos_df.to_csv("DataSetPartidos.txt", index=False, sep=',', header=True)
    print("Exportación a 'DataSetPartidos.txt' completada.")

# Devuelve el valor del contador
def get_contador():
    return contador

# Llamada para realizar el scraping y exportar los datos
get_partidos()
exportar_partidos_txt()
