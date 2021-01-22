# Copyright (c) 2021 Samia

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import bmesh
import copy
import math
import mathutils

from .utils.bl_anotations import make_annotations


@make_annotations
class PAT_ToolSettings(bpy.types.PropertyGroup):
    display_edge_oder = bpy.props.BoolProperty(
        name="Selected Edge Loop Oder Settings",
        description="Display Settings of the Selected Edge Loop Oder",
        default=True,
        options={'HIDDEN'}
    )
    display_edge_loop_order = bpy.props.BoolProperty(
        name="Midpoint of selected Edge Loop Oder Settings",
        description="Display Settings of Midpoint of selected Edge Loop Oder",
        default=True,
        options={'HIDDEN'}
    )
    edge_offset = bpy.props.FloatProperty(
        name="Offset",
        description="Bone location offset",
        default=0.0,
        options={'HIDDEN'}
    )
    use_auto_bone_roll = bpy.props.BoolProperty(
        name="Auto Bone Roll",
        description="Automatically sets the roll value of the bones",
        default=True,
        options={'HIDDEN'}
    )
    use_auto_bone_weight = bpy.props.BoolProperty(
        name="Auto Bone Weight",
        description="Automatically sets the bone weights",
        default=True,
        options={'HIDDEN'}
    )
    # bone_name = bpy.props.StringProperty(
    #     name="BoneName",
    #     description="Bone name",
    #     default="Bone"
    # )
    #
    # bone_name_junction = bpy.props.StringProperty(
    #     name="BoneNameSeparator",
    #     description="Bone name separator",
    #     default="."
    # )
    #
    # bone_name_suffix = bpy.props.StringProperty(
    #     name="BoneNameSuffix",
    #     description="Bone name suffix",
    #     default=""
    # )
    #
    # zero_padding = bpy.props.IntProperty(
    #     name="Zeropadding",
    #     description="Number of digits of bone name zero padding",
    #     default=3,
    #     min=0,
    #     max=6
    # )
    #
    # is_reverse = bpy.props.BoolProperty(
    #     name="Reverse",
    #     description="Change the bone order to the reverse order",
    #     default=False
    # )
    #
    # is_parent = bpy.props.BoolProperty(
    #     name="Parent",
    #     description="Set parent bone",
    #     default=True
    # )
    #
    # use_connect = bpy.props.BoolProperty(
    #     name="Connected",
    #     description="When Bone has a parent,bone's head is stuck tp the parent's tail",
    #     default=True
    # )


