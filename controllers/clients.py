# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from models import conn,cursor
from global_functions import titleFont, validar_cpf

class ClientsListWidget(QtGui.QWidget):

    def __init__(self):
        super(ClientsListWidget, self).__init__()

        self.mainLayout = QtGui.QVBoxLayout()
        self.listLayout = QtGui.QHBoxLayout()
        self.btnsLayout = QtGui.QVBoxLayout()

        self.titleLabel = QtGui.QLabel(u"Clientes", self)
        self.titleLabel.setFont(titleFont)

        self.addBtn = QtGui.QPushButton(u"Adicionar")
        self.addBtn.clicked.connect(self.add_client)
        self.editBtn = QtGui.QPushButton(u"Editar")
        self.editBtn.clicked.connect(self.update_client)
        self.removeBtn = QtGui.QPushButton(u"Remover")
        self.removeBtn.clicked.connect(self.remove_client)
        self.btnsLayout.addWidget(self.addBtn)
        self.btnsLayout.addWidget(self.editBtn)
        self.btnsLayout.addWidget(self.removeBtn)
        self.btnsLayout.addStretch()

        self.clientsTable = QtGui.QTableWidget()
        self.load_table()

        self.listLayout.addWidget(self.clientsTable)
        self.listLayout.addLayout(self.btnsLayout)

        self.errorMsg = QtGui.QLabel(u"",self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addLayout(self.listLayout)
        self.mainLayout.addWidget(self.errorMsg)

        self.setLayout(self.mainLayout)

    def load_table(self):
        self.clientsTable.clear()

        cursor.execute("SELECT * FROM clients ORDER BY name ASC")
        data = cursor.fetchall()

        if len(data) < 10:
            self.clientsTable.setRowCount(10)
        else:
            self.clientsTable.setRowCount(len(data))
        self.clientsTable.setColumnCount(4)
        self.clientsTable.setHorizontalHeaderLabels((u"ID",
                                                    u"Nome Completo",
                                                    u"E-mail",
                                                    u"CPF"))
        self.clientsTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.clientsTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        r,c=0,0
        for item in data:
            for i in range(4):
                newitem = QtGui.QTableWidgetItem(unicode(item[i]))
                self.clientsTable.setItem(r,c,newitem)
                c += 1
            r += 1
            c = 0

    def add_client(self):
        self.add_client_widget = ClientDialog(self)
        self.add_client_widget.show()

    def remove_client(self):
        try:
            r = self.clientsTable.currentRow()
            client_id = self.clientsTable.item(r,0).text()
            choice = QtGui.QMessageBox.question(self, u"Apagar cliente",
                                                u"Tem certeza que deseja apagar este cliente?",
                                                QtGui.QMessageBox.Yes |
                                                QtGui.QMessageBox.No)
            if choice == QtGui.QMessageBox.Yes:
                cursor.execute("DELETE FROM clients WHERE id=?", str(client_id))
                conn.commit()
            else:
                pass
            self.load_table()
        except AttributeError:
            self.errorMsg.setText(u"Selecione um registro existente!")

    def update_client(self):
        try:
            r = self.clientsTable.currentRow()
            client_id = self.clientsTable.item(r,0).text()
            self.edit_client_dialog = ClientDialog(self, client_id)
            self.edit_client_dialog.show()
        except AttributeError:
            self.errorMsg.setText(u"Selecione um registro existente!")

class ClientDialog(QtGui.QDialog):

    def __init__(self, clients_list_instance, client_id=None):
        super(ClientDialog,self).__init__()
        self.setGeometry(450,300,400,200)
        self.clients_list_instance = clients_list_instance

        self.client_id = client_id

        self.mainLayout = QtGui.QVBoxLayout()
        self.formLayout = QtGui.QFormLayout()

        self.clientName = QtGui.QLabel(u"Nome completo", self)
        self.clientNameLineEdit = QtGui.QLineEdit(self)
        self.clientNameLineEdit.setPlaceholderText(u"Ex: Fulano da Silva")
        self.formLayout.addRow(self.clientName, self.clientNameLineEdit)

        self.clientEmail = QtGui.QLabel(u"E-mail", self)
        self.clientEmailLineEdit = QtGui.QLineEdit(self)
        self.clientEmailLineEdit.setPlaceholderText(u"Ex: email@cliente.com")
        self.formLayout.addRow(self.clientEmail, self.clientEmailLineEdit)

        self.clientRegister = QtGui.QLabel(u"CPF", self)
        self.clientRegisterLineEdit = QtGui.QLineEdit(self)
        self.clientRegisterLineEdit.setInputMask(u"999.999.999-99") ## Brazil CPF
        self.formLayout.addRow(self.clientRegister, self.clientRegisterLineEdit)

        self.errorMsg = QtGui.QLabel(u"",self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        self.saveBtn = QtGui.QPushButton(u"Salvar")
        self.saveBtn.clicked.connect(self.save_data)

        if self.client_id:
            self.setWindowTitle(u"Editar cliente")
            self.titleLabel = QtGui.QLabel(u"Editar cliente", self)
            self.titleLabel.setFont(titleFont)

            cursor.execute("SELECT * FROM clients WHERE id=?", str(self.client_id))
            data = cursor.fetchone()

            self.clientNameLineEdit.setText(unicode(data[1]))
            self.clientEmailLineEdit.setText(unicode(data[2]))
            self.clientRegisterLineEdit.setText(unicode(data[3]))
        else:
            self.setWindowTitle(u"Cadastrar cliente")
            self.titleLabel = QtGui.QLabel(u"Cadastrar cliente", self)
            self.titleLabel.setFont(titleFont)

        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addLayout(self.formLayout)
        self.mainLayout.addWidget(self.errorMsg)
        self.mainLayout.addWidget(self.saveBtn)

        self.setLayout(self.mainLayout)

    def save_data(self):
        if unicode(self.clientNameLineEdit.text()) == "":
            self.errorMsg.setText(u"O nome precisa estar preenchido!")
        elif unicode(self.clientEmailLineEdit.text()) == "":
            self.errorMsg.setText(u"O email precisa estar preenchido!")
        elif unicode(validar_cpf(self.clientRegisterLineEdit.text())) == False:
            self.errorMsg.setText(u"O CPF é inválido!")
        else:
            if self.client_id:
                cursor.execute("""
                                UPDATE clients
                                SET name=?,
                                email=?,
                                register=?
                                WHERE id=?
                               """,(
                               unicode(self.clientNameLineEdit.text()),
                               unicode(self.clientEmailLineEdit.text()),
                               unicode(self.clientRegisterLineEdit.text()),
                               str(self.client_id)
                               ))
                conn.commit()
                self.clients_list_instance.load_table()
                self.hide()
            else:
                cursor.execute("SELECT id FROM clients WHERE register=?",
                              [str(self.clientRegisterLineEdit.text())])
                existing_user = cursor.fetchone()

                if existing_user:
                    error = QtGui.QMessageBox()
                    error.setIcon(QtGui.QMessageBox.Critical)
                    error.setText(u"O cliente já está cadastrado!")
                    error.setInformativeText(u"Já existe um cliente com este CPF cadastrado no programa.")
                    error.setWindowTitle(u"Cliente já cadastrado!")
                    error.setStandardButtons(QtGui.QMessageBox.Ok)
                    error.exec_()
                else:
                    cursor.execute("INSERT INTO clients VALUES (NULL,?,?,?)",
                                  (
                                    unicode(self.clientNameLineEdit.text()),
                                    unicode(self.clientEmailLineEdit.text()),
                                    unicode(self.clientRegisterLineEdit.text())
                                  ))
                    conn.commit()
                    self.clients_list_instance.load_table()
                    self.hide()
