# -*- coding: utf-8 -*-
import os
import pdfkit
from datetime import date
from PyPDF2 import PdfFileReader, PdfFileMerger

def generate_certificate(path,cert_data):
    new_filename = str(path+"/"+cert_data["name"].replace(" ",""))

    options = {"page-size":"A4",
               "orientation":"Landscape",
               "margin-left": "0",
               "margin-right": "0",
               "margin-top": "0",
               "margin-bottom": "0",
               "encoding":"UTF-8",
               "quiet":"",
               "background":"",
               "images":""}

    for filename in os.listdir('images/'):
        if "logo" in filename:
            cert_data["logo"] = filename
            break
    else:
        cert_data["logo"] = ""

    today = date.today()
    months_pt = ("Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                 "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro")
    cert_data["date"] = "{0} de {1} de {2}".format(today.day,
                                                   months_pt[int(today.month)-1],
                                                   today.year)

    cert_html = open("certificate_front.html","r")
    content = cert_html.read().format(**cert_data)
    cert_html.close()
    open("temp_front.html", "w").close # first clear file
    tmp_front = open("temp_front.html", "w")
    tmp_front.write(content)
    tmp_front.close()

    cert_html = open("certificate_back.html","r")
    content = cert_html.read().format(**cert_data)
    cert_html.close()
    open("temp_back.html", "w").close # first clear file
    tmp_back = open("temp_back.html", "w")
    tmp_back.write(content)
    tmp_back.close()

    pdfkit.from_file("temp_front.html", new_filename+"_front.pdf", options=options)
    pdfkit.from_file("temp_back.html", new_filename+"_back.pdf", options=options)

    merger = PdfFileMerger()
    merger.append(PdfFileReader(new_filename+"_front.pdf", "rb"))
    merger.append(PdfFileReader(new_filename+"_back.pdf", "rb"))
    merger.write(new_filename+".pdf")

    os.remove(new_filename+"_front.pdf")
    os.remove(new_filename+"_back.pdf")

def generate_certificate_responsible(path, cert_data):
    new_filename = str(path+"/responsible.pdf")

    options = {"page-size":"A4",
               "orientation":"Landscape",
               "margin-left": "0",
               "margin-right": "0",
               "margin-top": "0",
               "margin-bottom": "0",
               "encoding":"UTF-8",
               "quiet":"",
               "background":"",
               "images":""}

    for filename in os.listdir('images/'):
        if "logo" in filename:
            cert_data["logo"] = filename
            break
    else:
        cert_data["logo"] = ""

    today = date.today()
    months_pt = ("Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                 "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro")
    cert_data["date"] = "{0} de {1} de {2}".format(today.day,
                                                   months_pt[int(today.month)-1],
                                                   today.year)

    cert_html = open("certificate_resp.html","r")
    content = cert_html.read().format(**cert_data)
    cert_html.close()
    open("temp_resp.html", "w").close # first clear file
    tmp_front = open("temp_resp.html", "w")
    tmp_front.write(content)
    tmp_front.close()

    pdfkit.from_file("temp_resp.html", new_filename, options=options)
