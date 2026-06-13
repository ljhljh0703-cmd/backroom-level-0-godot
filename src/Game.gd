extends Control

const ROOM_CONFIG_PATH := "res://data/rooms.json"
const ROOM_FORK := "fork_stop"
const ROOM_STOP_BACK := "stop_back_space"
const ROOM_LEFT_PATH := "left_blood_path"
const ROOM_RIGHT_PATH := "right_panel_path"
const ROOM_RIGHT_DEAD_END := "right_dead_end"
const ROOM_TRUE_EXIT := "true_exit_room"
const ROOM_FALSE_EXIT := "false_exit_room"
const DEV_LOGGING := false
const REVIEW_HOLD_SCREEN := false
const REVIEW_ASSET_PATH := "res://assets/review/screen_fork_stop_candidate.png"
const UI_FONT := preload("res://assets/fonts/NotoSansKR-Regular.ttf")

const FLAG_DEFAULTS := {
	"stop_back_seen_once": false,
	"stop_back_reentry_armed": false,
	"light_switch_pressed": false,
	"stop_back_red_seen": false,
	"blood_trace_clicked": false,
	"panel_clue_clicked": false,
	"right_dead_end_seen": false,
	"right_door_warning_seen": false,
	"right_note_available": false,
	"right_note_read": false,
	"panel_sound_played": false,
	"creature_peek_seen": false
}

var room_config: Dictionary = {}
var room_data: Dictionary = {}
var start_room := ROOM_FORK
var room_id := ROOM_FORK
var game_state := "play"
var ending_id := ""
var flags: Dictionary = {}
var clicked_events: Dictionary = {}
var creature_stage := 0
var creature_peek_active := false
var move_count := 0
var miss_clicks := 0
var input_cooldown := 0.0
var elapsed := 0.0
var shake_time := 0.0
var shake_power := 0.0
var hover_prompt := ""
var menu_mode := ""
var debug_hotspots_visible := false
var debug_viewport_size := Vector2.ZERO

var world: Control
var background: TextureRect
var creature: TextureRect
var foreground: TextureRect
var note_shadow: ColorRect
var note_marker: ColorRect
var noise: TextureRect
var vignette: TextureRect
var threat_tint: ColorRect
var flash_rect: ColorRect
var note_flash: TextureRect
var click_feedback: ColorRect
var black_fade: ColorRect
var caption_label: Label
var prompt_label: Label
var hold_label: Label
var hover_highlight: ColorRect
var hover_badge_bg: ColorRect
var hover_badge_label: Label
var menu_layer: Control
var menu_scrim: ColorRect
var menu_box: PanelContainer
var menu_stack: VBoxContainer
var menu_title: Label
var menu_body: Label
var menu_primary_button: Button
var menu_secondary_button: Button
var note_layer: Control
var note_scrim: ColorRect
var note_box: PanelContainer
var note_label: Label
var debug_layer: Control
var hum_player: AudioStreamPlayer
var sfx_player: AudioStreamPlayer
var sting_player: AudioStreamPlayer

var creature_texture: Texture2D
var click_sound: AudioStream
var thump_sound: AudioStream
var sting_sound: AudioStream


func _ready() -> void:
	randomize()
	process_mode = Node.PROCESS_MODE_ALWAYS
	_load_room_config()
	_build_nodes()
	_load_assets()
	if REVIEW_HOLD_SCREEN:
		_show_review_hold_screen()
		return
	_show_lobby()
	set_process(true)


func _load_room_config() -> void:
	var text := FileAccess.get_file_as_string(ROOM_CONFIG_PATH)
	var parsed: Variant = JSON.parse_string(text)
	if typeof(parsed) != TYPE_DICTIONARY:
		push_error("Could not parse room config: %s" % ROOM_CONFIG_PATH)
		room_config = {}
		room_data = {}
		return
	room_config = parsed
	start_room = str(room_config.get("start_room", ROOM_FORK))
	room_data = room_config.get("rooms", {})


