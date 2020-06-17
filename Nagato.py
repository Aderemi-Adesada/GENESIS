import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QPropertyAnimation
from genesis import Project
import gazu
from gazu.exception import MethodNotAllowedException, RouteNotFoundException
import json
from requests.exceptions import MissingSchema, InvalidSchema, ConnectionError
import resources
import os

project = Project()
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
        self.refresh()
        self.refresh_button.clicked.connect(self.refresh)

        self.progress_bar.setValue(0)

        self.menu_button.clicked.connect(lambda: self.toggleMenu(220, True))
        self.project_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.settings_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))

        selected_project = self.project_select.currentText
        self.gen_project_files.clicked.connect(lambda: project.files_gen(project_name=selected_project(),
                                                                         blender=self.blender_directory_input.text(),
                                                                         mount_point=self.project_mounting_point_input.text()))
        self.access_control.clicked.connect(lambda: project.svn_config(selected_project(),
                                                                      self.svn_parent_path_input.text()))
        self.set_file_tree_button.clicked.connect(lambda: project.set_file_tree(project_name=selected_project(),
                                                                        file_tree_name=self.file_tree_select.currentText()))
        self.new_file_tree_button.clicked.connect(project.new_file_tree)
        # self.project_task_details.clicked.connect(lambda: project_task_info_gen(str(selected_project())))
        self.save_settings_button.clicked.connect(self.setings)
        self.set_svn_button.clicked.connect(lambda:project.svn_url(project_name=selected_project(),
                                                               url=self.svn_url_input.text()))

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

    def file_tree_list(self):
        file_trees = os.listdir('file_trees')
        self.file_tree_select.clear()
        for file_tree in file_trees:
            file_tree_name = file_tree.rsplit('.', 1)
            if file_tree_name[1] == 'json':
                self.file_tree_select.addItem(file_tree_name[0])

    def refresh(self):
        self.project_list()
        self.file_tree_list()

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
        self.login_button.clicked.connect(self.login)
    def login(self):
        host = self.host_url.text()
        username = self.username_input.text()
        password = self.password_input.text()
        project.login(host, username, password, switch=self.switch_window)
        # project.login('https://eaxum.cg-wire.com/api', 'aderemi@eaxum.com', 'testing', switch= self.switch_window)






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