from attr import NOTHING
import bpy
from bpy.types import Scene

# For more information about Blender Properties, visit:
# <https://blender.org/api/blender_python_api_2_78a_release/bpy.types.Property.html>
from bpy.props import BoolProperty
# from bpy.props import CollectionProperty
# from bpy.props import EnumProperty
# from bpy.props import FloatProperty
# from bpy.props import IntProperty
# from bpy.props import PointerProperty
# from bpy.props import StringProperty
# from bpy.props import PropertyGroup

PROPS1 = [
    ('fur_puff', bpy.props.FloatProperty(name='Puff', default=0.1)),
    ('fur_length', bpy.props.FloatProperty(name='Length', default=1.2, min=0.1)),
    ('fur_distance', bpy.props.FloatProperty(name='Distance', default=0, min=0, max=1)),
    ('fur_trapecia', bpy.props.FloatProperty(name='Trapecia', default=0.3, min=-1)),
    ('fur_length_random', bpy.props.FloatProperty(name='Randomize Length', default=0.3, min=0, max=1)),
    ('fur_distance_random', bpy.props.FloatProperty(name='Randomize Distance', default=0.3, min=0, max=1)),
    ('fur_puff_random', bpy.props.FloatProperty(name='Randomize Puff', default=0.3, min=0, max=1)),
    ('fur_trapecia_random', bpy.props.FloatProperty(name='Randomize Trapecia', default=0.3, min=0, max=1)),
    ('fur_copy_skin', bpy.props.BoolProperty(name='Copy Skin', default=True)),
    ('fur_force_ref', bpy.props.PointerProperty(name='Force object', type=bpy.types.Object)),
]

PROPS2 = [
    ('fur_vert_color_threshold', bpy.props.FloatProperty(name='Vert color UV threshold', default=0.2, min=0, max=1)),
]

#
# Add additional functions or classes here
#

# This is where you assign any variables you need in your script. Note that they
# won't always be assigned to the Scene object but it's a good place to start.
def register():
    for (prop_name, prop_value) in PROPS1:
        setattr(bpy.types.Scene, prop_name, prop_value)
    for (prop_name, prop_value) in PROPS2:
        setattr(bpy.types.Scene, prop_name, prop_value)
        
def unregister():
    for (prop_name, _) in PROPS1:
        delattr(bpy.types.Scene, prop_name)
    for (prop_name, _) in PROPS2:
        delattr(bpy.types.Scene, prop_name)