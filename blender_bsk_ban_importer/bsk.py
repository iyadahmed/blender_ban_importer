import struct
from typing import Dict

import bpy
from bpy.utils import time_from_frame, time_to_frame
from mathutils import Matrix, Quaternion, Vector

from .common import read_jmx_string, read_jmx_trasnform, read_uint32

__all__ = ("import_bsk",)


def import_bsk(context: bpy.types.Context, filepath):
    """
    File format:
    https://github.com/DummkopfOfHachtenduden/SilkroadDoc/blob/197686f97fdf8815042fb0e8fd62d632390176a9/Formats/JMXVBSK%200101.cs
    https://github.com/DummkopfOfHachtenduden/SilkroadDoc/wiki/JMXVBSK
    """
    bone_parent_map: Dict[str, str] = dict()
    translation_to_parent_map: Dict[str, Vector] = dict()

    armature = bpy.data.armatures.new("")
    armature_object = bpy.data.objects.new("", armature)
    context.scene.collection.objects.link(armature_object)
    armature_object.select_set(True)
    context.view_layer.objects.active = armature_object
    bpy.ops.object.mode_set(mode="EDIT", toggle=False)

    with open(filepath, "rb") as file:
        header = file.read(12)
        assert header == b"JMXVBSK 0101"

        bone_count = read_uint32(file)
        for _ in range(bone_count):
            bone_type = int.from_bytes(file.read(1), "little", signed=False)
            assert bone_type == 0

            bone_name = read_jmx_string(file)
            parent_bone_name = read_jmx_string(file)
            bone_parent_map[bone_name] = parent_bone_name

            new_bone = armature.edit_bones.new(bone_name)

            translation_to_parent, roation_to_parent = read_jmx_trasnform(file)
            translation_to_world, rotation_to_world = read_jmx_trasnform(file)
            translation_to_local, rotation_to_local = read_jmx_trasnform(file)

            translation_to_parent_map[bone_name] = translation_to_parent

            t = translation_to_world.xzy
            t.y *= -1
            new_bone.translate(t)

            child_bone_count = read_uint32(file)
            for _ in range(child_bone_count):
                child_bone_name = read_jmx_string(file)

        file.read(4 * 2)  # Skip unknown data

    editbone: bpy.types.EditBone
    # This is deferred so that all bones are created first
    print("__________________________________")
    # This assumes aramture edit bones is the same order read from file
    for editbone in armature.edit_bones:
        parent_bone_name = bone_parent_map[editbone.name]
        if parent_bone_name != "":
            parent = armature.edit_bones[parent_bone_name]
            editbone.head = parent.tail
            editbone.parent = parent
            editbone.use_connect = True

    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
    return armature_object


if __name__ == "__main__":
    import_bsk(
        bpy.context, bpy.path.abspath("//bsk_ban_test_files/bsk/chinaman_skel.BSK")
    )
