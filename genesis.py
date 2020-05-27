import os
import gazu
import shutil
import ctypes
import json
from configparser import ConfigParser

gazu.set_host('https://eaxum.cg-wire.com/api')
gazu.log_in('aderemi@eaxum.com', 'efosadiya')
# project = gazu.project.get_project_by_name('tao')
# project_id = '665ce354-8e1f-41b5-9c47-16132aa98bc7'
# blender = "C:/Program Files/Blender Foundation/Blender 2.82/blender.exe"


####################################################################################################
# todo


def asset_gen(asset, asset_path):
    asset_name = asset['name']
    asset_file = asset_path + '/' + asset_name + '.blend'
    shutil.copy('./genesis.blend', asset_path)
    os.rename(asset_path + '/genesis.blend', asset_file)
    ctypes.windll.shell32.ShellExecuteW(None, "open", blender,
                                        f' -b --factory-startup "{asset_file}" --python "./setup.py"', None, 1)
    while os.path.isfile(asset_file + '1') == False:
        pass
    os.remove(asset_file + '1')


def test():
    a = gazu.project.all_open_projects()
    for i in a:
        print(i['name'])

def create_svn_config(json_data, project_name):
    with open(json_data, 'r') as data:
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
        # this should be called after the set_write_permissions functions
        assignees = task_info['assignees']
        for assignee in assignees:
            for dependency in task_info['dependencies']:
                if dependency['svn_dir'] in config:
                    if config.has_option(dependency['svn_dir'], assignee['full_name']):
                        pass
                    else:
                        config.set(dependency['svn_dir'], assignee['full_name'], 'r')

    for task_info in task_infos:
        set_write_permissions(task_info)

    for task_info in task_infos:
        set_read_permission(task_info)

    with open(f'{project_name}_svn_config.txt', 'w') as f:
        config.write(f)


def project_task_info_gen(project_name):
    project = gazu.project.get_project_by_name(project_name)
    project_id = project['id']
    shots = gazu.shot.all_shots_for_project(project_id)
    assets = gazu.asset.all_assets_for_project(project_id)
    kitsu_task_types = gazu.task.all_task_types()
    project_tasks_info = []

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

    for asset in assets:
        asset_task_info(asset, project_tasks_info)
    for shot in shots:
        shot_task_info(shot, project_tasks_info)
    with open(f'{project_name}_tasks_info.json', 'w') as data:
        json.dump(project_tasks_info, data, indent=2)


def project_files_gen(project_name,
                      blender,
                      mount_point='C:' + os.environ.get('homepath').replace("\\", "/") + '/projects/'):
    project = gazu.project.get_project_by_name(project_name)
    project_id = project['id']

    cast_data = []
    shot_data = []

    # creating main directories
    base_directories = ['edit', 'lib', 'refs', 'scenes', 'tools']
    lib_directories = ['chars', 'envs', 'maps', 'nodes', 'props']
    # drive = 'C:'
    # user = os.environ.get('homepath').replace("\\", "/")
    # mount_point = drive + user + '/projects/'
    project_path = mount_point + project_name

    if not os.path.isdir(mount_point):
        # checking if mount point exist
        os.mkdir(mount_point)

    if not os.path.isdir(project_path):
        # checking if project path exist
        os.mkdir(project_path)

        # creating base directories in the project folder
        for directory in base_directories:
            os.mkdir(project_path + '/' + directory)

        # creates lib sub directories
        for directory in lib_directories:
            os.mkdir(project_path + '/lib/' + directory)

        # creates all required assets for the project#########################################
        project_asset_types = gazu.asset.all_asset_types_for_project(project)

        chars_type_id = None
        props_type_id = None
        envs_type_id = None

        for asset_type in project_asset_types:
            if asset_type['name'] == 'chars':
                chars_type_id = asset_type['id']
            if asset_type['name'] == 'props':
                props_type_id = asset_type['id']
            if asset_type['name'] == 'envs':
                envs_type_id = asset_type['id']

        chars = gazu.asset.all_assets_for_project_and_type(project_id, chars_type_id)
        envs = gazu.asset.all_assets_for_project_and_type(project_id, envs_type_id)
        props = gazu.asset.all_assets_for_project_and_type(project_id, props_type_id)
        chars_path = project_path + '/lib/' + 'chars/'
        envs_path = project_path + '/lib/' + 'envs/'
        props_path = project_path + '/lib/' + 'props/'

        for char in chars:
            asset_gen(char, chars_path)
        for env in envs:
            asset_gen(env, envs_path)
        for prop in props:
            asset_gen(prop, props_path)

        # creates scenes, shots, and shot files
        scenes = gazu.context.all_sequences_for_project(project_id)
        for scene in scenes:
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
                            cast_data.append({'filepath': chars_path + cast['asset_name'] + '.blend', 'filename': cast['asset_name']})
                        if cast['asset_type_name'] == 'envs':
                            cast_data.append({'filepath': envs_path + cast['asset_name'] + '.blend', 'filename': cast['asset_name']})
                        if cast['asset_type_name'] == 'props':
                            cast_data.append({'filepath': props_path + cast['asset_name'] + '.blend', 'filename': cast['asset_name']})
                    with open('cast_data.json', 'w') as data:
                        json.dump(cast_data, data, indent=2)
                    ctypes.windll.shell32.ShellExecuteW(None, "open", blender, f'-b --factory-startup "{shot_file_name_task}" --python "./scenes_setup.py"', None, 1)
                    while os.path.isfile(shot_file_name_task + '1') == False:
                        pass
                    os.remove(shot_file_name_task + '1')


blender = "C:/Program Files/Blender Foundation/Blender 2.82/blender.exe"
project_files_gen('tao', blender)