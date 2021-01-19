# <pep8-80 compliant>

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

__author__ = "Nutti <nutti.metro@gmail.com>"
__status__ = "production"
__version__ = "6.3"
__date__ = "10 Aug 2020"

import os
import bpy

from .utils.bl_anotations import make_annotations
from .utils.bl_class_registry import BlClassRegistry
from .utils.addon_updater import (
    AddonUpdaterManager,
    AddonUpdaterConfig,
    get_separator,
)


class GitSettings:
    owner = "samia-done"
    repository = "Petit-Armature-Tools"
    branches = ["main"]
    default_target_addon_path = "petit_armature_tools"
    target_addon_path = {
        "main": "src{}petit_armature_tools".format(get_separator()),
    }
    update_text = 'Check add-on update'


@BlClassRegistry()
@make_annotations
class PAT_OT_CheckAddonUpdate(bpy.types.Operator):
    bl_idname = "armature.pat_check_addon_update"
    bl_label = "Check Update"
    bl_description = "Check add-on Update"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, _):
        updater = AddonUpdaterManager.get_instance()
        updater.check_update_candidate()

        return {'FINISHED'}


@BlClassRegistry()
@make_annotations
class PAT_OT_UpdateAddon(bpy.types.Operator):
    bl_idname = "armature.pat_update_addon"
    bl_label = "Update"
    bl_description = "Update add-on"
    bl_options = {'REGISTER', 'UNDO'}

    branch_name = bpy.props.StringProperty(
        name="Branch Name",
        description="Branch name to update",
        default="",
    )

    def execute(self, _):
        updater = AddonUpdaterManager.get_instance()
        updater.update(self.branch_name)

        return {'FINISHED'}


def draw_updater_ui(prefs_obj):
    updater = AddonUpdaterManager.get_instance()

    layout = prefs_obj.layout
    layout.label(text="Update:")

    if not updater.candidate_checked():
        col = layout.column()
        col.scale_y = 2
        row = col.row()
        row.operator(PAT_OT_CheckAddonUpdate.bl_idname,
                     text=GitSettings.update_text,
                     icon='FILE_REFRESH')
    else:
        row = layout.row(align=True)
        row.scale_y = 2
        col = row.column()
        col.operator(PAT_OT_CheckAddonUpdate.bl_idname,
                     text=GitSettings.update_text,
                     icon='FILE_REFRESH')
        col = row.column()
        if updater.latest_version() != "":
            col.enabled = True
            ops = col.operator(
                PAT_OT_UpdateAddon.bl_idname,
                text="Update to the latest release version".format(updater.latest_version()),
                icon='TRIA_DOWN_BAR')
            ops.branch_name = updater.latest_version()
        else:
            col.enabled = False
            col.operator(PAT_OT_UpdateAddon.bl_idname,
                         text="No updates are available.")

        layout.separator()
        layout.label(text="Manual Update:")
        row = layout.row(align=True)
        row.prop(prefs_obj, "updater_branch_to_update", text="Version")
        ops = row.operator(
            PAT_OT_UpdateAddon.bl_idname, text="Update Now",
            icon='TRIA_DOWN_BAR')
        ops.branch_name = prefs_obj.updater_branch_to_update

        layout.separator()
        if updater.has_error():
            box = layout.box()
            box.label(text=updater.error(), icon='CANCEL')
        elif updater.has_info():
            box = layout.box()
            box.label(text=updater.info(), icon='ERROR')


def register_updater(bl_info):
    config = AddonUpdaterConfig()
    config.owner = GitSettings.owner
    config.repository = GitSettings.repository
    config.current_addon_path = os.path.dirname(os.path.realpath(__file__))
    config.branches = GitSettings.branches
    config.addon_directory = \
        config.current_addon_path[
            :config.current_addon_path.rfind(get_separator())]
    config.min_release_version = bl_info["version"]
    config.default_target_addon_path = GitSettings.default_target_addon_path
    config.target_addon_path = GitSettings.target_addon_path
    updater = AddonUpdaterManager.get_instance()
    updater.init(bl_info, config)
