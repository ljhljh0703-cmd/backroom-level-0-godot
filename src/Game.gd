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
const REVIEW_HOLD_SCREEN := true
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
var debug_hotspots_visible := false
var debug_viewport_size := Vector2.ZERO

var world: Control
var background: TextureRect
var creature: TextureRect
var foreground: TextureRect
var noise: TextureRect
var vignette: TextureRect
var threat_tint: ColorRect
var flash_rect: ColorRect
var click_feedback: ColorRect
var black_fade: ColorRect
var caption_label: Label
var prompt_label: Label
var hold_label: Label
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
	_reset_game()
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


func _reset_game() -> void:
	game_state = "play"
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
	threat_tint.color.a = 0.0
	flash_rect.color.a = 0.0
	prompt_label.text = ""
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


func _handle_click(screen_pos: Vector2) -> void:
	if game_state == "hold":
		return
	if input_cooldown > 0.0:
		return
	input_cooldown = 0.10
	_show_click_feedback(screen_pos)
	if game_state == "ending":
		_reset_game()
		return
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


func _attempt_exit() -> void:
	_dev_log("event=attempt_exit true_requirements=%s flags=%s" % [str(_has_true_exit_requirements()), _debug_flag_summary()])
	if _has_true_exit_requirements():
		_show_ending("A")
		return
	game_state = "transition"
	caption_label.text = "뒤가 막혔다."
	prompt_label.text = ""
	debug_layer.visible = false
	creature.visible = false
	foreground.visible = false
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
	creature.scale = Vector2.ONE
	creature.rotation_degrees = 0.0

	match id:
		"A":
			room_id = ROOM_TRUE_EXIT
			creature.visible = false
			_render_room()
			caption_label.text = "드디어. 돌아왔다."
			prompt_label.text = "A 엔딩: 진짜 출구. 클릭하면 다시 시작."
			_fade_from_black(0.65)
		"B":
			room_id = ROOM_FALSE_EXIT
			creature.visible = false
			_render_room()
			caption_label.text = ""
			prompt_label.text = "B 엔딩. 클릭하면 다시 시작."
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
			caption_label.text = "돌아보면 안 됐다."
			prompt_label.text = "C 엔딩: 크리처에게 잡힘. 클릭하면 다시 시작."
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
		return
	var hotspot := _hotspot_at(screen_pos)
	if hotspot.is_empty():
		hover_prompt = ""
	else:
		hover_prompt = str(hotspot.get("prompt", ""))
	prompt_label.text = hover_prompt


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
	return "room=%s  end=%s\nswitch=%s red=%s trace=%s panel=%s\nstop_reentry=%s dead_end=%s peek=%s" % [
		room_id,
		ending_id,
		str(flags.get("light_switch_pressed", false)),
		str(flags.get("stop_back_red_seen", false)),
		str(flags.get("blood_trace_clicked", false)),
		str(flags.get("panel_clue_clicked", false)),
		str(flags.get("stop_back_reentry_armed", false)),
		str(flags.get("right_dead_end_seen", false)),
		str(flags.get("creature_peek_seen", false))
	]


func _debug_flag_summary() -> String:
	return "switch=%s red=%s trace=%s panel=%s reentry=%s dead=%s peek=%s" % [
		str(flags.get("light_switch_pressed", false)),
		str(flags.get("stop_back_red_seen", false)),
		str(flags.get("blood_trace_clicked", false)),
		str(flags.get("panel_clue_clicked", false)),
		str(flags.get("stop_back_reentry_armed", false)),
		str(flags.get("right_dead_end_seen", false)),
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