@make_annotations
class PAT_OT_Base:
    use_offset = bpy.props.BoolProperty(
        name="Offset",
        description="Bone location offset",
        default=False,
        options={'HIDDEN'}
    )
    use_auto_bone_roll = bpy.props.BoolProperty(
        name="Auto Bone Roll",
        description="Automatically sets the roll value of the bones",
        default=True,
        options={'HIDDEN'}
    )
    use_auto_bone_weight = bpy.props.BoolProperty(
        name="Auto Bone Weight",
        description="Automatically sets the bone weights",
        default=True,
        options={'HIDDEN'}
    )

    def _get_distance(self, vector0, vector1):
        distance = math.sqrt((vector0[0] - vector1[0]) ** 2 +
                             (vector0[1] - vector1[1]) ** 2 +
                             (vector0[2] - vector1[2]) ** 2)
        return distance

    def _get_select_edge_location(self, context, bm):
        new_bones = []
        head = None
        tail = None

        for i, e in enumerate(bm.select_history):  # type: (int, bmesh.types.BMEdge)
            if isinstance(e, bmesh.types.BMEdge) and e.select:
                v0 = e.verts[0]
                v1 = e.verts[1]
                if head:
                    if self._get_distance(head.co, v0.co) > self._get_distance(head.co, v1.co):
                        v0, v1 = v1, v0
                    if not self.pref.use_connect:
                        head = v0
                    tail = v1
                else:
                    if len(bm.select_history) > 2:
                        v2 = bm.select_history[i + 1].verts[0]
                        v3 = bm.select_history[i + 1].verts[1]

                        if self._get_distance(v0.co, v2.co) < self._get_distance(v1.co, v2.co):
                            v0, v1 = v1, v0
                    head = v0
                    tail = v1

                normal = (head.normal + tail.normal) / 2
                new_bones.append({"indexes": (copy.copy(head.index), copy.copy(tail.index)), "head": copy.copy(head.co),
                                  "tail": copy.copy(tail.co), "roll": 0, "normal": copy.copy(normal)})
                head = tail

        return new_bones

    def _get_select_edge_loops_location(self, context, bm):
        current_cursor = copy.copy(context.scene.cursor_location) if bpy.app.version < (2, 80) \
            else copy.copy(context.scene.cursor.location)

        select_edges = []
        for select_edge in bm.select_history:
            if isinstance(select_edge, bmesh.types.BMEdge) and select_edge.select:
                select_edges.append(select_edge)

        bpy.ops.mesh.select_all(action='DESELECT')
        self.active.update_from_editmode()

        # Check if local view is enabled
        current_local = False
        if context.space_data.local_view:
            # Disable local view
            bpy.ops.view3d.localview()
            current_local = True

        new_bones = []
        head = None
        tail = None
        head_indexes = []
        tail_indexes = []
        for i, e in enumerate(select_edges):
            e.select = True
            bpy.ops.mesh.loop_multi_select(ring=False)

            # 見た目の更新
            # bmesh.update_edit_mesh(self.active.data)
            # データの更新
            self.active.update_from_editmode()

            if i == 0:
                head_indexes = [v.index for s_e in bm.edges if s_e.select == True for v in s_e.verts]
                bpy.ops.view3d.snap_cursor_to_selected()
                head = copy.copy(context.scene.cursor_location) if bpy.app.version < (2, 80) \
                    else copy.copy(context.scene.cursor.location)
            else:
                tail_indexes = [v.index for s_e in bm.edges if s_e.select == True for v in s_e.verts]
                bpy.ops.view3d.snap_cursor_to_selected()
                tail = copy.copy(context.scene.cursor_location) if bpy.app.version < (2, 80) \
                    else copy.copy(context.scene.cursor.location)

                new_bones.append({"indexes": tuple(head_indexes + tail_indexes),
                                  "head": head, "tail": tail, "roll": 0})
                head = tail
                head_indexes = tail_indexes

            bpy.ops.mesh.select_all(action='DESELECT')

        if current_local:
            bpy.ops.view3d.localview()

        if bpy.app.version < (2, 80):
            context.scene.cursor_location = current_cursor
        else:
            context.scene.cursor.location = current_cursor

        return new_bones

    def __init__(self):
        self.pref = bpy.context.user_preferences.addons[__package__].preferences if bpy.app.version < (2, 80) else \
            bpy.context.preferences.addons[__package__].preferences
        self.active = None
        self.bm = None
        self.location = (0, 0, 0)
        self.new_bones = []

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH' and (obj.mode == 'EDIT'):
            # Check if select_mode is 'EDGE'
            if context.scene.tool_settings.mesh_select_mode[1]:
                return True
        return False

    def invoke(self, context, event):
        self.active = context.active_object
        self.active.update_from_editmode()

        self.bm = bmesh.new()
        self.bm = bmesh.from_edit_mesh(self.active.data)
        if bpy.app.version[0] >= 2 and bpy.app.version[1] >= 73:
            self.bm.verts.ensure_lookup_table()
            self.bm.edges.ensure_lookup_table()
            self.bm.faces.ensure_lookup_table()

    def execute(self, context):
        obj = context.object

        if obj.type != 'MESH':
            raise TypeError("Active object is not a Mesh.")

        if obj:
            pat_tool_settings = context.scene.PAT_ToolSettings  # type: PAT_ToolSettings

            current_cursor = copy.copy(bpy.context.scene.cursor_location) if bpy.app.version < (2, 80) \
                else copy.copy(bpy.context.scene.cursor.location)

            bone_name_prefix = self.pref.bone_name + self.pref.bone_name_junction
            bone_name_suffix = self.pref.bone_name_suffix

            if self.pref.bone_name_prefix != "":
                bone_name_prefix = self.pref.bone_name_prefix + self.pref.bone_name_junction + bone_name_prefix

            if self.pref.bone_name_suffix != "":
                bone_name_suffix = self.pref.bone_name_junction + bone_name_suffix

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.object.add(type='ARMATURE', enter_editmode=True, location=self.location)
            armature_object = context.active_object

            parentBone = None
            normal = mathutils.Vector((0, 0, 0))
            length = len(self.new_bones)
            for i in range(length):
                bone_name = bone_name_prefix + str(self.pref.start_number + i).rjust(self.pref.zero_padding, '0')\
                            + bone_name_suffix
                bone = bpy.context.object.data.edit_bones.new(bone_name)  # type: bpy.types.EditBone
                bone.head = self.new_bones[i]['head']
                bone.tail = self.new_bones[i]['tail']

                if self.use_auto_bone_roll:
                    bone.align_roll(self.new_bones[i]['normal'])
                    bone.roll = math.radians(round(math.degrees(bone.roll), 0))
                else:
                    bone.roll = self.new_bones[i]['roll']

                if self.use_offset:
                    normal = normal + self.new_bones[i]['normal']

                if self.use_auto_bone_weight:
                    vertex_groups = self.active.vertex_groups.new(name=bone_name)
                    vertex_groups.add(self.new_bones[i]['indexes'], 1.0, 'ADD')

                if self.pref.is_parent:
                    if parentBone:
                        bone.parent = parentBone
                        bone.use_connect = self.pref.use_connect
                    parentBone = bone

            if self.use_offset:
                bpy.ops.armature.select_all(action='SELECT')
                normal = (normal / len(self.new_bones)) * pat_tool_settings.edge_offset
                bpy.ops.transform.translate(value=normal)

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
            bpy.ops.view3d.snap_cursor_to_center()
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

            if self.use_auto_bone_weight:
                if hasattr(context, "view_layer"):
                    armature_object.show_in_front = True
                    armature_object.select_set(True)
                    bpy.ops.object.mode_set(mode='POSE', toggle=False)
                    bpy.ops.pose.select_all(action='SELECT')
                    context.view_layer.objects.active = self.active
                    context.view_layer.objects.active.select_set(True)
                else:
                    armature_object.show_x_ray = True
                    armature_object.select = True
                    bpy.ops.object.mode_set(mode='POSE', toggle=False)
                    bpy.ops.pose.select_all(action='SELECT')
                    context.scene.objects.active = self.active
                    context.scene.objects.active.select = True

                bpy.ops.object.modifier_add(type='ARMATURE')
                self.active.modifiers["Armature"].object = bpy.data.objects[armature_object.name]

                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.object.mode_set(mode='WEIGHT_PAINT', toggle=False)
                bpy.ops.object.vertex_group_normalize_all(group_select_mode='BONE_SELECT', lock_active=False)
                bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            if bpy.app.version < (2, 80):
                bpy.context.scene.cursor_location = current_cursor
            else:
                bpy.context.scene.cursor.location = current_cursor


