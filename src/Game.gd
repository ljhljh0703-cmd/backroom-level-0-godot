extends Control

const ROOM_START := "start"
const ROOM_DATA := {
	"start": {
		"image": "res://assets/images/bg_start.png",
		"caption": "The lights hum too close.",
		"hotspots": [
			{"rect": Rect2(0.700, 0.240, 0.220, 0.520), "target": "hallway", "prompt": "DARK HALL"}
		]
	},
	"hallway": {
		"image": "res://assets/images/bg_hallway.png",
		"caption": "The same wallpaper keeps going.",
		"hotspots": [
			{"rect": Rect2(0.425, 0.245, 0.170, 0.380), "target": "junction", "prompt": "END OF HALL"},
			{"rect": Rect2(0.030, 0.420, 0.180, 0.360), "target": "start", "prompt": "BACK"}
		]
	},
	"junction": {
		"image": "res://assets/images/bg_junction.png",
		"caption": "Footsteps answer one beat late.",
		"hotspots": [
			{"rect": Rect2(0.080, 0.245, 0.240, 0.470), "target": "sign", "prompt": "LEFT ROOM"},
			{"rect": Rect2(0.700, 0.265, 0.230, 0.450), "target": "hallway", "prompt": "RIGHT HALL"}
		]
	},
	"sign": {
		"image": "res://assets/images/bg_sign.png",
		"caption": "That sign was not here before.",
		"hotspots": [
			{"rect": Rect2(0.430, 0.210, 0.280, 0.180), "target": "door", "prompt": "EXIT SIGN"},
			{"rect": Rect2(0.030, 0.280, 0.220, 0.480), "target": "junction", "prompt": "GO BACK"}
		]
	},
	"door": {
		"image": "res://assets/images/bg_door.png",
		"caption": "Cold air leaks through the frame.",
		"hotspots": [
			{"rect": Rect2(0.405, 0.195, 0.245, 0.600), "target": "jump", "prompt": "OPEN"}
		]
	},
	"other": {
		"image": "res://assets/images/bg_other.png",
		"caption": "You got out. Outside was still inside.",
		"hotspots": []
	}
}

var room_id := ROOM_START
var creature_stage := 0
var game_state := "title"
var shake_time := 0.0
var shake_power := 0.0
var hover_prompt := ""
var elapsed := 0.0
var miss_clicks := 0

var world: Control
var background: TextureRect
var creature: TextureRect
var noise: TextureRect
var vignette: TextureRect
var black_fade: ColorRect
var caption_label: Label
var prompt_label: Label
var title_layer: Control
var title_label: Label
var subtitle_label: Label
var restart_label: Label
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
	_build_nodes()
	_load_assets()
	_show_title()
	set_process(true)


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

	title_layer = Control.new()
	title_layer.name = "TitleLayer"
	title_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	title_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(title_layer)

	var title_shade := ColorRect.new()
	title_shade.name = "TitleShade"
	title_shade.set_anchors_preset(Control.PRESET_FULL_RECT)
	title_shade.color = Color(0, 0, 0, 0.44)
	title_shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	title_layer.add_child(title_shade)

	title_label = _make_label(64, Color(0.98, 0.91, 0.56), 4)
	title_label.name = "Title"
	title_label.text = "LEVEL 0"
	title_label.set_anchors_preset(Control.PRESET_CENTER)
	title_label.offset_left = -360
	title_label.offset_right = 360
	title_label.offset_top = -112
	title_label.offset_bottom = -30
	title_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	title_layer.add_child(title_label)

	subtitle_label = _make_label(22, Color(0.84, 0.78, 0.60), 2)
	subtitle_label.name = "Subtitle"
	subtitle_label.text = "CLICK / TOUCH"
	subtitle_label.set_anchors_preset(Control.PRESET_CENTER)
	subtitle_label.offset_left = -360
	subtitle_label.offset_right = 360
	subtitle_label.offset_top = -24
	subtitle_label.offset_bottom = 24
	subtitle_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	title_layer.add_child(subtitle_label)

	restart_label = _make_label(18, Color(0.75, 0.70, 0.53), 2)
	restart_label.name = "Restart"
	restart_label.text = "CLICK TO RESTART"
	restart_label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	restart_label.offset_left = 42
	restart_label.offset_right = -42
	restart_label.offset_top = -70
	restart_label.offset_bottom = -28
	restart_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	restart_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	restart_label.visible = false
	add_child(restart_label)

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
	_render_room()


func _show_title() -> void:
	game_state = "title"
	room_id = ROOM_START
	creature_stage = 0
	miss_clicks = 0
	title_layer.visible = true
	restart_label.visible = false
	caption_label.text = ""
	prompt_label.text = ""
	creature.visible = false
	_render_room()
	_fade_from_black(0.5)


func _start_game() -> void:
	game_state = "play"
	title_layer.visible = false
	restart_label.visible = false
	caption_label.text = ROOM_DATA[room_id]["caption"]
	creature_stage = 0
	miss_clicks = 0
	if not hum_player.playing:
		hum_player.play()
	_play_sound(click_sound)
	_fade_from_black(0.35)


