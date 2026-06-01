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

	await _test_c_ending()
	await _test_right_route_peek()
	await _test_a_ending()
	await _test_b_ending()

	if failures.is_empty():
		print("QA flow passed: A/B/C routes")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		quit(1)


func _test_c_ending() -> void:
	game._reset_game()
	await process_frame
	_expect_room("fork_stop", "C start")
	await _click_norm(0.50, 0.10)
	_expect_room("stop_back_space", "C first stop back")
	await _click_norm(0.10, 0.50)
	_expect_room("fork_stop", "C back to fork")
	_expect_flag("stop_back_reentry_armed", true, "C reentry armed")
	await _click_norm(0.50, 0.10)
	_expect_ending("C", "C reentry ending")


func _test_a_ending() -> void:
	game._reset_game()
	await process_frame
	await _click_norm(0.12, 0.55)
	await _click_norm(0.45, 0.65)
	await _click_norm(0.76, 0.45)
	await _click_norm(0.50, 0.43)
	await _click_norm(0.10, 0.50)
	await _click_norm(0.10, 0.50)
	await _click_norm(0.50, 0.10)
	_expect_flag("stop_back_red_seen", true, "A red stop back seen")
	await _click_norm(0.50, 0.50)
	_expect_ending("A", "A true exit")


func _test_b_ending() -> void:
	game._reset_game()
	await process_frame
	await _click_norm(0.12, 0.55)
	await _click_norm(0.76, 0.45)
	await _click_norm(0.50, 0.43)
	await _click_norm(0.10, 0.50)
	await _click_norm(0.10, 0.50)
	await _click_norm(0.50, 0.10)
	await _click_norm(0.50, 0.50)
	await _wait_seconds(0.9)
	_expect_ending("B", "B false exit")
	_expect_room("false_exit_room", "B stop sign room")


func _test_right_route_peek() -> void:
	game._reset_game()
	await process_frame
	await _click_norm(0.82, 0.55)
	await _click_norm(0.50, 0.45)
	await _click_norm(0.80, 0.45)
	await _click_norm(0.10, 0.50)
	await _click_norm(0.10, 0.50)
	await _wait_seconds(1.1)
	_expect_flag("panel_clue_clicked", true, "right panel clue")
	_expect_flag("creature_peek_seen", true, "right return creature peek")


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
