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


def create_name(base_name, separator='.', prefix='', suffix='', start_number=1, count=0, zero_padding=3):
    """
    名前を作成します
    :param base_name: 名前の基本形
    :type base_name: str
    :param separator: 名前や数字、接頭辞、接尾辞を区切る文字
    :type separator: str
    :param prefix: 接頭辞
    :type prefix: str
    :param suffix: 接尾辞
    :type suffix: str
    :param start_number: 開始番号
    :type start_number: int
    :param count: カウントアップした後の数値
    :type count: int
    :param zero_padding: ゼロ埋めする際の数字の桁数
    :type zero_padding: int
    :return: 作成された名前
    :rtype: str
    """

    bone_name_prefix = base_name + separator
    bone_name_suffix = ""

    if prefix:
        bone_name_prefix = prefix + separator + bone_name_prefix

    if suffix:
        bone_name_suffix = separator + suffix

    return bone_name_prefix + str(start_number + count).rjust(zero_padding, '0') + bone_name_suffix


# def target_armature_poll(self, context):
#     """
#
#     :param self:
#     :type self:
#     :param context:
#     :type context: bpy_types.Object
#     :return:
#     :rtype:
#     """
#     print("poll:",type(self))
#     print("poll:",type(context))
#     return context.type == 'ARMATURE' and context.is_visible(bpy.context.scene) if bpy.app.version < (2, 80)\
#         else context.type == 'ARMATURE' and context.visible_get()
#
#
# def target_armature_update(self, context):
#     """
#
#     :param self:
#     :type self:
#     :param context:
#     :type context:
#     """
#     print("update:",type(self))
#     print("update:",type(context))
#     self.target_bone = ''


@make_annotations
class PAT_ToolSettings(bpy.types.PropertyGroup):
    # target_armature = bpy.props.PointerProperty(
    #     name="Target Armature",
    #     description="",
    #     type=bpy.types.Object,
    #     poll=target_armature_poll,
    #     update=target_armature_update,
    #     options={'HIDDEN'}
    # )
    # target_bone = bpy.props.StringProperty(
    #     name="Target Bone",
    #     description="",
    #     options={'HIDDEN'}
    # )
    display_edge_oder = bpy.props.BoolProperty(
        name="Selected Edge Loop Oder Settings",
        description="Display Settings of Selected Edge Oder",
        default=False,
        options={'HIDDEN'}
    )
    display_edge_loop_order = bpy.props.BoolProperty(
        name="Midpoint of Selected Edge Loop Oder Settings",
        description="Display Settings of Selected Edge Loop Oder",
        default=False,
        options={'HIDDEN'}
    )
    edge_offset = bpy.props.FloatProperty(
        name="Offset",
        description="Offset value",
        default=0.0,
        unit='LENGTH',
        options={'HIDDEN'}
    )
    use_auto_bone_roll = bpy.props.BoolProperty(
        name="Auto Bone Roll",
        description="Enable Auto bone roll",
        default=True,
        options={'HIDDEN'}
    )
    use_auto_bone_weight = bpy.props.BoolProperty(
        name="Auto Bone Weight",
        description="Enable Auto bone weights",
        default=True,
        options={'HIDDEN'}
    )
    use_offset = bpy.props.BoolProperty(
        name="Offset",
        description="Enable Bone location offset",
        default=False,
        options={'HIDDEN'}
    )
    bone_name_base = bpy.props.StringProperty(
        name="Base Name",
        description="Base of bone name",
        default="Bone",
        options={'HIDDEN'}
    )
    bone_name_junction = bpy.props.StringProperty(
        name="Separator",
        description="Bone name separator",
        default=".",
        options={'HIDDEN'}
    )
    bone_name_prefix = bpy.props.StringProperty(
        name="Prefix",
        description="Bone name prefix",
        default="",
        options={'HIDDEN'}
    )
    bone_name_suffix = bpy.props.StringProperty(
        name="Suffix",
        description="Bone name suffix",
        default="",
        options={'HIDDEN'}
    )
    start_number = bpy.props.IntProperty(
        name="Start Number",
        description="Starting number of bone name",
        default=1,
        min=0,
        options={'HIDDEN'}
    )
    zero_padding = bpy.props.IntProperty(
        name="Zero-padding",
        description="Zero-padding of digits in bone names",
        default=3,
        min=1,
        options={'HIDDEN'}
    )
    # is_reverse = bpy.props.BoolProperty(
    #     name="Reverse",
    #     description="Change the bone order to the reverse order",
    #     default=False,
    #     options={'HIDDEN'}
    # )
    is_parent = bpy.props.BoolProperty(
        name="Parent",
        description="Set the previously created bone as the parent",
        default=True,
        options={'HIDDEN'}
    )
    use_connect = bpy.props.BoolProperty(
        name="Connected",
        description="When Bone has a parent,bone's head is stuck to the parent's tail",
        default=True,
        options={'HIDDEN'}
    )


