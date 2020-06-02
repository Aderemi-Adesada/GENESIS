import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QPropertyAnimation
from genesis import project_files_gen, project_task_info_gen, create_svn_config
import gazu
import resources

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('genesis.ui', self)
        self.menu_button.clicked.connect(lambda: self.toggleMenu(220, True))
        self.project_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.settings_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.project_list()

        print(str(self.project_select.currentText()))
        # print(blender)
        self.gen_project_files.clicked.connect(self.gen)
        self.access_control.clicked.connect(lambda: create_svn_config(str(self.project_select.currentText())))
        self.project_task_details.clicked.connect(lambda: project_task_info_gen(str(self.project_select.currentText())))


    def toggleMenu(self, maxWidth, enable):
        if enable:
            # GET WIDTH
            width = self.side_menu.width()
            print(width)
            maxExtend = maxWidth
            standard = 55

            # SET MAX WIDTH
            if width == 55:
                widthExtended = maxExtend
            else:
                widthExtended = standard

            # ANIMATION
            self.animation = QPropertyAnimation(self.side_menu, b"minimumWidth")
            self.animation.setDuration(300)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation.start()


    def project_list(self):
        all_open_projects = gazu.project.all_open_projects()
        self.project_select.clear()
        for project in all_open_projects:
            self.project_select.addItem(project['name'])

    def gen(self):
        blender = "C:/Program Files/Blender Foundation/Blender 2.82/blender.exe"
        name = str(self.project_select.currentText())
        # print(name)
        # print(type(name))
        project_files_gen(name, blender)

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
            password = 'testing'
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