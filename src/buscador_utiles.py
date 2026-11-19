from collections import Counter

# Conjunto con palabras huecas (se ignoran en las búsquedas, no se indexan)
STOP_WORDS = {'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para', 'con', 'no', 'una', 'su', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o'}

# Caracteres de puntuación
PUNTUACION = '!¡"#$%&\'()*+,-./:;<=>?¿@[\\]^_`{|}~'

def normalizar_texto(texto: str) -> list[str]:
    """
    Recibe un texto, lo limpia y devuelve una lista de palabras. En el proceso de limpieza, 
    la función:
    1. Convierte el texto a minúsculas.
    2. Quita los signos de puntuación (los caracteres contenidos en PUNTUACION).
    3.Filtra las palabras huecas (las palabras contenidas en STOP_WORDS).
    
    Ejemplo: normalizar_texto("¡Hola, Mundo!") debería devolver ['hola', 'mundo']

    Parámetros:
    texto (str): El texto a normalizar.
    
    Devuelve:
    list[str]: Una lista de palabras normalizadas.
    """    
    texto = texto.lower()
    for i in PUNTUACION:
        texto = texto.replace(i, " ")
    texto = texto.split()
    for palabra in texto[:]: #recorre copia de la lista
        if palabra in STOP_WORDS:
            texto.remove(palabra) 
        if not palabra.isalpha():
            for c in palabra:
                if c.isdigit():
                    texto.remove(c)
    return texto

def procesar_url_en_indice(url: str, texto: str, indice: dict[str, set[str]]):
    """
    Recibe la URL, el texto ya extraído de esa URL y un diccionario que indexa
    URLs de páginas web usando las palabras contenidas en la web como clave.
    La función actualiza el diccionario para incluir la URL en los conjuntos asociados
    a las palabras que aparecen en el texto.
    
    Parámetros:
    url (str): La URL de la página web.
    texto (str): El texto extraído de la página web.
    indice (dict[str, set[str]]): El índice de búsqueda a actualizar.
    """
    texto = normalizar_texto(texto)
    for p in texto:
        if p not in indice:
            indice[p] = set()
        indice[p].add(url)


def buscar_palabra_simple(palabra: str, indice: dict[str, set[str]]) -> set[str]:
    """
    Recibe una única palabra de búsqueda y el índice, y devuelve
    un conjunto de URLs donde se encontró esa palabra.
    Si la palabra no está en el índice, debe devolver un conjunto vacío.
    Antes de buscarla, la palabra será normalizada.

    Parámetros:
    palabra (str): La palabra a buscar.
    indice (dict[str, set[str]]): El índice de búsqueda.

    Devuelve:
    set[str]: Un conjunto de URLs donde se encontró la palabra.
    """    
    palabra = normalizar_texto(palabra)
    if palabra[0] not in indice:
        return set()
    return indice[palabra[0]]

def buscar_palabras_or(frase: str, indice: dict[str, set[str]]) -> set[str]:
    """
    Recibe una frase de búsqueda y el índice, y devuelve
    un conjunto de URLs donde se encuentren alguna de las palabras de la frase.
    Si ninguna de las palabras están en el índice, debe devolver un conjunto vacío.
    La función normalizará el texto de la frase antes de buscar.

    Parámetros:
    frase (str): La frase de búsqueda.
    indice (dict[str, set[str]]): El índice de búsqueda.

    Devuelve:
    set[str]: Un conjunto de URLs donde se encontraron todas las palabras.
    """    
    frase_norm = normalizar_texto(frase)
    res = set()
    for palabra in frase_norm:
        res = res.union(buscar_palabra_simple(palabra, indice))
    return res

def buscar_palabras_and(frase: str, indice: dict[str, set[str]]) -> set[str]:
    """
    Recibe una frase de búsqueda y el índice, y devuelve
    un conjunto de URLs donde se encuentren todas las palabras de la frase.
    Si ninguna de las palabras están en el índice, debe devolver un conjunto vacío.
    La función normalizará el texto de la frase antes de buscar.

    Parámetros:
    frase (str): La frase de búsqueda.
    indice (dict[str, set[str]]): El índice de búsqueda.

    Devuelve:
    set[str]: Un conjunto de URLs donde se encontraron todas las palabras.
    """
    frase_norm = normalizar_texto(frase)
    res = buscar_palabra_simple(frase_norm[0], indice)
    if frase_norm == []:
        return set()

    for p in frase_norm[1:]:
        res = res.intersection(buscar_palabra_simple(p, indice))
    return res


def procesar_url_en_indice_top_n(url: str, texto: str, indice: dict[str, set[str]], top_n: int=1000):
    """
    Recibe la URL, el texto ya extraído de esa URL y un diccionario que indexa
    URLs de páginas web usando las palabras contenidas en la web como clave.
    La función actualiza el diccionario para incluir la URL en los conjuntos asociados
    a las 'top_n' palabras más frecuentes de entre las que aparecen en el texto.

    Parámetros:
    url (str): La URL de la página web.
    texto (str): El texto extraído de la página web.
    indice (dict[str, set[str]]): El índice de búsqueda a actualizar.
    top_n (int): Número de palabras más frecuentes a indexar.
    """
    texto = normalizar_texto(texto)
    contador = Counter(texto)

    for p, _ in contador.most_common(top_n):
        if p not in indice:
            indice[p] = set()
        indice[p].add(url)


def calcula_estadisticas_indice(indice: dict[str, set[str]]) -> tuple[int, int, float]:
    """
    Recibe un índice y calcula estadísticas sobre él.

    Parámetros:
    indice (dict[str, set[str]]): El índice de búsqueda.

    Devuelve:
    tuple[int, int, float]: Una tupla con tres valores:
        - Número total de palabras indexadas.
        - Número total de URLs indexadas (sin duplicados).
        - Promedio de URLs por palabra: cuántas URLs hay indexadas para cada palabra, en promedio.
    """
    num_palabras = len(indice.keys())
    url_unica = set()
    promedio = 0.0
    for p in indice:
        for j in indice[p]:
            if j not in url_unica:
                url_unica.add(j)
    suma = 0
    for p in indice:
        suma += len(indice[p])
    if num_palabras != 0:
        promedio = suma/num_palabras
        
    return (num_palabras,len(url_unica), promedio)  