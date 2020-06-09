import os
import shutil
import gazu
import pysvn
import sys
from pprint import pprint
from PyQt5.QtWidgets import (QWidget, QProgressBar, QPushButton, QApplication)

class Tut(QWidget):
    def __init__(self):
        super().__init__()
        self.progressbar

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pprint('input parameters = ' + str(sys.argv))
    tut_win = Tut()
    tut_win.show()
    sys.exit(app.exec_())

# folder = 'C:/Users/Tanjiro/AppData/Roaming/Subversion/auth/svn.simple'
# for filename in os.listdir(folder):
#     file_path = os.path.join(folder, filename)
#     try:
#         if os.path.isfile(file_path) or os.path.islink(file_path):
#             os.unlink(file_path)
#         elif os.path.isdir(file_path):
#             shutil.rmtree(file_path)
#     except Exception as e:
#         print('Failed to delete %s. Reason: %s' % (file_path, e))


# folu = 'ftaiwo'
# remi='aderemi'
# rpassword = 'testing'
# fpassword = 'default'
# client = pysvn.Client()
# # if len(kitsu.current_project) != 0:
# repo_url = 'http://rukia:8080/svn/tao/'
# file_path = 'C:/Users/Tanjiro/Projects/tao'
# client.set_store_passwords(True)
# client.set_auth_cache(True)
# client.set_default_username('remi')
# client.set_default_password(rpassword)
# if os.path.isdir(file_path) == False:
#     os.mkdir(file_path)
#     try:
#         client.checkout(repo_url, file_path)
#     except pysvn._pysvn_3_8.ClientError as e:
#         print(e)
# elif len(os.listdir(file_path)) == 0:
#     try:
#         client.checkout(repo_url, file_path)
#     except pysvn._pysvn_3_8.ClientError as e:
#         print(e)
# elif os.path.isdir(file_path + '/.svn') == True:
#     print('exist')
# else:
#     print("Directory is not empty and not under version control")




# import gazu
# import shutil
# import ctypes
# import json
# from configparser import ConfigParser
# x = os.environ.get('homepath')
# print(x)
# drive = 'C:'
# p_dir = drive + x + '/project'
# print(p_dir)
############################################################

######################################################################
# config = ConfigParser()
#
# config['settings'] = {
#     'debug': 'true',
#     'secret_key': 'abc123',
#     'log_path': '/my_app/log'
# }
#
# config['db'] = {
#     'db_name': 'myapp_dev',
#     'db_host': 'localhost',
#     'db_port': '8889'
# }
#
# config.set('db','val', '300')
#
# if 'db' in config:
#     print(True)
# config['files'] = {
#     'use_cdn': 'false',
#     'images_path': '/my_app/images'
# }
#


# with open('svn_config.txt', 'w') as f:
#     config.write(f)

# with open(f'{svn_parent_path}/{project_name}/conf/authz') as data:
#     config_text = data.read()
#     print(config_text)
#     gazu.project.update_project_data(project_id, {'svn_access_control': config_text})