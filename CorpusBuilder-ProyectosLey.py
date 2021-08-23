from bs4 import BeautifulSoup
from bs4.element import Declaration
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import re
import nltk
import string
import operator
import math
import pandas as pd
import re
import nltk
import string

#nltk.download('punkt')

def Limpiar(arreglo):
    numeros = []
    textos = []
    for i in arreglo:
        if not i.isnumeric():
            aux = i.split("-")
            for j in aux:
                if j.isnumeric():
                    numeros.append(j)
                else:
                    textos.append(j)
        else:
            numeros.append(i)
    return(numeros)

def Preprocessing_Especial(cadena, stop_words):
    cadena_minuscula = cadena.lower()
    pattern = re.compile('[,.\"!@#$%^&*(){}?/;`~:<>+=°]')
    cadena_minuscula = pattern.sub('', cadena_minuscula)
    arreglo_cadena = word_tokenize(cadena_minuscula)
    arreglo_cadena_sin_stopwords = [w for w in arreglo_cadena if not w in stop_words]
    leyes = []
    articulos = []
    urgencias = []
    legislativos = []
    supremos = []
    for i in range(len(arreglo_cadena_sin_stopwords)-1):
        if arreglo_cadena_sin_stopwords[i] == "ley" or arreglo_cadena_sin_stopwords[i] == "leyes":
            k=i
            while(arreglo_cadena_sin_stopwords[k+1][0].isnumeric()):
                if k < len(arreglo_cadena_sin_stopwords)-2:
                    k+=1
                    leyes.append(arreglo_cadena_sin_stopwords[k])
                else:
                    leyes.append(arreglo_cadena_sin_stopwords[k+1])
                    break
                    
        elif arreglo_cadena_sin_stopwords[i] == "articulo" or arreglo_cadena_sin_stopwords[i] == "artículo" or arreglo_cadena_sin_stopwords[i] == "articulos" or arreglo_cadena_sin_stopwords[i] == "artículos":
            k=i
            while(arreglo_cadena_sin_stopwords[k+1][0].isnumeric()):
                if k < len(arreglo_cadena_sin_stopwords)-2:
                    k+=1
                    articulos.append(arreglo_cadena_sin_stopwords[k])
                else:
                    articulos.append(arreglo_cadena_sin_stopwords[k+1])
                    break
                
        elif arreglo_cadena_sin_stopwords[i] == "urgencia":
            k=i
            while(arreglo_cadena_sin_stopwords[k+1][0].isnumeric()):
                if k < len(arreglo_cadena_sin_stopwords)-2:
                    k+=1
                    urgencias.append(arreglo_cadena_sin_stopwords[k])
                else:
                    urgencias.append(arreglo_cadena_sin_stopwords[k+1])
                    break
                
        elif arreglo_cadena_sin_stopwords[i] == "legislativo":
            k=i
            while(arreglo_cadena_sin_stopwords[k+1][0].isnumeric()):
                if k < len(arreglo_cadena_sin_stopwords)-2:
                    k+=1
                    legislativos.append(arreglo_cadena_sin_stopwords[k])
                else:
                    legislativos.append(arreglo_cadena_sin_stopwords[k+1])
                    break
                
        elif arreglo_cadena_sin_stopwords[i] == "supremo":
            k=i
            while(arreglo_cadena_sin_stopwords[k+1][0].isnumeric()):
                if k < len(arreglo_cadena_sin_stopwords)-2:
                    k+=1
                    supremos.append(arreglo_cadena_sin_stopwords[k])
                else:
                    supremos.append(arreglo_cadena_sin_stopwords[k+1])
                    break
    return(Limpiar(leyes),articulos,Limpiar(urgencias),Limpiar(legislativos),Limpiar(supremos))

def remove_useless_data(row, stop_words=[]):
    pattern1 = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    pattern2 = re.compile('[,.\"!@#$%^&*(){}?/;`~:<>+=-]')
    table = str.maketrans('', '', string.punctuation)

    row = row.lower()
    row = pattern1.sub('', row)
    row = pattern2.sub('', row)
    tokens = word_tokenize(row)
    row_no_punctuation = [w.translate(table) for w in tokens]
    row_no_num = [w for w in row_no_punctuation if w.isalpha()]
    row = [w for w in row_no_num if not w in stop_words]
    # row = [PorterStemmer().stem(w) for w in row_no_num if not w in stop_words]
    # row = [SnowballStemmer('spanish').stem(w) for w in row_no_num if not w in stop_words]
    row = ' '.join(row)
    return row