@make_annotations
class PAT_OT_Base:
    use_offset = bpy.props.BoolProperty(
        name="Offset",
        description="Enable Bone location offset",
        default=False,
        options={'HIDDEN'}
    )
    offset = bpy.props.FloatProperty(
        name="Offset",
        description="Offset value",
        default=0.0,
        unit='LENGTH',
        options={'HIDDEN'}
    )
    use_auto_bone_roll = bpy.props.BoolProperty(
        name="Auto Bone Roll",
        description="Enable Auto bone roll",
        default=True,
        options={'HIDDEN'}
    )
    use_auto_bone_weight = bpy.props.BoolProperty(
        name="Auto Bone Weight",
        description="Enable Auto bone weights",
        default=True,
        options={'HIDDEN'}
    )
    is_parent = bpy.props.BoolProperty(
        name="Parent",
        description="Set the previously created bone as the parent",
        default=True,
        options={'HIDDEN'}
    )
    use_connect = bpy.props.BoolProperty(
        name="Connected",
        description="When Bone has a parent,bone's head is stuck to the parent's tail",
        default=True,
        options={'HIDDEN'}
    )

    def _get_distance(self, vector0, vector1):
        distance = math.sqrt((vector0[0] - vector1[0]) ** 2 +
                             (vector0[1] - vector1[1]) ** 2 +
                             (vector0[2] - vector1[2]) ** 2)
        return distance

    def __init__(self):
        self.pat_tool_settings = None
        self.mesh_object = None
        self.matrix_world = None
        self.new_bones = []
        self.new_bone_names = []

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
            # Check if select_mode is 'EDGE'
            if context.scene.tool_settings.mesh_select_mode[1]:
                return True
        return False

    def invoke(self, context, event):
        self.pat_tool_settings = context.scene.PAT_ToolSettings  # type: PAT_ToolSettings
        self.mesh_object = context.active_object
        self.mesh_object.update_from_editmode()
        self.matrix_world = self.mesh_object.matrix_world

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        bpy.ops.object.add(type='ARMATURE', enter_editmode=True)

        armature_object = context.active_object  # type: bpy.types.Object
        armature_object.name = 'PAT_Armature'
        armature_object.matrix_world = self.matrix_world
        armature_object.data.name = 'PAT_Armature'

        create_bones = []
        create_bones_append = create_bones.append
        parentBone = None
        normals = mathutils.Vector((0, 0, 0))
        for i, (bone_name, new_bone) in enumerate(zip(self.new_bone_names, self.new_bones)):
            bone = armature_object.data.edit_bones.new(bone_name)  # type: bpy.types.EditBone
            bone.head = new_bone['head']
            bone.tail = new_bone['tail']

            if self.use_auto_bone_roll:
                bone.align_roll(new_bone['normal'])
                bone.roll = math.radians(round(math.degrees(bone.roll), 0))
            else:
                bone.roll = 0.0

            create_bones_append(bone)

            if self.use_auto_bone_weight:
                try:
                    vertex_groups = self.mesh_object.vertex_groups[bone_name]
                    self.report({'ERROR'}, "The vertex group " + bone_name + " has already been created")
                except KeyError:
                    vertex_groups = self.mesh_object.vertex_groups.new(name=bone_name)

                vertex_groups.add(new_bone['indexes'], 1.0, 'ADD')

            if self.use_offset:
                normals += new_bone['normal']

            if self.is_parent:
                if parentBone:
                    bone.parent = parentBone
                    bone.use_connect = self.use_connect
                parentBone = bone

        for bone in create_bones:
            bone.select = True

        if self.use_offset:
            normal = (normals / len(self.new_bones)).normalized()
            normal = normal * self.offset
            for bone in create_bones:
                if bone.use_connect:
                    bone.tail += normal
                else:
                    bone.translate(normal)

        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        if self.use_auto_bone_weight:
            if hasattr(context, "view_layer"):
                armature_object.show_in_front = True
                armature_object.select_set(True)
                bpy.ops.object.mode_set(mode='POSE', toggle=False)
                context.view_layer.objects.active = self.mesh_object
                context.view_layer.objects.active.select_set(True)
            else:
                armature_object.show_x_ray = True
                armature_object.select = True
                bpy.ops.object.mode_set(mode='POSE', toggle=False)
                context.scene.objects.active = self.mesh_object
                context.scene.objects.active.select = True

            try:
                modifiers = self.mesh_object.modifiers['PAT_Armature']
            except KeyError:
                modifiers = self.mesh_object.modifiers.new(name='PAT_Armature', type='ARMATURE')
            modifiers.object = armature_object

            bpy.ops.object.mode_set(mode='WEIGHT_PAINT', toggle=False)
            bpy.ops.object.vertex_group_normalize_all(group_select_mode='BONE_SELECT', lock_active=False)
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

        # if self.pat_tool_settings.target_armature:
        #     # print(pat_tool_settings.target_armature)
        #     if hasattr(context, "view_layer"):
        #         context.view_layer.objects.active = self.pat_tool_settings.target_armature
        #         context.view_layer.objects.active.select_set(True)
        #     else:
        #         context.scene.objects.active = self.pat_tool_settings.target_armature
        #         context.scene.objects.active.select = True
        #     bpy.ops.object.join()
        #     self.active.modifiers["Armature"].object = self.pat_tool_settings.target_armature
        #     bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