func _build_nodes() -> void:
	world = Control.new()
	world.name = "World"
	world.set_anchors_preset(Control.PRESET_FULL_RECT)
	world.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(world)

	background = TextureRect.new()
	background.name = "Background"
	background.set_anchors_preset(Control.PRESET_FULL_RECT)
	background.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	background.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	world.add_child(background)

	creature = TextureRect.new()
	creature.name = "Creature"
	creature.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	creature.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT
	creature.mouse_filter = Control.MOUSE_FILTER_IGNORE
	creature.visible = false
	world.add_child(creature)

	foreground = TextureRect.new()
	foreground.name = "Foreground"
	foreground.set_anchors_preset(Control.PRESET_FULL_RECT)
	foreground.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	foreground.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	foreground.mouse_filter = Control.MOUSE_FILTER_IGNORE
	foreground.visible = false
	world.add_child(foreground)

	note_shadow = ColorRect.new()
	note_shadow.name = "FloorNoteShadow"
	note_shadow.color = Color(0.0, 0.0, 0.0, 0.34)
	note_shadow.mouse_filter = Control.MOUSE_FILTER_IGNORE
	note_shadow.visible = false
	world.add_child(note_shadow)

	note_marker = ColorRect.new()
	note_marker.name = "FloorNote"
	note_marker.color = Color(0.92, 0.86, 0.62, 0.92)
	note_marker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	note_marker.visible = false
	world.add_child(note_marker)

	noise = TextureRect.new()
	noise.name = "Noise"
	noise.set_anchors_preset(Control.PRESET_FULL_RECT)
	noise.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	noise.stretch_mode = TextureRect.STRETCH_TILE
	noise.modulate = Color(1.0, 1.0, 1.0, 0.13)
	noise.mouse_filter = Control.MOUSE_FILTER_IGNORE
	world.add_child(noise)

	vignette = TextureRect.new()
	vignette.name = "Vignette"
	vignette.set_anchors_preset(Control.PRESET_FULL_RECT)
	vignette.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	vignette.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	vignette.modulate = Color(1.0, 1.0, 1.0, 0.78)
	vignette.mouse_filter = Control.MOUSE_FILTER_IGNORE
	world.add_child(vignette)

	threat_tint = ColorRect.new()
	threat_tint.name = "ThreatTint"
	threat_tint.set_anchors_preset(Control.PRESET_FULL_RECT)
	threat_tint.color = Color(0.30, 0.08, 0.03, 0.0)
	threat_tint.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(threat_tint)

	flash_rect = ColorRect.new()
	flash_rect.name = "Flash"
	flash_rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	flash_rect.color = Color(1, 0.94, 0.62, 0.0)
	flash_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(flash_rect)

	click_feedback = ColorRect.new()
	click_feedback.name = "ClickFeedback"
	click_feedback.size = Vector2(18, 18)
	click_feedback.color = Color(0.95, 0.88, 0.52, 0.0)
	click_feedback.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(click_feedback)

	hover_highlight = ColorRect.new()
	hover_highlight.name = "HoverHighlight"
	hover_highlight.color = Color(1.0, 0.86, 0.28, 0.0)
	hover_highlight.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hover_highlight.visible = false
	add_child(hover_highlight)

	hover_badge_bg = ColorRect.new()
	hover_badge_bg.name = "HoverBadgeBg"
	hover_badge_bg.size = Vector2(132, 34)
	hover_badge_bg.color = Color(0.02, 0.018, 0.012, 0.78)
	hover_badge_bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hover_badge_bg.visible = false
	add_child(hover_badge_bg)

	hover_badge_label = _make_label(16, Color(0.98, 0.90, 0.56), 2)
	hover_badge_label.name = "HoverBadge"
	hover_badge_label.size = hover_badge_bg.size
	hover_badge_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hover_badge_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	hover_badge_label.visible = false
	add_child(hover_badge_label)

	black_fade = ColorRect.new()
	black_fade.name = "BlackFade"
	black_fade.set_anchors_preset(Control.PRESET_FULL_RECT)
	black_fade.color = Color(0, 0, 0, 1)
	black_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(black_fade)

	caption_label = _make_label(24, Color(0.94, 0.88, 0.64), 2)
	caption_label.name = "Caption"
	caption_label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	caption_label.offset_left = 42
	caption_label.offset_right = -42
	caption_label.offset_top = -104
	caption_label.offset_bottom = -62
	caption_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	caption_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	add_child(caption_label)

	prompt_label = _make_label(18, Color(0.78, 0.72, 0.52), 2)
	prompt_label.name = "Prompt"
	prompt_label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	prompt_label.offset_left = 42
	prompt_label.offset_right = -42
	prompt_label.offset_top = -54
	prompt_label.offset_bottom = -24
	prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	prompt_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	add_child(prompt_label)

	hold_label = _make_label(28, Color(0.86, 0.82, 0.68), 2)
	hold_label.name = "ReviewHold"
	hold_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	hold_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hold_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	hold_label.visible = false
	add_child(hold_label)

	_build_menu_layer()
	_build_note_layer()

	note_flash = TextureRect.new()
	note_flash.name = "NoteFlash"
	note_flash.set_anchors_preset(Control.PRESET_FULL_RECT)
	note_flash.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	note_flash.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	note_flash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	note_flash.visible = false
	add_child(note_flash)

	debug_layer = Control.new()
	debug_layer.name = "DebugHotspots"
	debug_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	debug_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(debug_layer)

	hum_player = AudioStreamPlayer.new()
	hum_player.name = "Hum"
	hum_player.volume_db = -25.0
	add_child(hum_player)

	sfx_player = AudioStreamPlayer.new()
	sfx_player.name = "Sfx"
	sfx_player.volume_db = -8.0
	add_child(sfx_player)

	sting_player = AudioStreamPlayer.new()
	sting_player.name = "Sting"
	sting_player.volume_db = -3.0
	add_child(sting_player)


func _build_menu_layer() -> void:
	menu_layer = Control.new()
	menu_layer.name = "MenuLayer"
	menu_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	menu_layer.mouse_filter = Control.MOUSE_FILTER_STOP
	menu_layer.visible = false
	add_child(menu_layer)

	menu_scrim = ColorRect.new()
	menu_scrim.name = "MenuScrim"
	menu_scrim.set_anchors_preset(Control.PRESET_FULL_RECT)
	menu_scrim.color = Color(0.0, 0.0, 0.0, 0.54)
	menu_scrim.mouse_filter = Control.MOUSE_FILTER_STOP
	menu_layer.add_child(menu_scrim)

	menu_box = PanelContainer.new()
	menu_box.name = "MenuBox"
	menu_box.add_theme_stylebox_override("panel", _panel_style())
	menu_box.mouse_filter = Control.MOUSE_FILTER_STOP
	menu_layer.add_child(menu_box)

	menu_stack = VBoxContainer.new()
	menu_stack.name = "MenuStack"
	menu_stack.add_theme_constant_override("separation", 14)
	menu_stack.set_anchors_preset(Control.PRESET_FULL_RECT)
	menu_stack.offset_left = 24
	menu_stack.offset_top = 22
	menu_stack.offset_right = -24
	menu_stack.offset_bottom = -22
	menu_box.add_child(menu_stack)

	menu_title = _make_label(30, Color(0.98, 0.91, 0.58), 3)
	menu_title.name = "MenuTitle"
	menu_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	menu_title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	menu_title.custom_minimum_size = Vector2(0, 44)
	menu_stack.add_child(menu_title)

	menu_body = _make_label(19, Color(0.84, 0.78, 0.58), 2)
	menu_body.name = "MenuBody"
	menu_body.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	menu_body.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	menu_body.custom_minimum_size = Vector2(0, 58)
	menu_stack.add_child(menu_body)

	menu_primary_button = _make_menu_button("시작", true)
	menu_primary_button.pressed.connect(_on_menu_primary_pressed)
	menu_stack.add_child(menu_primary_button)

	menu_secondary_button = _make_menu_button("종료", false)
	menu_secondary_button.pressed.connect(_on_menu_secondary_pressed)
	menu_stack.add_child(menu_secondary_button)

	_layout_menu()


