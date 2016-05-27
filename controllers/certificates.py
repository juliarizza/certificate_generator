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

        self.titleLabel = QtGui.QLabel("Certificados",self)
        self.titleLabel.setFont(titleFont)

        self.addBtn = QtGui.QPushButton("Adicionar")
        self.addBtn.clicked.connect(self.add_client)
        self.removeBtn = QtGui.QPushButton("Remover")
        self.removeBtn.clicked.connect(self.remove_client)
        self.btnsLayout.addWidget(self.addBtn)
        self.btnsLayout.addWidget(self.removeBtn)
        self.btnsLayout.addStretch()

        self.eventsListName = QtGui.QLabel("Selecione um evento:", self)
        self.eventsList = QtGui.QComboBox()
        for event in self.events:
            self.eventsList.addItem(event[1])
        self.eventsList.currentIndexChanged.connect(self.load_list)

        self.subscriptionListName = QtGui.QLabel("Inscritos", self)
        self.subscriptionList = QtGui.QListWidget()
        self.load_list()

        self.responsibleListName = QtGui.QLabel(u"Selecione um responsável/ministrante:",self)
        self.responsibleList = QtGui.QComboBox()
        self.institutionListName = QtGui.QLabel(u"Assinatura da instituição:", self)
        self.institutionList = QtGui.QComboBox()
        for sig in self.signatures:
            self.responsibleList.addItem(str(sig[1]))
            self.institutionList.addItem(str(sig[1]))

        self.errorMsg = QtGui.QLabel("",self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        self.generateBtn = QtGui.QPushButton("Gerar!")
        self.generateBtn.clicked.connect(self.generate)
        self.generateSendBtn = QtGui.QPushButton("Gerar e enviar por email!")
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
            client_name = cursor.fetchone()[0]
            self.subscriptionList.addItem(str(client_name))

    def add_client(self):
        try:
            event_id = self.events[self.eventsList.currentIndex()][0]
            self.add_client_widget = AddClientDialog(self, event_id)
            self.add_client_widget.show()
        except IndexError:
            self.errorMsg.setText("Selecione um evento existente!")

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
            self.errorMsg.setText("Selecione um cliente existente!")

    def generate(self):
        if len(self.clients) == 0:
            self.errorMsg.setText("Primeiro inscreva clientes!")
        else:
            self.save_folder = QtGui.QFileDialog.getExistingDirectory(None,
                                                                "Salvar em")

            self.cert_data = {"event": self.events[self.eventsList.currentIndex()][1].upper(),
                         "start_date": self.events[self.eventsList.currentIndex()][2],
                         "end_date": self.events[self.eventsList.currentIndex()][3],
                         "hours": self.events[self.eventsList.currentIndex()][4],
                         "content": self.events[self.eventsList.currentIndex()][5].upper(),
                         "responsible_sig": self.signatures[self.responsibleList.currentIndex()][0],
                         "institution_sig": self.signatures[self.institutionList.currentIndex()][0],
                         "role": self.signatures[self.institutionList.currentIndex()][2],
                         "institution": str(self.Config.get("Main","Name")).upper(),
                         "inst_register": str(self.Config.get("Main","ID"))}

            for client in self.clients:
                cursor.execute("SELECT name,register FROM clients WHERE id=?",str(client[1]))
                client_data = cursor.fetchone()
                self.cert_data["name"] = str(client_data[0]).upper()
                self.cert_data["register"] = str(client_data[1])
                generate_certificate(self.save_folder, self.cert_data)

            cursor.execute("SELECT * FROM signatures WHERE id=?",
                           str(self.signatures[self.responsibleList.currentIndex()][0]))
            responsible = cursor.fetchone()
            self.cert_data["name"] = str(responsible[1]).upper()
            self.cert_data["register"] = str(responsible[4]).upper()
            generate_certificate_responsible(self.save_folder, self.cert_data)

    def generate_send(self):
        if len(self.clients) == 0:
            self.errorMsg.setText("Primeiro inscreva clientes!")
        else:
            self.generate()
            self.mailer = Mailer()
            self.mailer.connect()
            for client in self.clients:
                cursor.execute("SELECT name,email FROM clients WHERE id=?",str(client[1]))
                client_data = cursor.fetchone()

                filepath = self.save_folder+"/"+client_data[0].replace(" ","").upper()+".pdf"
                self.mailer.send_certificate(filepath,client_data[1])

            cursor.execute("SELECT name,email FROM signatures WHERE id=?",
                           self.signatures[self.responsibleList.currentIndex()][0])
            responsible = cursor.fetchone()
            filepath = self.save_folder+"/responsible.pdf"
            self.mailer.send_certificate(filepath,responsible[3])

            self.mailer.quit()

class AddClientDialog(QtGui.QDialog):

    def __init__(self, certificates_instance, event_id):
        super(AddClientDialog,self).__init__()
        self.event_id = event_id
        self.certificates_instance = certificates_instance

        cursor.execute("SELECT * FROM clients")
        self.clients = cursor.fetchall()

        self.mainLayout = QtGui.QVBoxLayout()

        self.titleLabel = QtGui.QLabel("Selecione um cliente")
        self.titleLabel.setFont(titleFont)

        self.clientsList = QtGui.QComboBox()
        for client in self.clients:
            self.clientsList.addItem(str(client[1]))

        self.saveBtn = QtGui.QPushButton("Selecionar")
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
