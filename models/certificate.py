# -*- coding: utf-8 -*-
import os
import pdfkit
import codecs
from datetime import date
from PyPDF2 import PdfFileReader, PdfFileMerger

def generate_certificate(path,cert_data):
    new_filename = path+"/"
    new_filename += ''.join(i for i in unicode(cert_data["name"]) if ord(i)<128).upper()
    new_filename.replace(" ","")
    new_filename = unicode(new_filename)

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
    cert_data["date"] = u"{0} de {1} de {2}".format(today.day,
                                                   months_pt[int(today.month)-1],
                                                   today.year)

    content_lines = cert_data["content"].split("\n")
    if not "<ul>" in cert_data["content"]:
        new_content = "<ul>"
        for line in content_lines:
            new_content += unicode("<li>{line}</li>").format(line=line)
        new_content += "</ul>"
        cert_data["content"] = new_content

    cert_html = codecs.open("certificate_front.html","r","utf-8")
    content = cert_html.read().format(**cert_data)
    cert_html.close()
    open("temp_front.html", "w").close # first clear file
    tmp_front = codecs.open("temp_front.html", "w", "utf-8")
    tmp_front.write(unicode(content))
    tmp_front.close()

    cert_html = codecs.open("certificate_back.html","r","utf-8")
    content = cert_html.read().format(**cert_data)
    cert_html.close()
    open("temp_back.html", "w").close # first clear file
    tmp_back = codecs.open("temp_back.html", "w", "utf-8")
    tmp_back.write(unicode(content))
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
    generate_certificate(path,cert_data)
    new_filename = unicode(path+"/responsible.pdf")

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

    cert_html = codecs.open("certificate_resp.html","r","utf-8")
    content = cert_html.read().format(**cert_data)
    cert_html.close()
    open("temp_resp.html", "w").close # first clear file
    tmp_front = codecs.open("temp_resp.html", "w", "utf-8")
    tmp_front.write(unicode(content))
    tmp_front.close()

    pdfkit.from_file("temp_resp.html", new_filename, options=options)