func _build_note_layer() -> void:
	note_layer = Control.new()
	note_layer.name = "NoteLayer"
	note_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	note_layer.mouse_filter = Control.MOUSE_FILTER_STOP
	note_layer.visible = false
	add_child(note_layer)

	note_scrim = ColorRect.new()
	note_scrim.name = "NoteScrim"
	note_scrim.set_anchors_preset(Control.PRESET_FULL_RECT)
	note_scrim.color = Color(0.0, 0.0, 0.0, 0.46)
	note_scrim.mouse_filter = Control.MOUSE_FILTER_STOP
	note_layer.add_child(note_scrim)

	note_box = PanelContainer.new()
	note_box.name = "NoteBox"
	var style := _panel_style()
	style.bg_color = Color(0.54, 0.49, 0.34, 0.94)
	style.border_color = Color(0.15, 0.11, 0.06, 0.86)
	note_box.add_theme_stylebox_override("panel", style)
	note_box.mouse_filter = Control.MOUSE_FILTER_STOP
	note_layer.add_child(note_box)

	note_label = _make_label(25, Color(0.10, 0.07, 0.03), 0)
	note_label.name = "NoteText"
	note_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	note_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	note_label.set_anchors_preset(Control.PRESET_FULL_RECT)
	note_label.offset_left = 26
	note_label.offset_top = 22
	note_label.offset_right = -26
	note_label.offset_bottom = -22
	note_box.add_child(note_label)

	_layout_note()


func _panel_style() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.025, 0.022, 0.015, 0.88)
	style.border_color = Color(0.75, 0.65, 0.36, 0.58)
	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1
	style.corner_radius_top_left = 8
	style.corner_radius_top_right = 8
	style.corner_radius_bottom_left = 8
	style.corner_radius_bottom_right = 8
	return style


func _make_menu_button(text: String, primary: bool) -> Button:
	var button := Button.new()
	button.text = text
	button.custom_minimum_size = Vector2(0, 48)
	button.focus_mode = Control.FOCUS_NONE
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	button.add_theme_font_override("font", UI_FONT)
	button.add_theme_font_size_override("font_size", 19)
	button.add_theme_color_override("font_color", Color(0.98, 0.94, 0.72) if primary else Color(0.82, 0.78, 0.62))
	button.add_theme_color_override("font_hover_color", Color(1.0, 0.98, 0.82))
	button.add_theme_color_override("font_pressed_color", Color(1.0, 0.86, 0.54))
	button.add_theme_stylebox_override("normal", _button_style(primary, false))
	button.add_theme_stylebox_override("hover", _button_style(primary, true))
	button.add_theme_stylebox_override("pressed", _button_style(primary, true))
	button.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	return button


func _button_style(primary: bool, hover: bool) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.32, 0.10, 0.07, 0.86) if primary else Color(0.08, 0.075, 0.055, 0.82)
	if hover:
		style.bg_color = style.bg_color.lightened(0.15)
	style.border_color = Color(0.94, 0.78, 0.38, 0.70 if hover else 0.42)
	style.border_width_left = 1
	style.border_width_top = 1
	style.border_width_right = 1
	style.border_width_bottom = 1
	style.corner_radius_top_left = 6
	style.corner_radius_top_right = 6
	style.corner_radius_bottom_left = 6
	style.corner_radius_bottom_right = 6
	return style


func _layout_menu() -> void:
	if menu_box == null:
		return
	var view := get_viewport_rect().size
	var width := minf(430.0, maxf(288.0, view.x - 32.0))
	var height := 268.0 if menu_secondary_button.visible else 206.0
	height = minf(height, maxf(190.0, view.y - 32.0))
	menu_box.anchor_left = 0.5
	menu_box.anchor_right = 0.5
	menu_box.anchor_top = 0.5
	menu_box.anchor_bottom = 0.5
	menu_box.offset_left = -width * 0.5
	menu_box.offset_right = width * 0.5
	menu_box.offset_top = -height * 0.5
	menu_box.offset_bottom = height * 0.5


func _layout_note() -> void:
	if note_box == null:
		return
	var view := get_viewport_rect().size
	var width := minf(520.0, maxf(300.0, view.x * 0.54))
	var height := minf(220.0, maxf(150.0, view.y * 0.25))
	note_box.anchor_left = 0.5
	note_box.anchor_right = 0.5
	note_box.anchor_top = 0.5
	note_box.anchor_bottom = 0.5
	note_box.offset_left = -width * 0.5
	note_box.offset_right = width * 0.5
	note_box.offset_top = -height * 0.5
	note_box.offset_bottom = height * 0.5


func _make_label(font_size: int, color: Color, outline_size: int) -> Label:
	var label := Label.new()
	var settings := LabelSettings.new()
	settings.font = UI_FONT
	settings.font_size = font_size
	settings.font_color = color
	settings.outline_size = outline_size
	settings.outline_color = Color(0, 0, 0, 0.86)
	label.label_settings = settings
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label


func _load_assets() -> void:
	creature_texture = load("res://assets/images/creature.png")
	creature.texture = creature_texture
	note_flash.texture = load(_transition_image_path("note_flash"))
	noise.texture = load("res://assets/images/noise_overlay.png")
	vignette.texture = load("res://assets/images/vignette.png")
	click_sound = load("res://assets/audio/click.wav")
	thump_sound = load("res://assets/audio/thump.wav")
	sting_sound = load("res://assets/audio/sting.wav")
	var hum := load("res://assets/audio/hum_loop.wav")
	if hum is AudioStreamWAV:
		hum.loop_mode = AudioStreamWAV.LOOP_FORWARD
	hum_player.stream = hum
	sting_player.stream = sting_sound


func _show_review_hold_screen() -> void:
	game_state = "hold"
	room_id = ""
	background.texture = load(REVIEW_ASSET_PATH)
	background.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	background.visible = true
	creature.visible = false
	foreground.visible = false
	noise.visible = false
	vignette.visible = false
	threat_tint.color.a = 0.0
	flash_rect.color.a = 0.0
	black_fade.color = Color(0, 0, 0, 0)
	caption_label.text = "컨펌용 프리뷰 - 아직 게임에 미적용"
	prompt_label.text = "화면 및 에셋 컨펌 대기 중"
	debug_layer.visible = false
	hold_label.text = ""
	hold_label.visible = true
	if hum_player.playing:
		hum_player.stop()
	_publish_state("review_hold")


