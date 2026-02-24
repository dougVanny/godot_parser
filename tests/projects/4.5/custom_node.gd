@tool

extends Node
class_name CustomNode

@export var godot_version : String;
@export var internalResource : CustomResource;
@export var externalResource : CustomResource;
@export_node_path var remoteNode;

func _ready():
	var file = FileAccess.open("res://resource.tres", FileAccess.READ)
	print(file.get_as_text())
