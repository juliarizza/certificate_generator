# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore

from global_functions import titleFont
from models import conn, cursor


class EventsListWidget(QtGui.QWidget):

    """
        Creates the frame with the list of registered events
        and CRUD options.
    """

    def __init__(self):
        """
            Setup widgets and select client data from the
            database.
        """
        super(EventsListWidget, self).__init__()

        # Defines all layouts
        self.mainLayout = QtGui.QVBoxLayout()
        self.listLayout = QtGui.QHBoxLayout()
        self.btnsLayout = QtGui.QVBoxLayout()

        # Window config
        self.titleLabel = QtGui.QLabel(u"Eventos", self)
        self.titleLabel.setFont(titleFont)

        # Creates all buttons and add the to the btnsLayout
        self.addBtn = QtGui.QPushButton(u"Adicionar")
        self.addBtn.clicked.connect(self.add_event)
        self.editBtn = QtGui.QPushButton(u"Editar")
        self.editBtn.clicked.connect(self.update_event)
        self.removeBtn = QtGui.QPushButton(u"Remover")
        self.removeBtn.clicked.connect(self.remove_event)
        self.btnsLayout.addWidget(self.addBtn)
        self.btnsLayout.addWidget(self.editBtn)
        self.btnsLayout.addWidget(self.removeBtn)
        self.btnsLayout.addStretch()

        # Creates a table widget for showing events
        # and loads them
        self.eventsTable = QtGui.QTableWidget()
        self.load_table()

        # Add the btnsLayout and eventsTable to an
        # horizontal layout
        self.listLayout.addWidget(self.eventsTable)
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
            Populates the events table with the existing
            events.
        """
        # Clears the table to show new records
        self.eventsTable.clear()

        # Select the records to show
        cursor.execute("SELECT * FROM events ORDER BY id DESC")
        data = cursor.fetchall()

        # Set the table default number of rows to 10
        # If there is more than 10 records, set to the len
        # of the records
        if len(data) < 10:
            self.eventsTable.setRowCount(10)
        else:
            self.eventsTable.setRowCount(len(data))

        # Set columns quantity and name
        self.eventsTable.setColumnCount(4)
        self.eventsTable.setHorizontalHeaderLabels(
            (u"ID", u"Título", u"Data de Início", u"Data de Término")
        )

        # Make columns and rows fit sizes to the window
        self.eventsTable.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch
        )
        self.eventsTable.verticalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch
        )

        # Updates the table with the selected records
        r,c = 0,0
        for item in data:
            for i in range(4):
                newitem = QtGui.QTableWidgetItem(unicode(item[i]))
                self.eventsTable.setItem(r, c, newitem)
                c += 1
            r += 1
            c = 0

    def add_event(self):
        """
            Register a new event.
        """
        # Opens a dialog with a form to register the new event
        self.add_event_dialog = EventDialog(self)
        self.add_event_dialog.show()

    def remove_event(self):
        """
            Delete an existing event.
        """
        # Verifies if there is a selected event
        try:
            # Gets the event id
            r = self.eventsTable.currentRow()
            event_id = self.eventsTable.item(r, 0).text()

            # Asks if the user really wants to remove the event
            choice = QtGui.QMessageBox.question(
                self, u"Apagar evento",
                u"Tem certeza que deseja apagar este evento?",
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
            )
            if choice == QtGui.QMessageBox.Yes:
                cursor.execute("DELETE FROM events WHERE id=?", str(event_id))
                conn.commit()
            else:
                pass

            # Updates the events table
            self.load_table()
        except AttributeError:
            self.errorMsg.setText(u"Selecione um registro existente!")

    def update_event(self):
        """
            Edit an existing event.
        """
        # Verifies if there is a selected event
        try:
            # Gets the event id
            r = self.eventsTable.currentRow()
            event_id = self.eventsTable.item(r, 0).text()
            # Open a dialog with a form to edit the event data
            self.edit_event_dialog = EventDialog(self, event_id)
            self.edit_event_dialog.show()
        except AttributeError:
            self.errorMsg.setText(u"Selecione um registro existente!")


class EventDialog(QtGui.QDialog):
    """
        A dialog with a form to fill event data for
        creating a new event or editing an existing one.
    """

    def __init__(self, events_list_instance, event_id=None):
        """
            Setup widgets.
        """
        super(EventDialog, self).__init__()
        # Window config
        self.event_id = event_id
        self.events_list_instance = events_list_instance

        # Defines all layouts
        self.mainLayout = QtGui.QVBoxLayout()
        self.formLayout = QtGui.QFormLayout()

        # Title field
        self.eventTitle = QtGui.QLabel(u"Título", self)
        self.eventTitleLineEdit = QtGui.QLineEdit(self)
        self.eventTitleLineEdit.setPlaceholderText(u"Ex: Curso de Excel")
        self.formLayout.addRow(self.eventTitle, self.eventTitleLineEdit)

        # Content field
        self.eventContent = QtGui.QLabel(u"Conteúdo", self)
        self.eventContentTextEdit = QtGui.QTextEdit(self)
        self.formLayout.addRow(self.eventContent, self.eventContentTextEdit)

        # Start date field
        self.eventStartDate = QtGui.QLabel(u"Data de Início", self)
        self.eventStartDateLineEdit = QtGui.QLineEdit(self)
        # Mask for brazilian date format
        self.eventStartDateLineEdit.setInputMask(u"99/99/9999")
        self.formLayout.addRow(
            self.eventStartDate,
            self.eventStartDateLineEdit
        )

        # End date field
        self.eventEndDate = QtGui.QLabel(u"Data de Término", self)
        self.eventEndDateLineEdit = QtGui.QLineEdit(self)
        # Mask for brazilian date format
        self.eventEndDateLineEdit.setInputMask(u"99/99/9999")
        self.formLayout.addRow(self.eventEndDate, self.eventEndDateLineEdit)

        # Hours field
        self.eventHours = QtGui.QLabel(u"Horas Totais", self)
        self.eventHoursLineEdit = QtGui.QLineEdit(self)
        self.eventHoursLineEdit.setPlaceholderText(u"Ex: 15")
        self.formLayout.addRow(self.eventHours, self.eventHoursLineEdit)

        # A label for showing errors
        self.errorMsg = QtGui.QLabel(u"", self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        # Save button
        self.saveBtn = QtGui.QPushButton(u"Salvar")
        self.saveBtn.clicked.connect(self.save_data)

        # If we are editing an event, it will show a filled form
        # if not, shows an empty form
        if self.event_id:
            # Window config
            self.setWindowTitle(u"Editar evento")
            self.titleLabel = QtGui.QLabel(u"Editar evento", self)
            self.titleLabel.setFont(titleFont)

            # Select the existing client data
            cursor.execute(
                "SELECT * FROM events WHERE id=?",
                str(self.event_id)
            )
            data = cursor.fetchone()

            # Fills the form with the data
            self.eventTitleLineEdit.setText(unicode(data[1]))
            self.eventStartDateLineEdit.setText(unicode(data[2]))
            self.eventEndDateLineEdit.setText(unicode(data[3]))
            self.eventHoursLineEdit.setText(unicode(data[4]))
            self.eventContentTextEdit.setText(unicode(data[5]))
        else:
            # Window config
            self.setWindowTitle(u"Cadastrar evento")
            self.titleLabel = QtGui.QLabel(u"Cadastrar evento", self)
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
            Saves the event data.
        """
        # Verifies if all fields are filled
        if unicode(self.eventTitleLineEdit.text()) == "":
            self.errorMsg.setText(u"O título precisa ser preenchido!")
        elif len(unicode(self.eventStartDateLineEdit.text())) < 10 or \
                len(unicode(self.eventEndDateLineEdit.text())) < 10:
            self.errorMsg.setText(u"As datas precisam estar \
                                  em um formato xx/xx/xxxx!")
        elif unicode(self.eventHoursLineEdit.text()) == "":
            self.errorMsg.setText(u"As horas precisam ser um inteiro!")
        else:
            if self.event_id:
                # Updates the record if it is an existing event
                cursor.execute(
                    "UPDATE events SET title=?, start_date=?, end_date=?, \
                    hours=?, content=? WHERE id=?",
                    (
                        unicode(self.eventTitleLineEdit.text()),
                        unicode(self.eventStartDateLineEdit.text()),
                        unicode(self.eventEndDateLineEdit.text()),
                        unicode(self.eventHoursLineEdit.text()),
                        unicode(self.eventContentTextEdit.toPlainText()),
                        str(self.event_id)
                    )
                )
            else:
                # Register the event
                cursor.execute(
                    "INSERT INTO events VALUES (NULL,?,?,?,?,?)",
                    (
                        unicode(self.eventTitleLineEdit.text()),
                        unicode(self.eventStartDateLineEdit.text()),
                        unicode(self.eventEndDateLineEdit.text()),
                        unicode(self.eventHoursLineEdit.text()),
                        unicode(self.eventContentTextEdit.toPlainText())
                    )
                )
            # Saves the database
            conn.commit()
            # Update the table
            self.events_list_instance.load_table()
            # Hide the dialog
            self.hide()
