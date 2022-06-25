import bpy
from bpy.utils import time_from_frame, time_to_frame
from mathutils import Matrix

from .common import read_jmx_string, read_jmx_trasnform, read_uint32


def import_ban(context: bpy.types.Context, filepath, bsk_pose: bpy.types.Pose):
    """Reference:
    https://github.com/DummkopfOfHachtenduden/SilkroadDoc/blob/197686f97fdf8815042fb0e8fd62d632390176a9/Formats/JMXVBAN%200102.cs
    https://github.com/DummkopfOfHachtenduden/SilkroadDoc/wiki/JMXVBAN
    """
    return
    with open(filepath, "rb") as file:
        header = file.read(12)
        assert header == b"JMXVBAN 0102"
        # Two unknown integers
        file.read(4)  # Introduced in JMXVBAN 0102, 0 in all files
        file.read(4)  # Introduced in JMXVBAN 0102, 0 in all files
        name = read_jmx_string(file)
        duration = read_uint32(file)
        fps = read_uint32(file)
        is_continuos = read_uint32(file)

        keyframe_timings_count = read_uint32(file)
        keyframe_timings = [read_uint32(file) for _ in range(keyframe_timings_count)]

        # Amount of bones that have transformations, that are diffrent from their bind poses.
        animated_bones_count = read_uint32(file)
        for _ in range(animated_bones_count):
            bone_name = read_jmx_string(file).decode()
            keyframe_count = read_uint32(file)
            assert keyframe_count == keyframe_timings_count
            for i in range(keyframe_count):
                translation, rotation = read_jmx_trasnform(file)
                pose_bone = bsk_pose.bones[bone_name]
                # pose_bone.rotation_mode = "QUATERNION"
                # pose_bone.rotation_quaternion = rotation
                # pose_bone.location = translation
                if pose_bone.parent:
                    mat = pose_bone.parent.matrix
                else:
                    mat = Matrix()
                mat = mat @ Matrix.Translation(translation)
                mat = mat @ rotation.to_matrix().to_4x4()
                pose_bone.matrix = mat
                pose_bone.keyframe_insert(
                    "rotation_quaternion", frame=keyframe_timings[i]
                )
                pose_bone.keyframe_insert("location", frame=keyframe_timings[i])