func _show_lobby() -> void:
	game_state = "lobby"
	menu_mode = "lobby"
	ending_id = ""
	room_id = start_room
	creature_stage = 0
	creature_peek_active = false
	move_count = 0
	miss_clicks = 0
	input_cooldown = 0.0
	clicked_events.clear()
	_reset_flags()
	creature.visible = false
	creature.scale = Vector2.ONE
	creature.rotation_degrees = 0.0
	foreground.visible = false
	_hide_floor_note()
	_hide_note_screen()
	_hide_note_flash()
	noise.visible = true
	vignette.visible = true
	threat_tint.color.a = 0.0
	flash_rect.color.a = 0.0
	black_fade.color = Color(0, 0, 0, 0)
	caption_label.text = ""
	prompt_label.text = ""
	_hide_hover_feedback()
	if room_data.has(room_id):
		background.texture = load(_room_image_path(room_data[room_id]))
	background.visible = true
	if not hum_player.playing:
		hum_player.play()
	_show_menu("lobby", "NO EXIT", "나가는 길을 찾아라.", "시작", "종료")
	_fade_from_black(0.45)
	_publish_state("lobby")


func _show_menu(mode: String, title: String, body: String, primary_text: String, secondary_text: String) -> void:
	menu_mode = mode
	menu_title.text = title
	menu_body.text = body
	menu_primary_button.text = primary_text
	menu_secondary_button.text = secondary_text
	menu_secondary_button.visible = secondary_text != ""
	menu_layer.visible = true
	_layout_menu()
	Input.set_default_cursor_shape(Input.CURSOR_ARROW)
	_hide_hover_feedback()


func _hide_menu() -> void:
	menu_mode = ""
	if menu_layer != null:
		menu_layer.visible = false


func _on_menu_primary_pressed() -> void:
	match menu_mode:
		"lobby":
			_reset_game()
		"ending":
			_show_lobby()
		"quit":
			_show_lobby()


func _on_menu_secondary_pressed() -> void:
	_quit_game()


func _quit_game() -> void:
	game_state = "quit"
	ending_id = ""
	room_id = ""
	creature.visible = false
	foreground.visible = false
	_hide_floor_note()
	_hide_note_screen()
	_hide_note_flash()
	noise.visible = false
	vignette.visible = false
	debug_layer.visible = false
	caption_label.text = ""
	prompt_label.text = ""
	_hide_hover_feedback()
	background.texture = null
	black_fade.color = Color(0, 0, 0, 1)
	if hum_player.playing:
		hum_player.stop()
	_show_menu("quit", "종료되었습니다.", "", "처음으로", "")
	_publish_state("quit")


func _reset_game() -> void:
	game_state = "play"
	menu_mode = ""
	ending_id = ""
	room_id = start_room
	creature_stage = 0
	creature_peek_active = false
	move_count = 0
	miss_clicks = 0
	input_cooldown = 0.0
	clicked_events.clear()
	_reset_flags()
	creature.visible = false
	creature.scale = Vector2.ONE
	creature.rotation_degrees = 0.0
	_hide_floor_note()
	_hide_note_screen()
	_hide_note_flash()
	threat_tint.color.a = 0.0
	flash_rect.color.a = 0.0
	prompt_label.text = ""
	_hide_menu()
	_hide_hover_feedback()
	if not hum_player.playing:
		hum_player.play()
	_render_room()
	_fade_from_black(0.45)
	_dev_log("reset room=%s" % room_id)


func _reset_flags() -> void:
	flags.clear()
	for key in FLAG_DEFAULTS.keys():
		flags[key] = FLAG_DEFAULTS[key]


func _input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		_update_hover(event.position)
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		_handle_click(event.position)
	elif event is InputEventScreenTouch and event.pressed:
		_handle_click(event.position)
	elif event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_H:
			debug_hotspots_visible = not debug_hotspots_visible
			_render_debug_overlay()


func _process(delta: float) -> void:
	elapsed += delta
	input_cooldown = maxf(0.0, input_cooldown - delta)
	noise.modulate.a = 0.10 + sin(elapsed * 21.0) * 0.018 + randf() * 0.025
	if game_state == "play":
		hum_player.volume_db = -25.0 + min(creature_stage, 4) * 1.2
		threat_tint.color.a = lerpf(threat_tint.color.a, creature_stage * 0.035, delta * 2.0)
	if shake_time > 0.0:
		shake_time = maxf(0.0, shake_time - delta)
		var amount := shake_power * (shake_time / maxf(shake_time + delta, 0.001))
		world.position = Vector2(randf_range(-amount, amount), randf_range(-amount, amount))
	else:
		world.position = Vector2.ZERO
	if debug_hotspots_visible and debug_viewport_size != get_viewport_rect().size:
		_render_debug_overlay()
	if menu_layer != null and menu_layer.visible:
		_layout_menu()
	if note_layer != null and note_layer.visible:
		_layout_note()


func _handle_click(screen_pos: Vector2) -> void:
	if game_state == "hold":
		return
	if game_state == "note":
		_handle_note_screen_click(screen_pos)
		return
	if game_state == "lobby" or game_state == "ending" or game_state == "quit":
		return
	if input_cooldown > 0.0:
		return
	input_cooldown = 0.10
	_show_click_feedback(screen_pos)
	if game_state != "play":
		return

	_play_sound(click_sound)
	var hotspot := _hotspot_at(screen_pos)
	if hotspot.is_empty():
		_miss_click()
		return

	if hotspot.has("event"):
		_handle_event(str(hotspot["event"]))
	elif hotspot.has("target"):
		_go_to_room(str(hotspot["target"]))


func _miss_click() -> void:
	miss_clicks += 1
	if miss_clicks % 3 == 0:
		_flash_caption("아무것도 없는 것 같다.")
	else:
		_flash_caption("아무것도 움직이지 않는다.")


