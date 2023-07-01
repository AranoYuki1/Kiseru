import bpy
import re

def cleanup_all_vertex(objects):
    bpy.ops.object.mode_set(mode = 'OBJECT')
    for obj in objects:
        target_vertex_groups = obj.vertex_groups
        for vg in target_vertex_groups:
            target_vertex_groups.remove(vg)

def cleanup_all_unused_vertex(objects):
    for obj in objects:
        cleanup_unused_vertex_groups(obj)
        
def cleanup_unused_vertex_groups(obj):
    ob = obj
    me = obj.data
    
    dict = {}

    for AVG in ob.vertex_groups:
        flag = 0
        index = AVG.index
        for mev in me.vertices:
            for mevg in mev.groups:
                if mevg.group == index:
                    if mevg.weight > 0:
                        flag = 0
                        break                    
                    else:
                        flag = 1                    
                else:
                    flag = 1
            if flag == 0:
                break
        if AVG.name not in dict:
            dict[AVG.name] = flag
        if flag == 0:

            m = re.search(r"(^|_|\.|-|\s)(LEFT|RIGHT)(_+|$|\.+|\s+)|(^|_|\.|-|\s+)(L|R)(_+|$|\.+|\s+)", AVG.name, re.IGNORECASE)

            if m != None:
                m2 = re.search("[A-Z]+", m.group(), re.IGNORECASE)
                if m2 != None:
                    flip_word = ""
                    if m2.group() == "LEFT":
                        flip_word = m.group().replace("LEFT", "RIGHT")
                    elif m2.group() == "Left":
                        flip_word = m.group().replace("Left", "Right")
                    elif m2.group() == "left":
                        flip_word = m.group().replace("left", "right")
                    elif m2.group() == "L":
                        flip_word = m.group().replace("L", "R")
                    elif m2.group() == "l":
                        flip_word = m.group().replace("l", "r")
                    elif m2.group() == "RIGHT":
                        flip_word = m.group().replace("RIGHT", "LEFT")
                    elif m2.group() == "Right":
                        flip_word = m.group().replace("Right", "Left")
                    elif m2.group() == "right":
                        flip_word = m.group().replace("right", "left")
                    elif m2.group() == "R":
                        flip_word = m.group().replace("R", "L")
                    elif m2.group() == "r":
                        flip_word = m.group().replace("r", "l")
                        
                    search_name = re.sub(r"(^|_|\.|-|\s)(LEFT|RIGHT)(_+|$|\.+|\s+)|(^|_|\.|-|\s+)(L|R)(_+|$|\.+|\s+)", flip_word, AVG.name)

                    if search_name in ob.vertex_groups.keys():
                        if search_name not in dict:
                            dict[search_name] = 0

                    else:
                        pass
                else:
                    pass
            else:
                pass

    for key in dict.keys():
        if dict[key] == 1:
            vg = ob.vertex_groups.get(key)
            if vg is not None:
                ob.vertex_groups.remove(vg)