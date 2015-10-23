#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtSql import *
from PyQt5.QtWidgets import *


class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        lay_main = QVBoxLayout(self)
        lay_query = QHBoxLayout()
        lay_main.addLayout(lay_query)
        lbl_select = QLabel("SELECT * FROM members WHERE first_name like")
        lay_query.addWidget(lbl_select)
        self.edt_filter = QLineEdit("%")
        lay_query.addWidget(self.edt_filter)
        self.btn_ok = QPushButton("&OK")
        self.btn_ok.setEnabled(False)
        self.btn_ok.clicked.connect(self.execute_query)
        lay_query.addWidget(self.btn_ok)

        self.edt_result = QPlainTextEdit()
        self.edt_result.setReadOnly(True)
        lay_main.addWidget(self.edt_result)

        self.database = QSqlDatabase("QSQLITE")
        self.database.setDatabaseName("VereinsKasse.db")
        if self.database.open():
            self.edt_result.appendPlainText("Erfolgreich verbunden")
            self.btn_ok.setEnabled(True)
        else:
            error = self.database.lastError()
            assert isinstance(error, QSqlError)
            self.edt_result.appendPlainText("Fehler: " + error.text())

        # restore settings
        self.settings = QSettings()
        self.move(self.settings.value("Position", QPoint(100, 100)))
        self.resize(self.settings.value("Size", QSize(300, 300)))

    def execute_query(self):
        query = QSqlQuery(self.database)
        str_query = "SELECT * FROM members WHERE first_name like :filter"
        if query.prepare(str_query):
            query.bindValue(":filter", self.edt_filter.text())
            if query.exec_():
                while query.next():
                    record = query.record()
                    text = ""
                    for i in range(record.count()):
                        field = record.field(i)
                        text += field.name() + ": " + str(field.value()) + " "
                    self.edt_result.appendPlainText(text)
            else:
                error = query.lastError()
                self.edt_result.appendPlainText(error.text())
        else:
            error = query.lastError()
            self.edt_result.appendPlainText(error.text())

    def closeEvent(self, QCloseEvent):
        self.database.close()

        # save settings
        self.settings.setValue("Position", self.pos())
        self.settings.setValue("Size", self.size())


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    app.setOrganizationName("Wene")
    app.setApplicationName("SqlTest")

    translator = QTranslator()
    lib_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    translator.load("qt_de.qm", lib_path)
    translator.load("qtbase_de.qm", lib_path)
    app.installTranslator(translator)

    window = Form()
    window.show()

    sys.exit(app.exec_())