func _go_to_room(target: String) -> void:
	if not room_data.has(target):
		push_warning("Missing room target: %s" % target)
		_flash_caption("그쪽은 아직 이어지지 않았다.")
		return

	var previous_room := room_id
	var post_caption := ""
	var play_panel_sound := false
	var play_stop_back_warning := false

	if target == ROOM_STOP_BACK and bool(flags["stop_back_reentry_armed"]):
		_show_ending("C")
		return

	if previous_room == ROOM_FORK and (target == ROOM_LEFT_PATH or target == ROOM_RIGHT_PATH):
		flags["stop_back_reentry_armed"] = false

	if target == ROOM_STOP_BACK:
		flags["stop_back_seen_once"] = true
		if bool(flags["light_switch_pressed"]):
			flags["stop_back_red_seen"] = true

	if previous_room == ROOM_STOP_BACK and target == ROOM_FORK:
		flags["stop_back_reentry_armed"] = true
		play_stop_back_warning = true

	if target == ROOM_RIGHT_DEAD_END:
		flags["right_dead_end_seen"] = true

	if previous_room == ROOM_RIGHT_DEAD_END and target == ROOM_RIGHT_PATH and not bool(flags["panel_sound_played"]):
		if bool(flags["right_door_warning_seen"]) and not bool(flags["right_note_read"]):
			flags["right_note_available"] = true
			post_caption = "바닥에 무언가 떨어져 있다."
		else:
			flags["panel_sound_played"] = true
			post_caption = "판넬 뒤에서 소리가 났다."
			play_panel_sound = true

	room_id = target
	move_count += 1
	_dev_log("move %s -> %s flags=%s" % [previous_room, room_id, _debug_flag_summary()])
	_render_room()
	_play_sound(thump_sound)
	_shake(1.5, 0.12)
	_fade_from_black(0.20)

	if play_panel_sound:
		_play_sting(thump_sound)
		_shake(4.0, 0.18)
	if play_stop_back_warning:
		_play_sting(sting_sound)
		_shake(2.4, 0.14)
	if post_caption != "":
		_flash_caption(post_caption, 1.45)

	if target == ROOM_FORK and previous_room == ROOM_RIGHT_PATH and bool(flags["right_dead_end_seen"]) and not bool(flags["creature_peek_seen"]):
		var timer := get_tree().create_timer(_creature_beat_float("right_return_peek", "delay", 0.28))
		timer.timeout.connect(_show_stop_sign_creature_peek)


func _render_room() -> void:
	if not room_data.has(room_id):
		return
	var room: Dictionary = room_data[room_id]
	background.texture = load(_room_image_path(room))
	if room.has("foreground"):
		foreground.texture = load(str(room["foreground"]))
		foreground.visible = true
	else:
		foreground.texture = null
		foreground.visible = false

	if game_state == "play":
		caption_label.text = _room_caption(room)
	elif game_state == "ending":
		caption_label.text = str(room.get("caption", ""))
	else:
		caption_label.text = ""
	_update_floor_note_marker()
	prompt_label.text = ""
	_update_creature()
	_render_debug_overlay()
	_publish_state("render")


func _room_image_path(room: Dictionary) -> String:
	if room_id == ROOM_STOP_BACK and bool(flags.get("light_switch_pressed", false)):
		var state_images: Dictionary = room.get("state_images", {})
		return str(state_images.get("red", room.get("image", "")))
	return str(room.get("image", ""))


func _room_caption(room: Dictionary) -> String:
	if room_id == ROOM_STOP_BACK and bool(flags.get("light_switch_pressed", false)):
		return str(room.get("red_caption", room.get("caption", "")))
	if creature_stage >= 4 and room_id != ROOM_STOP_BACK:
		return "이 방을 들킨 것 같다."
	return str(room.get("caption", ""))


func _update_creature() -> void:
	if game_state != "play" or creature_stage <= 0 or creature_peek_active:
		if not creature_peek_active:
			creature.visible = false
		return

	var placements := [
		{"center": Vector2(0.50, 0.48), "height": 0.10, "alpha": 0.00},
		{"center": Vector2(0.515, 0.455), "height": 0.145, "alpha": 0.16},
		{"center": Vector2(0.180, 0.500), "height": 0.250, "alpha": 0.28},
		{"center": Vector2(0.780, 0.500), "height": 0.395, "alpha": 0.43},
		{"center": Vector2(0.185, 0.510), "height": 0.680, "alpha": 0.64}
	]
	var data: Dictionary = placements[mini(creature_stage, placements.size() - 1)]
	var view := get_viewport_rect().size
	var target_h: float = view.y * data["height"]
	var ratio := float(creature_texture.get_width()) / float(creature_texture.get_height())
	var target_w := target_h * ratio
	creature.size = Vector2(target_w, target_h)
	var center: Vector2 = data["center"]
	creature.position = Vector2(view.x * center.x - target_w * 0.5, view.y * center.y - target_h * 0.5)
	creature.modulate = Color(0.92, 0.83, 0.48, data["alpha"])
	creature.rotation_degrees = sin(elapsed * 5.1) * 0.6
	creature.visible = true


func _handle_event(event_name: String) -> void:
	if event_name == "attempt_exit":
		_attempt_exit()
		return
	if event_name == "blocked_passage":
		_show_blocked_passage_transition()
		return
	if event_name == "right_door":
		_handle_right_door()
		return
	if event_name == "floor_note":
		_show_note_screen()
		return

	if clicked_events.has(event_name):
		_flash_caption(_repeat_event_line(event_name))
		return
	clicked_events[event_name] = true

	match event_name:
		"stop_sign":
			_flash_caption("글자가 칠해진 게 아니라 파여 있다.")
		"blood_trace":
			flags["blood_trace_clicked"] = true
			_dev_log("event=blood_trace flags=%s" % _debug_flag_summary())
			_flash_caption("자국은 왼쪽에서 끊겨있다.")
			_flash_screen(Color(0.82, 0.08, 0.04, 0.18), 0.16)
		"light_switch":
			flags["light_switch_pressed"] = true
			_dev_log("event=light_switch flags=%s" % _debug_flag_summary())
			_flash_caption("무언가 변한 것 같다.")
			_play_sting(thump_sound)
			_flash_screen(Color(1.0, 0.12, 0.06, 0.20), 0.18)
			_shake(2.5, 0.16)
			_schedule_creature_beat("switch_shadow")
			_render_debug_overlay()
		"human_panel":
			flags["panel_clue_clicked"] = true
			_dev_log("event=human_panel flags=%s" % _debug_flag_summary())
			_flash_caption("이런 곳에 어째서?")
			_flash_screen(Color(1.0, 0.92, 0.58, 0.10), 0.12)
		"dead_wall":
			_flash_caption("길이 끊겼다.")
		_:
			_flash_caption("아무것도 변하지 않는다.")


func _repeat_event_line(event_name: String) -> String:
	match event_name:
		"stop_sign":
			return "여전히 STOP이다."
		"blood_trace":
			return "붉은 자국은 이미 말라 있다."
		"light_switch":
			return "버튼은 이미 눌려 있다."
		"human_panel":
			return "단순한 판넬인 것 같다."
		"dead_wall":
			return "막힌 벽이다."
	return "아무것도 변하지 않는다."


