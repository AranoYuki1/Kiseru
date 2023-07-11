from typing import Sequence
from dataclasses import dataclass

import bpy
import re

def cleanup_all_vertex(objects: Sequence[bpy.types.Object]):
    bpy.ops.object.mode_set(mode = 'OBJECT')
    for obj in objects:
        target_vertex_groups = obj.vertex_groups
        for vg in target_vertex_groups:
            target_vertex_groups.remove(vg)


def cleanup_all_unused_vertex(objects: Sequence[bpy.types.Object]):
    for obj in objects:
        cleanup_unused_vertex_groups(obj)
    
# ------------------------------------------------------------------------------ # 

@dataclass
class CleanupContext:
    object: bpy.types.Object
    mesh: bpy.types.Mesh
    index_to_name: dict[int, str] 
    name_to_index: dict[str, int] 
    
    def __init__(self, object: bpy.types.Object):
        self.object = object
        self.mesh = object.data # type: ignore
        assert isinstance(self.mesh, bpy.types.Mesh)
        self.index_to_name = {}
        self.name_to_index = {}
        for name, group in object.vertex_groups.items():
            self.index_to_name[group.index] = name
            self.name_to_index[name] = group.index
    
def flip_vertex_group_name(name: str) -> str | None:
    """Flip the vertex group name. If the name is not a left or right name, return None."""

    match = re.search(r"(^|_|\.|-|\s)(LEFT|RIGHT)(_+|$|\.+|\s+)|(^|_|\.|-|\s+)(L|R)(_+|$|\.+|\s+)", name, re.IGNORECASE)

    if match is None: return None
    
    match2 = re.search("[A-Z]+", match.group(), re.IGNORECASE)

    if match2 is None: return None
    
    flip_word = ""
    if   match2.group() == "LEFT":  flip_word = match.group().replace("LEFT", "RIGHT")
    elif match2.group() == "Left":  flip_word = match.group().replace("Left", "Right")
    elif match2.group() == "left":  flip_word = match.group().replace("left", "right")
    elif match2.group() == "L":     flip_word = match.group().replace("L", "R")
    elif match2.group() == "l":     flip_word = match.group().replace("l", "r")
    elif match2.group() == "RIGHT": flip_word = match.group().replace("RIGHT", "LEFT")
    elif match2.group() == "Right": flip_word = match.group().replace("Right", "Left")
    elif match2.group() == "right": flip_word = match.group().replace("right", "left")
    elif match2.group() == "R":     flip_word = match.group().replace("R", "L")
    elif match2.group() == "r":     flip_word = match.group().replace("r", "l")
        
    search_name = re.sub(r"(^|_|\.|-|\s)(LEFT|RIGHT)(_+|$|\.+|\s+)|(^|_|\.|-|\s+)(L|R)(_+|$|\.+|\s+)", flip_word, name)

    return search_name


def depending_vertex_group_indices(context: CleanupContext) -> set[int]:
    """Return the set of vertex group indices that are used in the mesh."""
    indices = set()

    for vertice in context.mesh.vertices:
        for group in vertice.groups:
            if group.weight > 0:
                indices.add(group.group)

    return indices


def depending_vertex_group_indices_with_flip(context: CleanupContext) -> set[int]:
    """Return the set of vertex group indices that are used in the mesh. If the vertex group name is a left or right name, also add the opposite name."""
    indices = depending_vertex_group_indices(context)

    for index in indices:
        name = context.index_to_name[index]
        flip_name = flip_vertex_group_name(name)
        
        if flip_name is not None and flip_name in context.name_to_index:
            indices.add(context.name_to_index[flip_name])

    return indices

def has_mirror_modifier(object: bpy.types.Object) -> bool:
    """Return True if the object has a mirror modifier."""
    for modifier in object.modifiers:
        if modifier.type == "MIRROR":
            return True
    return False

def cleanup_unused_vertex_groups(object: bpy.types.Object):
    mesh = object.data
    if not isinstance(mesh, bpy.types.Mesh): return

    context = CleanupContext(object)

    indices = depending_vertex_group_indices_with_flip(context)

    for _, group in object.vertex_groups.items():
        if context.name_to_index[group.name] not in indices:
            object.vertex_groups.remove(group)
    

























# def cleanup_unused_vertex_groups(obj: bpy.types.Object):
#     mesh = obj.data
#     if not isinstance(mesh, bpy.types.Mesh):
#         return
    
#     should_remove_table: dict[str, bool] = {}

#     for vertex_group in obj.vertex_groups:
#         should_remove = False
        
#         for vertice in mesh.vertices:
#             for group in vertice.groups:
#                 if group.group == vertex_group.index and group.weight > 0:
#                     should_remove = False
#                     break
#                 else:
#                     should_remove = True
                    
#             if should_remove == False:
#                 break
            
#         if vertex_group.name not in should_remove_table:
#             should_remove_table[vertex_group.name] = should_remove
        
#         if should_remove == True: continue

#         match = re.search(r"(^|_|\.|-|\s)(LEFT|RIGHT)(_+|$|\.+|\s+)|(^|_|\.|-|\s+)(L|R)(_+|$|\.+|\s+)", vertex_group.name, re.IGNORECASE)

#         if match != None:
#             m2 = re.search("[A-Z]+", match.group(), re.IGNORECASE)
#             if m2 != None:
#                 flip_word = ""
#                 if m2.group() == "LEFT":    flip_word = match.group().replace("LEFT", "RIGHT")
#                 elif m2.group() == "Left":  flip_word = match.group().replace("Left", "Right")
#                 elif m2.group() == "left":  flip_word = match.group().replace("left", "right")
#                 elif m2.group() == "L":     flip_word = match.group().replace("L", "R")
#                 elif m2.group() == "l":     flip_word = match.group().replace("l", "r")
#                 elif m2.group() == "RIGHT": flip_word = match.group().replace("RIGHT", "LEFT")
#                 elif m2.group() == "Right": flip_word = match.group().replace("Right", "Left")
#                 elif m2.group() == "right": flip_word = match.group().replace("right", "left")
#                 elif m2.group() == "R":     flip_word = match.group().replace("R", "L")
#                 elif m2.group() == "r":     flip_word = match.group().replace("r", "l")
                    
#                 search_name = re.sub(r"(^|_|\.|-|\s)(LEFT|RIGHT)(_+|$|\.+|\s+)|(^|_|\.|-|\s+)(L|R)(_+|$|\.+|\s+)", flip_word, vertex_group.name)

#                 if search_name in obj.vertex_groups.keys() and search_name not in should_remove_table:
#                     should_remove_table[search_name] = False

#     for key in should_remove_table.keys():
#         if should_remove_table[key] == True:
#             vg = obj.vertex_groups.get(key)
#             if vg is not None:
#                 obj.vertex_groups.remove(vg)