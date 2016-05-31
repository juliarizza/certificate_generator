# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore

from global_functions import titleFont, validar_cpf
from models import conn, cursor


class ClientsListWidget(QtGui.QWidget):

    """
        Creates the frame with the list of registered clients
        and CRUD options.
    """

    def __init__(self):
        """
            Setup widgets and select client data from the database.
        """
        super(ClientsListWidget, self).__init__()

        # Defines all layouts
        self.mainLayout = QtGui.QVBoxLayout()
        self.listLayout = QtGui.QHBoxLayout()
        self.btnsLayout = QtGui.QVBoxLayout()

        # Window config
        self.titleLabel = QtGui.QLabel(u"Clientes", self)
        self.titleLabel.setFont(titleFont)

        # Creates all buttons and add them to the btnsLayout
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

        # Creates a table widget for showing cilents
        # and loads them
        self.clientsTable = QtGui.QTableWidget()
        self.load_table()

        # Add the btnsLayout and clientsTable to an horizontal layout
        self.listLayout.addWidget(self.clientsTable)
        self.listLayout.addLayout(self.btnsLayout)

        # A label for showing errors
        self.errorMsg = QtGui.QLabel(u"", self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        # Add all widgets to the mainLayout
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addLayout(self.listLayout)
        self.mainLayout.addWidget(self.errorMsg)

        # Set the mainLayout as the visible layout
        self.setLayout(self.mainLayout)

    def load_table(self):
        """
            Populates the clients table with the existing clients.
        """
        # Clears the table to show new records
        self.clientsTable.clear()

        # Select the records to show
        cursor.execute("SELECT * FROM clients ORDER BY name ASC")
        data = cursor.fetchall()

        # Set the table default number of rows to 10
        # If there is more than 10 records, set to the len
        # of the records
        if len(data) < 10:
            self.clientsTable.setRowCount(10)
        else:
            self.clientsTable.setRowCount(len(data))

        # Set columns quantity and name
        self.clientsTable.setColumnCount(4)
        self.clientsTable.setHorizontalHeaderLabels(
            (u"ID", u"Nome Completo", u"E-mail", u"CPF")
        )

        # Make columns and rows fit sizes to the window
        self.clientsTable.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch
        )
        self.clientsTable.verticalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch
        )

        # Updates the table with the selected records
        r,c = 0,0
        for item in data:
            for i in range(4):
                newitem = QtGui.QTableWidgetItem(unicode(item[i]))
                self.clientsTable.setItem(r, c, newitem)
                c += 1
            r += 1
            c = 0

    def add_client(self):
        """
            Register a new client.
        """
        # Opens a dialog with a form to register the new client
        self.add_client_widget = ClientDialog(self)
        self.add_client_widget.show()

    def remove_client(self):
        """
            Delete an existing client.
        """
        # Verifies if there is a selected client
        try:
            # Gets the client id
            r = self.clientsTable.currentRow()
            client_id = self.clientsTable.item(r, 0).text()

            # Asks if the user really wants to remove the client
            choice = QtGui.QMessageBox.question(
                self, u"Apagar cliente",
                u"Tem certeza que deseja apagar este cliente?",
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
            )
            if choice == QtGui.QMessageBox.Yes:
                cursor.execute(
                    "DELETE FROM clients WHERE id=?",
                    str(client_id)
                )
                conn.commit()
            else:
                pass

            # Updates the clients table
            self.load_table()
        except AttributeError:
            self.errorMsg.setText(u"Selecione um registro existente!")

    def update_client(self):
        """
            Edit an existing client.
        """
        # Verifies if there is a selected client
        try:
            # Gets the client id
            r = self.clientsTable.currentRow()
            client_id = self.clientsTable.item(r, 0).text()
            # Open a dialog with a form to edit the client data
            self.edit_client_dialog = ClientDialog(self, client_id)
            self.edit_client_dialog.show()
        except AttributeError:
            self.errorMsg.setText(u"Selecione um registro existente!")


