# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore
from models import conn, cursor
from global_functions import titleFont

class EventsListWidget(QtGui.QWidget):

    def __init__(self):
        super(EventsListWidget, self).__init__()

        self.mainLayout = QtGui.QVBoxLayout()
        self.listLayout = QtGui.QHBoxLayout()
        self.btnsLayout = QtGui.QVBoxLayout()

        self.titleLabel = QtGui.QLabel(u"Eventos", self)
        self.titleLabel.setFont(titleFont)

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

        self.eventsTable = QtGui.QTableWidget()
        self.load_table()

        self.listLayout.addWidget(self.eventsTable)
        self.listLayout.addLayout(self.btnsLayout)

        self.errorMsg = QtGui.QLabel(u"",self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addLayout(self.listLayout)
        self.mainLayout.addWidget(self.errorMsg)

        self.setLayout(self.mainLayout)

    def load_table(self):
        self.eventsTable.clear()

        cursor.execute("SELECT * FROM events")
        data = cursor.fetchall()

        if len(data) < 10:
            self.eventsTable.setRowCount(10)
        else:
            self.eventsTable.setRowCount(len(data))
        self.eventsTable.setColumnCount(4)
        self.eventsTable.setHorizontalHeaderLabels((u"ID",
                                                    u"Título",
                                                    u"Data de Início",
                                                    u"Data de Término"))
        self.eventsTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.eventsTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        r,c=0,0
        for item in data:
            for i in range(4):
                newitem = QtGui.QTableWidgetItem(unicode(item[i]))
                self.eventsTable.setItem(r,c,newitem)
                c += 1
            r += 1
            c = 0

    def add_event(self):
        self.add_event_dialog = EventDialog(self)
        self.add_event_dialog.show()

    def remove_event(self):
        try:
            r = self.eventsTable.currentRow()
            event_id = self.eventsTable.item(r,0).text()
            choice = QtGui.QMessageBox.question(self, u"Apagar evento",
                                                u"Tem certeza que deseja apagar este evento?",
                                                QtGui.QMessageBox.Yes |
                                                QtGui.QMessageBox.No)
            if choice == QtGui.QMessageBox.Yes:
                cursor.execute("DELETE FROM events WHERE id=?", str(event_id))
                conn.commit()
            else:
                pass
            self.load_table()
        except AttributeError:
            self.errorMsg.setText(u"Selecione um registro existente!")

    def update_event(self):
        try:
            r = self.eventsTable.currentRow()
            event_id = self.eventsTable.item(r,0).text()
            self.edit_event_dialog = EventDialog(self, event_id)
            self.edit_event_dialog.show()
        except AttributeError:
            self.errorMsg.setText(u"Selecione um registro existente!")

class EventDialog(QtGui.QDialog):

    def __init__(self, events_list_instance, event_id=None):
        super(EventDialog, self).__init__()
        self.event_id = event_id
        self.events_list_instance = events_list_instance

        self.mainLayout = QtGui.QVBoxLayout()
        self.formLayout = QtGui.QFormLayout()

        self.eventTitle = QtGui.QLabel(u"Título", self)
        self.eventTitleLineEdit = QtGui.QLineEdit(self)
        self.eventTitleLineEdit.setPlaceholderText(u"Ex: Curso de Excel")
        self.formLayout.addRow(self.eventTitle, self.eventTitleLineEdit)

        self.eventContent = QtGui.QLabel(u"Conteúdo", self)
        self.eventContentTextEdit = QtGui.QTextEdit(self)
        self.formLayout.addRow(self.eventContent, self.eventContentTextEdit)

        self.eventStartDate = QtGui.QLabel(u"Data de Início", self)
        self.eventStartDateLineEdit = QtGui.QLineEdit(self)
        self.eventStartDateLineEdit.setInputMask(u"99/99/9999")
        self.formLayout.addRow(self.eventStartDate, self.eventStartDateLineEdit)

        self.eventEndDate = QtGui.QLabel(u"Data de Término", self)
        self.eventEndDateLineEdit = QtGui.QLineEdit(self)
        self.eventEndDateLineEdit.setInputMask(u"99/99/9999")
        self.formLayout.addRow(self.eventEndDate, self.eventEndDateLineEdit)

        self.eventHours = QtGui.QLabel(u"Horas Totais", self)
        self.eventHoursLineEdit = QtGui.QLineEdit(self)
        self.eventHoursLineEdit.setPlaceholderText(u"Ex: 15")
        self.formLayout.addRow(self.eventHours, self.eventHoursLineEdit)

        self.errorMsg = QtGui.QLabel(u"",self)
        self.errorMsg.setStyleSheet("color: red; font-weight: bold;")

        self.saveBtn = QtGui.QPushButton(u"Salvar")
        self.saveBtn.clicked.connect(self.save_data)

        if self.event_id:
            self.setWindowTitle(u"Editar evento")
            self.titleLabel = QtGui.QLabel(u"Editar evento", self)
            self.titleLabel.setFont(titleFont)

            cursor.execute("SELECT * FROM events WHERE id=?", str(self.event_id))
            data = cursor.fetchone()

            self.eventTitleLineEdit.setText(unicode(data[1]))
            self.eventStartDateLineEdit.setText(unicode(data[2]))
            self.eventEndDateLineEdit.setText(unicode(data[3]))
            self.eventHoursLineEdit.setText(unicode(data[4]))
            self.eventContentTextEdit.setText(unicode(data[5]))
        else:
            self.setWindowTitle(u"Cadastrar evento")
            self.titleLabel = QtGui.QLabel(u"Cadastrar evento", self)
            self.titleLabel.setFont(titleFont)

        self.mainLayout.addWidget(self.titleLabel)
        self.mainLayout.addLayout(self.formLayout)
        self.mainLayout.addWidget(self.errorMsg)
        self.mainLayout.addWidget(self.saveBtn)

        self.setLayout(self.mainLayout)

    def save_data(self):
        if unicode(self.eventTitleLineEdit.text()) == "":
            self.errorMsg.setText(u"O título precisa ser preenchido!")
        elif len(unicode(self.eventStartDateLineEdit.text())) < 10 or \
                len(unicode(self.eventEndDateLineEdit.text())) < 10:
            self.errorMsg.setText(u"As datas precisam estar em um formato xx/xx/xxxx!")
        elif unicode(self.eventHoursLineEdit.text()) == "":
            self.errorMsg.setText(u"As horas precisam ser um inteiro!")
        else:
            if self.event_id:
                cursor.execute("""
                                UPDATE events
                                SET title=?,
                                start_date=?,
                                end_date=?,
                                hours=?,
                                content=?
                                WHERE id=?
                                """, (
                                unicode(self.eventTitleLineEdit.text()),
                                unicode(self.eventStartDateLineEdit.text()),
                                unicode(self.eventEndDateLineEdit.text()),
                                unicode(self.eventHoursLineEdit.text()),
                                unicode(self.eventContentTextEdit.toPlainText()),
                                str(self.event_id)
                                ))
            else:
                cursor.execute("INSERT INTO events VALUES (NULL,?,?,?,?,?)",
                                (
                                unicode(self.eventTitleLineEdit.text()),
                                unicode(self.eventStartDateLineEdit.text()),
                                unicode(self.eventEndDateLineEdit.text()),
                                unicode(self.eventHoursLineEdit.text()),
                                unicode(self.eventContentTextEdit.toPlainText())
                                ))
            conn.commit()
            self.events_list_instance.load_table()
            self.hide()