func _handle_right_door() -> void:
	if bool(flags["right_door_warning_seen"]):
		_show_blocked_passage_transition()
		return
	flags["right_door_warning_seen"] = true
	_dev_log("event=right_door_warning flags=%s" % _debug_flag_summary())
	_flash_caption("뒤쪽에서 소리가 났다.", 1.35)
	_play_sting(thump_sound)
	_flash_screen(Color(0.72, 0.02, 0.02, 0.18), 0.18)
	_shake(5.0, 0.20)
	_render_debug_overlay()


func _attempt_exit() -> void:
	_dev_log("event=attempt_exit true_requirements=%s flags=%s" % [str(_has_true_exit_requirements()), _debug_flag_summary()])
	if _has_true_exit_requirements():
		_show_ending("A")
		return
	_show_blocked_passage_transition()


func _show_blocked_passage_transition() -> void:
	game_state = "transition"
	caption_label.text = "뒤가 막혔다."
	prompt_label.text = ""
	debug_layer.visible = false
	creature.visible = false
	foreground.visible = false
	_hide_floor_note()
	_hide_note_screen()
	_hide_note_flash()
	var blocked_path := _transition_image_path("blocked_passage")
	if blocked_path != "":
		background.texture = load(blocked_path)
	_publish_state("blocked_passage")
	_play_sting(thump_sound)
	_flash_screen(Color(0.75, 0.02, 0.02, 0.22), 0.22)
	_shake(6.0, 0.24)
	var blocked_timer := get_tree().create_timer(0.62)
	blocked_timer.timeout.connect(func() -> void:
		if game_state != "transition":
			return
		caption_label.text = ""
		_publish_state("false_exit_chase")
		_flash_screen(Color(0.9, 0.07, 0.03, 0.30), 0.28)
		_show_creature_beat("false_exit_chase")
		var ending_timer := get_tree().create_timer(_creature_beat_total("false_exit_chase", 0.95))
		ending_timer.timeout.connect(func() -> void:
			_show_ending("B")
		)
	)


func _has_true_exit_requirements() -> bool:
	return bool(flags["light_switch_pressed"]) and bool(flags["stop_back_red_seen"]) and bool(flags["blood_trace_clicked"])


func _show_ending(id: String) -> void:
	game_state = "ending"
	ending_id = id
	_dev_log("ending=%s flags=%s" % [ending_id, _debug_flag_summary()])
	input_cooldown = 0.22
	debug_layer.visible = false
	creature_peek_active = false
	creature_stage = 0
	_hide_floor_note()
	_hide_note_screen()
	_hide_note_flash()
	creature.scale = Vector2.ONE
	creature.rotation_degrees = 0.0

	match id:
		"A":
			room_id = ROOM_TRUE_EXIT
			creature.visible = false
			_render_room()
			caption_label.text = ""
			prompt_label.text = ""
			_show_menu("ending", "A 엔딩", "드디어. 돌아왔다.", "재시작", "종료")
			_fade_from_black(0.65)
		"B":
			room_id = ROOM_FALSE_EXIT
			creature.visible = false
			_render_room()
			caption_label.text = ""
			prompt_label.text = ""
			_show_menu("ending", "B 엔딩", "다시 시작점이다.", "재시작", "종료")
			_fade_from_black(0.65)
		"C":
			ending_id = "C"
			creature.visible = true
			var view := get_viewport_rect().size
			var target_h := view.y * 1.55
			var ratio := float(creature_texture.get_width()) / float(creature_texture.get_height())
			creature.size = Vector2(target_h * ratio, target_h)
			creature.position = Vector2(view.x * 0.5 - creature.size.x * 0.5, view.y * 0.52 - creature.size.y * 0.5)
			creature.modulate = Color(1.0, 0.86, 0.58, 0.96)
			caption_label.text = ""
			prompt_label.text = ""
			_show_menu("ending", "C 엔딩", "돌아보면 안 됐다.", "재시작", "종료")
			_play_sting(sting_sound)
			_shake(24.0, 0.72)
			_flash_screen(Color(1.0, 0.05, 0.02, 0.42), 0.34)
	_publish_state("ending_%s" % id)


func _show_stop_sign_creature_peek() -> void:
	if game_state != "play" or room_id != ROOM_FORK or bool(flags["creature_peek_seen"]):
		return
	flags["creature_peek_seen"] = true
	_dev_log("creature_peek flags=%s" % _debug_flag_summary())
	_show_creature_beat("right_return_peek")


func _schedule_creature_beat(name: String) -> void:
	var timer := get_tree().create_timer(_creature_beat_float(name, "delay", 0.0))
	timer.timeout.connect(func() -> void:
		_show_creature_beat(name)
	)


func _show_creature_beat(name: String) -> void:
	var beat := _creature_beat(name)
	if beat.is_empty() or creature_texture == null:
		return
	creature_peek_active = true
	var view := get_viewport_rect().size
	var center := _creature_beat_vector(beat, "center", Vector2(0.50, 0.315))
	var target_h := view.y * float(beat.get("height", 0.50))
	var ratio := float(creature_texture.get_width()) / float(creature_texture.get_height())
	var target_w := target_h * ratio
	creature.size = Vector2(target_w, target_h)
	creature.position = Vector2(view.x * center.x - target_w * 0.5, view.y * center.y - target_h * 0.5)
	creature.rotation_degrees = 0.0
	creature.scale = Vector2.ONE
	creature.modulate = Color(0.88, 0.76, 0.42, 0.0)
	creature.visible = true
	var beat_caption := str(beat.get("caption", ""))
	if beat_caption != "":
		_flash_caption(beat_caption, 1.5)
	_play_sting(_sound_from_name(str(beat.get("sound", "thump"))))
	_shake(float(beat.get("shake_power", 4.0)), float(beat.get("shake_duration", 0.18)))
	var tween := create_tween()
	tween.tween_property(creature, "modulate:a", float(beat.get("alpha", 0.55)), float(beat.get("fade_in", 0.12)))
	tween.tween_interval(float(beat.get("hold", 0.68)))
	tween.tween_property(creature, "modulate:a", 0.0, float(beat.get("fade_out", 0.20)))
	tween.tween_callback(func() -> void:
		creature_peek_active = false
		creature.visible = false
	)


func _creature_beat_total(name: String, fallback: float) -> float:
	var beat := _creature_beat(name)
	if beat.is_empty():
		return fallback
	return float(beat.get("delay", 0.0)) + float(beat.get("fade_in", 0.0)) + float(beat.get("hold", 0.0)) + float(beat.get("fade_out", 0.0))


