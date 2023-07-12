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
import time
from .VertexCleaner import cleanup_all_unused_vertex, cleanup_all_vertex
from .WeightTransfer import apply_cloth, unapply_cloth, find_armature, ClothApplyOptions, applicable_meshes
from .Localize import localize

class MY_PT_ui(bpy.types.Panel):  
    bl_label = "Kiseru"
    bl_space_type = "VIEW_3D"  
    bl_region_type = "UI"
    bl_category = "Tool"
    
    def draw(self, context): 
        self.layout.label(text=localize("Cloth"))

        self.layout.prop(context.scene.panel_input, "smooth", slider=True)  # type: ignore
        self.layout.prop(context.scene.panel_input, "auto_clean")  # type: ignore
        self.layout.prop(context.scene.panel_input, "apply_transform")  # type: ignore

        if len(context.scene.processing): # type: ignore
            self.layout.label(text=localize(context.scene.processing)) # type: ignore
        
        row = self.layout.row()
        row.operator(OBJECT_OT_apply_cloth.bl_idname, icon="MOD_CLOTH")
        row.operator(OBJECT_OT_unapply_cloth.bl_idname, icon="MOD_CLOTH")

        self.layout.separator()
        self.layout.label(text=localize("Vertex Groups"))
        
        row = self.layout.row()
        row.operator(OBJECT_OT_remove_all_vertex_groups.bl_idname, icon="TRASH")
        row.operator(OBJECT_OT_remove_all_ununsed_vertex_groups.bl_idname, icon="BRUSH_DATA")

def update_progress_message(message: str|None):
    bpy.context.scene.processing = message or "" # type: ignore
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

def apply_cloth_handler(context):
    try:
        target_objs = applicable_meshes(bpy.context.selected_objects[1:])
        if len(target_objs) < 1:
            print(localize("All selected objects are not applicable."))
            return None
        scene = bpy.context.scene
        smooth_factor = scene.panel_input.smooth # type: ignore
        cleanup = scene.panel_input.auto_clean # type: ignore
        apply_transform = scene.panel_input.apply_transform # type: ignore

        options = ClothApplyOptions(smooth_factor, cleanup, apply_transform, update_progress_message)

        if not apply_cloth(bpy.context.active_object, target_objs, options):
            print("Error")
    finally:
        # update panel
        update_progress_message(None)


class OBJECT_OT_apply_cloth(bpy.types.Operator):
    """Apply weight to all selected objects. 
Last selected mesh will be the source of weight"""
    bl_idname = "mesh.apply_cloth"
    bl_label = localize("Dress Up")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        if context.active_object is None: return False
        if len(bpy.context.selected_objects) < 2: return False
        if find_armature(bpy.context.active_object) is None: return False
        return True

    def execute(self, context): 
        update_progress_message(localize("Dressing up..."))
        
        bpy.app.timers.register(lambda: apply_cloth_handler(bpy.context), first_interval=0.001)

        return {'PASS_THROUGH'}


class OBJECT_OT_unapply_cloth(bpy.types.Operator):
    """Undress all selected objects. Do not select body mesh"""
    bl_idname = "mesh.unapply_cloth"
    bl_label = localize("Undress")
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

class OBJECT_OT_remove_all_vertex_groups(bpy.types.Operator):
    """Remove all vertex groups from selected objects"""
    bl_idname = "mesh.remove_all_vertex_groups"
    bl_label = localize("Remove All")

    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return len(bpy.context.selected_objects) >= 1

    def execute(self, context): 
        if len(bpy.context.selected_objects) < 1: return {'CANCELLED'}
        cleanup_all_vertex(bpy.context.selected_objects)

        return {'FINISHED'}
    
class OBJECT_OT_remove_all_ununsed_vertex_groups(bpy.types.Operator):
    """Remove all unused vertex groups from selected objects"""
    bl_idname = "mesh.remove_all_ununsed_vertex_groups"
    bl_label = localize("Clean")
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
        name=localize("Auto Clean Vertex Groups"),
        description="Auto clean vertex group",
        default=True
    )
    
    apply_transform: bpy.props.BoolProperty( # type: ignore
        name=localize("Apply Transform"),
        description="Apply transform",
        default=False
    )


def register():
    bpy.types.Scene.panel_input = bpy.props.PointerProperty(type=PanelInputsProps) # type: ignore
    bpy.types.Scene.processing = bpy.props.StringProperty(default="") # type: ignore

def unregister():
    del bpy.types.Scene.panel_input # type: ignore
    del bpy.types.Scene.processing # type: ignore
