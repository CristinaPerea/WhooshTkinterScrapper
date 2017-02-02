# encoding: utf-8

import urllib, urllib2, re
import os.path
from os import listdir

from Tkinter import *
import tkMessageBox
from datetime import datetime, date, time, timedelta

from bs4 import BeautifulSoup

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.query import *
from whoosh.qparser.dateparse import DateParserPlugin
from whoosh import qparser
from whoosh.qparser import QueryParser, MultifieldParser, GtLtPlugin, OperatorsPlugin
from whoosh.index import open_dir

def read_url(url, file):
    try:
        # Creo fichero si no existe
        data = open(file, 'w')
        # Obtengo codigo fuente de la url
        url_data = urllib.urlopen(url)
        # Guardo codigo fuente en un fichero
        data.write(url_data.read())
        # Cierro conexion con url
        url_data.close()
    except:
        print "Error in Url read"

def read_file(file):
    f = open(file, "r")
    fr = f.read()
    f.close()
    return fr

def procesa_fecha(data):
    datos = data.split("/")
    fecha = ""
    if datos[0] == "hoy":
        fecha = "20161114"
    else:
        fecha = datos[2] + datos[1] + datos[0]

    return fecha

def almacenar():
    #read_url("http://foros.derecho.com/foro/20-Derecho-Civil-General", "p6.txt")
    data = read_file("p6.txt")

    # SCHEMA
    schema = Schema(titulo=TEXT(stored=True), link=ID(stored=True), autor=TEXT(stored=True), link_autor=ID(stored=True),
                    fecha=DATETIME(stored=True), num_respuestas=TEXT(stored=True), num_visitas=TEXT(stored=True),
                    respuestas=TEXT(stored=True), contador=TEXT(stored=True))

    # INDICE
    if not os.path.exists("index"):
        os.mkdir("index")
    ix = create_in("index", schema)

    # BEAUTIFULSOUP
    html = BeautifulSoup(data, 'html.parser')

    titulo = ""
    link = ""
    respuestas = ""
    autor = ""
    link_autor = ""
    fecha = ""
    n_respuestas = 0
    visitas = 0

    for elem in html.find_all(class_=['title', 'username understate', 'threadstats td alt']):
        if (elem.get('class')[0] == "title"):
            titulo = elem.get('title')
            link = ("http://foros.derecho.com/" + elem.get(u'href'))
            respuestas = u"ERROR CON LAS RESPUESTAS"

        elif (elem.get('class')[0] == "username"):
            autor = elem.get_text()
            link_autor = "http://foros.derecho.com/" + elem.get('href')
            fecha = procesa_fecha(elem.get('title').split(", el")[1].split(" ")[1])
        elif (elem.get('class')[0] == "threadstats"):
            n_respuestas = elem.get_text().split("\n")[1].split(" ")[1]
            visitas = elem.get_text().split("\n")[2].split(" ")[1]
            print link
            # WRITTER
            writer = ix.writer()
            writer.add_document(titulo=titulo, link=link, autor=autor, link_autor=link_autor, fecha=fecha,
                                num_respuestas=n_respuestas, num_visitas=visitas, respuestas=respuestas, contador=u"uno")
            writer.commit()

    tkMessageBox.showinfo("Almacenar", "Datos almacenados en el índice correctamente")

def searchTe(busqueda):
    ix = open_dir("index")
    searcher = ix.searcher()
    parser = QueryParser("contador", ix.schema)
    myquery = parser.parse(busqueda)

    results = searcher.search(myquery)

    return results

def searchTeApp():
        results = searchTe("uno")
        v = Toplevel()
        sc = Scrollbar(v)
        sc.pack(side=RIGHT, fill=Y)
        lb = Listbox(v, width=150, yscrollcommand=sc.set)
        lb.insert(END, "Número de temas en nuestro índice: " + str(len(results)))
        lb.insert(END, '')
        lb.pack(side=LEFT, fill=BOTH)
        sc.config(command=lb.yview)

def searchFe(busqueda):
    ix = open_dir("index")
    searcher = ix.searcher()
    date = "{" + busqueda + " to]"
    parser = QueryParser("fecha", ix.schema)

    parser.add_plugin(DateParserPlugin(free=True))
    parser.add_plugin(GtLtPlugin())
    myquery = parser.parse(date)

    results = searcher.search(myquery)

    return results

def searchFeApp():
    box = Tk()
    L1 = Label(box, text="Fecha: (YYYYMMDD)")
    L1.pack(side=LEFT)

    E1 = Entry(box)
    E1.pack(side=RIGHT)

    def search(event):
        results = searchFe(E1.get())

        v = Toplevel()
        sc = Scrollbar(v)
        sc.pack(side=RIGHT, fill=Y)
        lb = Listbox(v, width=150, yscrollcommand=sc.set)
        if(len(results) != 0):
            for e in results:
                lb.insert(END, "Título: " + str(e['titulo']))
                lb.insert(END, "Autor: " + str(e['autor']))
                lb.insert(END, "Fecha: " + str(e['fecha']))
                lb.insert(END, "Número de respuestas: " + str(e['num_respuestas']))
                lb.insert(END, '')
        else:
            lb.insert(END, "Error")
            lb.insert(END, '')
        lb.pack(side=LEFT, fill=BOTH)
        sc.config(command=lb.yview)

    E1.bind('<Return>', search)
    E1.focus_set()

    box.mainloop()

def ventanaApp():
    top = Tk()

    buttonAlmacenar = Button(top, text="Almacenar", command=almacenar)
    buttonBuscar1 = Button(top, text="Busca A", command=searchTeApp)
    buttonBuscar2 = Button(top, text="Busca B", command=searchFeApp)

    buttonAlmacenar.pack()
    buttonBuscar1.pack()
    buttonBuscar2.pack()

    top.mainloop()

if __name__ == "__main__":
    ventanaApp()