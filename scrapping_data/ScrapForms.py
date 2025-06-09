from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import unidecode  # Asegúrate de tener esta librería instalada

# Configura el driver de Selenium
driver = webdriver.Chrome()

# Abre la URL
url = 'https://www.transfermarkt.es/verein-statistik/formtabelle/statistik/stat/plus/1?sortierung=best&letzte=10&selectedOptionKey=1'
driver.get(url)

# Inicializar contenedor de datos
data = []

# Función para esperar dinámicamente hasta que la tabla esté cargada
def wait_for_table():
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'table.items'))
        )
    except Exception as e:
        print(f"Error al esperar la tabla: {e}")

# Extraer datos mientras haya paginación
while True:
    # Esperar a que la tabla esté presente en la página
    wait_for_table()
    
    # Obtener el HTML de la página actual
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Buscar la tabla por clase
    table = soup.find('table', {'class': 'items'})

    # Recorrer las filas de la tabla
    if table:
        rows = table.find_all('tr')  # type: ignore

        for row in rows:
            columns = row.find_all('td')
            # Extraer datos específicos: Posición, Club, Puesto en Liga, País
            if len(columns) >= 4:
                position = columns[0].text.strip()
                club = columns[1].text.strip().split("\n")[0]  # Solo el nombre del club
                league_position = columns[4].text.strip()
                country = columns[2].text.strip()  # El país o la liga
                
                # Eliminar acentos
                position = unidecode.unidecode(position)
                club = unidecode.unidecode(club)
                league_position = unidecode.unidecode(league_position)
                country = unidecode.unidecode(country)
                
                # Formatear los datos en el orden que deseas
                formatted_row = f"{position},{club},{league_position},{country}"
                data.append(formatted_row)

    # Buscar el enlace "Siguiente" en el componente <a>
    next_page_link = soup.find('a', {'class': 'tm-pagination__link', 'title': 'A la página siguiente'})
    
    # Si existe el enlace de la página siguiente, navegar a la siguiente página
    if next_page_link:
        next_url = 'https://www.transfermarkt.es' + next_page_link['href']  # type: ignore
        driver.get(next_url)
        time.sleep(2)  # Esperar a que la página cargue
    else:
        break  # Si no hay más páginas, salir del loop

# Guardar todos los datos en un archivo .txt
with open('tabla_teamform.txt', 'w') as f:
    for line in data:
        f.write(line + '\n')

print("Datos guardados en 'tabla_teamform.txt'")

# Filtrar los equipos de "LaLiga"
with open('tabla_teamform.txt', 'r') as file:
    lines = file.readlines()

# Filtrar solo los equipos que tengan "LaLiga"
la_liga_teams = [line for line in lines if 'LaLiga' in line]

# Renumerar los equipos de LaLiga con posiciones consecutivas
renumbered_la_liga_teams = []
for idx, team in enumerate(la_liga_teams, 1):
    parts = team.split(',')
    parts[0] = str(idx)  # Reemplazar la posición por un número consecutivo
    renumbered_la_liga_teams.append(",".join(parts))

# Guardar los equipos de LaLiga con nueva numeración en un nuevo archivo
with open('tabla_teamform_laliga.txt', 'w') as file:
    for line in renumbered_la_liga_teams:
        file.write(line)

print("Equipos de LaLiga renumerados guardados en 'tabla_teamform_laliga.txt'")

# Cerrar el navegador
driver.quit()