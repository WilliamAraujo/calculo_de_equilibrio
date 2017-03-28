from PyQt5.QtWidgets import QApplication, QMainWindow
import PyQt5.QtGui 
import PyQt5.QtCore 
from PyQt5 import uic
import sys
from other_windows import app_calculoEquilibrio, app_ajusteParametros
Ui_Form, QtBaseClass = uic.loadUiType("mainwindow.ui")

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.pushButton_open1.clicked.connect(self.open_Calculo_Equilibrio)
        self.ui.pushButton_open2.clicked.connect(self.open_Ajuste_Parametros)

    def open_Calculo_Equilibrio(self):
        print("Opening Calculo Equilibrio")
        self.calculoEquilibrio = app_calculoEquilibrio(self)
        self.calculoEquilibrio.show()

    def open_Ajuste_Parametros(self):
        print("Opening Ajuste Parametros")
        #self.window2 = Window2(self)
        self.ajusteParametro = app_ajusteParametros(self)
        self.ajusteParametro.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
