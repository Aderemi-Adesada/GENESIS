import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets
# from genesis import
import gazu

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('genesis.ui', self)


class LoginWindow(QMainWindow):
    switch_window = QtCore.pyqtSignal()

    def __init__(self):
        super(LoginWindow, self).__init__()
        loadUi('login.ui', self)
        # self.login_button.clicked.connect(self.login)

        self.login_button.clicked.connect(self.login)

    def login(self):
        try:
            host = 'https://eaxum.cg-wire.com/api'
            username = 'aderemi@eaxum.com'
            password = 'efosadiya'
            # host = self.host_url.text()
            # username = self.username_input.text()
            # password = self.password_input.text()
            gazu.set_host(host)
            gazu.log_in(username, password)
            self.switch_window.emit()
            print('Finished')
        except:
            error = QMessageBox()
            error.setWindowTitle('Login Error')
            error.setText('Login failure, Wrong credecials')
            error.setIcon(QMessageBox.Critical)

            x = error.exec_()
            print('error')



class Controller:

    def __init__(self):
        pass

    def show_login(self):
        self.login = LoginWindow()
        self.login.switch_window.connect(self.show_main)
        self.login.show()

    def show_main(self):
        self.window = MainWindow()
        self.login.close()
        self.window.show()


def main():
    app = QApplication(sys.argv)
    controller = Controller()
    controller.show_login()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()