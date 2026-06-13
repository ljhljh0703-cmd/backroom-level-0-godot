# CodeGraph

이 문서는 현재 프로토타입의 코드/데이터 연결 구조를 빠르게 파악하기 위한 지도다.

## Runtime Graph

```mermaid
flowchart TD
    project["project.godot"] --> scene["scenes/main.tscn"]
    scene --> game["src/Game.gd"]

    game --> roomData["data/rooms.json"]
    game --> nodes["_build_nodes()"]
    game --> assets["_load_assets()"]
    game --> input["_input()"]
    game --> frame["_process()"]

    assets --> render["_render_room()"]
    roomData --> render
    input --> click["_handle_click()"]
    click --> hotspot["_hotspot_at()"]
    hotspot --> goRoom["_go_to_room()"]
    hotspot --> event["_handle_event()"]

    goRoom --> render
    goRoom --> peek["_show_stop_sign_creature_peek()"]
    event --> caption["_flash_caption()"]
    event --> ending["_show_ending()"]

    requirements["docs/DEV_REQUIREMENTS.md"] --> roomData
    roomData --> validation["tools/validate_routes.py"]
    game --> qa["tools/qa_game_flow.gd"]
    generator["tools/generate_assets.py"] --> images["assets/images/*.png"]
    generator --> audio["assets/audio/*.wav"]
    images --> assets
    audio --> assets
```

## 파일 역할

| 파일 | 역할 | 수정할 때 |
| --- | --- | --- |
| `src/Game.gd` | 게임 루프, JSON 방 데이터 로딩, 상태 플래그, 엔딩 분기, UI 레이어, 오디오 재생. | 상태 로직, 엔딩 처리, 디버그 표시, 공통 입력 처리 수정. |
| `data/rooms.json` | 방 그래프, 이미지, 핫스팟, 캡션, 이벤트 target, 크리처 beat 데이터. | 방 이동, 클릭 영역, 문구, 크리처 등장 타이밍 수정. |
| `docs/DEV_REQUIREMENTS.md` | GDD 승인 후 route graph, hotspot, state flag, event/ending 조건을 구현 기준으로 고정. | 구현 전에 방/상태/엔딩 조건을 바꿀 때. |
| `tools/validate_routes.py` | JSON 방 그래프의 누락 target/image, unknown event/flag, 도달 불가능 방 검사. | 방 데이터 수정 후. |
| `tools/qa_game_flow.gd` | Godot headless에서 A/B/C 주요 루트를 실제 클릭 좌표로 자동 검증. | 상태 로직이나 핫스팟 수정 후. |
| `tools/generate_assets.py` | 블록아웃 이미지, STOP 표지 전경, 오버레이, 임시 오디오 생성. | 블록아웃 배치 변경 또는 최종 배경 일괄 생성. |
| `tools/prepare_web_build.py` | Web export 후 commit-suffixed `.pck`를 만들고 `index.html`의 `mainPack`을 갱신. | GitHub Pages/browser 캐시가 오래된 `index.pck`를 줄 때. |
| `assets/images/*.png` | 생성/교체되는 방 이미지와 오버레이. | 레이아웃 승인 뒤 최종 비주얼 패스 적용. |
| `assets/audio/*.wav` | 임시 앰비언스와 효과음. | 사운드 패스에서 교체 또는 튜닝. |
| `scenes/main.tscn` | `Game.gd`가 붙은 최소 루트 씬. | UI를 씬 노드로 분리할 때만 수정. |
| `project.godot` | 앱 설정, 해상도, 스트레치, 렌더러, 아이콘. | 프로젝트 설정 변경. |
| `export_presets.cfg` | Web export 프리셋. | 배포/export 설정 변경. |

## Hot Edit Map

수정 전 이 표에서 먼저 수정 위치를 잡는다.

