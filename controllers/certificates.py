# -*- coding: utf-8 -*-
import os
import ConfigParser

from PyQt4 import QtGui, QtCore

from global_functions import app_dir, titleFont
from models import conn, cursor, \
                    generate_certificate, \
                    Mailer


class CertificatesWidget(QtGui.QWidget):

    """
        Creates the frame with options for certificate preview,
        generation and mailing.
    """

    def __init__(self):
        """
            Setup widgets and select data from database.
        """
        super(CertificatesWidget, self).__init__()
        # Window settings
        self.save_folder = ""

        # Connects with configuration file to get info
        self.Config = ConfigParser.ConfigParser()
        self.Config.read(os.path.join(app_dir, "institution.ini"))

        cursor.execute("SELECT * FROM events ORDER BY id DESC")
        self.events = cursor.fetchall()

        cursor.execute("SELECT * FROM signatures ORDER BY name ASC")
        self.signatures = cursor.fetchall()

        # Defines all layouts
        self.mainLayout = QtGui.QVBoxLayout()
        self.listLayout = QtGui.QHBoxLayout()
        self.btnsLayout = QtGui.QVBoxLayout()
        self.respLayout = QtGui.QVBoxLayout()
        self.instLayout = QtGui.QVBoxLayout()
        self.combosLayoutH = QtGui.QHBoxLayout()
        self.generateBtnsLayout = QtGui.QHBoxLayout()

        # Window config
        self.titleLabel = QtGui.QLabel(u"Certificados", self)
        self.titleLabel.setFont(titleFont)

        # Make buttons layout
        self.addBtn = QtGui.QPushButton(u"Adicionar")
        self.addBtn.clicked.connect(self.add_client)
        self.removeBtn = QtGui.QPushButton(u"Remover")
        self.removeBtn.clicked.connect(self.remove_client)
        self.btnsLayout.addWidget(self.addBtn)
        self.btnsLayout.addWidget(self.removeBtn)
        self.btnsLayout.addStretch()

        # Fill combobox with event info
        self.eventsListName = QtGui.QLabel(u"Selecione um evento:", self)
        self.eventsList = QtGui.QComboBox()
        for event in self.events:
            self.eventsList.addItem(unicode(event[1]))
        self.eventsList.currentIndexChanged.connect(self.load_list)

        # Fill listwidget with subscriptions info
        self.subscriptionListName = QtGui.QLabel(u"Inscritos", self)
        self.subscriptionList = QtGui.QListWidget()
        self.load_list()

        # Fill both responsible and institution combos
        # with signatures info
        self.responsibleListName = QtGui.QLabel(
            u"Selecione um responsável/ministrante:",
            self
        )
        self.responsibleList = QtGui.QComboBox()

        self.institutionListName = QtGui.QLabel(
            u"Assinatura da instituição:",
            self
        )
        self.institutionList = QtGui.QComboBox()

        for sig in self.signatures:
            self.responsibleList.addItem(unicode(sig[1]))
            self.institutionList.addItem(unicode(sig[1]))

        # A label for showing errors
        self.errorMsg = QtGui.QLabel(u"", self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        # Defines buttons for preview, generate and mail certificates
        self.previewBtn = QtGui.QPushButton(u"Preview")
        self.previewBtn.clicked.connect(self.preview_certificate)
        self.generateBtn = QtGui.QPushButton(u"Gerar!")
        self.generateBtn.clicked.connect(self.generate)
        self.generateSendBtn = QtGui.QPushButton(u"Gerar e enviar por email!")
        self.generateSendBtn.clicked.connect(self.generate_send)
        # Add them to generateBtnsLayout
        self.generateBtnsLayout.addWidget(self.previewBtn)
        self.generateBtnsLayout.addWidget(self.generateBtn)
        self.generateBtnsLayout.addWidget(self.generateSendBtn)

        # Add subscriptions list to listLayout
        self.listLayout.addWidget(self.subscriptionList)
        self.listLayout.addLayout(self.btnsLayout)

        # Add signatures info to their specific layouts
        self.respLayout.addWidget(self.responsibleListName)
        self.respLayout.addWidget(self.responsibleList)
        self.instLayout.addWidget(self.institutionListName)
        self.instLayout.addWidget(self.institutionList)
        self.combosLayoutH.addLayout(self.respLayout)
        self.combosLayoutH.addLayout(self.instLayout)

        # Add everything to the mainLayout
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(self.eventsListName)
        self.mainLayout.addWidget(self.eventsList)
        self.mainLayout.addWidget(self.subscriptionListName)
        self.mainLayout.addLayout(self.listLayout)
        self.mainLayout.addLayout(self.combosLayoutH)
        self.mainLayout.addWidget(self.errorMsg)
        self.mainLayout.addLayout(self.generateBtnsLayout)

        # Set the mainLayout as the visible layout
        self.setLayout(self.mainLayout)

    def load_list(self):
        """
            Loads all subscriptions of the selected event
            and insert them in the subscriptionList widget.
        """

        # Get the subscripted clients
        if self.events:
            cursor.execute(
                "SELECT id,client_id FROM subscriptions WHERE event_id=?",
                str(self.events[self.eventsList.currentIndex()][0])
            )
            self.clients = cursor.fetchall()
        else:
            self.clients = []

        # Clears the widget to insert updated info
        self.subscriptionList.clear()

        # Select all subscripted clients and add them
        # to the subscriptionList widget
        for client in self.clients:
            cursor.execute(
                "SELECT name FROM clients WHERE id=?",
                str(client[1])
            )
            client_name = cursor.fetchone()
            if client:
                self.subscriptionList.addItem(unicode(client_name[0]))

    def add_client(self):
        """
            Subscribes a new client to the event.
        """

        # If there is an event selected, get it's ID and passes
        # it to the AddClientDialog.
        # If there is not, shows up an error message.
        try:
            event_id = self.events[self.eventsList.currentIndex()][0]
            self.add_client_widget = AddClientDialog(self, event_id)
            self.add_client_widget.show()
        except IndexError:
            self.errorMsg.setText(u"Selecione um evento existente!")

    def remove_client(self):
        """
            Remove a client from the event's subscriptions.
        """

        # If there is a client selected, removes it.
        # If there is not, shows up an error message.
        try:
            current_subscription = self.subscriptionList.currentRow()
            subscription_id = self.clients[current_subscription][0]
            # Asks if the user really wants to remove the client
            choice = QtGui.QMessageBox.question(
                self, u"Apagar inscrição",
                u"Tem certeza que deseja apagar esta inscrição?",
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
            )
            if choice == QtGui.QMessageBox.Yes:
                cursor.execute(
                    "DELETE FROM subscriptions WHERE id=?",
                    str(subscription_id)
                )
                conn.commit()
            else:
                pass
            self.load_list()
        except IndexError:
            self.errorMsg.setText(u"Selecione um cliente existente!")

    def generate_general(self, preview=False):
        """
            Prepare all general info that needs to be passed whenever
            the user wants to preview, generate or mail a certificate.
        """

        # Asks for subscripted clients to generate certificates
        if len(self.clients) == 0 and not preview:
            self.errorMsg.setText(u"Primeiro inscreva clientes!")
        else:
            # Get the folder where to save the certificates
            self.save_folder = QtGui.QFileDialog.getExistingDirectory(
                None,
                u"Salvar em"
            )

            self.cert_data = {}

            # Collect all data that needs to be passed
            # Selected items
            current_event = self.eventsList.currentIndex()
            current_responsible = self.responsibleList.currentIndex()
            current_institution = self.institutionList.currentIndex()

            if current_event == -1:
                self.errorMsg.setText(u"Primeiro cadastre um evento!")
                return 0
            elif current_responsible == -1 or current_institution == -1:
                self.errorMsg.setText(u"Primeiro cadastre assinaturas!")
                return 0

            # Current event
            event_title = unicode(self.events[current_event][1]).upper()
            event_start_date = unicode(self.events[current_event][2])
            event_end_date = unicode(self.events[current_event][3])
            event_hours = unicode(self.events[current_event][4])
            event_content = unicode(self.events[current_event][5]).upper()

            # Current responsible
            responsible_id = unicode(self.signatures[current_responsible][0])
            responsible_sig = os.path.join(
                app_dir,
                "signatures",
                "{0}.png".format(responsible_id)
            )

            # Current institution
            institution_id = unicode(self.signatures[current_institution][0])
            institution_sig = os.path.join(
                app_dir,
                "signatures",
                "{0}.png".format(institution_id)
            )
            institution_role = unicode(self.signatures[current_institution][2])
            try:
                institution_name = unicode(self.Config.get("Main",
                                                           "Name")).upper()
                institution_register = unicode(self.Config.get("Main", "ID"))
            except:
                self.errorMsg.setText(u"Cadastre os dados da aba "
                                      u"Instituição primeiro!")
                return 0

            # Fills with the data
            self.cert_data = {
                "event": event_title,
                "start_date": event_start_date,
                "end_date": event_end_date,
                "hours": event_hours,
                "content": event_content,
                "responsible_sig": responsible_sig,
                "institution_sig": institution_sig,
                "role": institution_role,
                "institution": institution_name,
                "inst_register": institution_register
            }

            # Get data about the event's responsible
            # to generate it's certificate
            cursor.execute(
                "SELECT * FROM signatures WHERE id=?",
                str(self.signatures[current_responsible][0])
            )
            self.responsible = cursor.fetchone()

            return 1

    def preview_certificate(self):
        """
            Open a dialog for showing the progress of the
            preview certificate generation.
        """

        r = self.generate_general(preview=True)

        # Verifies if user selected a folder or cancelled
        if self.save_folder != u"" and r == 1:
            self.preview_progress = GenerateCertificateProgress(
                self.save_folder,
                self.cert_data,
                (),
                (),
                True
            )
            self.preview_progress.show()

    def generate(self):
        """
            Open a dialog for showing the progress of the
            subscriptions and responsible certificate generation.
        """
        r = self.generate_general()

        # Verifies if user selected a folder or cancelled
        if self.save_folder != u"" and r == 1:
            self.generate_progress = GenerateCertificateProgress(
                self.save_folder,
                self.cert_data,
                self.clients,
                self.responsible
            )
            self.generate_progress.show()

    def generate_send(self):
        """
            Open a dialog for showing the progress of the
            subscriptions and responsible certificate
            generation and mailing.
        """

        r = self.generate_general()

        # Verifies if user selected a folder or cancelled
        if self.save_folder != u"" and r == 1:
            self.generate_send_progress = GenerateSendProgress(
                self.save_folder,
                self.cert_data,
                self.clients,
                self.responsible
            )
            self.generate_send_progress.show()


class AddClientDialog(QtGui.QDialog):
    """
        A dialog to subscribe new clients to an event.
    """

    def __init__(self, certificates_instance, event_id):
        """
            Setup widgets and select data from database.
        """
        super(AddClientDialog, self).__init__()
        # Window config
        self.setWindowTitle(u"Adicionar cliente")
        self.certificates_instance = certificates_instance
        self.event_id = event_id

        # Select clients in alphabetical order
        cursor.execute("SELECT * FROM clients ORDER BY name ASC")
        self.clients = cursor.fetchall()

        # Define layouts
        self.mainLayout = QtGui.QVBoxLayout()

        # Frame config
        self.titleLabel = QtGui.QLabel(u"Selecione um cliente")
        self.titleLabel.setFont(titleFont)

        # Fill combo with clients info
        self.clientsList = QtGui.QComboBox()
        for client in self.clients:
            self.clientsList.addItem(unicode(client[1]))

        # Create the main button
        self.saveBtn = QtGui.QPushButton(u"Selecionar")
        self.saveBtn.clicked.connect(self.add_client)

        # Add all widgets to the mainLayout
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(self.clientsList)
        self.mainLayout.addWidget(self.saveBtn)

        # Set mainLayout as the visible layout
        self.setLayout(self.mainLayout)

    def add_client(self):
        """
            Inserts the selected user into the database
            as a subscription to the selected event.
        """

        # Inserts data into the database
        cursor.execute(
            "INSERT INTO subscriptions VALUES (NULL,?,?)",
            (
                str(self.event_id),
                str(self.clients[self.clientsList.currentIndex()][0])
            )
        )
        conn.commit()

        # Update the listwidget that contains
        # the subscripted clients
        self.certificates_instance.load_list()

        # Hide the dialog
        self.hide()


class GenerateCertificateProgress(QtGui.QDialog):
    """
        A dialog to show the progress of the certificate
        generation and manage the generation thread.
    """

    def __init__(self, save_folder, cert_data, clients,
                 responsible, preview=False):
        """
            Setup all widgets.
        """
        super(GenerateCertificateProgress, self).__init__()

        # Window config
        self.setWindowTitle(u"Gerando certificados")
        self.setGeometry(450, 300, 400, 200)
        self.preview = preview
        self.n = 0
        self.total = len(clients)+1

        # Creates the new thread
        self.generate_thread = GenerateThread(self.preview)
        self.generate_thread._get_info(save_folder, cert_data,
                                       clients, responsible)
        # Connect the signals with slots
        self.connect(
            self.generate_thread,
            QtCore.SIGNAL("finished()"),
            self.done
        )
        self.connect(
            self.generate_thread,
            QtCore.SIGNAL("update"),
            self.update
        )

        # Defines the layouts
        self.mainLayout = QtGui.QVBoxLayout()

        # Widget config
        self.titleLabel = QtGui.QLabel(u"Gerando certificados", self)
        self.titleLabel.setFont(titleFont)

        # Make the progress bar from 0 to 100
        self.progress_bar = QtGui.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.status = QtGui.QLabel(u"Carregando...", self)

        # Make the cancel button
        self.cancelBtn = QtGui.QPushButton(u"Cancelar")
        self.cancelBtn.clicked.connect(self.generate_thread.terminate)

        # Add all widgets to the mainLayout
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(self.progress_bar)
        self.mainLayout.addWidget(self.status)
        self.mainLayout.addWidget(self.cancelBtn)

        # Runs the thread
        self.generate_thread.start()

        # Set the mainLayout as the visible layout
        self.setLayout(self.mainLayout)

    def update(self, step, n):
        """
            Updates the progress bar value and text
            according to the signal received.
        """
        # Percentage calcs
        self.n += 100/self.total

        # Update progress bar value
        self.progress_bar.setValue(int(self.n))

        # Update status according to the signal
        if step == 1:
            if self.preview:
                certs = 1
            else:
                certs = self.total-1

            self.status.setText(
                u"Gerando certificado {0}/{1}".format(n, certs)
            )
        elif step == 2:
            self.status.setText(u"Gerando certificado do responsável")
        elif step == 3:
            self.progress_bar.setValue(100)
            self.status.setText("Finalizando...")

    def done(self):
        """
            Shows up a message box informing that
            the task is completed.
        """

        # Setup the message box
        self.message = QtGui.QMessageBox()
        self.message.setGeometry(450, 300, 300, 200)
        self.message.setIcon(QtGui.QMessageBox.Information)
        self.message.setWindowTitle(u"Pronto!")
        self.message.setStandardButtons(QtGui.QMessageBox.Ok)
        if not self.preview:
            self.message.setText(u"Todos os certificados foram gerados!")
        else:
            self.message.setText(u"O certificado foi gerado com "
                                 u"o nome PREVIEWDECLIENTE.pdf")

        # Shows up the message box
        self.message.exec_()

        # Hide the dialog
        self.hide()


class GenerateThread(QtCore.QThread):
    """
        The thread that deals with the certificate generation.
    """

    def __init__(self, preview=False):
        """
            Setup the thread.
        """
        super(GenerateThread, self).__init__()
        self.preview = preview

    def __del__(self):
        self.wait()

    def _get_info(self, save_folder, cert_data, clients, responsible):
        """
            Gets all the needed info for generating certificates.
        """
        self.save_folder = save_folder
        self.cert_data = cert_data
        self.clients = clients
        self.responsible = responsible

    def run(self):
        """
            Generate all certificates.
        """
        n = 1
        if not self.preview:
            for client in self.clients:
                # Select client info
                cursor.execute(
                    "SELECT name,register FROM clients \
                    WHERE id=?",
                    str(client[1])
                )
                client_data = cursor.fetchone()
                self.cert_data["name"] = unicode(client_data[0]).upper()
                self.cert_data["register"] = unicode(client_data[1])

                # Updates the progress bar status
                self.emit(QtCore.SIGNAL("update"), 1, n)

                # Generate the certificate
                generate_certificate(self.save_folder, self.cert_data)
                n += 1

            # Updates the progress bar status
            self.emit(QtCore.SIGNAL("update"), 2, 0)

            # Get the responsible info
            self.cert_data["name"] = unicode(self.responsible[1]).upper()
            self.cert_data["register"] = unicode(self.responsible[4]).upper()

            # Generate the responsible certificate
            generate_certificate(self.save_folder, self.cert_data, True)

            # Updates the progress bar status
            self.emit(QtCore.SIGNAL("update"), 3, 0)
        else:
            # Setup preview info
            self.cert_data["name"] = u"Preview de Cliente".upper()
            self.cert_data["register"] = u"000.000.000-00"

            # Generate preview certificate
            self.emit(QtCore.SIGNAL("update"), 1, n)
            generate_certificate(self.save_folder, self.cert_data)
            self.emit(QtCore.SIGNAL("update"), 3, 0)


class GenerateSendProgress(QtGui.QDialog):
    """
        A dialog to generate and sent certificates.
    """

    def __init__(self, save_folder, cert_data, clients, responsible):
        """
            Setup all widgets.
        """
        super(GenerateSendProgress, self).__init__()

        # Window config
        self.setWindowTitle(u"Gerando & enviando certificados")
        self.setGeometry(450, 300, 400, 200)
        self.n = 0
        self.total = len(clients)+3
        self.error = False

        # Create thread for dealing with
        # the generation and mailing
        self.generate_send_thread = GenerateSendThread()
        self.generate_send_thread._get_info(save_folder, cert_data,
                                            clients, responsible)

        # Connects signals with slots
        self.connect(
            self.generate_send_thread,
            QtCore.SIGNAL("finished()"),
            self.done
        )
        self.connect(
            self.generate_send_thread,
            QtCore.SIGNAL("update"),
            self.update
        )
        self.connect(
            self.generate_send_thread,
            QtCore.SIGNAL("error_raised()"),
            self.error_raised
        )

        # Defines all layouts
        self.mainLayout = QtGui.QVBoxLayout()

        # Widget config
        self.titleLabel = QtGui.QLabel(u"Gerando & enviando certificados",
                                       self)
        self.titleLabel.setFont(titleFont)

        # Creates progress bar from 0 to 100
        self.progress_bar = QtGui.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.status = QtGui.QLabel(u"Carregando...", self)

        # Cancel button
        self.cancelBtn = QtGui.QPushButton(u"Cancelar")
        self.cancelBtn.clicked.connect(self.generate_send_thread.terminate)

        # Adds all widgets to the mainLayout
        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addWidget(self.progress_bar)
        self.mainLayout.addWidget(self.status)
        self.mainLayout.addWidget(self.cancelBtn)

        # Starts the thread
        self.generate_send_thread.start()

        # Set the mainLayout as the visible layout
        self.setLayout(self.mainLayout)

    def update(self, step, n):
        """
            Updates the progress bar value and information text.
        """
        # Updates value
        self.n += 100/self.total
        self.progress_bar.setValue(int(self.n))

        # Updates status
        if step == 1:
            self.status.setText(u"Conectando...")
        if step == 2:
            self.status.setText(
                u"Gerando & enviando "
                "certificado {0}/{1}".format(n, (self.total-3))
            )
        if step == 3:
            self.status.setText(u"Gerando & enviando "
                                u"certificado do responsável")
        if step == 4:
            self.progress_bar.setValue(100)
            self.status.setText(u"Finalizando")

    def error_raised(self):
        """
            Updates error status to True.
        """
        self.error = True

    def done(self):
        """
            Shows up message box with information about the completed thread.
        """

        # Verifies if the connection was OK
        if self.error is False:
            # Creates the message box
            self.message = QtGui.QMessageBox()
            self.message.setGeometry(450, 300, 300, 200)
            self.message.setIcon(QtGui.QMessageBox.Information)
            self.message.setText(u"Todos os certificados "
                                 u"foram gerados e enviados!")
            self.message.setWindowTitle(u"Pronto!")
            self.message.setStandardButtons(QtGui.QMessageBox.Ok)

            # Shows up message box
            self.message.exec_()
        else:
            # Display a message box for more error info
            self.error = QtGui.QMessageBox()
            self.error.setGeometry(450, 300, 300, 200)
            self.error.setIcon(QtGui.QMessageBox.Critical)
            self.error.setWindowTitle(u"Erro de autenticação!")
            self.error.setText(u"Erro de autenticação!")
            self.error.setInformativeText(u"Houve uma falha na autenticação! "
                                          u"Verifique as informações de "
                                          u"conexão na aba Instituição.")
            self.error.setStandardButtons(QtGui.QMessageBox.Ok)
            self.error.exec_()

        # Hide the dialog
        self.hide()


class GenerateSendThread(QtCore.QThread):
    """
        A thread for dealing with certificates generation and mailing.
    """

    def __init__(self):
        """
            Setup widgets.
        """
        super(GenerateSendThread, self).__init__()

    def __del__(self):
        self.wait()

    def _get_info(self, save_folder, cert_data, clients, responsible):
        """
            Gets info to generate and send certificates.
        """
        self.save_folder = save_folder
        self.cert_data = cert_data
        self.clients = clients
        self.responsible = responsible

    def run(self):
        """
            Connects with the mailer, generates and send the certificates.
        """

        # connects to the mailer and updates progress bar
        self.emit(QtCore.SIGNAL("update"), 1, 0)
        self.mailer = Mailer()
        r = self.mailer.connect()

        # Verifies authentication
        if r == 1:
            n = 1
            for client in self.clients:
                # Get client info
                cursor.execute(
                    "SELECT name,email FROM clients WHERE id=?",
                    str(client[1])
                )
                client_data = cursor.fetchone()

                filepath = os.path.join(
                    unicode(self.save_folder),
                    u''.join(i for i in unicode(client_data[0])
                             if ord(i) < 128)
                    .upper()
                    .replace(" ", "")
                )
                filepath += ".pdf"

                self.cert_data["name"] = unicode(client_data[0]).upper()
                self.cert_data["register"] = unicode(client_data[1])

                # Updates progress bar and generate and send certificate
                self.emit(QtCore.SIGNAL("update"), 2, n)
                generate_certificate(self.save_folder, self.cert_data)
                self.mailer.send_certificate(filepath, unicode(client_data[1]))
                n += 1

            # Gets responsible info
            filepath = os.path.join(
                unicode(self.save_folder),
                u"responsible.pdf"
            )
            self.cert_data["name"] = unicode(self.responsible[1]).upper()
            self.cert_data["register"] = unicode(self.responsible[4]).upper()

            # Updates progress bar and generate and send certificate
            self.emit(QtCore.SIGNAL("update"), 3, 0)
            generate_certificate(self.save_folder, self.cert_data, True)
            self.mailer.send_certificate(
                unicode(filepath),
                unicode(self.responsible[3])
            )

            self.emit(QtCore.SIGNAL("update"), 4, 0)

            # Quits mailer
            self.mailer.quit()
        else:
            self.emit(QtCore.SIGNAL("error_raised()"))
