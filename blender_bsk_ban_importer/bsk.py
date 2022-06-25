import struct
from typing import Dict

import bpy
from bpy.utils import time_from_frame, time_to_frame
from mathutils import Matrix, Quaternion, Vector

from .common import read_jmx_string, read_jmx_trasnform, read_little_int_unsigned

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
        bone_count = read_little_int_unsigned(file)
        for bone_index in range(bone_count):
            if bone_index > 0:
                related_bone_count = read_little_int_unsigned(file)
                for _ in range(related_bone_count):
                    related_bone_name = read_jmx_string(file)

            bone_type = int.from_bytes(file.read(1), "little", signed=False)
            print("Bone Type: ", bone_type)

            bone_name = read_jmx_string(file)
            parent_bone_name = read_jmx_string(file)
            bone_parent_map[bone_name] = parent_bone_name

            new_bone = armature.edit_bones.new(bone_name)

            translation_to_parent, roation_to_parent = read_jmx_trasnform(file)
            translation, rotation = read_jmx_trasnform(file)
            unknown_translation, unknown_rotation = read_jmx_trasnform(file)

            translation_to_parent_map[bone_name] = translation_to_parent

            print("\n")
            print(f"BONE {bone_name}")
            print(f"PARENT: {parent_bone_name}")
            print(f"TRANSLATION TO PARENT: {translation_to_parent}")
            print(f"TRANSLATION: {translation}")
            print(f"UNKNOWN TRANSLATION: {unknown_translation}")
            print("\n")

            t = translation.xzy
            t.y *= -1
            new_bone.translate(t)

        unknown_ints = file.read(4 * 3)  # Unknwon integers
        i, j, k = struct.unpack("<3I", unknown_ints)
        # print("Unknown integers: ", i, j, k)

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
