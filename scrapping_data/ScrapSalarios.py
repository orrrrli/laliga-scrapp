import requests
from bs4 import BeautifulSoup
import unicodedata
import re

# Función para normalizar el texto y eliminar acentos
def normalize_text(text):
    normalized = unicodedata.normalize('NFKD', text)
    return normalized.encode('ASCII', 'ignore').decode('utf-8')

# Función para extraer el salario en dólares usando expresiones regulares
def extraer_salario_dolares(texto_salario):
    match = re.search(r'\$[\d,]+', texto_salario)
    if match:
        return match.group(0)
    return None

# Función para obtener los salarios de una temporada específica
def obtener_salarios_temporada(temporada):
    url = f"https://fbref.com/es/comps/12/{temporada}/wages/{temporada}-La-Liga-Salarios"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error al obtener datos para la temporada {temporada}: {response.status_code}")
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

                # Añadir los datos de esta fila a la lista de sueldos
                sueldos_temporada.append({
                    'Equipo': equipo,
                    'Jugadores': jugadores,
                    'Salario Semanal': salario_semanal,
                    'Salario Anual': salario_anual,
                    'Temporada': temporada
                })

    return sueldos_temporada

# Temporadas desde 2013-2014 hasta 2023-2024
temporadas = [f"{year}-{year+1}" for year in range(2017, 2024)]

# Lista para almacenar los datos de todas las temporadas
dataset_sueldos = []

# Obtener los sueldos de cada temporada
for temporada in temporadas:
    print(f"Procesando temporada {temporada}...")
    sueldos_temporada = obtener_salarios_temporada(temporada)
    dataset_sueldos.extend(sueldos_temporada)

# Función para guardar los datos en un archivo .txt
def guardar_en_txt(datos, nombre_archivo):
    with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
        # Escribir el encabezado
        archivo.write("Equipo,Jugadores,Salario Semanal,Salario Anual,Temporada\n")
        # Escribir los datos
        for sueldo in datos:
            archivo.write(f"{sueldo['Equipo']},{sueldo['Jugadores']},{sueldo['Salario Semanal']},{sueldo['Salario Anual']},{sueldo['Temporada']}\n")
    print(f"Datos guardados en {nombre_archivo}")

# Guardar los datos en un archivo .txt
guardar_en_txt(dataset_sueldos, "sueldos_equipos.txt")
