extends SceneTree

const MAIN_SCENE := "res://scenes/main.tscn"

var game: Node
var failures: Array[String] = []


func _init() -> void:
	call_deferred("_run")


func _run() -> void:
	game = load(MAIN_SCENE).instantiate()
	root.add_child(game)
	await process_frame
	await process_frame

	await _test_lobby_start()
	await _test_ending_menu()
	await _test_c_ending()
	await _test_right_route_peek()
	await _test_right_dead_end_warning_note()
	await _test_right_dead_end_door_block()
	await _test_a_ending()
	await _test_b_ending()

	if failures.is_empty():
		print("QA flow passed: A/B/C routes")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		quit(1)


func _test_lobby_start() -> void:
	_expect_state("lobby", "initial lobby")
	if not game.menu_layer.visible:
		failures.append("initial lobby: menu layer is hidden")
	if game.menu_primary_button.text != "시작":
		failures.append("initial lobby: expected primary button 시작, got %s" % game.menu_primary_button.text)
	game._on_menu_primary_pressed()
	await process_frame
	_expect_state("play", "lobby start button")
	_expect_room("fork_stop", "lobby start room")


func _test_ending_menu() -> void:
	game._reset_game()
	await process_frame
	game._show_ending("A")
	await process_frame
	_expect_ending("A", "A ending menu")
	if not game.menu_layer.visible:
		failures.append("A ending menu: menu layer is hidden")
	if game.menu_primary_button.text != "재시작":
		failures.append("A ending menu: expected primary button 재시작, got %s" % game.menu_primary_button.text)
	if game.menu_secondary_button.text != "종료":
		failures.append("A ending menu: expected secondary button 종료, got %s" % game.menu_secondary_button.text)
	game._on_menu_primary_pressed()
	await process_frame
	_expect_state("lobby", "ending restart returns lobby")
	game._on_menu_primary_pressed()
	await process_frame
	_expect_state("play", "restart lobby start")
	_expect_room("fork_stop", "restart lobby room")
	game._show_ending("B")
	await process_frame
	game._on_menu_secondary_pressed()
	await process_frame
	_expect_state("quit", "ending quit button")
	if game.menu_primary_button.text != "처음으로":
		failures.append("quit menu: expected primary button 처음으로, got %s" % game.menu_primary_button.text)


func _test_c_ending() -> void:
	game._reset_game()
	await process_frame
	_expect_room("fork_stop", "C start")
	await _click_norm(0.50, 0.10)
	_expect_room("stop_back_space", "C first stop back")
	await _click_norm(0.50, 0.90)
	_expect_room("fork_stop", "C back to fork")
	_expect_flag("stop_back_reentry_armed", true, "C reentry armed")
	await _click_norm(0.50, 0.10)
	_expect_ending("C", "C reentry ending")


func _test_a_ending() -> void:
	game._reset_game()
	await process_frame
	await _click_norm(0.12, 0.55)
	await _click_norm(0.45, 0.65)
	await _click_norm(0.43, 0.54)
	await _click_norm(0.50, 0.43)
	await _click_norm(0.50, 0.90)
	await _click_norm(0.50, 0.90)
	await _click_norm(0.50, 0.10)
	_expect_flag("stop_back_red_seen", true, "A red stop back seen")
	await _click_norm(0.50, 0.50)
	_expect_ending("A", "A true exit")


func _test_b_ending() -> void:
	game._reset_game()
	await process_frame
	await _click_norm(0.12, 0.55)
	await _click_norm(0.43, 0.54)
	await _click_norm(0.50, 0.43)
	await _click_norm(0.50, 0.90)
	await _click_norm(0.50, 0.90)
	await _click_norm(0.50, 0.10)
	await _click_norm(0.50, 0.50)
	await _wait_seconds(0.25)
	_expect_state("transition", "B blocked passage transition")
	await _wait_seconds(1.4)
	_expect_ending("B", "B false exit")
	_expect_room("false_exit_room", "B stop sign room")


