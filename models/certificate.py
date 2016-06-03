# -*- coding: utf-8 -*-
import os
import codecs
from datetime import date

import pdfkit

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

    new_filename = unicode(new_filename+".pdf")

    # Pdfkit options
    options = {"page-size": "A4",
               "orientation": "Landscape",
               "margin-left": "0",
               "margin-right": "0",
               "margin-top": "0",
               "margin-bottom": "0",
               "encoding": "UTF-8",
               "quiet": "",
              }

    # Verifies if there is an existing logo
    for filename in os.listdir(os.path.join(app_dir, "images")):
        if "logo" in filename:
            # If a logo exists, pass it as data
            # so the certificate will have in the corner
            cert_data["logo"] = os.path.join(app_dir, "images", filename)
            break
    else:
        cert_data["logo"] = ""

    # Windows paths for images so wkhtmltopdf works. I hate Windows.
    if "C:" in cert_data["logo"] and not "file:///" in cert_data["responsible_sig"]:
        cert_data["logo"] = "file:///"+cert_data["logo"].replace("\\","/")
        cert_data["responsible_sig"] = "file:///"+cert_data["responsible_sig"].replace("\\","/")
        cert_data["institution_sig"] = "file:///"+cert_data["institution_sig"].replace("\\","/")

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

    # Describes wich pages will be generated
    pages = []
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
        pages.append("temp_front.html")
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
        pages.append("temp_resp.html")

    if cert_data["content"] != "":
        # Do the same as the front, but now with the back of the certificate
        cert_html = codecs.open("certificate_back.html", "r", "utf-8")
        content = cert_html.read().format(**cert_data)
        cert_html.close()
        open("temp_back.html", "w").close()
        tmp_back = codecs.open("temp_back.html", "w", "utf-8")
        tmp_back.write(unicode(content))
        tmp_back.close()
        pages.append("temp_back.html")

    # Generate front and back
    if responsible is False:
        pdfkit.from_file(pages,
                         new_filename,
                         options=options)
    else:
        pdfkit.from_file(pages,
                         new_filename,
                         options=options)
