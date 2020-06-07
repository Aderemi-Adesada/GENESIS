import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QPropertyAnimation
from genesis import project_files_gen, project_task_info_gen, create_svn_config
import gazu
import json
import requests
import resources
settings_dir = 'settings.json'
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('genesis.ui', self)
        self.stackedWidget.setCurrentIndex(0)
        with open(settings_dir, 'r') as data:
            settings = json.load(data)
        self.project_mounting_point_input.setText(settings['mount point'])
        self.svn_parent_path_input.setText(settings['svn parent path'])
        self.blender_directory_input.setText(settings['blender directory'])

        self.menu_button.clicked.connect(lambda: self.toggleMenu(220, True))
        self.project_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.settings_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.project_list()

        print(str(self.project_select.currentText()))
        selected_project = self.project_select.currentText
        self.gen_project_files.clicked.connect(lambda: project_files_gen(project_name=selected_project(),
                                                                         blender=self.blender_directory_input.text(),
                                                                         mount_point=self.project_mounting_point_input.text()))
        self.access_control.clicked.connect(lambda: create_svn_config(selected_project(),
                                                                      self.svn_parent_path_input.text()))
        self.project_task_details.clicked.connect(lambda: project_task_info_gen(str(selected_project())))
        self.save_settings_button.clicked.connect(self.setings)

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

    def setings(self):
        mount_point = self.project_mounting_point_input.text()
        svn_parent_path = self.svn_parent_path_input.text()
        blender_directory = self.blender_directory_input.text()
        settings = {'mount point': mount_point,
                    'svn parent path': svn_parent_path,
                    'blender directory': blender_directory}
        with open('settings.json', 'w') as data:
            json.dump(settings, data, indent=2)


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
        except gazu.exception.NotAuthenticatedException:
            error = QMessageBox()
            error.setWindowTitle('Login Error')
            error.setText('Login failure, Wrong credecials')
            error.setIcon(QMessageBox.Critical)

            x = error.exec_()
            print('error')
        except requests.exceptions.ConnectionError:
            error = QMessageBox()
            error.setWindowTitle('Login Error')
            error.setText('no connection')
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