def stemmer(words):
    words_array = words.split()
    words_sin_repeticiones = list(set(words_array))
    words_dict = dict()
    for i in words_sin_repeticiones:
        nro_apariciones = words.count(i)
        words_dict[i] = nro_apariciones
    sorted_dict = dict(sorted(words_dict.items(), key=operator.itemgetter(1),reverse=True))
    roots = [SnowballStemmer('spanish').stem(w) for w in sorted_dict.keys()]
    roots = list(set(roots))
    stemmedwords = ""
    for key in sorted_dict.keys():
        for word in roots:
            if word in key:
                stemmedwords += key+" "
                roots.remove(word)
                break
        if len(roots)==0:
            break
    return stemmedwords

def modificar_a_textos(leyes,articulos,urgencias,legislativos,supremos):
    texto = " "
    for i in leyes:
        texto += "ley["+i+"] "
    for i in articulos:
        texto += "artículo["+i+"] "
    for i in urgencias:
        texto += "urgencia["+i+"] "
    for i in legislativos:
        texto += "legislativo["+i+"] "
    for i in supremos:
        texto += "supremo["+i+"] "
    return texto


ubicacion = 'chromedriver.exe'
#Ruta del driver - Selenium
driver = webdriver.Chrome(executable_path=ubicacion)

#Ruta Proyectos de Ley 2016-2021
home_link = "https://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2016.nsf/Local%20Por%20Numero%20Inverso?OpenView"
driver.get(home_link)

texto = []
pg_amount = 16 #Número de páginas visitadas
base = "https://www2.congreso.gob.pe"
page = BeautifulSoup(driver.page_source,'html.parser')
stop_words = open('spanish.txt', 'r')
special_words = ["ley","leyes","artículo","articulo","artículos","articulos","legislativo","urgencia","supremo"]
spanish_stop_words = stop_words.read().splitlines()
            
#Recorrido tablas que contienen leyes
tables = page.find_all("table")

