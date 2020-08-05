import os
import gazu
import shutil
import ctypes
import json
from configparser import ConfigParser, NoSectionError
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox
from gazu.exception import MethodNotAllowedException, RouteNotFoundException, NotAuthenticatedException, ParameterException
from requests.exceptions import MissingSchema, InvalidSchema, ConnectionError, InvalidURL


class Project():
    def __init__(self, debug = False):
        self.tasks_info = []
        self.debug = debug
        self.login_name = 'desktop_login'

    def login(self, host, username, password, switch=None):
        switch_window = QtCore.pyqtSignal()
        try:
            gazu.set_host(host)
            gazu.log_in(username, password)
            if switch != None:
                switch.emit()
            if self.debug == True:
                return gazu.log_in(username, password)['user']['full_name']
        except (NotAuthenticatedException, ParameterException):
            if self.debug is False:
                error = QMessageBox()
                error.setWindowTitle('Login Error')
                error.setText('Login failure, Wrong credentials. pls check login details or host')
                error.setIcon(QMessageBox.Critical)
                error.exec_()
            else:
                return 'Login failure, Wrong credentials. pls check login details or host'
        except (MethodNotAllowedException, RouteNotFoundException, InvalidURL):
            if self.debug is False:
                error = QMessageBox()
                error.setWindowTitle('Login Error')
                error.setText('invalid host url')
                error.setIcon(QMessageBox.Critical)
                error.exec_()
            else:
                return 'invalid host url'
        except (MissingSchema, InvalidSchema, ConnectionError) as err:
            if self.debug is False:
                error = QMessageBox()
                error.setWindowTitle('Login Error')
                error.setText(str(err))
                error.setIcon(QMessageBox.Critical)
                error.exec_()
            else:
                return 'bad schema or bad connection'
        except Exception as e:
            if self.debug is False:
                error = QMessageBox()
                error.setWindowTitle('Login Error')
                error.setText('something went wrong:   ' + str(e))
                error.setIcon(QMessageBox.Critical)
                error.exec_()
            else:
                return 'Login Error. something went wrong'

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

    def scene_gen(self, scene, project_path, blender):
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
            with open('data/shot_data.json', 'w') as s_data:
                json.dump(shot_data, s_data, indent=2)
            shot_name = shot['name']
            shot_path = project_path + '/scenes/' + scene_name + '/' + shot_name
            shot_file_tasks = ['lighting', 'anim', 'layout']
            shot_file_name = scene_name + '_' + shot_name + '_'
            os.mkdir(shot_path)

            for shot_file_task in shot_file_tasks:
                shutil.copy('./data/genesis.blend', shot_path)
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
                with open('data/cast_data.json', 'w') as data:
                    json.dump(cast_data, data, indent=2)
                ctypes.windll.shell32.ShellExecuteW(None, "open", blender,
                                                    f'-b --factory-startup "{shot_file_name_task}" --python "./scripts/scenes_setup.py"',
                                                    None, 1)
                while os.path.isfile(shot_file_name_task + '1') == False:
                    pass
                os.remove(shot_file_name_task + '1')

    def asset_gen(self, asset, asset_path, blender):
        asset_name = asset['name']
        asset_file = asset_path + '/' + asset_name + '.blend'
        shutil.copy('./data/genesis.blend', asset_path)
        os.rename(asset_path + '/genesis.blend', asset_file)
        ctypes.windll.shell32.ShellExecuteW(None, "open", blender,
                                            f' -b --factory-startup "{asset_file}" --python "./scripts/setup.py"', None, 1)
        while os.path.isfile(asset_file + '1') == False:
            pass
        os.remove(asset_file + '1')

    def task_info_gen(self, project_name, progress_bar, message_box):
        progress = 4
        project = gazu.project.get_project_by_name(project_name)
        project_id = project['id']
        shots = gazu.shot.all_shots_for_project(project_id)
        assets = gazu.asset.all_assets_for_project(project_id)

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
                    assignee_info = {'full_name': assignee['full_name'], 'id': assignee['id'], 'role': assignee['role'], 'desktop_login': assignee['desktop_login']}
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
                kitsu_working_path = gazu.files.build_working_file_path(asset_task)
                task = gazu.task.get_task(asset_task['id'])
                task_type_name = task["task_type"]["name"]
                assignees = []

                for user in task['assignees']:
                    assignee = gazu.person.get_person(user)
                    assignee_info = {'full_name': assignee['full_name'], 'id': assignee['id'], 'role': assignee['role'], 'desktop_login': assignee['desktop_login']}
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
        progress = 10
        try:
            self.tasks_info.clear()
            for asset in assets:
                asset_task_info(asset, self.tasks_info)
                progress += ((1) / len(assets)) * 35
                if self.debug is False:
                    progress_bar.emit(progress)
                else:
                    print(progress)
            for shot in shots:
                shot_task_info(shot, self.tasks_info)
                progress += ((1) / len(shots)) * 35
                if self.debug is False:
                    progress_bar.emit(progress)
                else:
                    print(progress)
        except gazu.exception.ParameterException as e:
            if self.debug is False:
                message_box.emit('Parameter Exception: ' + str(e))
            else:
                print('Parameter Exception: ' + str(e))

    def svn_config(self, project_name, svn_parent_path, progress_bar=None, message_box = None):
        progress = 80
        all_users = gazu.person.all_persons()

        def set_write_permissions(task_info):
            assignees = task_info['assignees']
            for assignee in assignees:
                if task_info['svn_dir'] in config:
                    config.set(task_info['svn_dir'], assignee[self.login_name], 'rw')
                else:
                    config[task_info['svn_dir']] = {
                        assignee[self.login_name]: 'rw'
                    }
            try:
                config.set(task_info['svn_dir'], '@admin', 'rw')
            except NoSectionError:
                config[task_info['svn_dir']] = {
                        '@admin': 'rw'
                    }


            # print(task_info['assignees'])
            # if task_info['svn_dir'] in config:
            #     assignees = task_info['assignees']
            #     print(assignees)
            #     for assignee in assignees:
            #         config.set(task_info['svn_dir'], assignee[self.login_name], 'rw')
            # else:
            #     assignees = task_info['assignees']
            #     print(assignees)
            #     for assignee in assignees:
            #         config[task_info['svn_dir']] = {
            #             assignee[self.login_name]: 'rw'
            #         }

        def set_read_permission(task_info):
            # this should be called after the set_write_permissions functions
            assignees = task_info['assignees']
            for assignee in assignees:
                for dependency in task_info['dependencies']:
                    if dependency['svn_dir'] in config:
                        if config.has_option(dependency['svn_dir'], assignee[self.login_name]):
                            pass
                        else:
                            config.set(dependency['svn_dir'], assignee[self.login_name], 'r')
                    else:
                        config[dependency['svn_dir']] = {
                            assignee[self.login_name]: 'r'
                        }

        def set_no_permission(task_info):
            # give restriction to non assigned tasks
            if task_info['svn_dir'] in config:
                for user in all_users:
                    if config.has_option(task_info['svn_dir'], user[self.login_name]):
                        pass
                    else:
                        config.set(task_info['svn_dir'], user[self.login_name], '')
            else:
                assignees = task_info['assignees']
                for assignee in assignees:
                    config[task_info['svn_dir']] = {
                        assignee[self.login_name]: 'rw'
                    }

            for user in all_users:
                for dependency in task_info['dependencies']:
                    if dependency['svn_dir'] in config:
                        if config.has_option(dependency['svn_dir'], user[self.login_name]):
                            pass
                        else:
                            config.set(dependency['svn_dir'], user[self.login_name], '')


        # process svn config
        if os.path.isdir(f'{svn_parent_path}/{project_name}'):
            self.task_info_gen(project_name, progress_bar, message_box)
            maps_dirs = [f'{project_name}:/lib/maps',f'{project_name}:/lib/envs/maps', f'{project_name}:/lib/props/maps', f'{project_name}:/lib/chars/maps', f'{project_name}:/lib/nodes/maps']
            task_infos = self.tasks_info
            config = ConfigParser()
            config['groups'] = {
                'admin': 'suser', 'maps': '', 'edit': ''
            }

            config['/'] = {
                '*': 'r', '@admin': 'rw'
            }

            config[f'{project_name}:/edit'] = {
                '@edit': 'rw'
            }
            config.set(f'{project_name}:/edit', '@admin', 'rw')
            for user in all_users:
                config.set(f'{project_name}:/edit', user[self.login_name], '')

            for directory in maps_dirs:
                config[directory] = {
                    '@maps': 'rw'
                }
                config.set(directory, '@admin', 'rw')
                for user in all_users:
                    config.set(directory, user[self.login_name], '')

            for task_info in task_infos:
                set_write_permissions(task_info)
                progress += ((1) / len(task_infos)) * 10
                if self.debug is False:
                    progress_bar.emit(progress)
                else:
                    print(progress)
            for task_info in task_infos:
                set_read_permission(task_info)
                progress += ((1) / len(task_infos)) * 10
                if self.debug is False:
                    progress_bar.emit(progress)
                else:
                    print(progress)
            for task_info in task_infos:
                set_no_permission(task_info)
            for task_info in task_infos:
                if task_info['svn_dir'] not in config:
                    config[task_info['svn_dir']] = {
                        '*': ''
                    }

            # write to svn conf
            # with open('inspection.json') as data:
            #     json.dump(self.tasks_info, data, indent=2)

            with open(f'{svn_parent_path}/{project_name}/conf/authz', 'w') as file:
                config.write(file)

            if self.debug is False:
                message_box.emit('Done')
            else:
                print('Done')
            progress = 0
            if self.debug is False:
                progress_bar.emit(progress)
            else:
                print(progress)
        else:
            if self.debug is False:
                progress = 0
                progress_bar.emit(progress)
                message_box.emit('svn path do not exist')
            else:
                print('svn path do not exist')

    def files_gen(self, project_name, blender,
                  progress_bar=None,
                  message_box = None,
                  mount_point='C:' + os.environ.get('homepath').replace("\\", "/") + '/projects/'):
        project = gazu.project.get_project_by_name(project_name)
        project_id = project['id']
        project_path = mount_point +'/'+ project_name
        progress = 0
        try:
            if not os.path.isdir(mount_point):
                # checking if mount point exist
                os.mkdir(mount_point)
        except FileNotFoundError:
            if self.debug is False:
                progress = 0
                progress_bar.emit(progress)
                message_box.emit('invalid mount point')
            else:
                return 'invalid mount point'

        if not os.path.isdir(project_path):
            if os.path.isfile(blender):
                self.folder_structure(mount_point, project_name)
                asset_types = gazu.asset.all_asset_types_for_project(project)
                chars_type_id = None
                props_type_id = None
                envs_type_id = None
                progress = 10
                if self.debug is False:
                    progress_bar.emit(progress)
                else:
                    print(progress)
                for asset_type in asset_types:
                    if asset_type['name'] == 'chars':
                        chars_type_id = asset_type['id']
                    if asset_type['name'] == 'props':
                        props_type_id = asset_type['id']
                    if asset_type['name'] == 'envs':
                        envs_type_id = asset_type['id']
                    progress += ((1) / len(asset_types)) * 10
                    if self.debug is False:
                        progress_bar.emit(progress)
                    else:
                        print(progress)

                if chars_type_id is not None:
                    chars = gazu.asset.all_assets_for_project_and_type(project_id, chars_type_id)
                    for char in chars:
                        chars_path = project_path + '/lib/' + 'chars/'
                        self.asset_gen(char, chars_path, blender)
                        progress += ((1) / len(chars)) * 10
                        if self.debug is False:
                            progress_bar.emit(progress)
                        else:
                            print(progress)

                if envs_type_id is not None:
                    envs = gazu.asset.all_assets_for_project_and_type(project_id, envs_type_id)
                    for env in envs:
                        envs_path = project_path + '/lib/' + 'envs/'
                        self.asset_gen(env, envs_path, blender)
                        progress += ((1) / len(envs)) * 10
                        if self.debug is False:
                            progress_bar.emit(progress)
                        else:
                            print(progress)

                if props_type_id is not None:
                    props = gazu.asset.all_assets_for_project_and_type(project_id, props_type_id)
                    for prop in props:
                        props_path = project_path + '/lib/' + 'props/'
                        self.asset_gen(prop, props_path, blender)
                        progress += ((1) / len(props)) * 10
                        if self.debug is False:
                            progress_bar.emit(progress)
                        else:
                            print(progress)

                # creates scenes, shots, and shot files
                scenes = gazu.context.all_sequences_for_project(project_id)
                for scene in scenes:
                    self.scene_gen(scene, project_path, blender)
                    progress += ((1) / len(scenes)) * 50
                    if self.debug is False:
                        progress_bar.emit(progress)
                    else:
                        print(progress)
                progress = 0
                if self.debug is False:
                    progress_bar.emit(progress)
                else:
                    print(progress)
                if self.debug is False:
                    message_box.emit('Done')
                else:return 'Done'
            else:
                if self.debug is False:
                    progress = 0
                    progress_bar.emit(progress)
                    message_box.emit('Blender executable do not exist')
                else:
                    return 'Blender executable do not exist'
        else:
            if self.debug is False:
                progress = 0
                progress_bar.emit(progress)
                message_box.emit('project already exist in stated directory')
            else:
                return 'project already exist in stated directory'

    def set_file_tree(self, project_name, file_tree_name):
        project = gazu.project.get_project_by_name(project_name)
        project_id = project['id']
        try:
            with open(f'file_trees/{file_tree_name}.json', 'r') as data:
                file_tree = json.load(data)
            gazu.files.update_project_file_tree(project_id, file_tree)
            if self.debug is False:
                info = QMessageBox()
                info.setWindowTitle('Set file tree')
                info.setText('Done')
                info.setIcon(QMessageBox.Information)
                info.exec_()
            else:
                print('Done')
        except json.decoder.JSONDecodeError:
            if self.debug is False:
                error = QMessageBox()
                error.setWindowTitle('Set file tree')
                error.setText('invalid json format')
                error.setIcon(QMessageBox.Critical)
                error.exec_()
            else:
                print('invalid json format')

    def open_blender(self, blender):
        if os.path.isfile(blender):
            ctypes.windll.shell32.ShellExecuteW(None, "open", blender, '', None, 1)
        else:
            error = QMessageBox()
            error.setWindowTitle('open blender')
            error.setText('blender path not existing')
            error.setIcon(QMessageBox.Critical)
            error.exec_()

    def create_repo(self, project_name, svn_path):
        try:
            shutil.copytree('data/svn_repo', f'{svn_path}/{project_name}')
            error = QMessageBox()
            error.setWindowTitle('svn')
            error.setText('Done')
            error.setIcon(QMessageBox.Information)
            error.exec_()
        except FileExistsError:
            error = QMessageBox()
            error.setWindowTitle('svn Error')
            error.setText('repository folder already exist')
            error.setIcon(QMessageBox.Critical)
            error.exec_()


    def svn_url(self, project_name, local_url, remote_url):
        project = gazu.project.get_project_by_name(project_name)
        project_id = project['id']
        gazu.project.update_project_data(project_id, {'local_svn_url': local_url})
        gazu.project.update_project_data(project_id, {'remote_svn_url': remote_url})
        if self.debug is False:
            info = QMessageBox()
            info.setWindowTitle('Set svn url')
            info.setText('Done')
            info.setIcon(QMessageBox.Information)
            info.exec_()
        else:
            print('Done')

if __name__ == '__main__':
    pass

