import bpy
# bpy.ops.wm.open_mainfile(filepath='')
bpy.data.collections.remove(bpy.data.collections['Collection'])
name = bpy.path.basename(bpy.context.blend_data.filepath)
collection = bpy.data.collections.new(name[:-6])
bpy.context.scene.collection.children.link(collection)
bpy.ops.wm.save_mainfile()
bpy.ops.wm.quit_blender()
