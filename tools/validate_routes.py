from __future__ import annotations

import json
import sys
from collections import deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ROOMS_JSON = ROOT / "data" / "rooms.json"


def resource_exists(path: str) -> bool:
    if not path.startswith("res://"):
        return False
    return (ROOT / path.removeprefix("res://")).exists()


def add_error(errors: list[str], message: str) -> None:
    errors.append(f"ERROR: {message}")


def add_warning(warnings: list[str], message: str) -> None:
    warnings.append(f"WARNING: {message}")


def validate_rect(errors: list[str], room_id: str, hotspot_id: str, rect: Any) -> None:
    if not isinstance(rect, list) or len(rect) != 4:
        add_error(errors, f"{room_id}.{hotspot_id} rect must be a 4-number list")
        return
    for value in rect:
        if not isinstance(value, (int, float)):
            add_error(errors, f"{room_id}.{hotspot_id} rect contains non-number value {value!r}")
            return
    x, y, w, h = [float(value) for value in rect]
    if w <= 0 or h <= 0:
        add_error(errors, f"{room_id}.{hotspot_id} rect must have positive size")
    if x < 0 or y < 0 or x + w > 1.05 or y + h > 1.05:
        add_warning(warnings, f"{room_id}.{hotspot_id} rect extends outside normalized screen bounds")


def main() -> int:
    data = json.loads(ROOMS_JSON.read_text(encoding="utf-8"))
    rooms: dict[str, Any] = data.get("rooms", {})
    start_room = data.get("start_room")
    state_flags = set(data.get("state_flags", []))
    known_events = set(data.get("events", []))
    event_targets: dict[str, list[str]] = data.get("event_targets", {})
    transition_images: dict[str, str] = data.get("transition_images", {})
    ending_rooms = set(data.get("ending_rooms", []))
    errors: list[str] = []
    warnings: list[str] = []

    if start_room not in rooms:
        add_error(errors, f"start_room {start_room!r} is missing")

    for room_id, room in rooms.items():
        image = room.get("image")
        if not isinstance(image, str) or not resource_exists(image):
            add_error(errors, f"{room_id} image is missing: {image!r}")

        foreground = room.get("foreground")
        if foreground is not None and (not isinstance(foreground, str) or not resource_exists(foreground)):
            add_error(errors, f"{room_id} foreground is missing: {foreground!r}")

        for state_name, state_image in room.get("state_images", {}).items():
            if not isinstance(state_image, str) or not resource_exists(state_image):
                add_error(errors, f"{room_id} state image {state_name!r} is missing: {state_image!r}")

        hotspots = room.get("hotspots", [])
        if not isinstance(hotspots, list):
            add_error(errors, f"{room_id} hotspots must be a list")
            continue

        ids_seen: set[str] = set()
        for index, hotspot in enumerate(hotspots):
            hotspot_id = hotspot.get("id", f"#{index}")
            if hotspot_id in ids_seen:
                add_error(errors, f"{room_id} has duplicate hotspot id {hotspot_id!r}")
            ids_seen.add(hotspot_id)
            validate_rect(errors, room_id, str(hotspot_id), hotspot.get("rect"))

            has_target = "target" in hotspot
            has_event = "event" in hotspot
            if has_target == has_event:
                add_error(errors, f"{room_id}.{hotspot_id} must define exactly one of target or event")
            if has_target and hotspot["target"] not in rooms:
                add_error(errors, f"{room_id}.{hotspot_id} target is missing: {hotspot['target']!r}")
            if has_event and hotspot["event"] not in known_events:
                add_error(errors, f"{room_id}.{hotspot_id} event is unknown: {hotspot['event']!r}")

            required_flag = hotspot.get("requires_flag")
            if required_flag is not None and required_flag not in state_flags:
                add_error(errors, f"{room_id}.{hotspot_id} requires unknown flag {required_flag!r}")
            hidden_flag = hotspot.get("hidden_when_flag")
            if hidden_flag is not None and hidden_flag not in state_flags:
                add_error(errors, f"{room_id}.{hotspot_id} hides on unknown flag {hidden_flag!r}")

    reachable: set[str] = set()
    queue: deque[str] = deque([start_room]) if start_room in rooms else deque()
    while queue:
        room_id = queue.popleft()
        if room_id in reachable:
            continue
        reachable.add(room_id)
        room = rooms[room_id]
        for hotspot in room.get("hotspots", []):
            target = hotspot.get("target")
            if target in rooms and target not in reachable:
                queue.append(target)
            event = hotspot.get("event")
            for event_target in event_targets.get(event, []):
                if event_target in rooms and event_target not in reachable:
                    queue.append(event_target)

    unreachable = set(rooms) - reachable
    if unreachable:
        add_error(errors, f"unreachable rooms: {', '.join(sorted(unreachable))}")

    for ending_room in ending_rooms:
        if ending_room not in rooms:
            add_error(errors, f"ending room is missing: {ending_room!r}")

    for transition_name, transition_image in transition_images.items():
        if not isinstance(transition_image, str) or not resource_exists(transition_image):
            add_error(errors, f"transition image {transition_name!r} is missing: {transition_image!r}")

    for message in warnings + errors:
        print(message)

    if errors:
        print(f"Route validation failed with {len(errors)} error(s).")
        return 1

    print(f"Route validation passed: {len(rooms)} rooms, {len(reachable)} reachable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
