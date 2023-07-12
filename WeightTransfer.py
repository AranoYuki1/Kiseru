from typing import Sequence, Callable
from dataclasses import dataclass

import bpy
import time

from .VertexCleaner import cleanup_unused_vertex_groups, cleanup_all_vertex

def unapply_cloth(obj):
    # remove armature modifier
    remove_all_armature_modifier(obj)
    cleanup_all_vertex([obj])

    obj.parent = None # type: ignore

def smooth_weight(obj: bpy.types.Object, factor: float):
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    
    for group in obj.vertex_groups:
        obj.vertex_groups.active_index = group.index
        bpy.ops.object.vertex_group_smooth(group_select_mode="ALL", factor=factor, repeat=1, expand=0.0)

    bpy.ops.object.mode_set(mode='OBJECT')


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

def remove_all_armature_modifier(obj: bpy.types.Object):
    for modifier in obj.modifiers:
        if modifier.type == "ARMATURE":
            obj.modifiers.remove(modifier)

def make_armature_parent(objs: list[bpy.types.Object], armature: bpy.types.Object):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objs:
        obj.select_set(True)
    
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.parent_set(type='ARMATURE')


def find_armature(source_obj: bpy.types.Object):
    if source_obj.parent is None: return None
    if source_obj.parent.type == "ARMATURE": return source_obj.parent
    return find_armature(source_obj.parent)

def applicable_meshes(target_objs: Sequence[bpy.types.Object]) -> Sequence[bpy.types.Object]:
    res = []

    for target in target_objs:
        if target.type != "MESH": continue
        res.append(target)

    return res

@dataclass  
class ClothApplyOptions:
    smooth: float
    clean: bool
    apply_transform: bool
    message_updator: Callable[[str], None]

def transfer_weights(source_obj: bpy.types.Object, target_objs: Sequence[bpy.types.Object], options: ClothApplyOptions):
    # Select the source object
    bpy.ops.object.select_all(action='DESELECT')
    source_obj.select_set(True)
    bpy.context.view_layer.objects.active = source_obj

    for target_obj in target_objs:
        target_obj.select_set(True)

    options.message_updator("Transfering weights...")

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


def apply_cloth(source_obj: bpy.types.Object, target_objs: Sequence[bpy.types.Object], options: ClothApplyOptions) -> bool:
    # filter target objects with mesh type
    target_objs = list(filter(lambda obj: obj.type == "MESH", target_objs))
    if source_obj.parent is None or len(target_objs) < 1: return False
    
    armature = find_armature(source_obj)
    if armature is None or armature.type != "ARMATURE": return False

    # remove all armature modifier
    if options.clean:
        for i, target_mesh in enumerate(target_objs):
            remove_all_armature_modifier(target_mesh)
            options.message_updator(f"Remove all armature modifier from '{target_mesh.name}' ({i+1} / {len(target_objs)})")

    # apply transform
    if options.apply_transform:
        for i, target_obj in enumerate(target_objs):
            apply_transforms(target_obj)
            options.message_updator(f"Apply transform to '{target_obj.name}' ({i+1} / {len(target_objs)})")

    # make every target objects to armature children
    make_armature_parent(target_objs, armature)
    
    # transfar weight from source to target
    transfer_weights(source_obj, target_objs, options)

    if options.smooth > 0.01:
        for i, target_mesh in enumerate(target_objs):
            # smooth weight
            options.message_updator(f"Smooth weight of '{target_mesh.name}' ({i+1} / {len(target_objs)})")
            smooth_weight(target_mesh, options.smooth)

    # cleanup unused vertex groups
    if options.clean:
        for i, target_mesh in enumerate(target_objs):
            options.message_updator(f"Cleanup unused vertex groups of '{target_mesh.name}' ({i+1} / {len(target_objs)})")
            cleanup_unused_vertex_groups(target_mesh)

    # reselect target objects
    bpy.ops.object.select_all(action='DESELECT')
    for target_mesh in target_objs:
        target_mesh.select_set(True)

    return True
        
