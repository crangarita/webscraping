import requests
import networkx as nx
import openpyxl
from difflib import SequenceMatcher

from bs4 import BeautifulSoup

def extraction(cadena, str_ini=None, str_fin=None):
    if str_fin is not None:
        if str_ini is not None:
            indice_c = cadena.index(str_ini)  # obtenemos la posición del carácter c
            indice_h = cadena.index(str_fin)  # obtenemos la posición del carácter h
            found_text = cadena[indice_c:indice_h]
        else:
            indice_h = cadena.index(str_fin)  # obtenemos la posición del carácter h
            found_text = cadena[:indice_h]
    else:
        indice_c = cadena.index(str_ini)  # obtenemos la posición del carácter c
        found_text = cadena[indice_c:]
    return found_text


def extraction_position(cadena, indice_c=0, indice_h=0):
    found_text = cadena[indice_c:len(cadena) - indice_h]
    return found_text


def normalize(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
        ("È", "E"),
        ("Ñ", "N"),
        ("Ò", "O"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s


def validar(cadena):
    search = (
        "INDUSTRI",
        "MINISTR",
        "PRESIDEN",
        "VICEM",
        "ACOMPA",

    )
    for x in search:
        if cadena.find('la'):
            return True

    return False


def normalize_frases(cadena):
    replacements = (
        "H.R:",
        "H.R.",
        "H.S:",
        "H.S.",
        "H.S",
        "HS:",
        "DOCTOR",
        "DR.",
        "DRA."
        "HR.",
        "HR",

    )
    cadena = cadena.rstrip(".")
    for x in replacements:
        cadena = cadena.replace(x, "", 1)

    cadena = cadena.rstrip()
    cadena = cadena.lstrip()
    cadena = cadena.rstrip(".")
    return cadena


def normalize_spaces(cadena):
    cadena = cadena.rstrip()
    cadena = cadena.lstrip()
    return cadena

def autoresvstitulos():
    r = requests.get(
        'https://leyes.senado.gov.co/proyectos/index.php/proyectos-ley/cuatrenio-2018-2022/2021-2022?limit=1000&start=1',
        verify=False)
    soup = BeautifulSoup(r.text, 'lxml')

    M = nx.Graph()

    tables = soup.find_all('table')
    for table in tables:
        if table.td:
            tds = table.find_all('td')

            cadena_comision = tds[0].text
            cadena_estado = tds[1].text

            cadena_search = tds[2].text
            cadena_titulo = extraction(cadena_search, str_fin='F Radicado:')
            cadena_titulo = cadena_titulo.lstrip()
            cadena_titulo = cadena_titulo.rstrip()
            cadena_radicado = extraction(cadena_search, 'F Radicado:', '|')
            cadena_numero_senado = extraction(cadena_search, 'N° Senado:', '|')
            cadena_numero_camara = extraction(cadena_search, 'N° Camara:', 'Autor:')
            cadena_honorables = extraction(cadena_search, 'Autor:')
            autores = cadena_honorables[7:]

            autores = normalize(autores)
            autores = autores.upper()

            autores_list = autores.split(",")
            autores_cp = autores_list[:]
            index = 0
            for autor in autores_list:
                autor = normalize_frases(autor)

                M.add_node(autor, tipo="autor")
                M.add_node(cadena_titulo, tipo="proyecto", radicado=cadena_radicado)
                M.add_edge(autor, cadena_titulo)

    nx.write_gexf(M, "autoresvstitulos.gexf")

autoresvstitulos()