| 목표 | 1차 수정 위치 | 같이 확인할 위치 |
| --- | --- | --- |
| 방 추가/삭제 | `data/rooms.json`의 `rooms` | `tools/generate_assets.py`의 `scene_*()`와 출력 키, `tools/validate_routes.py` |
| 클릭 영역 변경 | `data/rooms.json`의 `hotspots[].rect` | debug hotspot overlay, `tools/qa_game_flow.gd` |
| GDD v2 route 변경 | `docs/DEV_REQUIREMENTS.md` | `data/rooms.json`, route validation |
| 방 캡션 변경 | `data/rooms.json`의 `caption`/`red_caption` | 동적 캡션은 `_room_caption()` |
| 조사 문구 변경 | `_handle_event()`, `_repeat_event_line()` | `data/rooms.json`의 `event` id |
| 방 이동 조건 변경 | `_go_to_room()` | `data/rooms.json`의 hotspot target |
| 우측 복귀 크리처 등장 타이밍 변경 | `data/rooms.json`의 `creature_beats.right_return_peek` | `_show_stop_sign_creature_peek()` |
| 이후 크리처 접근감 변경 | `data/rooms.json`의 `creature_beats` | `_show_creature_beat()`와 엔딩 연출 |
| B 엔딩 전 길목 차단 frame 변경 | `data/rooms.json`의 `transition_images.blocked_passage`, `tools/generate_assets.py`의 `scene_blocked_passage()` | `_show_blocked_passage_transition()` |
| 엔딩 분기 변경 | `_attempt_exit()`, `_show_ending()` | `data/rooms.json`의 `event_targets.attempt_exit` |
| 전체 시각 스타일 변경 | `tools/generate_assets.py`의 상수/그리기 함수 | `assets/images/*.png` 재생성 |
| 최종 이미지 교체 | `assets/images/*.png` 파일 교체 | 파일명을 유지하면 `data/rooms.json` 수정 불필요 |

## Current Room Graph

```mermaid
flowchart LR
    fork_stop["fork_stop\nSTOP 갈림길"] --> stop_back_space["stop_back_space\n어두운/붉은 STOP 뒤 공간"]
    stop_back_space --> fork_stop
    stop_back_space --> true_exit_room["true_exit_room\nA 엔딩"]
    stop_back_space --> false_exit_room["false_exit_room\nB 엔딩"]

    fork_stop --> left_blood_path["left_blood_path\n붉은 흔적"]
    left_blood_path --> left_switch_room["left_switch_room\n전등 버튼"]
    left_switch_room --> left_blood_path
    left_blood_path --> fork_stop

    fork_stop --> right_panel_path["right_panel_path\n인간형 판넬"]
    right_panel_path --> right_dead_end["right_dead_end\n막다른 길"]
    right_dead_end --> right_panel_path
    right_dead_end -. "오른쪽 문" .-> blocked_passage["blocked_passage\n전환 화면"]
    blocked_passage -. "크리처 추격" .-> false_exit_room
    right_panel_path --> fork_stop

    stop_back_space -. "연속 재진입" .-> ending_c["C 엔딩"]
```

현재 그래프는 `data/rooms.json` 기준이며 `tools/validate_routes.py`에서 8개 방 도달 가능성을 검사한다.

## Target Room Graph

GDD v2 승인 후 구현 목표 그래프다. 상세 조건은 `docs/DEV_REQUIREMENTS.md`가 기준이다.

```mermaid
flowchart TD
    fork_stop["fork_stop\nSTOP 갈림길"] --> stop_back_space["stop_back_space\n어두운/붉은 STOP 뒤 공간"]
    stop_back_space --> fork_stop
    stop_back_space --> true_exit_room["true_exit_room\nA 엔딩"]
    stop_back_space --> false_exit_room["false_exit_room\nB 엔딩"]

    fork_stop --> left_blood_path["left_blood_path\n붉은 흔적"]
    left_blood_path --> left_switch_room["left_switch_room\n전등 버튼"]
    left_switch_room --> left_blood_path
    left_blood_path --> fork_stop

    fork_stop --> right_panel_path["right_panel_path\n인간형 판넬"]
    right_panel_path --> right_dead_end["right_dead_end\n막다른 길"]
    right_dead_end --> right_panel_path
    right_dead_end -. "오른쪽 문" .-> blocked_passage["blocked_passage\n전환 화면"]
    blocked_passage -. "크리처 추격" .-> false_exit_room
    right_panel_path --> fork_stop

    stop_back_space -. "연속 재진입" .-> ending_c["C 엔딩"]
```