class ClientDialog(QtGui.QDialog):
    """
        A dialog with a form to fill client data for creating
        a new client or editing an existing one.
    """

    def __init__(self, clients_list_instance, client_id=None):
        """
            Setup widgets.
        """
        super(ClientDialog, self).__init__()
        # Window config
        self.setGeometry(450, 300, 400, 200)
        self.clients_list_instance = clients_list_instance
        self.client_id = client_id

        # Defines all layouts
        self.mainLayout = QtGui.QVBoxLayout()
        self.formLayout = QtGui.QFormLayout()

        # Name field
        self.clientName = QtGui.QLabel(u"Nome completo", self)
        self.clientNameLineEdit = QtGui.QLineEdit(self)
        self.clientNameLineEdit.setPlaceholderText(u"Ex: Fulano da Silva")
        self.formLayout.addRow(self.clientName, self.clientNameLineEdit)

        # E-mail field
        self.clientEmail = QtGui.QLabel(u"E-mail", self)
        self.clientEmailLineEdit = QtGui.QLineEdit(self)
        self.clientEmailLineEdit.setPlaceholderText(u"Ex: email@cliente.com")
        self.formLayout.addRow(self.clientEmail, self.clientEmailLineEdit)

        # Register (civil ID) field
        self.clientRegister = QtGui.QLabel(u"CPF", self)
        self.clientRegisterLineEdit = QtGui.QLineEdit(self)
        # Mask for brazililian CPF
        self.clientRegisterLineEdit.setInputMask(u"999.999.999-99")
        self.formLayout.addRow(
            self.clientRegister,
            self.clientRegisterLineEdit
        )

        # A label for showing errors
        self.errorMsg = QtGui.QLabel(u"", self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        # Save button
        self.saveBtn = QtGui.QPushButton(u"Salvar")
        self.saveBtn.clicked.connect(self.save_data)

        # If we are editing a client, it will show a filled form
        # if not, shows an empty form
        if self.client_id:
            # Window config
            self.setWindowTitle(u"Editar cliente")
            self.titleLabel = QtGui.QLabel(u"Editar cliente", self)
            self.titleLabel.setFont(titleFont)

            # Select the existing client data
            cursor.execute(
                "SELECT * FROM clients WHERE id=?",
                str(self.client_id)
            )
            data = cursor.fetchone()

            # Fills the form with the data
            self.clientNameLineEdit.setText(unicode(data[1]))
            self.clientEmailLineEdit.setText(unicode(data[2]))
            self.clientRegisterLineEdit.setText(unicode(data[3]))
        else:
            # Window config
            self.setWindowTitle(u"Cadastrar cliente")
            self.titleLabel = QtGui.QLabel(u"Cadastrar cliente", self)
            self.titleLabel.setFont(titleFont)

        # Add all widgets to the mainLayout
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addLayout(self.formLayout)
        self.mainLayout.addWidget(self.errorMsg)
        self.mainLayout.addWidget(self.saveBtn)

        # Set the mainLayout as the visible layout
        self.setLayout(self.mainLayout)

    def save_data(self):
        """
            Saves the client data.
        """
        # Verifies if all fields are filled
        if unicode(self.clientNameLineEdit.text()) == "":
            self.errorMsg.setText(u"O nome precisa estar preenchido!")
        elif unicode(self.clientEmailLineEdit.text()) == "":
            self.errorMsg.setText(u"O email precisa estar preenchido!")
        elif unicode(validar_cpf(self.clientRegisterLineEdit.text())) is False:
            self.errorMsg.setText(u"O CPF é inválido!")
        else:
            if self.client_id:
                # Updates the record if it is an existing client
                cursor.execute(
                    "UPDATE clients SET name=?, email=?, register=? \
                    WHERE id=?",
                    (
                        unicode(self.clientNameLineEdit.text()),
                        unicode(self.clientEmailLineEdit.text()),
                        unicode(self.clientRegisterLineEdit.text()),
                        str(self.client_id)
                    )
                )
                conn.commit()
                # Updates the table
                self.clients_list_instance.load_table()
                # Hide the dialog
                self.hide()
            else:
                # Verifies if the user is trying to
                # register an existent client
                cursor.execute(
                    "SELECT id FROM clients WHERE register=?",
                    [str(self.clientRegisterLineEdit.text())]
                )
                existing_user = cursor.fetchone()

                if existing_user:
                    # Shows up an error message
                    error = QtGui.QMessageBox()
                    error.setIcon(QtGui.QMessageBox.Critical)
                    error.setText(u"O cliente já está cadastrado!")
                    error.setInformativeText(u"Já existe um cliente \
                                            com este CPF cadastrado \
                                            no programa.")
                    error.setWindowTitle(u"Cliente já cadastrado!")
                    error.setStandardButtons(QtGui.QMessageBox.Ok)
                    error.exec_()
                else:
                    # Register the client
                    cursor.execute(
                        "INSERT INTO clients VALUES (NULL,?,?,?)",
                        (
                            unicode(self.clientNameLineEdit.text()),
                            unicode(self.clientEmailLineEdit.text()),
                            unicode(self.clientRegisterLineEdit.text())
                        )
                    )
                    conn.commit()
                    # Updates the table
                    self.clients_list_instance.load_table()
                    # Hide the dialog
                    self.hide()
