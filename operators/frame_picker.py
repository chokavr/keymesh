import bpy
from ..functions.poll import is_not_linked, obj_data_type
from ..functions.timeline import insert_keyframe


#### ------------------------------ OPERATORS ------------------------------ ####

class OBJECT_OT_keymesh_pick_frame(bpy.types.Operator):
    bl_label = "Pick Keymesh Frame"
    bl_idname = "object.keymesh_pick_frame"
    bl_description = "Link the selected Keymesh block to the current object"

    keymesh_index: bpy.props.StringProperty(
    )

    def execute(self, context):
        scene = context.scene
        obj = context.active_object
        data_type = obj_data_type(obj)

        current_mode = obj.mode
        if current_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # assign_keymesh_block_to_object
        obj.data = data_type[self.keymesh_index]
        keymesh_block = context.active_object.data.keymesh.get("Data")

        # Keyframe Block
        if obj in context.editable_objects:
            if scene.keymesh.insert_on_selection:
                action = obj.animation_data.action
                if action:
                    if action.library is None:
                        insert_keyframe(obj, keymesh_block, scene.frame_current)
                    else:
                        self.report({'INFO'}, "You cannot animate in library overriden action. Create local one")
                else:
                    insert_keyframe(obj, keymesh_block, scene.frame_current)

            bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}


class OBJECT_OT_keymesh_block_move(bpy.types.Operator):
    bl_idname = "object.keymesh_block_move"
    bl_label = "Move Keymesh Block"
    bl_description = "Move the active Keymesh block up or down in the frame picker"
    bl_options = {'UNDO'}

    direction: bpy.props.EnumProperty(
        name = "Direction",
        items = [('UP', "", ""),
                ('DOWN', "", ""),],
    )

    @classmethod
    def poll(cls, context):
        return is_not_linked(context)

    def execute(self, context):
        obj = context.active_object
        index = int(obj.keymesh.block_active_index)

        if self.direction == 'UP' and index > 0:
            obj.keymesh.blocks.move(index, index - 1)
            obj.keymesh.block_active_index -= 1

        elif self.direction == 'DOWN' and (index + 1) < len(obj.keymesh.blocks):
            obj.keymesh.blocks.move(index, index + 1)
            obj.keymesh.block_active_index += 1
        return {'FINISHED'}



#### ------------------------------ REGISTRATION ------------------------------ ####

classes = [
    OBJECT_OT_keymesh_pick_frame,
    OBJECT_OT_keymesh_block_move,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