j = 0
for i in range(1, pg_amount+1):    
    for row in tables[2].findAll("tr"):
        cells = row.find_all('td')
        texto.clear()
        for cell in cells:
            if(cell.find('a')):
                a = cell.find('a')
                url = a.attrs['href']
                texto.append(url)
            if(cell.text!=''):
                texto.append(cell.text)   
        if(texto!=[]):
            #Recuperación de Metadata
            driver.get(base+str(texto[0]))
            page = BeautifulSoup(driver.page_source,'html.parser')
            Inputs = page.find_all("input")
            Titulo = ""
            Descripcion = ""
            Completo = 0
            for Input in Inputs:
                Input = str(Input)
                if Input.__contains__('<input name="TitIni"'):
                    Titulo=Input[42:-3]
                    Completo+=1
                elif Input.__contains__('<input name="SumIni"'):
                    Descripcion=Input[42:-3]
                    Completo+=1
                if(Completo == 2):
                    break
            textito = texto[1].split("/")

            #Pre procesado
            cadena = Titulo + Descripcion
            leyes,articulos,urgencias,legislativos,supremos = Preprocessing_Especial(cadena, spanish_stop_words)
            corpus_procesado = remove_useless_data(cadena,spanish_stop_words+special_words)
            adicional = modificar_a_textos(leyes,articulos,urgencias,legislativos,supremos)
            corpus_preprocesado = corpus_procesado+adicional
            corpus_final = stemmer(corpus_preprocesado)
            #Creación archivos .txt
            if (corpus_final != " "):
                if ("transparencia" in corpus_final or "accesibilidad" in corpus_final
                    or "portabilidad" in corpus_final or "disponibilidad" in corpus_final
                    or "publicidad" in corpus_final or "auditabilidad" in corpus_final
                    or "validez" in corpus_final or "controlabilidad" in corpus_final
                    or "verificabilidad" in corpus_final or "trazabilidad" in corpus_final
                    or "responsabilidad" in corpus_final or "informatividad" in corpus_final
                    or "claridad" in corpus_final or "comparable" in corpus_final
                    or "consistencia" in corpus_final or "actual" in corpus_final
                    or "completo" in corpus_final or "exactitud" in corpus_final
                    or "integridad" in corpus_final or "precisión" in corpus_final
                    or "usabilidad" in corpus_final or "uniformidad" in corpus_final
                    or "simplicidad" in corpus_final or "performabilidad" in corpus_final
                    or "intuitividad" in corpus_final or "operabilidad" in corpus_final
                    or "adaptabilidad" in corpus_final or "facilidad de uso" in corpus_final
                    or "comprensibilidad" in corpus_final or "concisión" in corpus_final
                    or "componibilidad" in corpus_final or "extensibilidad" in corpus_final
                    or "descomponibilidad" in corpus_final or "dependencia" in corpus_final
                    or "diafanidad" in corpus_final or "limpidez" in corpus_final
                    or "acceso" in corpus_final or "facilidad" in corpus_final
                    or "conexión" in corpus_final
                    or "asequibilidad" in corpus_final or "disposición" in corpus_final
                    or "sencillo" in corpus_final or "oportunidad" in corpus_final
                    or "transferibilidad" in corpus_final or "movilidad" in corpus_final
                    or "suministro" in corpus_final
                    or "prestación" in corpus_final
                    or "facilitación" in corpus_final
                    or "propaganda" in corpus_final or "publicitario" in corpus_final
                    or "anuncio" in corpus_final or "divulgación" in corpus_final
                    or "comercial" in corpus_final or "publicación" in corpus_final
                    or "promoción" in corpus_final or "difusión" in corpus_final
                    or "aviso" in corpus_final or "marketing" in corpus_final
                    or "fomento" in corpus_final
                    or "vigencia" in corpus_final or "pertenencia" in corpus_final
                    or "idoneidad" in corpus_final or "utilidad" in corpus_final
                    or "válido" in corpus_final or "efectividad" in corpus_final
                    or "adecuación" in corpus_final or "solidez" in corpus_final
                    or "veracidad" in corpus_final or "importancia" in corpus_final
                    or "repercusión" in corpus_final or "mérito" in corpus_final
                    or "procedencia" in corpus_final
                    or "efecto" in corpus_final or "maniobrabilidad" in corpus_final
                    or "verificación" in corpus_final or "control" in corpus_final
                    or "revisión" in corpus_final
                    or "inspección" in corpus_final
                    or "comprobación" in corpus_final or "chequeo" in corpus_final
                    or "seguimiento" in corpus_final
                    or "rastreabilidad" in corpus_final
                    or "trazado" in corpus_final
                    or "supervisión" in corpus_final or "vestigio" in corpus_final
                    or "investigación" in corpus_final or "deber" in corpus_final
                    or "tarea" in corpus_final
                    or "autoría" in corpus_final
                    or "misión" in corpus_final or "función" in corpus_final
                    or "cargo" in corpus_final
                    or "información" in corpus_final
                    or "aclaración" in corpus_final or "clarificación" in corpus_final
                    or "claro" in corpus_final
                    or "aclarado" in corpus_final
                    or "definido" in corpus_final
                    or "similar" in corpus_final
                    or "equivalente" in corpus_final or "semejante" in corpus_final
                    or "equiparable" in corpus_final
                    or "comparado" in corpus_final
                    or "comparativo" in corpus_final
                    or "coherencia" in corpus_final
                    or "consecuente" in corpus_final or "compatibilidad" in corpus_final
                    or "concordancia" in corpus_final
                    or "firmeza" in corpus_final
                    or "vigente" in corpus_final
                    or "imperante" in corpus_final
                    or "presente" in corpus_final
                    or "integral" in corpus_final or "absoluto" in corpus_final
                    or "íntegro" in corpus_final
                    or "fidelidad" in corpus_final
                    or "credibilidad" in corpus_final
                    or "inviolabilidad" in corpus_final
                    or "entereza" in corpus_final or "completitud" in corpus_final
                    or "seguridad" in corpus_final
                    or "especificación" in corpus_final
                    or "normalización" in corpus_final
                    or "uniformización" in corpus_final
                    or "unificación" in corpus_final
                    or "simplificación" in corpus_final
                    or "esclarecedor" in corpus_final
                    or "operatividad" in corpus_final
                    or "flexibilidad" in corpus_final
                    or "elasticidad" in corpus_final or "versatilidad" in corpus_final
                    or "legibilidad" in corpus_final or "brevedad" in corpus_final
                    or "conformación" in corpus_final
                    or "órgano" in corpus_final
                    or "departamento" in corpus_final
                    and ("información" in corpus_final or "tecnología" in corpus_final)):
                    Archivo = open("./CorpusT5/"+textito[0]+"-"+textito[1]+".txt","w")
                    Archivo.write(corpus_final)
                    Archivo.close
                    j += 1

    home_link = "https://www2.congreso.gob.pe/Sicr/TraDocEstProc/CLProLey2016.nsf/Local%20Por%20Numero%20Inverso?OpenView"
    driver.get(home_link)

    #Paso a una nueva página
    for k in range(0,i):
        #Click botón siguiente
        next_btn = driver.find_element_by_xpath('/html/body/form/table/tbody/tr/td/p/table/tbody/tr/td[3]/a') 
        next_btn.click()   
    page = BeautifulSoup(driver.page_source,'html.parser')
    tables = page.find_all("table")