func _creature_beat(name: String) -> Dictionary:
	var beats: Dictionary = room_config.get("creature_beats", {})
	return beats.get(name, {})


func _transition_image_path(name: String) -> String:
	var images: Dictionary = room_config.get("transition_images", {})
	return str(images.get(name, ""))


func _creature_beat_float(name: String, key: String, fallback: float) -> float:
	return float(_creature_beat(name).get(key, fallback))


func _creature_beat_vector(beat: Dictionary, key: String, fallback: Vector2) -> Vector2:
	var data: Array = beat.get(key, [])
	if data.size() != 2:
		return fallback
	return Vector2(float(data[0]), float(data[1]))


func _sound_from_name(sound_name: String) -> AudioStream:
	match sound_name:
		"click":
			return click_sound
		"sting":
			return sting_sound
		"thump":
			return thump_sound
	return thump_sound


func _hotspot_at(screen_pos: Vector2) -> Dictionary:
	var norm := _normalized_position(screen_pos)
	for hotspot in _active_hotspots():
		var rect := _hotspot_rect(hotspot)
		if rect.has_point(norm):
			return hotspot
	return {}


func _active_hotspots() -> Array:
	var result: Array = []
	if not room_data.has(room_id):
		return result
	var room: Dictionary = room_data[room_id]
	for hotspot in room.get("hotspots", []):
		if _hotspot_enabled(hotspot):
			result.append(hotspot)
	return result


func _hotspot_enabled(hotspot: Dictionary) -> bool:
	if hotspot.has("requires_flag") and not bool(flags.get(str(hotspot["requires_flag"]), false)):
		return false
	if hotspot.has("hidden_when_flag") and bool(flags.get(str(hotspot["hidden_when_flag"]), false)):
		return false
	return true


func _hotspot_rect(hotspot: Dictionary) -> Rect2:
	var rect_data: Array = hotspot.get("rect", [0.0, 0.0, 0.0, 0.0])
	return Rect2(
		Vector2(float(rect_data[0]), float(rect_data[1])),
		Vector2(float(rect_data[2]), float(rect_data[3]))
	)


func _update_hover(screen_pos: Vector2) -> void:
	if game_state != "play":
		prompt_label.text = ""
		_hide_hover_feedback()
		return
	var hotspot := _hotspot_at(screen_pos)
	if hotspot.is_empty():
		hover_prompt = ""
		_hide_hover_feedback()
	else:
		hover_prompt = str(hotspot.get("prompt", ""))
		_show_hover_feedback(screen_pos, hotspot, hover_prompt)
	prompt_label.text = hover_prompt


func _show_hover_feedback(screen_pos: Vector2, hotspot: Dictionary, prompt: String) -> void:
	if prompt == "":
		_hide_hover_feedback()
		return
	Input.set_default_cursor_shape(Input.CURSOR_POINTING_HAND)
	var view := get_viewport_rect().size
	var rect := _hotspot_rect(hotspot)
	hover_highlight.position = Vector2(rect.position.x * view.x, rect.position.y * view.y)
	hover_highlight.size = Vector2(rect.size.x * view.x, rect.size.y * view.y)
	hover_highlight.color = Color(1.0, 0.86, 0.28, 0.12)
	hover_highlight.visible = true

	var badge_text := "클릭: %s" % prompt
	hover_badge_label.text = badge_text
	var badge_width := clampf(74.0 + float(badge_text.length()) * 11.0, 112.0, 190.0)
	hover_badge_bg.size = Vector2(badge_width, 34)
	hover_badge_label.size = hover_badge_bg.size
	var badge_pos := screen_pos + Vector2(18, -46)
	badge_pos.x = clampf(badge_pos.x, 12.0, maxf(12.0, view.x - badge_width - 12.0))
	badge_pos.y = clampf(badge_pos.y, 12.0, maxf(12.0, view.y - hover_badge_bg.size.y - 12.0))
	hover_badge_bg.position = badge_pos
	hover_badge_label.position = badge_pos
	hover_badge_bg.visible = true
	hover_badge_label.visible = true


func _hide_hover_feedback() -> void:
	Input.set_default_cursor_shape(Input.CURSOR_ARROW)
	if hover_highlight != null:
		hover_highlight.visible = false
	if hover_badge_bg != null:
		hover_badge_bg.visible = false
	if hover_badge_label != null:
		hover_badge_label.visible = false


func _show_note_screen() -> void:
	game_state = "note"
	input_cooldown = 0.10
	caption_label.text = ""
	prompt_label.text = ""
	debug_layer.visible = false
	_hide_hover_feedback()
	note_label.text = "스위치를 찾고, 멈춤 너머로 나아가."
	note_layer.visible = true
	_layout_note()
	_publish_state("note_open")


func _handle_note_screen_click(screen_pos: Vector2) -> void:
	if input_cooldown > 0.0:
		return
	if _point_in_control(note_box, screen_pos):
		return
	_close_note_screen()


func _close_note_screen() -> void:
	flags["right_note_read"] = true
	game_state = "play"
	input_cooldown = 0.55
	_hide_note_screen()
	_update_floor_note_marker()
	_render_debug_overlay()
	_publish_state("note_closed")
	_show_note_flash(0.50)


func _hide_note_screen() -> void:
	if note_layer != null:
		note_layer.visible = false


func _point_in_control(control: Control, point: Vector2) -> bool:
	if control == null:
		return false
	return Rect2(control.global_position, control.size).has_point(point)


func _update_floor_note_marker() -> void:
	var visible := game_state == "play" and room_id == ROOM_RIGHT_PATH and bool(flags.get("right_note_available", false)) and not bool(flags.get("right_note_read", false))
	if not visible:
		_hide_floor_note()
		return
	var view := get_viewport_rect().size
	var size := Vector2(view.x * 0.120, view.y * 0.050)
	var pos := Vector2(view.x * 0.365, view.y * 0.765)
	note_shadow.position = pos + Vector2(5, 5)
	note_shadow.size = size
	note_shadow.visible = true
	note_marker.position = pos
	note_marker.size = size
	note_marker.visible = true


func _hide_floor_note() -> void:
	if note_shadow != null:
		note_shadow.visible = false
	if note_marker != null:
		note_marker.visible = false


