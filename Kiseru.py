bl_info = {
    "name": "kiseru_tools",
    "author": "Arano yuki",
    "version": (0, 0, 1),
    "blender": (3, 1, 0),
    "location": "View3D > Sidebar > Edit Tab > Tool > Kiseru",
    "description": "Auto weight transfer",
    "support": "COMMUNITY",
    "category": "Object"
}

import bpy
from .VertexCleaner import cleanup_all_unused_vertex, cleanup_all_vertex
from .WeightTransfer import apply_cloth, unapply_cloth, find_armature, ClothApplyOptions, applicable_meshes

translation_dict = {
    "en_US": {
        "Dress Up": "Dress Up",
        "Undress": "Undress",
        "Remove All": "Remove All",
        "Cloth": "Cloth",
        "Vertex Groups": "Vertex Groups",
        "Clean": "Clean",
        "Auto Clean Vertex Groups": "Auto Clean Vertex Groups",
        "Apply Transform": "Apply Transform",
        "All selected objects are not applicable.": "All selected objects are not applicable.",
    },
    "ja_JP": {
        "Dress Up": "着せる",
        "Undress": "脱がす",
        "Remove All": "全削除",
        "Cloth": "衣装",
        "Vertex Groups": "頂点グループ",
        "Clean": "クリーン",
        "Auto Clean Vertex Groups": "必要な頂点グループのみを残す",
        "Apply Transform": "衣装のトランスフォームを適応",
        "All selected objects are not applicable.": "選択されたすべてのオブジェクトはすでに着せられています。",
    }
}

def get_translation_table() -> dict[str, str]:
    locale = bpy.app.translations.locale or "en_US"
    if locale in translation_dict:
        return translation_dict[locale]
    else:
        return translation_dict["en_US"]

translation_table: dict[str, str] = get_translation_table()

class MY_PT_ui(bpy.types.Panel):  
    bl_label = "Kiseru"
    bl_space_type = "VIEW_3D"  
    bl_region_type = "UI"
    bl_category = "Tool"
    
    def draw(self, context): 
        self.layout.label(text=translation_table["Cloth"])

        self.layout.prop(context.scene.panel_input, "smooth", slider=True)  # type: ignore
        self.layout.prop(context.scene.panel_input, "auto_clean")  # type: ignore
        self.layout.prop(context.scene.panel_input, "apply_transform")  # type: ignore

        row = self.layout.row()
        row.operator(OBJECT_OT_apply_cloth.bl_idname, icon="MOD_CLOTH")
        row.operator(OBJECT_OT_unapply_cloth.bl_idname, icon="MOD_CLOTH")

        self.layout.separator()
        self.layout.label(text=translation_table["Vertex Groups"])
        
        row = self.layout.row()
        row.operator(OBJECT_OT_remove_all_vertex_groups.bl_idname, icon="TRASH")
        row.operator(OBJECT_OT_remove_all_ununsed_vertex_groups.bl_idname, icon="BRUSH_DATA")

class OBJECT_OT_unapply_cloth(bpy.types.Operator):
    """Apply Weight"""
    bl_idname = "mesh.unapply_cloth"
    bl_label = translation_table["Undress"]
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is None: return False
        if context.active_object.parent is None: return False
        if context.active_object.parent.type != "ARMATURE": return False
        # check if armature modifier exists
        for modifier in context.active_object.modifiers:
            if modifier.type == "ARMATURE": return True
        return False

    def execute(self, context): 
        for obj in bpy.context.selected_objects:
            unapply_cloth(obj)

        return {'FINISHED'}

class OBJECT_OT_apply_cloth(bpy.types.Operator):
    """Apply Weight"""
    bl_idname = "mesh.apply_cloth"
    bl_label = translation_table["Dress Up"]
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is None: return False
        if len(bpy.context.selected_objects) < 2: return False
        if find_armature(bpy.context.active_object) is None: return False
        return True

    def execute(self, context): 
        
        target_objs = applicable_meshes(bpy.context.selected_objects[1:])
        print(target_objs)
        if len(target_objs) < 1:
            self.report({'ERROR'}, translation_table["All selected objects are not applicable."])
            return {'CANCELLED'}
        scene = bpy.context.scene
        smooth_factor = scene.panel_input.smooth # type: ignore
        cleanup = scene.panel_input.auto_clean # type: ignore
        apply_transform = scene.panel_input.apply_transform # type: ignore

        options = ClothApplyOptions(smooth_factor, cleanup, apply_transform)

        if apply_cloth(bpy.context.active_object, target_objs, options):
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

class OBJECT_OT_remove_all_vertex_groups(bpy.types.Operator):
    """Apply Weight"""
    bl_idname = "mesh.remove_all_vertex_groups"
    bl_label = translation_table["Remove All"] 

    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(bpy.context.selected_objects) >= 1

    def execute(self, context): 
        if len(bpy.context.selected_objects) < 1: return {'CANCELLED'}
        cleanup_all_vertex(bpy.context.selected_objects)

        return {'FINISHED'}
    
class OBJECT_OT_remove_all_ununsed_vertex_groups(bpy.types.Operator):
    """Apply Weight"""
    bl_idname = "mesh.remove_all_ununsed_vertex_groups"
    bl_label = translation_table["Clean"] 
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(bpy.context.selected_objects) >= 1

    def execute(self, context): 
        if len(bpy.context.selected_objects) < 1: return {'CANCELLED'}
        cleanup_all_unused_vertex(bpy.context.selected_objects)

        return {'FINISHED'}

class PanelInputsProps(bpy.types.PropertyGroup):
    smooth: bpy.props.FloatProperty( # type: ignore
        name="Smooth",
        description="How much to smooth the weight",
        default=0.1,
        min=0,
        max=1
    )
    
    auto_clean: bpy.props.BoolProperty( # type: ignore
        name=translation_table["Auto Clean Vertex Groups"],
        description="Auto clean vertex group",
        default=True
    )

    apply_transform: bpy.props.BoolProperty( # type: ignore
        name=translation_table["Apply Transform"],
        description="Apply transform",
        default=False
    )


def register():
    bpy.types.Scene.panel_input = bpy.props.PointerProperty(type=PanelInputsProps) # type: ignore

def unregister():
    del bpy.types.Scene.panel_input # type: ignore
    bpy.app.translations.unregister(__name__)