import os
import gazu
import shutil
import ctypes
import json
from configparser import ConfigParser
iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii

# gazu.set_host('https://eaxum.cg-wire.com/api')
# gazu.log_in('aderemi@eaxum.com', 'efosadiya')
# project = gazu.project.get_project_by_name('tao')
# project_id = '665ce354-8e1f-41b5-9c47-16132aa98bc7'
############################################################
with open('directories.json', 'r') as data:
    task_infos = json.load(data)
print(task_infos[0])
config = ConfigParser()

for task_info in task_infos:
    if task_info['svn_dir'] in config:
        assignees = task_info['assignees']
        for assignee in assignees:
            config.set(task_info['svn_dir'], assignee['full_name'], 'rw')
    else:
        assignees = task_info['assignees']
        for assignee in assignees:
            config[task_info['svn_dir']] = {
                assignee['full_name']: 'rw'
            }

for task_info in task_infos:
    assignees = task_info['assignees']
    for dependency in task_info['dependencies']:
        if dependency['svn_dir'] in config:
            config.set(dependency['svn_dir'], assignee['full_name'], 'r')

with open('svn_config.txt', 'w') as f:
    config.write(f)
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