@make_annotations
class PAT_OT_SelectedEdgeOrder(PAT_OT_Base, bpy.types.Operator):
    bl_idname = "armature.pat_selected_edge_order"
    bl_label = "Create Bone:Selected Edge Order"
    bl_description = "Creates bones from selected edge order"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        print(self.bl_label, "__init__")
        super(PAT_OT_SelectedEdgeOrder, self).__init__()

    def invoke(self, context, event):
        super(PAT_OT_SelectedEdgeOrder, self).invoke(context, event)

        if len(self.active.data.edges) < 1:
            self.report({'ERROR'}, "This mesh does not have edges")
            return {'FINISHED'}

        self.location = self.active.location
        self.new_bones = self._get_select_edge_location(context, self.bm)

        # --- if none report an error and quit
        if not self.new_bones:
            self.report({'ERROR'}, "Select at least one edge")
            return {'FINISHED'}

        return self.execute(context)

    def execute(self, context):
        super(PAT_OT_SelectedEdgeOrder, self).execute(context)
        return {'FINISHED'}


@make_annotations
class PAT_OT_MidpointOfSelectedEdgeLoopOder(PAT_OT_Base, bpy.types.Operator):
    bl_idname = "armature.pat_midpoint_of_selected_edge_loop_order"
    bl_label = "Create Bone:Midpoint of selected Edge Loop Oder"
    bl_description = "Creates bones at the midpoint of selected edge loop order"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        print(self.bl_label, "__init__")
        super(PAT_OT_MidpointOfSelectedEdgeLoopOder, self).__init__()

    def invoke(self, context, event):
        super(PAT_OT_MidpointOfSelectedEdgeLoopOder, self).invoke(context, event)

        if len(self.active.data.edges) < 2:
            self.report({'ERROR'}, "This mesh does not have multiple edges")
            return {'FINISHED'}

        self.new_bones = self._get_select_edge_loops_location(context, self.bm)

        # --- if none report an error and quit
        if not self.new_bones:
            self.report({'ERROR'}, "Select at least two edge loops")
            return {'FINISHED'}

        return self.execute(context)

    def execute(self, context):
        super(PAT_OT_MidpointOfSelectedEdgeLoopOder, self).execute(context)
        return {'FINISHED'}


