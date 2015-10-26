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
        act_new.setEnabled(False)
        act_new.setStatusTip("Legt eine neue SqLite Datenbank mit der erforderlichen Struktur an.")
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
        self.konto_view = QTableView()
        tabs.addTab(self.konto_view, "Konto")
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
                                    "Öffne eine Datenbank oder leg eine neue an.")

        # restore settings
        self.settings = QSettings()
        self.move(self.settings.value("Position", QPoint(100, 100)))
        self.resize(self.settings.value("Size", QSize(600, 400)))

    def closeEvent(self, QCloseEvent):
        # save settings
        self.settings.setValue("Position", self.pos())
        self.settings.setValue("Size", self.size())

    def open_dialog(self):
        last_file = self.settings.value("Filename", ".")
        filename, active_filter = QFileDialog.getOpenFileName(self, "Datenbank öffnen",
                                                              last_file,
                                                              "SqLite Datenbankdateien (*.db);;Alle Dateien (*)")
        self.open_database(filename)

    def open_database(self, filename: str):
        self.sql_database = QSqlDatabase("QSQLITE")
        self.sql_database.setDatabaseName(filename)
        if self.sql_database.open():
            # TODO: check for correct DB schema
            self.debug.appendPlainText("Erfolgreich verbunden mit:")
            self.debug.appendPlainText(filename)
            # write last successful used filename to settings
            self.settings.setValue("Filename", filename)
        else:
            error = self.sql_database.lastError()
            assert isinstance(error, QSqlError)
            self.debug.appendPlainText("Fehler bei Verbindung:")
            self.debug.appendPlainText(error.text())


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
