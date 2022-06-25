import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

import os

from .bsk import import_bsk
from .ban import import_ban


class SILKROAD_OT_import_bsk(Operator):
    bl_idname = "silkroad.import_bsk"
    bl_label = "Import BSK"
    bl_description = "Import armature from a .bsk file"
    bl_options = {"UNDO"}

    bsk_filepath: bpy.props.StringProperty()
    ban_dirpath: bpy.props.StringProperty()

    def execute(self, context):
        if not self.bsk_filepath:
            self.report({"ERROR"}, "BSK filepath not set")
        if not self.ban_dirpath:
            self.report({"ERROR"}, "BAN folder path not set")

        armature_object = import_bsk(context, self.bsk_filepath)

        for entry in os.scandir(self.ban_dirpath):
            if entry.is_file() and entry.name.lower().endswith(".ban"):
                import_ban(context, entry.path, armature_object.pose)
        return {"FINISHED"}


def menu_item_draw_func(self, context):
    self.layout.operator(SILKROAD_OT_import_bsk.bl_idname)


def register():
    bpy.utils.register_class(SILKROAD_OT_import_bsk)
    # bpy.types.TOPBAR_MT_file_import.append(menu_item_draw_func)


def unregister():
    # bpy.types.TOPBAR_MT_file_import.remove(menu_item_draw_func)
    bpy.utils.unregister_class(SILKROAD_OT_import_bsk)