func _test_right_route_peek() -> void:
	game._reset_game()
	await process_frame
	await _click_norm(0.82, 0.55)
	await _click_norm(0.50, 0.45)
	await _click_norm(0.80, 0.45)
	await _click_norm(0.50, 0.90)
	await _click_norm(0.50, 0.90)
	await _wait_seconds(1.1)
	_expect_flag("panel_clue_clicked", true, "right panel clue")
	_expect_flag("creature_peek_seen", true, "right return creature peek")


func _test_right_dead_end_door_block() -> void:
	game._reset_game()
	await process_frame
	await _click_norm(0.82, 0.55)
	await _click_norm(0.80, 0.45)
	_expect_room("right_dead_end", "blocked door start")
	await _click_norm(0.88, 0.45)
	_expect_room("right_dead_end", "blocked door first warning stays")
	_expect_flag("right_door_warning_seen", true, "blocked door warning flag")
	await _click_norm(0.88, 0.45)
	await _wait_seconds(0.25)
	_expect_state("transition", "right dead end door blocked passage")
	await _wait_seconds(1.4)
	_expect_ending("B", "right dead end door B ending")
	_expect_room("false_exit_room", "right dead end door stop sign room")


func _test_right_dead_end_warning_note() -> void:
	game._reset_game()
	await process_frame
	await _click_norm(0.82, 0.55)
	await _click_norm(0.80, 0.45)
	_expect_room("right_dead_end", "warning note start")
	await _click_norm(0.88, 0.45)
	_expect_flag("right_door_warning_seen", true, "warning note door warning")
	await _click_norm(0.50, 0.90)
	_expect_room("right_panel_path", "warning note back room")
	_expect_flag("right_note_available", true, "warning note available")
	if not "floor_note" in game._active_hotspot_ids():
		failures.append("warning note: floor_note hotspot is not active")
	await _click_norm(0.43, 0.78)
	_expect_state("note", "warning note screen opened")
	if not game.note_layer.visible:
		failures.append("warning note: note layer is hidden")
	_expect_flag("right_note_read", false, "warning note unread while open")
	await _click_norm(0.10, 0.10)
	_expect_state("play", "warning note outside click closes")
	_expect_flag("right_note_read", true, "warning note read after outside click")
	if game.note_layer.visible:
		failures.append("warning note: note layer did not hide")
	if game.note_marker.visible:
		failures.append("warning note: floor note marker did not hide")
	if not game.note_flash.visible:
		failures.append("warning note: note flash image did not show")
	await _wait_seconds(0.58)
	if game.note_flash.visible:
		failures.append("warning note: note flash image did not hide")
	_expect_room("right_panel_path", "warning note remains right panel path")


func _click_norm(x: float, y: float) -> void:
	game.input_cooldown = 0.0
	var size := game.get_viewport().get_visible_rect().size
	game._handle_click(Vector2(size.x * x, size.y * y))
	await process_frame
	await _wait_seconds(0.12)


func _wait_seconds(seconds: float) -> void:
	await create_timer(seconds).timeout


func _expect_room(expected: String, label: String) -> void:
	if game.room_id != expected:
		failures.append("%s: expected room %s, got %s" % [label, expected, game.room_id])


func _expect_flag(flag_name: String, expected: bool, label: String) -> void:
	var actual: bool = bool(game.flags.get(flag_name, false))
	if actual != expected:
		failures.append("%s: expected flag %s=%s, got %s" % [label, flag_name, str(expected), str(actual)])


func _expect_ending(expected: String, label: String) -> void:
	if game.game_state != "ending" or game.ending_id != expected:
		failures.append("%s: expected ending %s, got state=%s ending=%s room=%s" % [label, expected, game.game_state, game.ending_id, game.room_id])


func _expect_state(expected: String, label: String) -> void:
	if game.game_state != expected:
		failures.append("%s: expected state %s, got state=%s ending=%s room=%s" % [label, expected, game.game_state, game.ending_id, game.room_id])
