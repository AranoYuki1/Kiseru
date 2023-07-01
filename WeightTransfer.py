from typing import Sequence


import bpy

from .VertexCleaner import cleanup_unused_vertex_groups, cleanup_all_vertex

def unapply_cloth(obj: bpy.types.Object):
    if "Armature" in obj.modifiers.keys():
        obj.modifiers.remove(obj.modifiers["Armature"])

    cleanup_all_vertex([obj])

    obj.parent = None # type: ignore

def smooth_weight(obj: bpy.types.Object, factor: float):
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    
    for group in obj.vertex_groups:
        obj.vertex_groups.active_index = group.index
        bpy.ops.object.vertex_group_smooth(group_select_mode="ALL", factor=factor, repeat=1, expand=0.0)

    bpy.ops.object.mode_set(mode='OBJECT')

def transfer_weights(source_obj: bpy.types.Object, target_objs: Sequence[bpy.types.Object]):
    # Select the source object
    bpy.ops.object.select_all(action='DESELECT')
    source_obj.select_set(True)
    bpy.context.view_layer.objects.active = source_obj

    for target_obj in target_objs:
        target_obj.select_set(True)

    # Transfer weights
    bpy.ops.object.data_transfer(
        data_type='VGROUP_WEIGHTS',
        use_create=True,
        layers_select_src="ALL",
        layers_select_dst='NAME',
        vert_mapping="POLYINTERP_NEAREST",
        mix_mode="REPLACE"
    )

    # Deselect the target objects
    for target_obj in target_objs:
        target_obj.select_set(False)

def apply_transforms(obj: bpy.types.Object):
    matrix = obj.matrix_world
    for vert in obj.data.vertices: # type: ignore
        vert.co = matrix @ vert.co
    obj.matrix_world = [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0 ,0, 1, 0],
        [0, 0, 0, 1]
    ]

def find_armature(source_obj: bpy.types.Object):
    if source_obj.parent is None: return None
    if source_obj.parent.type == "ARMATURE": return source_obj.parent
    return find_armature(source_obj.parent)

def apply_cloth(source_obj: bpy.types.Object, target_objs: Sequence[bpy.types.Object], smooth: float, clean: bool) -> bool:
    # filter target objects with mesh type
    target_objs = list(filter(lambda obj: obj.type == "MESH", target_objs))
    if source_obj.parent is None or len(target_objs) < 1: return False
    
    armature = find_armature(source_obj)
    if armature is None or armature.type != "ARMATURE": return False

    # apply transforms of target objects
    for target_mesh in target_objs:
        apply_transforms(target_mesh)
    
    # add armature modifier to target meshes

    for target_mesh in target_objs:
        a = target_mesh.modifiers.new(name="Armature", type='ARMATURE')
        a.object = armature #type: ignore
        target_mesh.parent = armature
    
    # transfar weight from source to target
    transfer_weights(source_obj, target_objs)

    for target_mesh in target_objs:
        smooth_weight(target_mesh, smooth)

    # cleanup unused vertex groups
    if clean:
        for target_mesh in target_objs:
            cleanup_unused_vertex_groups(target_mesh)

    return True
        
