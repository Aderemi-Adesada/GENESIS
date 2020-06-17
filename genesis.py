import os
import gazu
import shutil
import ctypes
import json
from configparser import ConfigParser
from PyQt5.QtWidgets import QMessageBox
from gazu.exception import MethodNotAllowedException, RouteNotFoundException
from requests.exceptions import MissingSchema, InvalidSchema, ConnectionError
# from pynput.keyboard import


class Project():
    def __init__(self):
        self.project_tasks_info = []

    def login(self, host, username, password):
        try:
            gazu.set_host(host)
            gazu.log_in(username, password)
        except gazu.exception.NotAuthenticatedException:
            error = QMessageBox()
            error.setWindowTitle('Login Error')
            error.setText('Login failure, Wrong credecials')
            error.setIcon(QMessageBox.Critical)
            error.exec_()
        except gazu.exception.ParameterException:
            error = QMessageBox()
            error.setWindowTitle('Login Error')
            error.setText('Login failure, Wrong credecials. pls check login details or host')
            error.setIcon(QMessageBox.Critical)
            error.exec_()
        except (MethodNotAllowedException, RouteNotFoundException):
            error = QMessageBox()
            error.setWindowTitle('Login Error')
            error.setText('invalid host url')
            error.setIcon(QMessageBox.Critical)
            error.exec_()
        except (MissingSchema, InvalidSchema, ConnectionError) as err:
            error = QMessageBox()
            error.setWindowTitle('Login Error')
            error.setText(str(err))
            error.setIcon(QMessageBox.Critical)
            error.exec_()
        except Exception as e:
            print(e)
            error = QMessageBox()
            error.setWindowTitle('Login Error')
            error.setText('something went wrong:   ' + str(e))
            error.setIcon(QMessageBox.Critical)
            error.exec_()

    def folder_structure(self, mount_point, project_name):
        project_path = mount_point +'/'+ project_name
        base_directories = ['edit', 'lib', 'refs', 'scenes', 'tools']
        lib_directories = ['chars', 'envs', 'maps', 'nodes', 'props']
        # checking if mount point exist
        if not os.path.isdir(mount_point):
            os.mkdir(mount_point)

        # checking if project path exist
        if not os.path.isdir(project_path):
            os.mkdir(project_path)
            # creating base directories in the project folder
            for directory in base_directories:
                os.mkdir(project_path + '/' + directory)
            # creates lib sub directories
            for directory in lib_directories:
                os.mkdir(project_path + '/lib/' + directory)

    def scene_files_gen(self, scene, project_path, blender):
        chars_path = project_path + '/lib/' + 'chars/'
        envs_path = project_path + '/lib/' + 'envs/'
        props_path = project_path + '/lib/' + 'props/'
        shot_data = []
        cast_data = []
        scene_name = scene['name']
        scene_id = scene['id']
        scene_shots = gazu.context.all_shots_for_sequence(scene_id)
        os.mkdir(project_path + '/scenes/' + scene_name)
        for shot in scene_shots:
            shot_data.clear()
            shot_data.append(shot['data'])
            with open('shot_data.json', 'w') as s_data:
                json.dump(shot_data, s_data, indent=2)
            shot_name = shot['name']
            shot_path = project_path + '/scenes/' + scene_name + '/' + shot_name
            shot_file_tasks = ['lighting', 'anim', 'layout']
            shot_file_name = scene_name + '_' + shot_name + '_'
            os.mkdir(shot_path)
            # shutil.copy('./genesis.blend', shot_path)

            for shot_file_task in shot_file_tasks:
                shutil.copy('./genesis.blend', shot_path)
                shot_file_name_task = shot_path + '/' + shot_file_name + shot_file_task + '.blend'
                os.rename(shot_path + '/genesis.blend', shot_file_name_task)
                casts = gazu.casting.get_shot_casting(shot)
                cast_data.clear()
                for cast in casts:
                    if cast['asset_type_name'] == 'chars':
                        cast_data.append(
                            {'filepath': chars_path + cast['asset_name'] + '.blend', 'filename': cast['asset_name']})
                    if cast['asset_type_name'] == 'envs':
                        cast_data.append(
                            {'filepath': envs_path + cast['asset_name'] + '.blend', 'filename': cast['asset_name']})
                    if cast['asset_type_name'] == 'props':
                        cast_data.append(
                            {'filepath': props_path + cast['asset_name'] + '.blend', 'filename': cast['asset_name']})
                with open('cast_data.json', 'w') as data:
                    json.dump(cast_data, data, indent=2)
                ctypes.windll.shell32.ShellExecuteW(None, "open", blender,
                                                    f'-b --factory-startup "{shot_file_name_task}" --python "./scenes_setup.py"',
                                                    None, 1)
                while os.path.isfile(shot_file_name_task + '1') == False:
                    pass
                os.remove(shot_file_name_task + '1')

    def asset_gen(self, asset, asset_path, blender):
        asset_name = asset['name']
        asset_file = asset_path + '/' + asset_name + '.blend'
        shutil.copy('./genesis.blend', asset_path)
        os.rename(asset_path + '/genesis.blend', asset_file)
        ctypes.windll.shell32.ShellExecuteW(None, "open", blender,
                                            f' -b --factory-startup "{asset_file}" --python "./setup.py"', None, 1)
        while os.path.isfile(asset_file + '1') == False:
            pass
        os.remove(asset_file + '1')

    def project_task_info_gen(self, project_name):
        project = gazu.project.get_project_by_name(project_name)
        project_id = project['id']
        shots = gazu.shot.all_shots_for_project(project_id)
        assets = gazu.asset.all_assets_for_project(project_id)
        kitsu_task_types = gazu.task.all_task_types()
        # project_tasks_info = []

        # generates dependency info of tasks
        def dependencies_cast(cast, dependency_list_output):
            cast_tasks = gazu.task.all_tasks_for_asset(cast['asset_id'])
            for task in cast_tasks:
                cast_dir = gazu.files.build_working_file_path(task['id'])
                path_split = cast_dir.split('/', 3)
                svn_dir = f"{path_split[2]}:/{path_split[3]}.blend"
                cast_task_info = {'name': task['entity_name'], 'id': task['id'], 'dir': cast_dir, 'svn_dir': svn_dir}
                dependency_list_output.append(cast_task_info)
                break

        def shot_task_info(shot, info_output):
            dependencies = []
            shot_tasks = gazu.task.all_tasks_for_shot(shot)
            casts = gazu.casting.get_shot_casting(shot)

            for cast in casts:
                dependencies_cast(cast, dependencies)

            for shot_task in shot_tasks:
                kitsu_working_path = gazu.files.build_working_file_path(shot_task)
                task = gazu.task.get_task(shot_task['id'])
                task_type_name = task["task_type"]["name"]
                task_dir = None
                assignees = []

                for user in task['assignees']:
                    assignee = gazu.person.get_person(user)
                    assignee_info = {'full_name': assignee['full_name'], 'id': assignee['id'], 'role': assignee['role']}
                    assignees.append(assignee_info)

                def task_info_gen():
                    task_dir_split = task_dir.split('/', 3)
                    svn_dir = f"{task_dir_split[2]}:/{task_dir_split[3]}"
                    task_info = {'task_id': task['id'], 'task_type': task_type_name, 'dir': task_dir, 'svn_dir': svn_dir, 'assignees': assignees, 'dependencies': dependencies}
                    info_output.append(task_info)
                if task_type_name in {'anim',}:
                    task_dir = f"{kitsu_working_path}_anim.blend"
                    task_info_gen()
                elif task_type_name in {'layout', 'previz'}:
                    task_dir = f"{kitsu_working_path}_layout.blend"
                    task_info_gen()
                elif task_type_name in {'lighting', 'rendering', 'comp'} :
                    task_dir = f"{kitsu_working_path}_lighting.blend"
                    task_info_gen()
                else:
                    pass
                    # task_info = {'task_id': task['id'], 'task_type': task_type_name, 'dir': '', 'svn_dir': '', 'assignees': assignees, 'dependencies': dependencies}
                    # directory.append(task_info)

        def asset_task_info(asset, info_output):
            dependencies = []
            asset_tasks = gazu.task.all_tasks_for_asset(asset)
            casts = gazu.casting.get_asset_casting(asset)

            # getting asset dependencies
            for cast in casts:
                dependencies_cast(cast, dependencies)

            for asset_task in asset_tasks:
                print('inner')
                kitsu_working_path = gazu.files.build_working_file_path(asset_task)
                task = gazu.task.get_task(asset_task['id'])
                task_type_name = task["task_type"]["name"]
                assignees = []

                for user in task['assignees']:
                    assignee = gazu.person.get_person(user)
                    assignee_info = {'full_name': assignee['full_name'], 'id': assignee['id'], 'role': assignee['role']}
                    assignees.append(assignee_info)

                if task_type_name == 'Concept':
                    pass
                else:
                    task_dir = f"{kitsu_working_path}.blend"
                    task_dir_split = task_dir.split('/', 3)
                    svn_dir = f"{task_dir_split[2]}:/{task_dir_split[3]}"
                    task_info = {'task_id': task['id'], 'task_type': task_type_name, 'dir': task_dir, 'svn_dir': svn_dir,
                                 'assignees': assignees, 'dependencies': dependencies}
                    info_output.append(task_info)
        print('here')
        try:
            for asset in assets:
                asset_task_info(asset, self.project_tasks_info)
            for shot in shots:
                shot_task_info(shot, self.project_tasks_info)
        except gazu.exception.ParameterException as e:
            error = QMessageBox()
            error.setWindowTitle('Access Control Generation Error')
            error.setText(str(e))
            error.setIcon(QMessageBox.Critical)
            error.exec_()

        #todo
        # stores infos to project details with is to much
        # create a dedicated table for the info

        # gazu.project.update_project_data(project_id, {'tasks_details': project_tasks_info})
        # with open(f'{project_name}_tasks_info.json', 'w') as data:
        #     json.dump(project_tasks_info, data, indent=2)

    def create_svn_config(self, project_name, svn_parent_path):
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
            # this should be called after the set_write_permissions functions
            assignees = task_info['assignees']
            for assignee in assignees:
                for dependency in task_info['dependencies']:
                    if dependency['svn_dir'] in config:
                        if config.has_option(dependency['svn_dir'], assignee['full_name']):
                            pass
                        else:
                            config.set(dependency['svn_dir'], assignee['full_name'], 'r')

        # todo write authz file to svn server
        if os.path.isdir(f'{svn_parent_path}/{project_name}'):
            self.project_task_info_gen(project_name)
            task_infos = self.project_tasks_info
            config = ConfigParser()

            for task_info in task_infos:
                set_write_permissions(task_info)
            for task_info in task_infos:
                set_read_permission(task_info)

            with open(f'{svn_parent_path}/{project_name}/conf/authz', 'w') as file:
                config.write(file)


            # info report
            info = QMessageBox()
            info.setWindowTitle('Access Control Generation')
            info.setText('Finished')
            info.setIcon(QMessageBox.Information)
            info.exec_()
        else:
            error = QMessageBox()
            error.setWindowTitle('Access Control Generation Error')
            error.setText('svn path do not exist')
            error.setIcon(QMessageBox.Critical)
            error.exec_()

    def project_files_gen(self, project_name, blender,
                          mount_point='C:' + os.environ.get('homepath').replace("\\", "/") + '/projects/'):
        project = gazu.project.get_project_by_name(project_name)
        project_id = project['id']
        project_path = mount_point +'/'+ project_name

        try:
            if not os.path.isdir(mount_point):
                # checking if mount point exist
                os.mkdir(mount_point)
        except FileNotFoundError:
            # info report
            error = QMessageBox()
            error.setWindowTitle('Project File Generation')
            error.setText('invalid mount point')
            error.setIcon(QMessageBox.Critical)
            error.exec_()

        if not os.path.isdir(project_path):
            if os.path.isfile(blender):
                self.folder_structure(mount_point, project_name)
                asset_types = gazu.asset.all_asset_types_for_project(project)
                chars_type_id = None
                props_type_id = None
                envs_type_id = None
                for asset_type in asset_types:
                    if asset_type['name'] == 'chars':
                        chars_type_id = asset_type['id']
                    if asset_type['name'] == 'props':
                        props_type_id = asset_type['id']
                    if asset_type['name'] == 'envs':
                        envs_type_id = asset_type['id']

                if chars_type_id is not None:
                    chars = gazu.asset.all_assets_for_project_and_type(project_id, chars_type_id)
                    for char in chars:
                        chars_path = project_path + '/lib/' + 'chars/'
                        self.asset_gen(char, chars_path, blender)

                if envs_type_id is not None:
                    envs = gazu.asset.all_assets_for_project_and_type(project_id, envs_type_id)
                    for env in envs:
                        envs_path = project_path + '/lib/' + 'envs/'
                        self.asset_gen(env, envs_path, blender)

                if props_type_id is not None:
                    props = gazu.asset.all_assets_for_project_and_type(project_id, props_type_id)
                    for prop in props:
                        props_path = project_path + '/lib/' + 'props/'
                        self.asset_gen(prop, props_path, blender)

                # creates scenes, shots, and shot files
                scenes = gazu.context.all_sequences_for_project(project_id)
                for scene in scenes:
                    self.scene_files_gen(scene, project_path, blender)
            else:
                # info report
                error = QMessageBox()
                error.setWindowTitle('Project File Generation')
                error.setText('Blender executable do not exist')
                error.setIcon(QMessageBox.Critical)
                error.exec_()
        else:
            # info report
            info = QMessageBox()
            info.setWindowTitle('Project File Generation')
            info.setText('project already exist in stated directory')
            info.setIcon(QMessageBox.Information)
            info.exec_()

    def set_file_tree(self, project_name, file_tree_name):
        project = gazu.project.get_project_by_name(project_name)
        project_id = project['id']
        try:
            with open(f'file_trees/{file_tree_name}.json', 'r') as data:
                file_tree = json.load(data)
            gazu.files.update_project_file_tree(project_id, file_tree)


            info = QMessageBox()
            info.setWindowTitle('Set file tree')
            info.setText('Done')
            info.setIcon(QMessageBox.Information)
            info.exec_()
        except json.decoder.JSONDecodeError:
            error = QMessageBox()
            error.setWindowTitle('Set file tree')
            error.setText('invalid json format')
            error.setIcon(QMessageBox.Critical)
            error.exec_()
        # gazu.files.set_project_file_tree(project_id, 'default')

    def new_file_tree(self):
        ctypes.windll.shell32.ShellExecuteW(None, "open", 'notepad', 'C:/users/tanjiro/projects/genesis/file_trees/default.json', None, 1)

    def set_svn_url(self, project_name, url):
        project = gazu.project.get_project_by_name(project_name)
        project_id = project['id']
        gazu.project.update_project_data(project_id, {'repository_url': url})

        info = QMessageBox()
        info.setWindowTitle('Set svn url')
        info.setText('Done')
        info.setIcon(QMessageBox.Information)
        info.exec_()

if __name__ == '__main__':
    pass
    project = Project()
    project.login('https://eaxum.cg-wire.com/api', 'aderemi@eaxum.com', 'testing')
    # set_svn_url('tao', 'isfdfdg')
    # print(gazu.files.build_working_file_path('task'))
    # print(gazu.project.get_project_by_name('tao'))
    # project_files_gen('tao', 'C:/Program Files/Blender Foundation/Blender 2.83/blender.exe', 'C:/users/tanjio/projects/task' )

