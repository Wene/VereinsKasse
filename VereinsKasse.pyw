#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtSql import *
from PyQt5.QtWidgets import *


class MainWin(QMainWindow):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        # create menu
        main_menu = self.menuBar()
        ''':type main_menu: QMenuBar'''
        file_menu = main_menu.addMenu("&Datenbank")
        ''':type file_menu: QMenu'''
        act_new = QAction("&Neu", self)
        act_new.setShortcut("CTRL+N")
        act_new.setStatusTip("Legt eine neue SqLite Datenbank mit der erforderlichen Struktur an.")
        act_new.triggered.connect(self.new_dialog)
        act_open = QAction("Ö&ffnen...", self)
        act_open.setShortcut("CTRL+O")
        act_open.setStatusTip("Öffnet eine vorhandene SqLite Datenbank mit der erforderlichen Struktur.")
        act_open.triggered.connect(self.open_dialog)
        act_import = QAction("&Importieren...", self)
        act_import.setEnabled(False)
        act_export = QAction("&Exportieren...", self)
        act_export.setEnabled(False)
        act_quit = QAction("&Beenden", self)
        act_quit.setShortcut("CTRL+Q")
        act_quit.setStatusTip("Beendet das Programm. "
                              "Änderungen und Einstellungen werden automatisch gespeichert.")
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_new)
        file_menu.addAction(act_open)
        file_menu.addAction(act_import)
        file_menu.addAction(act_export)
        file_menu.addSeparator()
        file_menu.addAction(act_quit)
        help_menu = main_menu.addMenu("&Hilfe")
        ''':type help_menu: QMenu'''
        act_help = QAction("&Hilfe", self)
        act_help.setShortcut("F1")
        act_help.setEnabled(False)
        act_about = QAction("Über &VereinsKasse", self)
        act_about.setEnabled(False)
        act_about_qt = QAction("Über &Qt", self)
        act_about_qt.triggered.connect(app.aboutQt)
        help_menu.addAction(act_help)
        help_menu.addSeparator()
        help_menu.addAction(act_about)
        help_menu.addAction(act_about_qt)

        # create central widget
        tabs = QTabWidget()
        self.account_view = QTableView()
        tabs.addTab(self.account_view, "Kontobewegungen")
        self.member_view = QTableView()
        tabs.addTab(self.member_view, "Mitglieder")
        self.debug = QPlainTextEdit()
        self.debug.setReadOnly(True)
        tabs.addTab(self.debug, "Debug")

        self.setCentralWidget(tabs)

        # create status bar
        self.status_bar = self.statusBar()      # The status bar gets shown as soon as it is used the first time.
        ''':type status_bar: QStatusBar'''
        self.status_bar.showMessage("Keine Datenbank geladen - "
                                    "Öffne eine Datenbank oder leg eine neue an.", 3000)

        self.sql_database = QSqlDatabase("QSQLITE")

        # restore settings
        self.settings = QSettings()
        self.move(self.settings.value("Position", QPoint(100, 100)))
        self.resize(self.settings.value("Size", QSize(600, 400)))

    def closeEvent(self, QCloseEvent):
        # save settings
        self.settings.setValue("Position", self.pos())
        self.settings.setValue("Size", self.size())

        # close database connection, if existing
        self.sql_database.close()

    def open_dialog(self):
        last_file = self.settings.value("Filename", ".")
        filename, active_filter = QFileDialog.getOpenFileName(self, "Datenbank öffnen",
                                                              last_file,
                                                              "SqLite Datenbankdateien (*.db);;Alle Dateien (*)")
        self.open_database(filename)

    def new_dialog(self):
        str_filter_db = "SqLite Datenbankdateien (*.db)"
        str_filter_all = "Alle Dateien (*)"
        str_filter = str_filter_db + ";;" + str_filter_all
        path_info = QFileInfo(self.settings.value("Filename", "."))
        dir_info = path_info.dir()
        ''':type dir_info: QDir'''
        filename, active_filter = QFileDialog.getSaveFileName(self, "Neue Datenbank anlegen",
                                                              dir_info.absolutePath(), str_filter,
                                                              options=QFileDialog.DontConfirmOverwrite)
        if active_filter == str_filter_db and not filename.lower().endswith(".db"):     # lower for case insensitivity
            filename += ".db"           # attach suffix if not entered
        file_info = QFileInfo(filename)
        if file_info.exists():
            QMessageBox.information(self, "Datei existiert bereits",
                                    "Die neue Datenbank kann nicht angelegt werden da die Datei bereits existiert. "
                                    "Lösche die Datei vorher wenn an dieser Stelle eine neue angelegt werden soll.")
        else:
            self.new_database(filename)

    def open_database(self, filename: str):
        self.sql_database.setDatabaseName(filename)
        if not self.sql_database.open():
            error = self.sql_database.lastError()
            assert isinstance(error, QSqlError)
            self.debug.appendPlainText("Fehler bei Verbindung:")
            self.debug.appendPlainText(error.text())
        else:
            # TODO: check for correct DB schema
            table_list = self.sql_database.tables()
            for table in table_list:
                self.debug.appendPlainText(table)
                record = self.sql_database.record(table)
                assert isinstance(record, QSqlRecord)
                for i in range(record.count()):
                    text = "  "
                    text += record.fieldName(i)
                    text += ": "
                    field_type = record.value(i)
                    if isinstance(field_type, str):
                        text += "String"
                    elif isinstance(field_type, int):
                        text += "Integer"
                    elif isinstance(field_type, float):
                        text += "Float"
                    self.debug.appendPlainText(text)

            self.debug.appendPlainText("Erfolgreich verbunden mit:")
            self.debug.appendPlainText(filename)

            # activate foreign keys - needs to be issued every time again
            sql_query = QSqlQuery(self.sql_database)
            sql_query.exec("PRAGMA foreign_keys = ON")

            model = QSqlQueryModel(self)
            model.setQuery("SELECT first_name, last_name, nick_name, email FROM member", self.sql_database)
            model.setHeaderData(0, Qt.Horizontal, "Vorname")
            model.setHeaderData(1, Qt.Horizontal, "Name")
            model.setHeaderData(2, Qt.Horizontal, "Nickname")
            model.setHeaderData(3, Qt.Horizontal, "E-Mail Adresse")
            self.member_view.setModel(model)

            # write last successful used filename to settings
            self.settings.setValue("Filename", filename)

    def new_database(self, filename: str):
            self.sql_database.setDatabaseName(filename)
            if not self.sql_database.open():
                error = self.sql_database.lastError()
                assert isinstance(error, QSqlError)
                self.debug.appendPlainText("Fehler beim Erstellen der Datenbank: ")
                self.debug.appendPlainText(error.text())
            else:
                # TODO: create proper database schema
                # sqlite supports only one statement per transaction - splitting statements in a list
                queries = ['PRAGMA foreign_keys = ON',  # needs to be issued every time the database is used
                           'CREATE TABLE transactions ('
                           'id                 INTEGER PRIMARY KEY AUTOINCREMENT,'
                           'date               TEXT,'
                           'original_text      TEXT,'
                           'custom_text        TEXT,'
                           'amount             INTEGER'
                           ')',
                           'CREATE TABLE member ('
                           'id                 INTEGER PRIMARY KEY AUTOINCREMENT,'
                           'first_name         TEXT,'
                           'last_name          TEXT,'
                           'nick_name          TEXT,'
                           'email              TEXT'
                           ')',
                           'CREATE TABLE share ('
                           'id                 INTEGER PRIMARY KEY AUTOINCREMENT,'
                           'name               TEXT,'
                           'description        TEXT,'
                           'interval           TEXT,'
                           'amount             INTEGER'
                           ')',
                           'CREATE TABLE member_share ('
                           'id                 INTEGER PRIMARY KEY AUTOINCREMENT,'
                           'member_id          INTEGER REFERENCES member(id) ON DELETE CASCADE,'
                           'share_id           INTEGER REFERENCES share(id) ON DELETE CASCADE'
                           ')']
                for query in queries:
                    sql_query = QSqlQuery(self.sql_database)
                    if not sql_query.exec(query):
                        self.debug.appendPlainText("--Fehler beim ausführen dieser Query:")
                        self.debug.appendPlainText(query)
                        self.debug.appendPlainText("--Der Fehler lautet:")
                        self.debug.appendPlainText(sql_query.lastError().text())
                self.sql_database.close()
                self.open_database(filename)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    app.setOrganizationName("Wene")
    app.setApplicationName("VereinsKasse")
    app.setApplicationVersion("0.0.1")

    translator = QTranslator()
    lib_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    translator.load("qt_de.qm", lib_path)
    translator.load("qtbase_de.qm", lib_path)
    app.installTranslator(translator)

    window = MainWin()
    window.show()

    sys.exit(app.exec_())
