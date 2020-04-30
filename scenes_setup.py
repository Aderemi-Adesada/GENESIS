import bpy
import json

bpy.data.collections.remove(bpy.data.collections['Collection'])
name = bpy.path.basename(bpy.context.blend_data.filepath)
collection = bpy.data.collections.new(name[:-6])
bpy.context.scene.collection.children.link(collection)
bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[0]
scene_name = name[:-6].split('_')
bpy.data.scenes['Scene'].name = scene_name[0] + '_' + scene_name[1]

with open('cast_data.json') as data:
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

with open('shot_data.json') as s_data:
    shot_metadata = json.load(s_data)
frame_rate = int(shot_metadata[0]['fps'])
start_frame = int(shot_metadata[0]['frame_in'])
end_frame = int(shot_metadata[0]['frame_out'])

bpy.context.scene.frame_start = start_frame
bpy.context.scene.frame_end = end_frame

def ffmpeg_mp4():
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    is_ntsc = (bpy.context.scene.render.fps != 25)

    bpy.context.scene.render.ffmpeg.format = "MPEG4"
    bpy.context.scene.render.ffmpeg.codec = "H264"

    if is_ntsc:
        bpy.context.scene.render.ffmpeg.gopsize = 18
    else:
        bpy.context.scene.render.ffmpeg.gopsize = 15
    bpy.context.scene.render.ffmpeg.use_max_b_frames = False

    bpy.context.scene.render.ffmpeg.video_bitrate = 6000
    bpy.context.scene.render.ffmpeg.maxrate = 9000
    bpy.context.scene.render.ffmpeg.minrate = 0
    bpy.context.scene.render.ffmpeg.buffersize = 224 * 8
    bpy.context.scene.render.ffmpeg.packetsize = 2048
    bpy.context.scene.render.ffmpeg.muxrate = 10080000


def HDTV_1080p():
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.pixel_aspect_x = 1
    bpy.context.scene.render.pixel_aspect_y = 1
    bpy.context.scene.render.fps = frame_rate
    bpy.context.scene.render.fps_base = 1


def anim_preset():
    ffmpeg_mp4()
    HDTV_1080p()
    bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
    bpy.context.scene.render.filepath = 'anim_preview'


def layout_preset():
    ffmpeg_mp4()
    HDTV_1080p()
    bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
    bpy.context.scene.render.filepath = 'previz'


def lighting_preset():
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    HDTV_1080p()
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.filepath = 'render'

if scene_name[2] == 'anim':
    anim_preset()
elif scene_name[2] == 'layout':
    layout_preset()
elif scene_name[2] == 'lighting':
    lighting_preset()
else:
    pass
##
# bpy.context.scene.render.engine = 'CYCLES'
# bpy.context.scene.render.engine = 'BLENDER_EEVEE'
# bpy.context.scene.render.engine = 'BLENDER_WORKBENCH'
# bpy.context.scene.render.filepath
# bpy.context.scene.render.image_settings.file_format = 'PNG'
# bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.cycles.device = 'GPU'
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_mainfile()
bpy.ops.wm.quit_blender()