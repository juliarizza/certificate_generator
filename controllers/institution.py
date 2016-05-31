# -*- coding: utf-8 -*-
import os
import ConfigParser
from shutil import copyfile

from PyQt4 import QtGui, QtCore

from global_functions import app_dir, titleFont, validar_cnpj
from models import conn, cursor


class InstitutionDataWidget(QtGui.QWidget):
    """
        Creates the frame that contains the form to insert institution data.
    """

    def __init__(self):
        """
            Setup widgets and select data from de .ini file.
        """
        super(InstitutionDataWidget, self).__init__()
        # Defines all layouts
        self.mainLayout = QtGui.QVBoxLayout()
        self.formLayout = QtGui.QFormLayout()

        # Initialize ConfigParser
        self.Config = ConfigParser.ConfigParser()

        # Window config
        self.titleLabel = QtGui.QLabel(u"Dados da Instituição", self)
        self.titleLabel.setFont(titleFont)

        # Name field
        self.instName = QtGui.QLabel(u"Nome da Instituição", self)
        self.instNameLineEdit = QtGui.QLineEdit(self)
        self.formLayout.addRow(self.instName, self.instNameLineEdit)

        # Register field
        self.instID = QtGui.QLabel(u"CNPJ", self)
        self.instIDLineEdit = QtGui.QLineEdit(self)
        # Mask for brazilian CNPJ
        self.instIDLineEdit.setInputMask(u"99.999.999/9999-99")
        self.formLayout.addRow(self.instID, self.instIDLineEdit)

        # Phone field
        self.instPhone = QtGui.QLabel(u"Telefone", self)
        self.instPhoneLineEdit = QtGui.QLineEdit(self)
        self.instPhoneLineEdit.setInputMask(u"(99) 09999-9999")
        self.formLayout.addRow(self.instPhone, self.instPhoneLineEdit)

        # Address field
        self.instAddress = QtGui.QLabel(u"Endereço", self)
        self.instAddressTextEdit = QtGui.QTextEdit(self)
        self.formLayout.addRow(self.instAddress, self.instAddressTextEdit)

        # Logo field
        self.instLogo = QtGui.QLabel(u"Logo da Instituição", self)
        self.instLogoBtn = QtGui.QPushButton(u"Upload")
        self.instLogoBtn.clicked.connect(self.upload_logo)
        self.instLogoName = QtGui.QLabel(u"Faça o upload de uma imagem", self)
        # Add logo buttons and labels to an horizontal layout
        self.logoLayout = QtGui.QHBoxLayout()
        self.logoLayout.addWidget(self.instLogoBtn)
        self.logoLayout.addWidget(self.instLogoName)
        self.formLayout.addRow(self.instLogo, self.logoLayout)

        # A label for showing errors
        self.errorMsg = QtGui.QLabel(u"", self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        # Verifies if the .ini file exists
        try:
            # If there is existing info in the .ini file
            # fills the form with it

            # Read the .ini file
            self.Config.read(app_dir+"institution.ini")

            # Fills the Main info
            self.instNameLineEdit.setText(
                unicode(self.Config.get("Main", "name"))
            )
            self.instIDLineEdit.setText(
                unicode(self.Config.get("Main", "id"))
            )
            self.instLogoName.setText(
                unicode(self.Config.get("Main", "logo"))
            )

            # Fills the Contact info
            self.instPhoneLineEdit.setText(
                unicode(self.Config.get("Contact", "phone"))
            )
            self.instAddressTextEdit.setText(
                unicode(self.Config.get("Contact", "address"))
            )
        except:
            pass

        # Save button
        self.saveBtn = QtGui.QPushButton(u"Salvar")
        self.saveBtn.clicked.connect(self.save_data)

        # Add all widgets to the mainLayout
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addLayout(self.formLayout)
        self.mainLayout.addWidget(self.errorMsg)
        self.mainLayout.addWidget(self.saveBtn)

        # Set the mainLayout as the visible layout
        self.setLayout(self.mainLayout)

    def upload_logo(self):
        """
            Uploads and stores the logo file.
        """
        # Grabs the file
        filename = QtGui.QFileDialog.getOpenFileName(
            self, u"Escolher",
            u"Image files (*.jpg *.png *.gif)"
        )

        # Split to get only the filename
        only_file = os.path.basename(unicode(filename))
        # Shows the filename in the form, as uploaded
        self.instLogoName.setText(only_file)

        # Verifies if there is another logo in the images file
        img_files = os.listdir(os.path.join(app_dir, "images"))
        for fl in img_files:
            if "logo" in fl:
                # If another logo exists, remove it
                os.remove(os.path.join(app_dir, "images", fl))

        # Change the filename of the new logo to "logo.extension"
        ext = filename.split(".")[-1]
        new_filename = os.path.join(app_dir, "images", "logo.{0}".format(ext))

        # Copy the logo file to the images folder
        copyfile(filename, new_filename)

    def save_data(self):
        """
            Saves the institution data in the .ini file.
        """
        # Verifies if all main fields were filled
        if unicode(self.instNameLineEdit.text()) == "":
            self.errorMsg.setText(u"O nome precisa estar preenchido!")
        elif validar_cnpj(unicode(self.instIDLineEdit.text())) is False:
            self.errorMsg.setText(u"O CNPJ é inválido!")
        else:
            # Open the .ini file
            cfgfile = open(app_dir+"institution.ini", "wb")

            # If the sections of the .ini file already exists, do nothing
            # else, create the section
            try:
                self.Config.add_section("Main")
                self.Config.add_section("Contact")
            except:
                pass

            # Fill the Main section
            self.Config.set("Main", "name",
                            str(self.instNameLineEdit.text()))
            self.Config.set("Main", "id",
                            str(self.instIDLineEdit.text()))

            # Fill the Contact section
            self.Config.set("Contact", "phone",
                            str(self.instPhoneLineEdit.text()))
            self.Config.set("Contact", "address",
                            str(self.instAddressTextEdit.toPlainText()))

            if unicode(self.instLogoName.text()) != \
                    u"Faça o upload de uma imagem":
                # If we uploaded the logo, then save it's original name
                # just for showing the user what file we are using
                self.Config.set("Main", "logo",
                                str(self.instLogoName.text()))
            else:
                # If we did not upload the logo, then there is no name
                self.Config.set("Main", "logo", "")

            # Write changes to the .ini file
            self.Config.write(cfgfile)
            cfgfile.close()


class ConfigMailWidget(QtGui.QWidget):
    """
        A frame with a form to fill the email info, so the app
        can send emails using the institution account.
    """

    def __init__(self):
        """
            Setup widgets and connect to the .ini file.
        """
        super(ConfigMailWidget, self).__init__()

        # Defines all layouts
        self.mainLayout = QtGui.QVBoxLayout()
        self.formLayout = QtGui.QFormLayout()

        # Initialize the ConfigParser
        self.Config = ConfigParser.ConfigParser()

        # Window config
        self.titleLabel = QtGui.QLabel(u"Configuração de email", self)
        self.titleLabel.setFont(titleFont)

        # Server field
        self.mailServer = QtGui.QLabel(u"Servidor SMTP")
        self.mailServerLineEdit = QtGui.QLineEdit(self)
        self.mailServerLineEdit.setPlaceholderText(u"Ex: smtp.gmail.com")
        self.formLayout.addRow(self.mailServer, self.mailServerLineEdit)

        # Port field
        self.mailPort = QtGui.QLabel(u"Porta SMTP")
        self.mailPortLineEdit = QtGui.QLineEdit(self)
        self.mailPortLineEdit.setPlaceholderText(u"Ex: 587")
        self.mailPortLineEdit.setValidator(QtGui.QIntValidator(0, 9999, self))
        self.formLayout.addRow(self.mailPort, self.mailPortLineEdit)

        # Email field
        self.mailEmail = QtGui.QLabel(u"Email")
        self.mailEmailLineEdit = QtGui.QLineEdit(self)
        self.mailEmailLineEdit.setPlaceholderText(u"Ex: seu@email.com")
        self.formLayout.addRow(self.mailEmail, self.mailEmailLineEdit)

        # Password field
        self.mailPswd = QtGui.QLabel(u"Password")
        self.mailPswdLineEdit = QtGui.QLineEdit(self)
        self.mailPswdLineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.formLayout.addRow(self.mailPswd, self.mailPswdLineEdit)

        # A label for showing errors
        self.errorMsg = QtGui.QLabel(u"", self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        # Save button
        self.saveBtn = QtGui.QPushButton(u"Salvar")
        self.saveBtn.clicked.connect(self.save_data)

        # Verifies if the .ini file exists
        try:
            # If the .ini file exists, fill the form
            # with the info saved in it

            # Read the .ini file
            self.Config.read("institution.ini")

            # Get Mail info
            self.mailServerLineEdit.setText(
                unicode(self.Config.get("Mail", "server"))
            )
            self.mailPortLineEdit.setText(
                unicode(self.Config.get("Mail", "port"))
            )
            self.mailEmailLineEdit.setText(
                unicode(self.Config.get("Mail", "email"))
            )
            self.mailPswdLineEdit.setText(
                unicode(self.Config.get("Mail", "password"))
            )
        except:
            pass

        # Add all widgets to the mainLayout
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addLayout(self.formLayout)
        self.mainLayout.addWidget(self.errorMsg)
        self.mainLayout.addWidget(self.saveBtn)
        self.mainLayout.addStretch()

        # Set the mainLayout as the visible layout
        self.setLayout(self.mainLayout)

    def save_data(self):
        """
            Saves the mail data in the .ini file.
        """

        # Verifies if all fields are filled
        if unicode(self.mailServerLineEdit.text()) == "":
            self.errorMsg.setText(u"O servidor precisa estar preenchido!")
        elif unicode(self.mailPortLineEdit.text()) == "":
            self.errorMsg.setText(u"A porta precisa estar preenchida!")
        elif unicode(self.mailEmailLineEdit.text()) == "":
            self.errorMsg.setText(u"O email precisa estar preenchido!")
        elif unicode(self.mailPswdLineEdit.text()) == "":
            self.errorMsg.setText(u"A senha precisa estar preenchida!")
        else:
            # Open the .ini file
            cfgfile = open(app_dir+"institution.ini", "wb")

            # Verifies if the Mail section already exists
            # If not, creates it
            try:
                self.Config.add_section("Mail")
            except:
                pass

            # Fill the Mail section
            self.Config.set("Mail", "server",
                            str(self.mailServerLineEdit.text()))
            self.Config.set("Mail", "port",
                            str(self.mailPortLineEdit.text()))
            self.Config.set("Mail", "email",
                            str(self.mailEmailLineEdit.text()))
            self.Config.set("Mail", "password",
                            str(self.mailPswdLineEdit.text()))

            # Write the data
            self.Config.write(cfgfile)
            cfgfile.close()


class SignaturesListWidget(QtGui.QWidget):
    """
        A frame to show a list of existing signatures
        and CRUD options.
    """

    def __init__(self):
        """
            Setup widgets and select signatures data from the database.
        """
        super(SignaturesListWidget, self).__init__()

        # Defines all layouts
        self.mainLayout = QtGui.QVBoxLayout()
        self.listLayout = QtGui.QHBoxLayout()
        self.btnsLayout = QtGui.QVBoxLayout()

        # Window config
        self.titleLabel = QtGui.QLabel(u"Assinaturas cadastradas", self)
        self.titleLabel.setFont(titleFont)

        # Creates the btnsLayout and adds CRUD buttons
        self.addBtn = QtGui.QPushButton(u"Adicionar")
        self.addBtn.clicked.connect(self.add_signature)
        self.editBtn = QtGui.QPushButton(u"Editar")
        self.editBtn.clicked.connect(self.update_signature)
        self.removeBtn = QtGui.QPushButton(u"Remover")
        self.removeBtn.clicked.connect(self.remove_signature)
        self.btnsLayout.addWidget(self.addBtn)
        self.btnsLayout.addWidget(self.editBtn)
        self.btnsLayout.addWidget(self.removeBtn)
        self.btnsLayout.addStretch()

        # Create a list widget for showing existing signatures
        self.signaturesList = QtGui.QListWidget()
        # Loads all signatures
        self.load_list()

        # A label for showing errors
        self.errorMsg = QtGui.QLabel(u"", self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        # Add widgets to an horizontal layout
        self.listLayout.addWidget(self.signaturesList)
        self.listLayout.addLayout(self.btnsLayout)

        # Add all widgets to the mainLayout
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addLayout(self.listLayout)
        self.mainLayout.addWidget(self.errorMsg)

        # Set the mainLayout as the visible layout
        self.setLayout(self.mainLayout)

    def load_list(self):
        """
            Updates the list widget with the signatures data.
        """

        # Clear the list widget to add new data
        self.signaturesList.clear()

        # Select all signatures
        cursor.execute("SELECT * FROM signatures ORDER BY name ASC")
        self.signatures = cursor.fetchall()

        # Add all signatures to the list widget
        for sig in self.signatures:
            self.signaturesList.addItem(unicode(sig[1]))

    def add_signature(self):
        """
            Register a new signature.
        """
        # Open a dialog with a form for creating a new signature
        self.add_sig_widget = SignaturesDialog(self)
        self.add_sig_widget.show()

    def update_signature(self):
        """
            Edit an existing signature.
        """
        # Verifies if there is a selectd signature
        try:
            # Gets the selected signature id
            sig_id = self.signatures[self.signaturesList.currentRow()][0]
            # Opens a dialog with a form filled with the signature data
            self.update_sig_widget = SignaturesDialog(self, sig_id)
            self.update_sig_widget.show()
        except IndexError:
            self.errorMsg.setText(u"Selecione um registro existente!")

    def remove_signature(self):
        """
            Delete an existing signature.
        """
        # Verifies if there is a selected signature
        try:
            # Gets the selected signature id
            sig_id = self.signatures[self.signaturesList.currentRow()][0]

            # Asks if the user really wants to delete the signature
            choice = QtGui.QMessageBox.question(
                self, u"Apagar assinatura",
                u"Tem certeza que deseja apagar esta assinatura?",
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
            )

            if choice == QtGui.QMessageBox.Yes:
                os.remove(os.path.join(app_dir, "signatures",
                                       "{0}.png".format(str(sig_id))))
                cursor.execute(
                    "DELETE FROM signatures WHERE id=?",
                    str(sig_id)
                )
                conn.commit()
            else:
                pass

            # Updates the signatures list
            self.load_list()
        except IndexError:
            self.errorMsg.setText(u"Selecione um registro existente!")


class SignaturesDialog(QtGui.QDialog):
    """
        A dialog with a form for register or update signatures.
    """

    def __init__(self, sig_list_instance, sig_id=None):
        """
            Setup widgets.
        """
        super(SignaturesDialog, self).__init__()
        # Window config
        self.setGeometry(450, 300, 450, 150)
        self.sig_id = sig_id
        self.sig_list_instance = sig_list_instance
        self.filename = None
        sig_name = str(self.sig_id)+".png"

        # Define all layouts
        self.mainLayout = QtGui.QVBoxLayout()
        self.formLayout = QtGui.QFormLayout()
        self.uploadLayout = QtGui.QHBoxLayout()

        # Name field
        self.sigName = QtGui.QLabel(u"Nome Completo", self)
        self.sigNameLineEdit = QtGui.QLineEdit(self)
        self.sigNameLineEdit.setPlaceholderText(u"Ex: Fulano da Silva")
        self.formLayout.addRow(self.sigName, self.sigNameLineEdit)

        # Role field
        self.sigRole = QtGui.QLabel(u"Cargo", self)
        self.sigRoleLineEdit = QtGui.QLineEdit(self)
        self.sigRoleLineEdit.setPlaceholderText(u"Ex: Presidente")
        self.formLayout.addRow(self.sigRole, self.sigRoleLineEdit)

        # Register (civil ID) field
        self.sigRegister = QtGui.QLabel(u"CPF", self)
        self.sigRegisterLineEdit = QtGui.QLineEdit(self)
        # Mask for brazilian CPF
        self.sigRegisterLineEdit.setInputMask(u"999.999.999-99")
        self.formLayout.addRow(self.sigRegister, self.sigRegisterLineEdit)

        # Email field
        self.sigEmail = QtGui.QLabel(u"Email", self)
        self.sigEmailLineEdit = QtGui.QLineEdit(self)
        self.sigEmailLineEdit.setPlaceholderText(u"Ex: seu@email.com")
        self.formLayout.addRow(self.sigEmail, self.sigEmailLineEdit)

        # Upload field
        self.sigUpload = QtGui.QLabel(u"Upload da Assinatura", self)
        self.sigUploadBtn = QtGui.QPushButton(u"Upload")
        self.sigUploadBtn.clicked.connect(self.upload_signature)
        self.uploadLayout.addWidget(self.sigUploadBtn)
        if sig_name not in os.listdir(os.path.join(app_dir, "signatures")):
            self.sigUploadName = QtGui.QLabel(
                u"Faça o upload da assinatura", self)
            self.uploadLayout.addWidget(self.sigUploadName)
        else:
            self.sigUploadName = QtGui.QLabel("", self)
        self.formLayout.addRow(self.sigUpload, self.uploadLayout)

        # A label for showing errors
        self.errorMsg = QtGui.QLabel(u"", self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        # Save button
        self.saveBtn = QtGui.QPushButton(u"Salvar")
        self.saveBtn.clicked.connect(self.save_data)

        # Verifies if the user is creating or updating the signature
        # If updating, fills the form with the record data
        if self.sig_id:
            # Window config
            self.setWindowTitle(u"Editar assinatura")
            self.titleLabel = QtGui.QLabel(u"Editar assinatura", self)
            self.titleLabel.setFont(titleFont)

            # Select the signature data
            cursor.execute(
                "SELECT * FROM signatures WHERE id=?",
                str(self.sig_id)
            )
            data = cursor.fetchone()

            # Fills the form with the data
            self.sigNameLineEdit.setText(unicode(data[1]))
            self.sigRoleLineEdit.setText(unicode(data[2]))
            self.sigEmailLineEdit.setText(unicode(data[3]))
            self.sigRegisterLineEdit.setText(unicode(data[4]))
        else:
            # Window config
            self.setWindowTitle(u"Cadastrar assinatura")
            self.titleLabel = QtGui.QLabel(u"Cadastrar assinatura", self)
            self.titleLabel.setFont(titleFont)

        # Add all widgets to the mainLayout
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addLayout(self.formLayout)
        self.mainLayout.addWidget(self.errorMsg)
        self.mainLayout.addWidget(self.saveBtn)

        # Set the mainLayout as the visible layout
        self.setLayout(self.mainLayout)

    def upload_signature(self):
        """
            Uploads the signature image.
        """
        # Asks for the signature image file
        self.filename = QtGui.QFileDialog.getOpenFileName(
            self, u"Escolher",
            u"Image files (*.png)"
        )

        # Gets only the filename
        only_file = os.path.basename(unicode(self.filename))
        self.sigUploadName.setText(only_file)

    def save_data(self):
        """
            Save the signature data.
        """

        # Verifies if all fields are filled
        if unicode(self.sigNameLineEdit.text()) == "":
            self.errorMsg.setText(u"O nome precisa estar preenchido!")
        elif unicode(self.sigRoleLineEdit.text()) == "":
            self.errorMsg.setText(u"O cargo precisa estar preenchido!")
        elif unicode(self.sigEmailLineEdit.text()) == "":
            self.errorMsg.setText(u"O email precisa estar preenchido!")
        elif unicode(self.sigUploadName.text()) == \
                u"Faça o upload da assinatura":
            self.errorMsg.setText(u"É necessário fazer upload \
                                  da assinatura em .png!")
        else:
            # Verifies if creating or updating the signature
            if self.sig_id:
                # Updates the signature in the database
                cursor.execute(
                    "UPDATE signatures SET name=?, role=?, email=?, \
                    register=? WHERE id=?",
                    (
                        unicode(self.sigNameLineEdit.text()),
                        unicode(self.sigRoleLineEdit.text()),
                        unicode(self.sigEmailLineEdit.text()),
                        unicode(self.sigRegisterLineEdit.text()),
                        unicode(self.sig_id)
                    )
                )

                # Replace signature image for the new one
                if self.filename:
                    new_filename = os.path.join(
                        app_dir,
                        "signatures",
                        "{0}.png".format(str(self.sig_id))
                    )
                    copyfile(self.filename, new_filename)

                # Save changes to the database
                conn.commit()
                # Updates the signatures list
                self.sig_list_instance.load_list()
                # Hide the dialog
                self.hide()
            else:
                # Verifies if the signature already exists
                cursor.execute(
                    "SELECT id FROM signatures WHERE register=?",
                    [str(self.sigRegisterLineEdit.text())]
                )
                existing_user = cursor.fetchone()

                if existing_user:
                    # If the signature exists, show an error message
                    error = QtGui.QMessageBox()
                    error.setIcon(QtGui.QMessageBox.Critical)
                    error.setText(u"A assinatura já está cadastrada!")
                    error.setInformativeText(u"Já existe uma assinatura \
                                            com este CPF cadastrada \
                                            no programa.")
                    error.setWindowTitle(u"Assinatura já cadastrada!")
                    error.setStandardButtons(QtGui.QMessageBox.Ok)
                    error.exec_()
                else:
                    # Else, insert data in the database
                    cursor.execute(
                        "INSERT INTO signatures VALUES (NULL,?,?,?,?)",
                        (
                            unicode(self.sigNameLineEdit.text()),
                            unicode(self.sigRoleLineEdit.text()),
                            unicode(self.sigEmailLineEdit.text()),
                            unicode(self.sigRegisterLineEdit.text())
                        )
                    )
                    self.sig_id = cursor.lastrowid

                    # Create the new signature file
                    if self.filename:
                        new_filename = os.path.join(
                            app_dir,
                            "signatures",
                            "{0}.png".format(str(self.sig_id))
                        )
                        copyfile(self.filename, new_filename)

                    # Save changes to the database
                    conn.commit()
                    # Updates the signatures list
                    self.sig_list_instance.load_list()
                    # Hide the dialog
                    self.hide()
