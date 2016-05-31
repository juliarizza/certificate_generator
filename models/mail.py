# -*- coding: utf-8 -*-
import os
import ConfigParser
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

from global_functions import app_dir


class Mailer():
    """
        Instance to manage the mailing.
    """

    def __init__(self):
        """
            Setup all needed info.
        """
        # Gets all the connection info from the .ini file
        self.Config = ConfigParser.ConfigParser()
        self.Config.read(os.path.join(app_dir, "institution.ini"))
        self.server = unicode(self.Config.get("Mail", "server"))
        self.port = int(self.Config.get("Mail", "port"))
        self.email = unicode(self.Config.get("Mail", "email"))
        self.password = unicode(self.Config.get("Mail", "password"))

    def connect(self):
        """
            Connects to the mail server using the .ini info.
        """
        self.smtp_server = smtplib.SMTP(self.server, self.port)
        self.smtp_server.ehlo()
        self.smtp_server.starttls()
        self.smtp_server.login(self.email, self.password)

    def send_certificate(self, path, send_to):
        """
            Send each certificate from the configured email.
        """

        # Email info
        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = send_to
        msg["Subject"] = u"Certificado"

        body = u"""Em anexo a este e-mail encontra-se o seu certificado de participação de um de nossos eventos.

        Qualquer problema, entre em contato respondendo a este e-mail ou procure-nos em:
        {address}
        Fone: {phone}
        """.format(
                    address=unicode(self.Config.get("Contact", "address")),
                    phone=unicode(self.Config.get("Contact", "phone"))
                  )
        msg.attach(MIMEText(unicode(body), 'plain', 'utf-8'))

        # Add the certificate file
        attachment = open(unicode(path), "rb")
        filename = os.path.basename(unicode(path))
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(u'Content-Disposition', "attachment; filename= %s" % filename)
        msg.attach(part)

        text = msg.as_string()
        # Send the email
        self.smtp_server.sendmail(self.email, send_to, text)

    def quit(self):
        # Quits the connection
        self.smtp_server.quit()
