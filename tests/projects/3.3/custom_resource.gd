extends Resource
class_name CustomResource

enum CustomEnum{A, B, C}

export(String, MULTILINE) var test_string : String;
export var test_vector3 : Vector3;
export(CustomEnum) var test_enum;
export(Array, Vector3) var test_array_vector3 : Array;
export(Dictionary) var test_dict : Dictionary;
export var test_array_pool : PoolVector2Array;