func _show_note_flash(duration: float) -> void:
	if note_flash.texture == null:
		return
	note_flash.visible = true
	note_flash.modulate = Color(1.0, 1.0, 1.0, 1.0)
	caption_label.text = ""
	prompt_label.text = ""
	_play_sting(thump_sound)
	_shake(4.5, 0.16)
	var timer := get_tree().create_timer(duration)
	timer.timeout.connect(_hide_note_flash)


func _hide_note_flash() -> void:
	if note_flash != null:
		note_flash.visible = false


func _normalized_position(screen_pos: Vector2) -> Vector2:
	var view_size := get_viewport_rect().size
	if view_size.x <= 0.0 or view_size.y <= 0.0:
		return Vector2.ZERO
	return Vector2(screen_pos.x / view_size.x, screen_pos.y / view_size.y)


func _render_debug_overlay() -> void:
	if debug_layer == null:
		return
	for child in debug_layer.get_children():
		child.queue_free()
	debug_layer.visible = debug_hotspots_visible and game_state == "play"
	if not debug_layer.visible:
		return
	debug_viewport_size = get_viewport_rect().size
	var view := debug_viewport_size
	for hotspot in _active_hotspots():
		var rect := _hotspot_rect(hotspot)
		var color_rect := ColorRect.new()
		color_rect.name = "Hotspot_%s" % str(hotspot.get("id", "unknown"))
		color_rect.position = Vector2(rect.position.x * view.x, rect.position.y * view.y)
		color_rect.size = Vector2(rect.size.x * view.x, rect.size.y * view.y)
		color_rect.color = Color(1.0, 0.80, 0.20, 0.16)
		color_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		debug_layer.add_child(color_rect)

		var label := _make_label(13, Color(1.0, 0.86, 0.30), 2)
		label.text = str(hotspot.get("id", "hotspot"))
		label.position = color_rect.position + Vector2(5, 4)
		label.size = Vector2(maxf(120.0, color_rect.size.x - 10.0), 22.0)
		label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		debug_layer.add_child(label)

	var info := _make_label(13, Color(0.72, 0.90, 1.0), 2)
	info.name = "DebugInfo"
	info.text = _debug_text()
	info.position = Vector2(14, 14)
	info.size = Vector2(500, 130)
	info.mouse_filter = Control.MOUSE_FILTER_IGNORE
	debug_layer.add_child(info)


func _debug_text() -> String:
	return "room=%s  end=%s\nswitch=%s red=%s trace=%s panel=%s\nstop_reentry=%s dead_end=%s warn=%s note=%s peek=%s" % [
		room_id,
		ending_id,
		str(flags.get("light_switch_pressed", false)),
		str(flags.get("stop_back_red_seen", false)),
		str(flags.get("blood_trace_clicked", false)),
		str(flags.get("panel_clue_clicked", false)),
		str(flags.get("stop_back_reentry_armed", false)),
		str(flags.get("right_dead_end_seen", false)),
		str(flags.get("right_door_warning_seen", false)),
		str(flags.get("right_note_read", false)),
		str(flags.get("creature_peek_seen", false))
	]


func _debug_flag_summary() -> String:
	return "switch=%s red=%s trace=%s panel=%s reentry=%s dead=%s warn=%s note=%s peek=%s" % [
		str(flags.get("light_switch_pressed", false)),
		str(flags.get("stop_back_red_seen", false)),
		str(flags.get("blood_trace_clicked", false)),
		str(flags.get("panel_clue_clicked", false)),
		str(flags.get("stop_back_reentry_armed", false)),
		str(flags.get("right_dead_end_seen", false)),
		str(flags.get("right_door_warning_seen", false)),
		str(flags.get("right_note_read", false)),
		str(flags.get("creature_peek_seen", false))
	]


func _state_payload(reason: String) -> Dictionary:
	return {
		"reason": reason,
		"room_id": room_id,
		"game_state": game_state,
		"ending_id": ending_id,
		"move_count": move_count,
		"flags": flags.duplicate(),
		"active_hotspots": _active_hotspot_ids()
	}


func _active_hotspot_ids() -> Array:
	var ids: Array = []
	for hotspot in _active_hotspots():
		ids.append(str(hotspot.get("id", "")))
	return ids


func _publish_state(reason: String) -> void:
	if not _is_web_runtime():
		return
	var json := JSON.stringify(_state_payload(reason))
	JavaScriptBridge.eval("window.__BR0_STATE__ = %s; globalThis.__BR0_STATE__ = %s;" % [json, json], true)


func _dev_log(message: String) -> void:
	if DEV_LOGGING:
		print("[BR0] %s" % message)
		if _is_web_runtime():
			JavaScriptBridge.eval("console.log(%s);" % JSON.stringify("[BR0] %s" % message), true)


func _is_web_runtime() -> bool:
	return OS.get_name() == "Web" or OS.has_feature("web")


func _flash_caption(text: String, duration: float = 1.25) -> void:
	caption_label.text = text
	var timer := get_tree().create_timer(duration)
	timer.timeout.connect(func() -> void:
		if game_state == "play" and room_data.has(room_id):
			caption_label.text = _room_caption(room_data[room_id])
	)


func _fade_from_black(duration: float) -> void:
	black_fade.color.a = 1.0
	var tween := create_tween()
	tween.tween_property(black_fade, "color:a", 0.0, duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)


func _flash_screen(color: Color, duration: float) -> void:
	flash_rect.color = color
	var tween := create_tween()
	tween.tween_property(flash_rect, "color:a", 0.0, duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)


func _show_click_feedback(screen_pos: Vector2) -> void:
	click_feedback.position = screen_pos - click_feedback.size * 0.5
	click_feedback.scale = Vector2.ONE
	click_feedback.color.a = 0.55
	var tween := create_tween()
	tween.set_parallel(true)
	tween.tween_property(click_feedback, "color:a", 0.0, 0.22)
	tween.tween_property(click_feedback, "scale", Vector2(1.8, 1.8), 0.22).from(Vector2.ONE)


func _shake(power: float, duration: float) -> void:
	shake_power = power
	shake_time = duration


func _play_sound(stream: AudioStream) -> void:
	if stream == null:
		return
	sfx_player.stop()
	sfx_player.stream = stream
	sfx_player.play()


func _play_sting(stream: AudioStream) -> void:
	if stream == null:
		return
	sting_player.stop()
	sting_player.stream = stream
	sting_player.play()
