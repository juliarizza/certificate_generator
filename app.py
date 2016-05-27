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

        ## File menu ##
        preferencesAction = QtGui.QAction(u"&Preferências", self)
        preferencesAction.setShortcut("Ctrl+P")
        preferencesAction.setStatusTip(u"Preferências do app")
        #preferencesAction.triggered.connect()

        exitAction = QtGui.QAction("&Sair", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("Sair do app")
        exitAction.triggered.connect(self.close_app)

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
        termsAction = QtGui.QAction(u"&Termos e Condições", self)
        termsAction.setStatusTip(u"Termos e condições de uso do app")

        licenseAction = QtGui.QAction(u"&Licença", self)
        licenseAction.setStatusTip(u"Licença do app")

        aboutAction = QtGui.QAction("&Sobre", self)
        aboutAction.setStatusTip(u"Mais informações sobre o app")
        aboutAction.triggered.connect(self.show_about)

        self.statusBar()

        mainMenu = self.menuBar()

        fileMenu = mainMenu.addMenu("&Arquivo")
        fileMenu.addAction(preferencesAction)
        fileMenu.addAction(exitAction)

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
        helpMenu.addAction(termsAction)
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
        about = QtGui.QDialog()
        about.setGeometry(100,100,400,200)
        about.setWindowTitle("Sobre o Certifica!")
        about.setModal(True)
        about.exec_()

    def close_app(self):
        choice = QtGui.QMessageBox.question(self, "Sair",
                                            "Tem certeza que deseja sair?",
                                            QtGui.QMessageBox.Yes |
                                            QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            conn.close()
            sys.exit()
        else:
            pass


def run():
    app = QtGui.QApplication(sys.argv)

    createDB()

    GUI = Window()
    GUI.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()
