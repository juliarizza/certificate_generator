# -*- coding: utf-8 -*-
import ConfigParser
from PyQt4 import QtGui, QtCore
from models import conn,cursor,\
                    generate_certificate,generate_certificate_responsible,\
                    Mailer
from global_functions import titleFont

class CertificatesWidget(QtGui.QWidget):

    def __init__(self):
        super(CertificatesWidget, self).__init__()
        self.Config = ConfigParser.ConfigParser()
        self.Config.read("institution.ini")

        cursor.execute("SELECT * FROM events")
        self.events = cursor.fetchall()

        cursor.execute("SELECT * FROM signatures")
        self.signatures = cursor.fetchall()

        self.mainLayout = QtGui.QVBoxLayout()
        self.listLayout = QtGui.QHBoxLayout()
        self.btnsLayout = QtGui.QVBoxLayout()
        self.respLayout = QtGui.QVBoxLayout()
        self.instLayout = QtGui.QVBoxLayout()
        self.combosLayoutH = QtGui.QHBoxLayout()
        self.generateBtnsLayout = QtGui.QHBoxLayout()

        self.titleLabel = QtGui.QLabel(u"Certificados",self)
        self.titleLabel.setFont(titleFont)

        self.addBtn = QtGui.QPushButton(u"Adicionar")
        self.addBtn.clicked.connect(self.add_client)
        self.removeBtn = QtGui.QPushButton(u"Remover")
        self.removeBtn.clicked.connect(self.remove_client)
        self.btnsLayout.addWidget(self.addBtn)
        self.btnsLayout.addWidget(self.removeBtn)
        self.btnsLayout.addStretch()

        self.eventsListName = QtGui.QLabel(u"Selecione um evento:", self)
        self.eventsList = QtGui.QComboBox()
        for event in self.events:
            self.eventsList.addItem(unicode(event[1]))
        self.eventsList.currentIndexChanged.connect(self.load_list)

        self.subscriptionListName = QtGui.QLabel(u"Inscritos", self)
        self.subscriptionList = QtGui.QListWidget()
        self.load_list()

        self.responsibleListName = QtGui.QLabel(u"Selecione um responsável/ministrante:",self)
        self.responsibleList = QtGui.QComboBox()
        self.institutionListName = QtGui.QLabel(u"Assinatura da instituição:", self)
        self.institutionList = QtGui.QComboBox()
        for sig in self.signatures:
            self.responsibleList.addItem(unicode(sig[1]))
            self.institutionList.addItem(unicode(sig[1]))

        self.errorMsg = QtGui.QLabel(u"",self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        self.generateBtn = QtGui.QPushButton(u"Gerar!")
        self.generateBtn.clicked.connect(self.generate)
        self.generateSendBtn = QtGui.QPushButton(u"Gerar e enviar por email!")
        self.generateSendBtn.clicked.connect(self.generate_send)
        self.generateBtnsLayout.addWidget(self.generateBtn)
        self.generateBtnsLayout.addWidget(self.generateSendBtn)

        self.listLayout.addWidget(self.subscriptionList)
        self.listLayout.addLayout(self.btnsLayout)

        self.respLayout.addWidget(self.responsibleListName)
        self.respLayout.addWidget(self.responsibleList)

        self.instLayout.addWidget(self.institutionListName)
        self.instLayout.addWidget(self.institutionList)

        self.combosLayoutH.addLayout(self.respLayout)
        self.combosLayoutH.addLayout(self.instLayout)

        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(self.eventsListName)
        self.mainLayout.addWidget(self.eventsList)
        self.mainLayout.addWidget(self.subscriptionListName)
        self.mainLayout.addLayout(self.listLayout)
        self.mainLayout.addLayout(self.combosLayoutH)
        self.mainLayout.addWidget(self.errorMsg)
        self.mainLayout.addLayout(self.generateBtnsLayout)

        self.setLayout(self.mainLayout)


    def load_list(self):
        if self.events:
            cursor.execute("SELECT id,client_id FROM subscriptions WHERE event_id=?",
                            str(self.events[self.eventsList.currentIndex()][0]))
            self.clients = cursor.fetchall()
        else:
            self.clients = []

        self.subscriptionList.clear()
        for client in self.clients:
            cursor.execute("SELECT name FROM clients WHERE id=?",str(client[1]))
            client_name = unicode(cursor.fetchone()[0])
            self.subscriptionList.addItem(client_name)

    def add_client(self):
        try:
            event_id = self.events[self.eventsList.currentIndex()][0]
            self.add_client_widget = AddClientDialog(self, event_id)
            self.add_client_widget.show()
        except IndexError:
            self.errorMsg.setText(u"Selecione um evento existente!")

    def remove_client(self):
        try:
            subscription_id = self.clients[self.subscriptionList.currentRow()][0]
            choice = QtGui.QMessageBox.question(self, u"Apagar inscrição",
                                                u"Tem certeza que deseja apagar esta inscrição?",
                                                QtGui.QMessageBox.Yes |
                                                QtGui.QMessageBox.No)
            if choice == QtGui.QMessageBox.Yes:
                cursor.execute("DELETE FROM subscriptions WHERE id=?",
                                str(subscription_id))
                conn.commit()
            else:
                pass
            self.load_list()
        except IndexError:
            self.errorMsg.setText(u"Selecione um cliente existente!")

    def generate(self):
        if len(self.clients) == 0:
            self.errorMsg.setText(u"Primeiro inscreva clientes!")
        else:
            self.save_folder = QtGui.QFileDialog.getExistingDirectory(None,
                                                                u"Salvar em")

            self.cert_data = {"event": unicode(self.events[self.eventsList.currentIndex()][1]).upper(),
                         "start_date": unicode(self.events[self.eventsList.currentIndex()][2]),
                         "end_date": unicode(self.events[self.eventsList.currentIndex()][3]),
                         "hours": unicode(self.events[self.eventsList.currentIndex()][4]),
                         "content": unicode(self.events[self.eventsList.currentIndex()][5]).upper(),
                         "responsible_sig": unicode(self.signatures[self.responsibleList.currentIndex()][0]),
                         "institution_sig": unicode(self.signatures[self.institutionList.currentIndex()][0]),
                         "role": unicode(self.signatures[self.institutionList.currentIndex()][2]),
                         "institution": unicode(self.Config.get("Main","Name")).upper(),
                         "inst_register": unicode(self.Config.get("Main","ID"))}

            for client in self.clients:
                cursor.execute("SELECT name,register FROM clients WHERE id=?",str(client[1]))
                client_data = cursor.fetchone()
                self.cert_data["name"] = unicode(client_data[0]).upper()
                self.cert_data["register"] = unicode(client_data[1])
                generate_certificate(self.save_folder, self.cert_data)

            cursor.execute("SELECT * FROM signatures WHERE id=?",
                           str(self.signatures[self.responsibleList.currentIndex()][0]))
            responsible = cursor.fetchone()
            self.cert_data["name"] = unicode(responsible[1]).upper()
            self.cert_data["register"] = unicode(responsible[4]).upper()
            generate_certificate_responsible(self.save_folder, self.cert_data)

    def generate_send(self):
        if len(self.clients) == 0:
            self.errorMsg.setText(u"Primeiro inscreva clientes!")
        else:
            self.generate()
            self.mailer = Mailer()
            self.mailer.connect()
            for client in self.clients:
                cursor.execute("SELECT name,email FROM clients WHERE id=?",str(client[1]))
                client_data = cursor.fetchone()

                filepath = self.save_folder+"/"
                filepath += ''.join(i for i in unicode(client_data[0]) if ord(i)<128).upper()
                filepath += ".pdf"
                filepath.replace(" ","")
                self.mailer.send_certificate(filepath,unicode(client_data[1]))

            cursor.execute("SELECT name,email FROM signatures WHERE id=?",
                           str(self.signatures[self.responsibleList.currentIndex()][0]))
            responsible = cursor.fetchone()
            filepath = self.save_folder+"/responsible.pdf"
            self.mailer.send_certificate(filepath,unicode(responsible[1]))

            self.mailer.quit()

class AddClientDialog(QtGui.QDialog):

    def __init__(self, certificates_instance, event_id):
        super(AddClientDialog,self).__init__()
        self.event_id = event_id
        self.certificates_instance = certificates_instance

        cursor.execute("SELECT * FROM clients")
        self.clients = cursor.fetchall()

        self.mainLayout = QtGui.QVBoxLayout()

        self.titleLabel = QtGui.QLabel(u"Selecione um cliente")
        self.titleLabel.setFont(titleFont)

        self.clientsList = QtGui.QComboBox()
        for client in self.clients:
            self.clientsList.addItem(unicode(client[1]))

        self.saveBtn = QtGui.QPushButton(u"Selecionar")
        self.saveBtn.clicked.connect(self.add_client)

        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(self.clientsList)
        self.mainLayout.addWidget(self.saveBtn)

        self.setLayout(self.mainLayout)

    def add_client(self):
        cursor.execute("INSERT INTO subscriptions VALUES (NULL,?,?)",
                      (
                      str(self.event_id),
                      str(self.clients[self.clientsList.currentIndex()][0])
                      ))
        conn.commit()
        self.certificates_instance.load_list()
        self.hide()
