import bpy
import json

bpy.data.collections.remove(bpy.data.collections['Collection'])
name = bpy.path.basename(bpy.context.blend_data.filepath)
collection = bpy.data.collections.new(name[:-6])
bpy.context.scene.collection.children.link(collection)
bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[0]
scene_name = name[:-6].split('_')
bpy.data.scenes['Scene'].name = scene_name[0] + '_' + scene_name[1]

with open('shot_data.json') as data:
    assets = json.load(data)

for i in assets:
    blend_file = i['filepath']
    section = "\\Collection\\"
    object = i['filename']

    file_path = blend_file + section + object
    directory = blend_file + section
    file_name = object

    bpy.ops.wm.link(
        filepath=file_path,
        filename=file_name,
        directory=directory)
bpy.ops.wm.save_mainfile()
bpy.ops.wm.quit_blender()