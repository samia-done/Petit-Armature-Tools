# Copyright (c) 2020 Samia
import os
import codecs
import csv

if "bpy" in locals():
    import importlib
    importlib.reload(utils)
    importlib.reload(pat_operator)
    importlib.reload(pat_preferences)
    importlib.reload(updater)
else:
    import bpy
    from . import utils
    from . import pat_operator
    from . import pat_preferences
    from . import updater

import bpy

bl_info = {
    "name": "Petit Armature Tools",
    "author": "Samia",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Edit Tab",
    "description": "Petit Armature Tools",
    "warning": "",
    "support": "COMMUNITY",
    "wiki_url": "https://github.com/samia-done/Petit-Armature-Tools",
    "tracker_url": "https://github.com/samia-done/Petit-Armature-Tools/issues",
    "category": "Armature"
}

classes = (
    pat_preferences.PAT_AddonPreferences,
    updater.PAT_OT_CheckAddonUpdate,
    updater.PAT_OT_UpdateAddon,
    pat_operator.PAT_ToolSettings,
    pat_operator.PAT_OT_SelectedEdgeOrder,
    pat_operator.PAT_OT_MidpointOfSelectedEdgeLoopOder,
    pat_operator.VIEW3D_PT_edit_petit_armature_tools
)


def get_translation_dict():
    translation_dict = {}
    path = os.path.join(os.path.dirname(__file__), "translation_dictionary.csv")
    with codecs.open(path, 'r', 'utf-8') as f:
        reader = csv.reader(f)
        translation_dict['ja_JP'] = {}
        for row in reader:
            for context in bpy.app.translations.contexts:
                translation_dict['ja_JP'][(context, row[1])] = row[0]
    return translation_dict


def register():
    updater.register_updater(bl_info)

    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.PAT_ToolSettings = bpy.props.PointerProperty(type=pat_operator.PAT_ToolSettings)
    pat_preferences.update_panel(None, bpy.context)

    # bpy.app.translations.register(__name__, get_translation_dict())


def unregister():
    # bpy.app.translations.unregister(__name__)

    del bpy.types.Scene.PAT_ToolSettings
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
