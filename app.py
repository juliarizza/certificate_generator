# -*- coding: utf-8 -*-a

import sys
from PyQt4 import QtGui, QtCore

from controllers import *
from models import *

class Window(QtGui.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(350,200,600,500)
        self.setWindowTitle("Certifica!")
        self.central_widget = QtGui.QStackedWidget()
        self.setCentralWidget(self.central_widget)
        #self.setWindowIcon(QtGui.QIcon('images/favicon.png'))

        ## Institution menu ##
        dataAction = QtGui.QAction("&Dados", self)
        dataAction.setStatusTip(u"Modificar dados da instituição")
        dataAction.triggered.connect(self.show_institution_data)

        mailAction = QtGui.QAction("&Email", self)
        mailAction.setStatusTip(u"Configurar envio de emails")
        mailAction.triggered.connect(self.config_mail)

        listSignatureAction = QtGui.QAction("&Assinaturas", self)
        listSignatureAction.setStatusTip(u"Ver todas as assinaturas")
        listSignatureAction.triggered.connect(self.list_signatures)

        ## Events menu ##
        eventsAction = QtGui.QAction("&Ver todos", self)
        eventsAction.setStatusTip("Ver todos os eventos")
        eventsAction.triggered.connect(self.list_events)

        ## Clients menu ##
        clientsAction = QtGui.QAction("&Ver todos", self)
        clientsAction.setStatusTip("Ver todos os clientes")
        clientsAction.triggered.connect(self.list_clients)

        ## Certificates menu ##
        certificatesAction = QtGui.QAction("&Gerar novos", self)
        certificatesAction.setStatusTip("Gerenciar certificados.")
        certificatesAction.triggered.connect(self.list_certificates)

        ## Help menu ##
        licenseAction = QtGui.QAction(u"&Licença", self)
        licenseAction.setStatusTip(u"Licença do app")
        licenseAction.triggered.connect(self.show_license)

        aboutAction = QtGui.QAction("&Sobre", self)
        aboutAction.setStatusTip(u"Mais informações sobre o app")
        aboutAction.triggered.connect(self.show_about)

        self.statusBar()

        mainMenu = self.menuBar()

        institutionMenu = mainMenu.addMenu(u"&Instituição")
        institutionMenu.addAction(dataAction)
        institutionMenu.addAction(mailAction)
        institutionMenu.addAction(listSignatureAction)

        eventsMenu = mainMenu.addMenu(u"&Eventos")
        eventsMenu.addAction(eventsAction)

        clientsMenu = mainMenu.addMenu(u"&Clientes")
        clientsMenu.addAction(clientsAction)

        certificatesMenu = mainMenu.addMenu(u"&Certificados")
        certificatesMenu.addAction(certificatesAction)

        helpMenu = mainMenu.addMenu("&Ajuda")
        helpMenu.addAction(licenseAction)
        helpMenu.addAction(aboutAction)

    def show_institution_data(self):
        inst_data_widget = InstitutionDataWidget()
        self.central_widget.addWidget(inst_data_widget)
        self.central_widget.setCurrentWidget(inst_data_widget)

    def config_mail(self):
        config_mail_widget = ConfigMailWidget()
        self.central_widget.addWidget(config_mail_widget)
        self.central_widget.setCurrentWidget(config_mail_widget)

    def list_signatures(self):
        signatures_widget = SignaturesListWidget()
        self.central_widget.addWidget(signatures_widget)
        self.central_widget.setCurrentWidget(signatures_widget)

    def list_events(self):
        events_widget = EventsListWidget()
        self.central_widget.addWidget(events_widget)
        self.central_widget.setCurrentWidget(events_widget)

    def list_clients(self):
        clients_widget = ClientsListWidget()
        self.central_widget.addWidget(clients_widget)
        self.central_widget.setCurrentWidget(clients_widget)

    def list_certificates(self):
        certificates_widget = CertificatesWidget()
        self.central_widget.addWidget(certificates_widget)
        self.central_widget.setCurrentWidget(certificates_widget)

    def show_about(self):
        msg = u"""Um gerador de certificados para cursos livres e eventos feito em Python para gerar certificados em PDF e, inclusive, enviá-los por e-mail. É só cadastrar seu evento e logo em seguida seus participantes e, voilà, certificados emitidos!\n\nMais informações em: https://github.com/juliarizza/certificate_generator
        """

        about = QtGui.QMessageBox()
        about.setGeometry(450,300,200,200)
        about.setIcon(QtGui.QMessageBox.Information)
        about.setText(u"Sobre o Certifica!")
        about.setInformativeText(msg)
        about.setWindowTitle(u"Sobre o Certifica!")
        about.setStandardButtons(QtGui.QMessageBox.Ok)
        about.exec_()

    def show_license(self):

        msg = u"""Copyright (c) 2016 Júlia Rizza & licensed under GNU GPLv3\n\nMais informações em: https://github.com/juliarizza/certificate_generator"""

        license = QtGui.QMessageBox()
        license.setGeometry(450,300,200,200)
        license.setIcon(QtGui.QMessageBox.Information)
        license.setText(u"Licença")
        license.setInformativeText(msg)
        license.setWindowTitle(u"Licença")
        license.setStandardButtons(QtGui.QMessageBox.Ok)
        license.exec_()

def run():
    app = QtGui.QApplication(sys.argv)

    createDB()

    GUI = Window()
    GUI.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