## State Graph

| 상태 | 변수 | 의미 |
| --- | --- | --- |
| 현재 방 | `room_id` | `data/rooms.json`의 room key. |
| 게임 모드 | `game_state` | 현재는 `play`, `transition`, `ending`. |
| 진행 횟수 | `move_count` | 방 이동 횟수. 동적 캡션에 사용. |
| 크리처 접근 단계 | `creature_stage` | 크리처 표시/접근감 단계. 현재 자동 증가 대부분 비활성. |
| STOP 등장 가드 | `creature_peek_seen`, `creature_peek_active` | STOP 표지 뒤 첫 등장 1회 제한. |
| 조사 반복 | `clicked_events` | 같은 조사 이벤트 반복 시 다른 문구 출력. |

v2 상태:

| 상태 | 변수 | 의미 |
| --- | --- | --- |
| STOP 뒤 연속 재진입 | `stop_back_reentry_armed` | `fork_stop -> stop_back_space -> fork_stop -> stop_back_space` C 엔딩 판정. |
| 좌측 버튼 | `light_switch_pressed` | STOP 뒤 공간을 붉은 상태로 바꿈. |
| 붉은 STOP 뒤 확인 | `stop_back_red_seen` | A/B 출구 판정에 사용. |
| 붉은 흔적 단서 | `blood_trace_clicked` | A 엔딩 필수 단서. |
| 인간형 판넬 단서 | `panel_clue_clicked` | 우측 루트 위화감/크리처 노출 단서. A 엔딩 필수 조건에서는 제외. |
| 우측 막다른 길 방문 | `right_dead_end_seen` | 복귀 판넬 소리와 크리처 1초 등장 조건. |
| 판넬 소리 1회 제한 | `panel_sound_played` | 우측 복귀 사운드 중복 방지. |
| 엔딩 분기 | `ending_id` | A/B/C 결과 표시. |

## Validation

```mermaid
flowchart LR
    rooms["data/rooms.json"] --> routeVal["python3 tools/validate_routes.py"]
    game["src/Game.gd"] --> qa["godot --headless --path . --script tools/qa_game_flow.gd"]
    routeVal --> export["Godot Web export"]
    qa --> export
```

현재 고정 검증:

- `tools/validate_routes.py`: 8개 방, 이미지, target, event, flag 검증.
- `tools/qa_game_flow.gd`: C 연속 재진입, A 진짜 출구, B 가짜 출구 루트 검증.
- B 루트 QA는 `blocked_passage` transition 상태를 거친 뒤 `false_exit_room`으로 들어가는지 확인한다.
- 우측 막다른 길 QA는 `right_dead_end`의 오른쪽 문 클릭이 `blocked_passage` transition을 거쳐 B 엔딩으로 이어지는지 확인한다.

## Asset Pipeline

```mermaid
flowchart TD
    edit["Edit tools/generate_assets.py"] --> gen["python3 tools/generate_assets.py"]
    gen --> png["assets/images/*.png"]
    gen --> wav["assets/audio/*.wav"]
    png --> import["godot --headless --path . --import"]
    wav --> import
    import --> export["godot --headless --path . --export-release Web builds/web/index.html"]
    export --> prepare["python3 tools/prepare_web_build.py"]
    prepare --> pages["Deploy builds/web to gh-pages"]
```

현재 원칙: 방 흐름과 오브젝트 위치가 승인되기 전까지 이미지는 블록아웃으로 유지한다. 최종 스타일은 방별로 따로 다듬지 말고 한 번에 적용한다.

## 리팩터링 후보

흐름이 안정된 뒤 적용하면 수정 효율이 올라가는 항목이다.

1. `data/rooms.json`을 Godot `Resource` 또는 여러 JSON으로 분리.
2. 크리처 beat를 여러 개로 확장하고 validation 대상에 포함.
3. 렌더링/UI 생성과 스토리 상태 로직 분리.
4. B 엔딩 추격 연출을 별도 beat runner로 분리.
5. 이미지 shot list와 hotspot 데이터를 함께 검토하는 preview tooling 추가.
