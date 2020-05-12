import os
import gazu
import shutil
import ctypes
import json
from configparser import ConfigParser

############################################################
with open('project_tasks_info.json', 'r') as data:
    task_infos = json.load(data)
print(task_infos[0])
config = ConfigParser()


def set_write_permissions(task_info):
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


def set_read_permission(task_info):
    assignees = task_info['assignees']
    for dependency in task_info['dependencies']:
        if dependency['svn_dir'] in config:
            for assignee in assignees:
                config.set(dependency['svn_dir'], assignee['full_name'], 'r')



for task_info in task_infos:
    set_write_permissions(task_info)

# for task_info in task_infos:
#     set_read_permission(task_info)

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

