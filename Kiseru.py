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
from .WeightTransfer import apply_cloth, unapply_cloth, find_armature

class MY_PT_ui(bpy.types.Panel):  
    bl_label = "Kiseru"
    bl_space_type = "VIEW_3D"  
    bl_region_type = "UI"
    bl_category = "Tool"
    
    def draw(self, context): 
        self.layout.label(text="衣装")

        self.layout.prop(context.scene.panel_input, "smooth", slider=True)  # type: ignore
        self.layout.prop(context.scene.panel_input, "auto_clean")  # type: ignore

        row = self.layout.row()
        row.operator(OBJECT_OT_apply_cloth.bl_idname, icon="MOD_CLOTH")
        row.operator(OBJECT_OT_unapply_cloth.bl_idname, icon="MOD_CLOTH")

        self.layout.separator()
        self.layout.label(text="頂点グループ")
        
        row = self.layout.row()
        row.operator(OBJECT_OT_remove_all_vertex_groups.bl_idname, icon="TRASH")
        row.operator(OBJECT_OT_remove_all_ununsed_vertex_groups.bl_idname, icon="BRUSH_DATA")

class OBJECT_OT_unapply_cloth(bpy.types.Operator):
    """Apply Weight"""
    bl_idname = "mesh.unapply_cloth"
    bl_label = "脱がす"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is None: return False
        if context.active_object.parent is None: return False
        if context.active_object.parent.type != "ARMATURE": return False
        if "Armature" not in context.active_object.modifiers.keys(): return False
        return True

    def execute(self, context): 
        for obj in bpy.context.selected_objects:
            unapply_cloth(obj)

        return {'FINISHED'}

class OBJECT_OT_apply_cloth(bpy.types.Operator):
    """Apply Weight"""
    bl_idname = "mesh.apply_cloth"
    bl_label = "着せる"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is None: return False
        if len(bpy.context.selected_objects) < 2: return False
        if find_armature(bpy.context.active_object) is None: return False
        return True

    def execute(self, context): 
        target_objs = bpy.context.selected_objects[1:]
        smooth_factor = bpy.context.scene.panel_input.smooth # type: ignore
        cleanup = bpy.context.scene.panel_input.auto_clean # type: ignore

        if apply_cloth(bpy.context.active_object, target_objs, smooth_factor, cleanup):
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

class OBJECT_OT_remove_all_vertex_groups(bpy.types.Operator):
    """Apply Weight"""
    bl_idname = "mesh.remove_all_vertex_groups"
    bl_label = "全削除"
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
    bl_label = "クリーン"
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
        name="頂点グループをクリーン",
        description="Auto clean vertex group",
        default=True
    )


def register():
    bpy.types.Scene.panel_input = bpy.props.PointerProperty(type=PanelInputsProps) # type: ignore

def unregister():
    del bpy.types.Scene.panel_input # type: ignore