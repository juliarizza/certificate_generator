# -*- coding: utf-8 -*-
import os
import codecs
from datetime import date

import pdfkit
from PyPDF2 import PdfFileReader, PdfFileMerger

from global_functions import app_dir


def generate_certificate(path, cert_data, responsible=False):
    """
        Function for generate certificate and save it in
        the specified path.
    """

    # Format the certificate filename
    if responsible is False:
        new_filename = os.path.join(
            unicode(path),
            u''.join(i for i in unicode(cert_data["name"]) if ord(i) < 128)
            .upper()
            .replace(" ", "")
        )
    else:
        new_filename = os.path.join(
            unicode(path),
            "responsible"
        )

    new_filename = unicode(new_filename)

    # Pdfkit options
    options = {"page-size": "A4",
               "orientation": "Landscape",
               "margin-left": "0",
               "margin-right": "0",
               "margin-top": "0",
               "margin-bottom": "0",
               "encoding": "UTF-8",
               "quiet": "",
               "background": "",
               "images": ""}

    # Verifies if there is an existing logo
    for filename in os.listdir(os.path.join(app_dir, "images")):
        if "logo" in filename:
            # If a logo exists, pass it as data
            # so the certificate will have in the corner
            cert_data["logo"] = filename
            break
    else:
        cert_data["logo"] = ""

    # Gets the generation date to insert into the certificate
    today = date.today()
    # Brazilian months name
    months_pt = ("Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                 "Julho", "Agosto", "Setembro", "Outubro", "Novembro",
                 "Dezembro")
    # Brazilian date format
    cert_data["date"] = u"{0} de {1} de {2}".format(
        today.day,
        months_pt[int(today.month)-1],
        today.year
    )

    # Organize the event content in a list
    # to insert in the back of the certificate
    content_lines = cert_data["content"].split("\n")
    if cert_data["content"] != "" and "<ul>" not in cert_data["content"]:
        new_content = "<ul>"
        for line in content_lines:
            new_content += unicode("<li>{line}</li>").format(line=line)
        new_content += "</ul>"
        cert_data["content"] = new_content

    # Verifies if the certificate is for a responsible or a client
    if responsible is False:
        # If it is for a client, use the certificate_front.html template

        # Reads the certificate_front.html template
        cert_html = codecs.open("certificate_front.html", "r", "utf-8")

        # Fills the template content with the cert_data
        content = cert_html.read().format(**cert_data)
        cert_html.close()

        # Clear the temporary file to store this new template
        open("temp_front.html", "w").close()

        # Creates the temporary template with the filled cert_data
        tmp_front = codecs.open("temp_front.html", "w", "utf-8")
        tmp_front.write(unicode(content))
        tmp_front.close()
    else:
        # If it is for a responsible, use the certificate_resp.html template

        # Reads the certificate_resp.html template
        cert_html = codecs.open("certificate_resp.html", "r", "utf-8")

        # Fills the template content with the cert_data
        content = cert_html.read().format(**cert_data)
        cert_html.close()

        # Clear the temporary file to store this new template
        open("temp_resp.html", "w").close()

        # Creates the temporary template with the filled cert_data
        tmp_front = codecs.open("temp_resp.html", "w", "utf-8")
        tmp_front.write(unicode(content))
        tmp_front.close()

    if cert_data["content"] != "":
        # Do the same as the front, but now with the back of the certificate
        cert_html = codecs.open("certificate_back.html", "r", "utf-8")
        content = cert_html.read().format(**cert_data)
        cert_html.close()
        open("temp_back.html", "w").close()
        tmp_back = codecs.open("temp_back.html", "w", "utf-8")
        tmp_back.write(unicode(content))
        tmp_back.close()

        # Generate back of the certificate
        pdfkit.from_file("temp_back.html",
                         new_filename+"_back.pdf",
                         options=options)

    # Generate the front pdf page and
    # merge front and back pdf pages into one pdf
    merger = PdfFileMerger()

    # Generate front and merge
    if responsible is False:
        pdfkit.from_file("temp_front.html",
                         new_filename+"_front.pdf",
                         options=options)
        merger.append(PdfFileReader(new_filename+"_front.pdf", "rb"))
    else:
        pdfkit.from_file("temp_resp.html",
                         new_filename+"_resp.pdf",
                         options=options)
        merger.append(PdfFileReader(new_filename+"_resp.pdf", "rb"))

    if cert_data["content"] != "":
        # Merge back
        merger.append(PdfFileReader(new_filename+"_back.pdf", "rb"))

    # Generate pdf
    merger.write(new_filename+".pdf")

    # Delete the pdf pages and leave just the complete pdf
    if responsible is False:
        os.remove(new_filename+"_front.pdf")
    else:
        os.remove(new_filename+"_resp.pdf")

    if cert_data["content"] != "":
        os.remove(new_filename+"_back.pdf")
