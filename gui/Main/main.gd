extends Control

func _ready():
	# The relayer will call any functions matching _ready_(.+), _process_(.+), or _on_(.+)_changed
	add_child(preload("res://relayer.tscn").instantiate())
	$TabContainer.current_tab = 2

#---------------------------------------------------------------------------
#
#---------------------------------------------------------------------------

func _on_start_pressed():
	ConfigData.save_to_disk()
	OS.shell_open(ConfigData.START_PATH)

@onready var cc_list : ItemList = $"TabContainer/Crisis/Left/ItemList"
func _ready_cc_list():
	cc_list.clear()
	cc_list.add_item("none")
	for c in ConfigData.crisis.keys():
		cc_list.add_item(c)
	var idx = ([null] + ConfigData.crisis.keys()).find(ConfigData.config["crisisConfig"]["selectedCrisis"])
	cc_list.select(idx)
	_on_item_list_item_selected(idx)
	ConfigData.dirty = false

@onready var no_cc = $"TabContainer/Crisis/NoCC"
@onready var cc_body = $"TabContainer/Crisis/Right"
@onready var cc_season : OptionButton = $"TabContainer/Crisis/Right/Info/VBoxContainer/Season/OptionButton"
@onready var cc_name : LineEdit = $"TabContainer/Crisis/Right/Info/VBoxContainer/StageName/LineEdit"
@onready var cc_code : LineEdit = $"TabContainer/Crisis/Right/Info/VBoxContainer/StageCode/LineEdit"
@onready var cc_level : LineEdit = $"TabContainer/Crisis/Right/Info/VBoxContainer/StageId/LineEdit"
@onready var cc_map : OptionButton = $"TabContainer/Crisis/Right/Info/VBoxContainer/MapId/OptionButton"
@onready var cc_loading : OptionButton = $"TabContainer/Crisis/Right/Info/VBoxContainer/LoadingId/OptionButton"
@onready var cc_description : TextEdit = $"TabContainer/Crisis/Right/Info/VBoxContainer/Description/TextEdit"

func _on_item_list_item_selected(idx):
	ConfigData.config["crisisConfig"]["selectedCrisis"] = null if idx == 0 else cc_list.get_item_text(idx)
	
	if idx == 0:
		no_cc.visible = true
		cc_body.visible = false
		return
	no_cc.visible = false
	cc_body.visible = true
	var cc : Dictionary = ConfigData.crisis[ConfigData.crisis.keys()[idx-1]]
	
	cc_season.select(cc["data"]["seasonInfo"][0]["seasonId"].substr(12,2).to_int())
	cc_name.text = cc["data"]["seasonInfo"][0]["stages"].values()[0]["name"]
	cc_code.text = cc["data"]["seasonInfo"][0]["stages"].values()[0]["code"]
	cc_description.text = cc["data"]["seasonInfo"][0]["stages"].values()[0]["description"]
	cc_level.text = cc["data"]["seasonInfo"][0]["stages"].values()[0]["mapId"]

func _ready_crisis_info():
	cc_season.clear()
	for i in range(11):
		cc_season.add_item("CC#"+str(i))
	GameData.connect("stage_table_loaded", _apply_loaded_stage_info)

func _apply_loaded_stage_info():
	# TODO
	return
	for s in GameData.stage_table["stages"].values():
		cc_level.add_item(s["code"])

@onready var save_button : Button = $TopRight/Save
@onready var autosave : CheckBox = $TopRight/Save/Autosave

func _process_save_button():
	save_button.toggle_mode = autosave.button_pressed
	save_button.button_pressed = autosave.button_pressed
	save_button.modulate = Color.LIGHT_CORAL if ConfigData.dirty else Color.WHITE

func _on_autosave_pressed():
	ConfigData.autosave = autosave.button_pressed

func _on_save_pressed():
	ConfigData.save_to_disk()

func _on_cc_season_item_selected(index):
	var cc = ConfigData.get_selected_crisis()
	cc["data"]["seasonInfo"][0]["seasonId"] = "rune_season_" + str(index) + "_1"

func _on_cc_code_text_changed(new_text):
	var cc = ConfigData.get_selected_stage()
	cc["code"] = new_text

func _on_cc_stage_name_text_changed(new_text):
	var cc = ConfigData.get_selected_stage()
	cc["name"] = new_text

func _on_cc_level_id_text_changed(new_text):
	var cc = ConfigData.get_selected_stage()
	cc["mapId"] = new_text
	var lid = GameData.stage_table["stages"][new_text]["levelId"] if GameData.stage_table["stages"].has(new_text) \
		else "Obt/Rune/level_" + new_text # for now, we assume that if a stage is not in the stage table it's a CC stage
	cc["levelId"] = lid
