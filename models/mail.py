# -*- coding: utf-8 -*-
import os
import smtplib
import ConfigParser
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders
from global_functions import app_dir

class Mailer():
    def __init__(self):
        self.Config = ConfigParser.ConfigParser()
        self.Config.read(os.path.join(app_dir,"institution.ini"))
        self.server = unicode(self.Config.get("Mail", "server"))
        self.port = int(self.Config.get("Mail", "port"))
        self.email = unicode(self.Config.get("Mail", "email"))
        self.password = unicode(self.Config.get("Mail", "password"))

    def connect(self):
        self.smtp_server = smtplib.SMTP(self.server, self.port)
        self.smtp_server.ehlo()
        self.smtp_server.starttls()
        self.smtp_server.login(self.email, self.password)

    def send_certificate(self, path, send_to):
        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = send_to
        msg["Subject"] = u"Certificado"

        body = u"""Em anexo a este e-mail encontra-se o seu certificado de participação de um de nossos eventos. O certificado contém duas páginas, que são sua frente e verso.

        Qualquer problema, entre em contato respondendo a este e-mail ou procure-nos em:
        {address}
        Fone: {phone}
        """.format(
                    address=unicode(self.Config.get("Contact","address")),
                    phone=unicode(self.Config.get("Contact","phone"))
                  )
        msg.attach(MIMEText(unicode(body),'plain', 'utf-8'))

        attachment = open(str(path),"rb")
        filename = os.path.split(path)[-1]
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(u'Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(part)

        text = msg.as_string()
        self.smtp_server.sendmail(self.email, send_to, text)

    def quit(self):
        self.smtp_server.quit()
