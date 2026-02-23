extends Resource
class_name CustomResource

enum CustomEnum{A, B, C}

@export var test_string_name : StringName;
@export_multiline var test_string : String;
@export var test_vector3 : Vector3;
@export var test_enum : CustomEnum;
@export var test_array_vector3 : Array[Vector3];
@export var test_dict : Dictionary;
# @export var test_dict_int_str : Dictionary[int,String];
@export var test_array_pool : PackedVector2Array;
@export var test_array_pool2 : PackedVector4Array;
@export var child_resource : CustomResource;
