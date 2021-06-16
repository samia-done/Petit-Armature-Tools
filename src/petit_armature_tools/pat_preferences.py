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
from .utils.bl_anotations import make_annotations
from .utils.addon_updater import AddonUpdaterManager
from . import updater
from . import pat_operator


def get_update_candidate_branches(_, __):
    manager = AddonUpdaterManager.get_instance()
    if not manager.candidate_checked():
        return []

    return [(name, name, "") for name in manager.get_candidate_branch_names()]

# Define Panel classes for updating


# def update_panel(self, context):
#     panels = (
#         pat_operator.VIEW3D_PT_edit_petit_armature_tools,
#     )
#     message = "Updating Panel locations has failed"
#     try:
#         for panel in panels:
#             if "bl_rna" in panel.__dict__:
#                 bpy.utils.unregister_class(panel)
#
#         for panel in panels:
#             panel.bl_category = context.user_preferences.addons[__package__].preferences.category if bpy.app.version < (2, 80) else context.preferences.addons[__package__].preferences.category
#             bpy.utils.register_class(panel)
#
#     except Exception as e:
#         print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
#         pass


@make_annotations
class PAT_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # category = bpy.props.StringProperty(
    #     name="Tab Category",
    #     description="Choose a name for the category of the panel",
    #     default="Tools" if bpy.app.version < (2, 80) else "Edit",
    #     update=update_panel
    # )

    # for add-on updater
    updater_branch_to_update = bpy.props.EnumProperty(
        name="branch",
        description="Target branch to update add-on",
        items=get_update_candidate_branches
    )

    def __init__(self):
        super(bpy.types.AddonPreferences, self).__init__()

    def draw(self, context):
        layout = self.layout
        # row = layout.row()
        # col = row.column()
        # col.label(text="Tab Category:")
        # col.prop(self, "category", text="")
        updater.draw_updater_ui(self)