func _input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		_update_hover(event.position)
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		_handle_click(event.position)
	elif event is InputEventScreenTouch and event.pressed:
		_handle_click(event.position)


func _process(delta: float) -> void:
	elapsed += delta
	noise.modulate.a = 0.10 + sin(elapsed * 21.0) * 0.018 + randf() * 0.025
	if game_state == "play":
		hum_player.volume_db = -25.0 + min(creature_stage, 4) * 1.2
	if shake_time > 0.0:
		shake_time = maxf(0.0, shake_time - delta)
		var amount := shake_power * (shake_time / maxf(shake_time + delta, 0.001))
		world.position = Vector2(randf_range(-amount, amount), randf_range(-amount, amount))
	else:
		world.position = Vector2.ZERO


func _handle_click(screen_pos: Vector2) -> void:
	if game_state == "title":
		_start_game()
		return
	if game_state == "ending":
		_show_title()
		return
	if game_state != "play":
		return

	_play_sound(click_sound)
	var hotspot := _hotspot_at(screen_pos)
	if hotspot.is_empty():
		_miss_click()
		return

	if hotspot["target"] == "jump":
		_trigger_jump()
	else:
		_go_to_room(hotspot["target"])


func _miss_click() -> void:
	miss_clicks += 1
	if miss_clicks % 3 == 0 and creature_stage < 4:
		creature_stage += 1
		_flash_caption("Something steps onto the carpet behind you.")
		_play_sound(thump_sound)
		_shake(3.0, 0.18)
		_update_creature()
	else:
		_flash_caption("The wallpaper is damp and warm.")


func _go_to_room(target: String) -> void:
	room_id = target
	creature_stage = mini(creature_stage + 1, 4)
	_render_room()
	_play_sound(thump_sound)
	_shake(1.5 + creature_stage * 0.5, 0.12)
	_fade_from_black(0.20)


func _render_room() -> void:
	var room: Dictionary = ROOM_DATA[room_id]
	background.texture = load(room["image"])
	caption_label.text = room["caption"] if game_state == "play" or game_state == "ending" else ""
	prompt_label.text = ""
	_update_creature()


func _update_creature() -> void:
	if game_state != "play" or creature_stage <= 0:
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


func _trigger_jump() -> void:
	game_state = "jump"
	creature_stage = 5
	creature.visible = true
	creature.modulate = Color(1, 0.92, 0.58, 0.96)
	var view := get_viewport_rect().size
	var target_h := view.y * 1.62
	var ratio := float(creature_texture.get_width()) / float(creature_texture.get_height())
	creature.size = Vector2(target_h * ratio, target_h)
	creature.position = Vector2(view.x * 0.5 - creature.size.x * 0.5, view.y * 0.52 - creature.size.y * 0.5)
	caption_label.text = ""
	prompt_label.text = ""
	_shake(28.0, 0.85)
	_play_sound(sting_sound)
	var tween := create_tween()
	tween.set_parallel(true)
	tween.tween_property(creature, "scale", Vector2(1.13, 1.13), 0.16).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_property(black_fade, "color:a", 0.0, 0.05)
	tween.chain().tween_interval(0.55)
	tween.chain().tween_callback(_show_ending)


func _show_ending() -> void:
	game_state = "ending"
	room_id = "other"
	creature.visible = false
	creature.scale = Vector2.ONE
	restart_label.visible = false
	_render_room()
	caption_label.text = "The door was not an exit."
	prompt_label.text = "Another yellow room. Click to restart."
	_fade_from_black(0.7)


func _hotspot_at(screen_pos: Vector2) -> Dictionary:
	var norm := _normalized_position(screen_pos)
	for hotspot in ROOM_DATA[room_id]["hotspots"]:
		var rect: Rect2 = hotspot["rect"]
		if rect.has_point(norm):
			return hotspot
	return {}


func _update_hover(screen_pos: Vector2) -> void:
	if game_state != "play":
		prompt_label.text = ""
		return
	var hotspot := _hotspot_at(screen_pos)
	if hotspot.is_empty():
		hover_prompt = ""
	else:
		hover_prompt = hotspot["prompt"]
	prompt_label.text = hover_prompt


func _normalized_position(screen_pos: Vector2) -> Vector2:
	var view_size := get_viewport_rect().size
	if view_size.x <= 0.0 or view_size.y <= 0.0:
		return Vector2.ZERO
	return Vector2(screen_pos.x / view_size.x, screen_pos.y / view_size.y)


func _flash_caption(text: String) -> void:
	caption_label.text = text
	var timer := get_tree().create_timer(1.25)
	timer.timeout.connect(func() -> void:
		if game_state == "play":
			caption_label.text = ROOM_DATA[room_id]["caption"]
	)


func _fade_from_black(duration: float) -> void:
	black_fade.color.a = 1.0
	var tween := create_tween()
	tween.tween_property(black_fade, "color:a", 0.0, duration).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)


func _shake(power: float, duration: float) -> void:
	shake_power = power
	shake_time = duration


func _play_sound(stream: AudioStream) -> void:
	if stream == null:
		return
	sfx_player.stop()
	sfx_player.stream = stream
	sfx_player.play()
