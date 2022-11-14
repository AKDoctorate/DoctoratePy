extends Node

func _ready():
	# The relayer will call any functions matching _ready_(.+), _process_(.+), or _on_(.+)_changed
	add_child(preload("res://relayer.tscn").instantiate())

#---------------------------------------------------------------------------
#	DoctoratePy Config
#---------------------------------------------------------------------------

# Change your dev path in the exported property
@export var dev_path = "C:\\Users\\Logos\\DoctoratePy"

var BASE_PATH = OS.get_executable_path().get_base_dir() if not OS.is_debug_build() else dev_path
var CRISIS_PATH = BASE_PATH + "\\data\\crisis\\"
var START_PATH = BASE_PATH + "\\start.bat"
var CONFIG_PATH = BASE_PATH + "\\config\\config.json"

var crisis = {}
var config = {}

var dirty = false:
	set(value):
		dirty = value
		if dirty and autosave:
			save_to_disk()

func _on_crisis_changed():
	dirty = true

func _on_config_changed():
	dirty = true

func get_selected_crisis():
	return crisis[config["crisisConfig"]["selectedCrisis"]]

func get_selected_stage():
	return get_selected_crisis()["data"]["seasonInfo"][0]["stages"].values()[0]

func _ready_config():
	for f in DirAccess.get_files_at(CRISIS_PATH):
		if "json" in f:
			var file = FileAccess.open(CRISIS_PATH + f, FileAccess.READ)
			crisis[f.substr(0, len(f)-5)] = JSON.parse_string(file.get_as_text())
	var file = FileAccess.open(CONFIG_PATH, FileAccess.READ)
	config = JSON.parse_string(file.get_as_text())

func save_to_disk():
	for c in crisis.keys():
		var file = FileAccess.open(CRISIS_PATH + c + ".json", FileAccess.WRITE)
		file.store_string(JSON.stringify(crisis[c], "\t"))
	var file = FileAccess.open(CONFIG_PATH, FileAccess.WRITE)
	file.store_string(JSON.stringify(config, "\t"))
	dirty = false

#---------------------------------------------------------------------------
#	GUI Config
#---------------------------------------------------------------------------

var gui_config = ConfigFile.new()

var autosave = false:
	set(value):
		autosave = value
		if autosave and dirty:
			save_to_disk()

func _ready_gui_config():
	gui_config.load("user://gui_config.cfg")
	for k in ["autosave"]:
		set(k, gui_config.get_value("gui", k))

func _on_autosave_changed():
	gui_config.set_value("gui", "autosave", autosave)
	gui_config.save("user://gui_config.cfg")
