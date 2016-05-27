# -*- coding: utf-8 -*-
import os
import ConfigParser
from shutil import copyfile
from PyQt4 import QtGui, QtCore
from global_functions import titleFont, validar_cnpj
from models import conn,cursor

class InstitutionDataWidget(QtGui.QWidget):

    def __init__(self):
        super(InstitutionDataWidget, self).__init__()
        self.mainLayout = QtGui.QVBoxLayout()
        self.formLayout = QtGui.QFormLayout()

        self.Config = ConfigParser.ConfigParser()

        self.titleLabel = QtGui.QLabel(u"Dados da Instituição", self)
        self.titleLabel.setFont(titleFont)

        self.instName = QtGui.QLabel(u"Nome da Instituição", self)
        self.instNameLineEdit = QtGui.QLineEdit(self)
        self.formLayout.addRow(self.instName, self.instNameLineEdit)

        self.instID = QtGui.QLabel("CNPJ", self) ## national register
        self.instIDLineEdit = QtGui.QLineEdit(self)
        self.instIDLineEdit.setInputMask("99.999.999/9999-99")
        self.formLayout.addRow(self.instID, self.instIDLineEdit)

        self.instPhone = QtGui.QLabel("Telefone", self)
        self.instPhoneLineEdit = QtGui.QLineEdit(self)
        self.instPhoneLineEdit.setInputMask("(99) 09999-9999")
        self.formLayout.addRow(self.instPhone, self.instPhoneLineEdit)

        self.instAddress = QtGui.QLabel(u"Endereço", self)
        self.instAddressTextEdit = QtGui.QTextEdit(self)
        self.formLayout.addRow(self.instAddress, self.instAddressTextEdit)

        self.instLogo = QtGui.QLabel(u"Logo da Instituição", self)
        self.instLogoBtn = QtGui.QPushButton("Upload")
        self.instLogoBtn.clicked.connect(self.upload_logo)
        self.instLogoName = QtGui.QLabel(u"Faça o upload de uma imagem", self)
        self.logoLayout = QtGui.QHBoxLayout()
        self.logoLayout.addWidget(self.instLogoBtn)
        self.logoLayout.addWidget(self.instLogoName)
        self.formLayout.addRow(self.instLogo, self.logoLayout)

        self.errorMsg = QtGui.QLabel("",self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        try:
            self.Config.read("institution.ini")
            self.instNameLineEdit.setText(str(self.Config.get("Main", "name")))
            self.instIDLineEdit.setText(str(self.Config.get("Main", "id")))
            self.instLogoName.setText(str(self.Config.get("Main", "logo")))
            self.instPhoneLineEdit.setText(str(self.Config.get("Contact", "phone")))
            self.instAddressTextEdit.setText(str(self.Config.get("Contact", "address")))
        except:
            pass

        self.saveBtn = QtGui.QPushButton("Salvar")
        self.saveBtn.clicked.connect(self.save_data)

        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addLayout(self.formLayout)
        self.mainLayout.addWidget(self.errorMsg)
        self.mainLayout.addWidget(self.saveBtn)

        self.setLayout(self.mainLayout)

    def upload_logo(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Escolher",
                                                    "Image files (*.jpg *.png *.gif)")
        only_file = filename.split("/")[-1]
        self.instLogoName.setText(only_file)

        img_files = os.listdir("images/")
        for fl in img_files:
            if "logo" in fl:
                os.remove("images/"+fl)

        ext = filename.split(".")[-1]
        new_filename = "images/logo.%s" % ext

        copyfile(filename, new_filename)

    def save_data(self):
        if self.instNameLineEdit.text() == "":
            self.errorMsg.setText("O nome precisa estar preenchido!")
        elif validar_cnpj(self.instIDLineEdit.text()) == False:
            self.errorMsg.setText(u"O CNPJ é inválido!")
        else:
            cfgfile = open("institution.ini", "wb")
            try:
                self.Config.add_section("Main")
                self.Config.add_section("Contact")
                # create new sections
            except:
                pass #just to update sections
            self.Config.set("Main","name",str(self.instNameLineEdit.text()))
            self.Config.set("Main","id",str(self.instIDLineEdit.text()))
            self.Config.set("Main","logo",str(self.instLogoName.text()))
            self.Config.set("Contact","phone",str(self.instPhoneLineEdit.text()))
            self.Config.set("Contact","address",str(self.instAddressTextEdit.toPlainText()))

            self.Config.write(cfgfile)
            cfgfile.close()

class ConfigMailWidget(QtGui.QWidget):

    def __init__(self):
        super(ConfigMailWidget, self).__init__()

        self.mainLayout = QtGui.QVBoxLayout()
        self.formLayout = QtGui.QFormLayout()

        self.Config = ConfigParser.ConfigParser()

        self.titleLabel = QtGui.QLabel(u"Configuração de email", self)
        self.titleLabel.setFont(titleFont)

        self.mailServer = QtGui.QLabel("Servidor SMTP")
        self.mailServerLineEdit = QtGui.QLineEdit(self)
        self.mailServerLineEdit.setPlaceholderText(u"smtp.gmail.com")
        self.formLayout.addRow(self.mailServer, self.mailServerLineEdit)

        self.mailPort = QtGui.QLabel("Porta SMTP")
        self.mailPortLineEdit = QtGui.QLineEdit(self)
        self.mailPortLineEdit.setPlaceholderText("587")
        self.mailPortLineEdit.setValidator(QtGui.QIntValidator(0,9999,self))
        self.formLayout.addRow(self.mailPort, self.mailPortLineEdit)

        self.mailEmail = QtGui.QLabel("Email")
        self.mailEmailLineEdit = QtGui.QLineEdit(self)
        self.mailEmailLineEdit.setPlaceholderText("seu@email.com")
        self.formLayout.addRow(self.mailEmail, self.mailEmailLineEdit)

        self.mailPswd = QtGui.QLabel("Password")
        self.mailPswdLineEdit = QtGui.QLineEdit(self)
        self.mailPswdLineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.formLayout.addRow(self.mailPswd, self.mailPswdLineEdit)

        self.errorMsg = QtGui.QLabel("",self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        self.saveBtn = QtGui.QPushButton("Salvar")
        self.saveBtn.clicked.connect(self.save_data)

        try:
            self.Config.read("institution.ini")
            self.mailServerLineEdit.setText(str(self.Config.get("Mail","server")))
            self.mailPortLineEdit.setText(str(self.Config.get("Mail","port")))
            self.mailEmailLineEdit.setText(str(self.Config.get("Mail","email")))
            self.mailPswdLineEdit.setText(str(self.Config.get("Mail","password")))
        except:
            pass

        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addLayout(self.formLayout)
        self.mainLayout.addWidget(self.errorMsg)
        self.mainLayout.addWidget(self.saveBtn)
        self.mainLayout.addStretch()

        self.setLayout(self.mainLayout)

    def save_data(self):
        if self.mailServerLineEdit.text() == "":
            self.errorMsg.setText("O servidor precisa estar preenchido!")
        elif self.mailPortLineEdit.text() == "":
            self.errorMsg.setText("A porta precisa estar preenchida!")
        elif self.mailEmailLineEdit.text() == "":
            self.errorMsg.setText("O email precisa estar preenchido!")
        elif self.mailPswdLineEdit.text() == "":
            self.errorMsg.setText("A senha precisa estar preenchida!")
        else:
            cfgfile = open("institution.ini", "wb")
            try:
                self.Config.add_section("Mail")
                # create new sections
            except:
                pass #just to update sections

            self.Config.set("Mail","server",str(self.mailServerLineEdit.text()))
            self.Config.set("Mail","port",str(self.mailPortLineEdit.text()))
            self.Config.set("Mail","email",str(self.mailEmailLineEdit.text()))
            self.Config.set("Mail","password",str(self.mailPswdLineEdit.text()))

            self.Config.write(cfgfile)
            cfgfile.close()


class SignaturesListWidget(QtGui.QWidget):

    def __init__(self):
        super(SignaturesListWidget, self).__init__()

        self.mainLayout = QtGui.QVBoxLayout()
        self.listLayout = QtGui.QHBoxLayout()
        self.btnsLayout = QtGui.QVBoxLayout()

        self.titleLabel = QtGui.QLabel(u"Assinaturas cadastradas", self)
        self.titleLabel.setFont(titleFont)

        self.addBtn = QtGui.QPushButton("Adicionar")
        self.addBtn.clicked.connect(self.add_signature)
        self.editBtn = QtGui.QPushButton("Editar")
        self.editBtn.clicked.connect(self.update_signature)
        self.removeBtn = QtGui.QPushButton("Remover")
        self.removeBtn.clicked.connect(self.remove_signature)
        self.btnsLayout.addWidget(self.addBtn)
        self.btnsLayout.addWidget(self.editBtn)
        self.btnsLayout.addWidget(self.removeBtn)
        self.btnsLayout.addStretch()

        self.signaturesList = QtGui.QListWidget()
        self.load_list()

        self.errorMsg = QtGui.QLabel("",self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        self.listLayout.addWidget(self.signaturesList)
        self.listLayout.addLayout(self.btnsLayout)

        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addLayout(self.listLayout)
        self.mainLayout.addWidget(self.errorMsg)

        self.setLayout(self.mainLayout)

    def load_list(self):
        self.signaturesList.clear()

        cursor.execute("SELECT * FROM signatures")
        self.signatures = cursor.fetchall()

        for sig in self.signatures:
            self.signaturesList.addItem(sig[1])

    def add_signature(self):
        self.add_sig_widget = SignaturesDialog(self)
        self.add_sig_widget.show()

    def update_signature(self):
        try:
            sig_id = self.signatures[self.signaturesList.currentRow()][0]
            self.update_sig_widget = SignaturesDialog(self, sig_id)
            self.update_sig_widget.show()
        except IndexError:
            self.errorMsg.setText("Selecione um registro existente!")

    def remove_signature(self):
        try:
            sig_id = self.signatures[self.signaturesList.currentRow()][0]
            choice = QtGui.QMessageBox.question(self, "Apagar assinatura",
            "Tem certeza que deseja apagar esta assinatura?",
            QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No)
            if choice == QtGui.QMessageBox.Yes:
                cursor.execute("DELETE FROM signatures WHERE id=?", str(sig_id))
                conn.commit()
            else:
                pass
            self.load_list()
        except IndexError:
            self.errorMsg.setText("Selecione um registro existente!")


class SignaturesDialog(QtGui.QDialog):

    def __init__(self, sig_list_instance, sig_id=None):
        super(SignaturesDialog, self).__init__()
        self.setGeometry(450,300,450,150)
        self.sig_id = sig_id
        self.sig_list_instance = sig_list_instance
        self.filename = None
        sig_name = str(self.sig_id)+".png"

        self.mainLayout = QtGui.QVBoxLayout()
        self.formLayout = QtGui.QFormLayout()
        self.uploadLayout = QtGui.QHBoxLayout()

        self.sigName = QtGui.QLabel("Nome Completo", self)
        self.sigNameLineEdit = QtGui.QLineEdit(self)
        self.sigNameLineEdit.setPlaceholderText("Ex: Fulano da Silva")
        self.formLayout.addRow(self.sigName, self.sigNameLineEdit)

        self.sigRole = QtGui.QLabel("Cargo", self)
        self.sigRoleLineEdit = QtGui.QLineEdit(self)
        self.sigRoleLineEdit.setPlaceholderText("Ex: Presidente")
        self.formLayout.addRow(self.sigRole, self.sigRoleLineEdit)

        self.sigRegister = QtGui.QLabel("CPF", self)
        self.sigRegisterLineEdit = QtGui.QLineEdit(self)
        self.sigRegisterLineEdit.setInputMask("999.999.999-99")
        self.formLayout.addRow(self.sigRegister, self.sigRegisterLineEdit)

        self.sigEmail = QtGui.QLabel("Email", self)
        self.sigEmailLineEdit = QtGui.QLineEdit(self)
        self.sigEmailLineEdit.setPlaceholderText("Ex: seu@email.com")
        self.formLayout.addRow(self.sigEmail, self.sigEmailLineEdit)

        self.sigUpload = QtGui.QLabel("Upload da Assinatura", self)
        self.sigUploadBtn = QtGui.QPushButton("Upload")
        self.sigUploadBtn.clicked.connect(self.upload_signature)
        self.uploadLayout.addWidget(self.sigUploadBtn)
        if not sig_name in os.listdir("signatures/"):
            self.sigUploadName = QtGui.QLabel(u"Faça o upload da assinatura", self)
            self.uploadLayout.addWidget(self.sigUploadName)
        self.formLayout.addRow(self.sigUpload, self.uploadLayout)

        self.errorMsg = QtGui.QLabel("",self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        self.saveBtn = QtGui.QPushButton("Salvar")
        self.saveBtn.clicked.connect(self.save_data)

        if self.sig_id:
            self.setWindowTitle("Editar assinatura")
            self.titleLabel = QtGui.QLabel("Editar assinatura", self)
            self.titleLabel.setFont(titleFont)

            cursor.execute("SELECT * FROM signatures WHERE id=?",str(self.sig_id))
            data = cursor.fetchone()

            self.sigNameLineEdit.setText(str(data[1]))
            self.sigRoleLineEdit.setText(str(data[2]))
        else:
            self.setWindowTitle("Cadastrar assinatura")
            self.titleLabel = QtGui.QLabel("Cadastrar assinatura", self)
            self.titleLabel.setFont(titleFont)

        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addLayout(self.formLayout)
        self.mainLayout.addWidget(self.errorMsg)
        self.mainLayout.addWidget(self.saveBtn)

        self.setLayout(self.mainLayout)

    def upload_signature(self):
        self.filename = QtGui.QFileDialog.getOpenFileName(self, "Escolher",
                                                    "Image files (*.png)")

        only_file = self.filename.split("/")[-1]
        self.sigUploadName.setText(only_file)

    def save_data(self):
        if self.sigNameLineEdit.text() == "":
            self.errorMsg.setText("O nome precisa estar preenchido!")
        elif self.sigRoleLineEdit.text() == "":
            self.errorMsg.setText("O cargo precisa estar preenchido!")
        elif self.sigEmailLineEdit.text() == "":
            self.errorMsg.setText("O email precisa estar preenchido!")
        elif self.sigUploadName.text() == u"Faça o upload da assinatura":
            self.errorMsg.setText(u"É necessário fazer upload da assinatura em .png!")
        else:
            if self.sig_id:
                cursor.execute("""
                               UPDATE signatures
                               SET name=?,
                               role=?,
                               email=?,
                               register=?
                               WHERE id=?
                               """,(
                               str(self.sigNameLineEdit.text()),
                               str(self.sigRoleLineEdit.text()),
                               str(self.sigEmailLineEdit.text()),
                               str(self.sigRegisterLineEdit.text()),
                               str(self.sig_id)
                               ))
            else:
                cursor.execute("INSERT INTO signatures VALUES (NULL,?,?,?,?)",
                              (
                                str(self.sigNameLineEdit.text()),
                                str(self.sigRoleLineEdit.text()),
                                str(self.sigEmailLineEdit.text()),
                                str(self.sigRegisterLineEdit.text())
                              ))
                self.sig_id = cursor.lastrowid

            if self.filename:
                new_filename = "signatures/"+str(self.sig_id)+".png"
                copyfile(self.filename, new_filename)

            conn.commit()
            self.sig_list_instance.load_list()
            self.hide()