@make_annotations
class VIEW3D_PT_edit_petit_armature_tools(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS' if bpy.app.version < (2, 80) else 'UI'
    bl_category = 'Tools' if bpy.app.version < (2, 80) else 'Edit'
    bl_context = 'mesh_edit'
    bl_label = 'Petit Armature Tools'

    # bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        pref = bpy.context.user_preferences.addons[__package__].preferences if bpy.app.version < (2, 80) else \
            bpy.context.preferences.addons[__package__].preferences  # type: PAT_AddonPreferences
        pat_tool_settings = context.scene.PAT_ToolSettings  # type: PAT_ToolSettings

        layout = self.layout
        layout.label(text="Create Bone:")
        col = layout.column(align=True)

        split = col.split(percentage=0.15, align=True) if bpy.app.version < (2, 80) else col.split(factor=0.15,
                                                                                                   align=True)

        if pat_tool_settings.display_edge_oder:
            split.prop(pat_tool_settings, "display_edge_oder", text="", icon='DOWNARROW_HLT')
        else:
            split.prop(pat_tool_settings, "display_edge_oder", text="", icon='RIGHTARROW')

        split.operator_context = 'INVOKE_DEFAULT'
        op = split.operator(PAT_OT_SelectedEdgeOrder.bl_idname,
                            text="Selected Edge Order")  # type: PAT_OT_SelectedEdgeOrder
        op.use_auto_bone_roll = pat_tool_settings.use_auto_bone_roll
        op.use_auto_bone_weight = pat_tool_settings.use_auto_bone_weight
        op.use_offset = True

        # SelectedEdgeOrder - settings
        if pat_tool_settings.display_edge_oder:
            box = col.column(align=True).box().column()
            box.prop(pref, "bone_name")
            box.prop(pref, "bone_name_junction")
            box.prop(pref, "bone_name_prefix")
            box.prop(pref, "bone_name_suffix")
            box.prop(pref, "start_number")
            box.prop(pref, "zero_padding")
            box.prop(pat_tool_settings, "edge_offset")
            box.prop(pat_tool_settings, "use_auto_bone_roll")
            box.prop(pat_tool_settings, "use_auto_bone_weight")
            box.prop(pref, "is_parent")
            # box.prop(pref, "is_reverse")
            box.prop(pref, "use_connect")

        split = col.split(percentage=0.15, align=True) if bpy.app.version < (2, 80) else col.split(factor=0.15,
                                                                                                   align=True)
        if pat_tool_settings.display_edge_loop_order:
            split.prop(pat_tool_settings, "display_edge_loop_order", text="", icon='DOWNARROW_HLT')
        else:
            split.prop(pat_tool_settings, "display_edge_loop_order", text="", icon='RIGHTARROW')

        split.operator_context = 'INVOKE_DEFAULT'
        op = split.operator(PAT_OT_MidpointOfSelectedEdgeLoopOder.bl_idname,
                            text="Midpoint of Selected Edge Loop Oder")  # type: PAT_OT_MidpointOfSelectedEdgeLoopOder
        op.use_auto_bone_roll = False
        op.use_auto_bone_weight = pat_tool_settings.use_auto_bone_weight
        op.use_offset = False

        # MidpointOfSelectedEdgeLoopOder - settings
        if pat_tool_settings.display_edge_loop_order:
            box = col.column(align=True).box().column()
            box.prop(pref, "bone_name")
            box.prop(pref, "bone_name_junction")
            box.prop(pref, "bone_name_prefix")
            box.prop(pref, "bone_name_suffix")
            box.prop(pref, "start_number")
            box.prop(pref, "zero_padding")
            box.prop(pat_tool_settings, "use_auto_bone_weight")
            box.prop(pref, "is_parent")
            # box.prop(preferences, "is_reverse")
            box.prop(pref, "use_connect")