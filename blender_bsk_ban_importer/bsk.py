from collections import defaultdict

import bpy

from .common import read_jmx_string, read_jmx_trasnform, read_uint32

__all__ = ("import_bsk",)


def import_bsk(context: bpy.types.Context, filepath):
    """
    File format:
    https://github.com/DummkopfOfHachtenduden/SilkroadDoc/blob/197686f97fdf8815042fb0e8fd62d632390176a9/Formats/JMXVBSK%200101.cs
    https://github.com/DummkopfOfHachtenduden/SilkroadDoc/wiki/JMXVBSK
    """

    armature = bpy.data.armatures.new("")
    armature_object = bpy.data.objects.new("", armature)

    context.scene.collection.objects.link(armature_object)
    armature_object.select_set(True)
    context.view_layer.objects.active = armature_object
    bpy.ops.object.mode_set(mode="EDIT", toggle=False)

    bone_map = defaultdict(lambda: armature.edit_bones.new(""))

    with open(filepath, "rb") as file:
        header = file.read(12)
        assert header == b"JMXVBSK 0101"

        bone_count = read_uint32(file)
        for _ in range(bone_count):
            bone_type = int.from_bytes(file.read(1), "little", signed=False)
            assert bone_type == 0

            bone_name = read_jmx_string(file)
            parent_bone_name = read_jmx_string(file)

            bone = bone_map[bone_name]
            bone.name = bone_name

            translation_to_parent, roation_to_parent = read_jmx_trasnform(file)
            translation_to_world, rotation_to_world = read_jmx_trasnform(file)
            translation_to_local, rotation_to_local = read_jmx_trasnform(file)

            t = translation_to_world.xzy
            t.y *= -1
            bone.translate(t)

            if parent_bone_name != "":
                parent = bone_map[parent_bone_name]
                bone.head = parent.tail
                bone.parent = parent
                bone.use_connect = True

            child_bone_count = read_uint32(file)
            for _ in range(child_bone_count):
                child_bone_name = read_jmx_string(file)

        file.read(4 * 2)  # Skip unknown data

    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
    return armature_object