@make_annotations
class PAT_OT_SelectedEdgeOrder(PAT_OT_Base, bpy.types.Operator):
    bl_idname = "armature.pat_selected_edge_order"
    bl_label = "Create Bone:Selected Edge Order"
    bl_description = "Creates bones from selected edge order"
    bl_options = {'REGISTER', 'UNDO'}

    def _get_new_bones(self, context):
        return self._get_select_edge_location(context)

    def _get_new_bone_names(self):
        length = len(self.new_bones)
        if length > 0:
            return [create_name(self.pat_tool_settings.bone_name_base, self.pat_tool_settings.bone_name_junction,
                                self.pat_tool_settings.bone_name_prefix, self.pat_tool_settings.bone_name_suffix,
                                self.pat_tool_settings.start_number, i, self.pat_tool_settings.zero_padding)
                    for i in range(length)]
        else:
            return ['']

    def _get_select_edge_location(self, context):
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(self.mesh_object.data)
        if bpy.app.version[0] >= 2 and bpy.app.version[1] >= 73:
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

        selected_edges = []
        new_bones = []
        head = None
        tail = None

        for i, e in enumerate(bm.select_history):  # type: (int, bmesh.types.BMEdge)
            if isinstance(e, bmesh.types.BMEdge) and e.select:
                selected_edges.append(e)
                v0 = e.verts[0]
                v1 = e.verts[1]
                if head:
                    if self._get_distance(head.co, v0.co) > self._get_distance(head.co, v1.co):
                        v0, v1 = v1, v0
                    if not self.use_connect:
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
                                  "tail": copy.copy(tail.co), "normal": copy.copy(normal.normalized())})
                head = tail

        for edge in selected_edges:
            edge.select = True
        self.mesh_object.update_from_editmode()

        return new_bones

    def __init__(self):
        super(PAT_OT_SelectedEdgeOrder, self).__init__()

    def invoke(self, context, event):
        super(PAT_OT_SelectedEdgeOrder, self).invoke(context, event)

        # 辺が一つも無い場合は終了
        if len(self.mesh_object.data.edges) < 1:
            self.report({'ERROR'}, "This mesh does not have edges")
            return {'FINISHED'}

        self.new_bones = self._get_new_bones(context)

        # 作成するボーンデータが一つも無い場合は終了
        if not self.new_bones:
            self.report({'ERROR'}, "Select at least one edge")
            return {'FINISHED'}

        self.new_bone_names = self._get_new_bone_names()

        # ボーンネームが空の場合は終了
        for bone_name in self.new_bone_names:
            if bone_name == '':
                self.report({'ERROR'}, "No blank names are allowed")
                return {'FINISHED'}

        # オートウェイトが有効で、作成するボーンと同名の頂点グループがある場合は終了
        if self.use_auto_bone_weight:
            for vg in self.mesh_object.vertex_groups:  # type: bpy.types.VertexGroup
                if vg.name in self.new_bone_names:
                    self.report({'ERROR'}, "The vertex group " + vg.name + " has already been created")
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

    def _get_new_bones(self, context):
        return self._get_select_edge_loops_location(context)

    def _get_new_bone_names(self):
        length = len(self.new_bones)
        if length > 0:
            return [create_name(self.pat_tool_settings.bone_name_base, self.pat_tool_settings.bone_name_junction,
                                self.pat_tool_settings.bone_name_prefix, self.pat_tool_settings.bone_name_suffix,
                                self.pat_tool_settings.start_number, i, self.pat_tool_settings.zero_padding)
                    for i in range(length)]
        else:
            return ['']

    def _get_select_edge_loops_location(self, context):
        bm = bmesh.new()
        bm = bmesh.from_edit_mesh(self.mesh_object.data)
        if bpy.app.version[0] >= 2 and bpy.app.version[1] >= 73:
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

        current_cursor = copy.copy(context.scene.cursor_location) if bpy.app.version < (2, 80) \
            else copy.copy(context.scene.cursor.location)

        select_history = []
        select_history_append = select_history.append
        for history_edge in bm.select_history:
            if isinstance(history_edge, bmesh.types.BMEdge):
                select_history_append(history_edge)

        # 選択した辺が2つ以上無い場合は終了
        if len(select_history) < 2:
            return

        bpy.ops.mesh.select_all(action='DESELECT')
        self.mesh_object.update_from_editmode()

        # ローカルビューが有効になっている場合、一時的に解除
        current_local = False
        if context.space_data.local_view:
            # Disable local view
            bpy.ops.view3d.localview()
            current_local = True

        selected_edges = []
        new_bones = []
        head = None
        tail = None
        head_indexes = []
        tail_indexes = []

        mwi = self.matrix_world.inverted()
        for i, e in enumerate(select_history):
            e.select = True
            bpy.ops.mesh.loop_multi_select(ring=False)
            self.mesh_object.update_from_editmode()

            # すでに選択した辺と同じ辺のときは終了
            if e in selected_edges:
                return

            select_loop_edges = [s_e for s_e in bm.edges if s_e.select == True]
            selected_edges += select_loop_edges

            if i > 0:
                tail_indexes = [v.index for s_e in select_loop_edges for v in s_e.verts]

                bpy.ops.view3d.snap_cursor_to_selected()
                local_cursor_location = mwi * context.scene.cursor_location if bpy.app.version < (2, 80)\
                    else mwi @ context.scene.cursor.location

                tail = copy.copy(local_cursor_location)

                new_bones.append({"indexes": tuple(head_indexes + tail_indexes), "head": head, "tail": tail})
                head = tail
                head_indexes = tail_indexes
            else:
                head_indexes = [v.index for s_e in select_loop_edges for v in s_e.verts]

                bpy.ops.view3d.snap_cursor_to_selected()
                local_cursor_location = mwi * context.scene.cursor_location if bpy.app.version < (2, 80)\
                    else mwi @ context.scene.cursor.location

                head = copy.copy(local_cursor_location)

            bpy.ops.mesh.select_all(action='DESELECT')

        if current_local:
            bpy.ops.view3d.localview()

        if bpy.app.version < (2, 80):
            context.scene.cursor_location = current_cursor
        else:
            context.scene.cursor.location = current_cursor

        for edge in selected_edges:
            edge.select = True
        self.mesh_object.update_from_editmode()

        return new_bones

    def __init__(self):
        super(PAT_OT_MidpointOfSelectedEdgeLoopOder, self).__init__()

    def invoke(self, context, event):
        super(PAT_OT_MidpointOfSelectedEdgeLoopOder, self).invoke(context, event)

        # 辺が2つ以上無い場合は終了
        if len(self.mesh_object.data.edges) < 2:
            self.report({'ERROR'}, "This mesh does not have multiple edges")
            return {'FINISHED'}

        self.new_bones = self._get_new_bones(context)

        # 作成するボーンデータが一つも無い場合は終了
        if not self.new_bones:
            self.report({'ERROR'}, "Select at least two edge loops")
            return {'FINISHED'}

        self.new_bone_names = self._get_new_bone_names()

        # ボーンネームが空の場合は終了
        for bone_name in self.new_bone_names:
            if bone_name == '':
                self.report({'ERROR'}, "No blank names are allowed")
                return {'FINISHED'}

        # オートウェイトが有効で、作成するボーンと同名の頂点グループがある場合は終了
        if self.use_auto_bone_weight:
            for vg in self.mesh_object.vertex_groups:  # type: bpy.types.VertexGroup
                if vg.name in self.new_bone_names:
                    self.report({'ERROR'}, "The vertex group " + vg.name + " has already been created")
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
        op.use_offset = pat_tool_settings.use_offset
        op.offset = pat_tool_settings.edge_offset
        op.is_parent = pat_tool_settings.is_parent
        op.use_connect = pat_tool_settings.use_connect

        bone_name = create_name(pat_tool_settings.bone_name_base, pat_tool_settings.bone_name_junction,
                                pat_tool_settings.bone_name_prefix, pat_tool_settings.bone_name_suffix,
                                pat_tool_settings.start_number, 0, pat_tool_settings.zero_padding)
        # SelectedEdgeOrder - settings
        if pat_tool_settings.display_edge_oder:
            box = col.column(align=True).box().column()
            row = box.row(align=True)
            row.label(text="Example of name display:")
            row = row.row(align=True)
            row.label(text=bone_name)
            box.separator()
            # box.prop(pat_tool_settings, "target_armature", text="Armature")
            # if pat_tool_settings.target_armature:
            #     box.prop_search(pat_tool_settings, "target_bone", pat_tool_settings.target_armature.data, "bones", text="Bone")
            box.prop(pat_tool_settings, "bone_name_base")
            box.prop(pat_tool_settings, "bone_name_junction")
            box.prop(pat_tool_settings, "bone_name_prefix")
            box.prop(pat_tool_settings, "bone_name_suffix")
            box.prop(pat_tool_settings, "start_number")
            box.prop(pat_tool_settings, "zero_padding")
            box.prop(pat_tool_settings, "use_auto_bone_roll")
            box.prop(pat_tool_settings, "use_auto_bone_weight")
            box.prop(pat_tool_settings, "is_parent")
            # box.prop(pat_tool_settings, "is_reverse")
            box_col = box.column(align=True)
            box_col.prop(pat_tool_settings, "use_connect")
            box_col.active = pat_tool_settings.is_parent
            row = box.row(align=True)
            row.prop(pat_tool_settings, "use_offset")
            row = row.row(align=True)
            row.prop(pat_tool_settings, "edge_offset", text="")
            row.active = pat_tool_settings.use_offset

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
        op.offset = 0.0
        op.is_parent = pat_tool_settings.is_parent
        op.use_connect = pat_tool_settings.use_connect

        # MidpointOfSelectedEdgeLoopOder - settings
        if pat_tool_settings.display_edge_loop_order:
            box = col.column(align=True).box().column()
            row = box.row(align=True)
            row.label(text="Example of name display:")
            row = row.row(align=True)
            row.label(text=bone_name)
            box.separator()
            # box.prop(pat_tool_settings, "target_armature", text="Armature")
            # if pat_tool_settings.target_armature:
            #     box.prop_search(pat_tool_settings, "target_bone", pat_tool_settings.target_armature.data, "bones", text="Bone")
            box.prop(pat_tool_settings, "bone_name_base")
            box.prop(pat_tool_settings, "bone_name_junction")
            box.prop(pat_tool_settings, "bone_name_prefix")
            box.prop(pat_tool_settings, "bone_name_suffix")
            box.prop(pat_tool_settings, "start_number")
            box.prop(pat_tool_settings, "zero_padding")
            box.prop(pat_tool_settings, "use_auto_bone_weight")
            box.prop(pat_tool_settings, "is_parent")
            # box.prop(pat_tool_settings, "is_reverse")
            box_col = box.column(align=True)
            box_col.prop(pat_tool_settings, "use_connect")
            box_col.active = pat_tool_settings.is_parent
