import bpy
from bpy.types import Panel


class SILKROAD_PT_import(Panel):
    bl_label = "Silkroad Import"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Silkroad Import"

    def draw(self, context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        layout.prop(context.window_manager, "silkroad_bsk_filepath")
        layout.prop(context.window_manager, "silkroad_ban_dirpath")
        op = layout.operator("silkroad.import_bsk")
        op.bsk_filepath = context.window_manager.silkroad_bsk_filepath
        op.ban_dirpath = context.window_manager.silkroad_ban_dirpath


def register():
    bpy.types.WindowManager.silkroad_bsk_filepath = bpy.props.StringProperty(name="BSK", subtype="FILE_PATH")
    bpy.types.WindowManager.silkroad_ban_dirpath = bpy.props.StringProperty(name="BAN Folder", subtype="DIR_PATH")
    bpy.utils.register_class(SILKROAD_PT_import)


def unregister():
    bpy.utils.unregister_class(SILKROAD_PT_import)
    del bpy.types.WindowManager.silkroad_bsk_filepath
    del bpy.types.WindowManager.silkroad_ban_dirpath
