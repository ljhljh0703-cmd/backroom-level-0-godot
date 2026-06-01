# Progress

기획, 구현, 피드백, 회고를 이어가기 위한 작업 기록이다.

## 현재 작업 원칙

방 흐름과 상호작용 구조가 승인되기 전에는 시각 디테일을 다듬지 않는다.

현재 시각 단계: 블록아웃 placeholder.

검토 대상:

- 방 순서
- 문과 갈림길
- 클릭 영역
- 크리처 등장 타이밍
- 엔딩 경로
- 캡션과 조사 이벤트

최종 배경 스타일은 나중에 한 번에 일관되게 적용한다.

## 현재 빌드

- 플레이어블 배포 커밋: `183c17f`
- 배포 URL: `https://ljhljh0703-cmd.github.io/backroom-level-0-godot/?v=183c17f`
- Godot: `4.6`
- 배포 형식: GitHub Pages Web export
- 현재 단계: flow/blockout review

## 결정 기록

| 날짜 | 결정 | 이유 |
| --- | --- | --- |
| 2026-06-01 | Godot Web export와 GitHub Pages 사용. | 링크 기반 외부 배포가 필요함. |
| 2026-06-01 | 2분 이내의 짧은 포인트앤클릭 백룸 어드벤처. | 범위 통제. |
| 2026-06-01 | 첫 화면에서 `LEVEL 0` 같은 타이틀 제거. | 즉시 진입하는 느낌이 더 적합함. |
| 2026-06-01 | 첫 검토 구조를 STOP 표지 갈림길로 설정. | 문처럼 보이지 않는 좌우 선택을 명확히 하기 위해. |
| 2026-06-01 | 두 번째 방에서는 크리처 미등장. | 초반 노출이 너무 빠름. |
| 2026-06-01 | 한쪽 길에 들어갔다가 STOP 갈림길로 돌아오면 크리처가 1초 등장. | 지연된 인지와 초반 긴장감을 만들기 위해. |
| 2026-06-01 | 상세 배경 시안을 버리고 블록아웃으로 회귀. | 이미지 디테일 피드백이 비효율적이었고, 구조 승인부터 필요함. |

## 고도화 방향

### 1. 방 흐름을 데이터 중심으로 분리

목표: 루트 수정이 게임 로직 수정이 아니라 데이터 수정으로 끝나게 한다.

권장 작업:

- `src/Game.gd`의 `ROOM_DATA`를 `rooms.json` 또는 Godot `Resource`로 분리.
- 방 데이터 필드 표준화: `id`, `image`, `foreground`, `caption`, `hotspots`, `tags`, `entry_events`.
- 누락 target, 누락 이미지, 중복 id, 도달 불가능 방을 검사하는 validation 스크립트 추가.

효과: 루트 수정 속도가 빨라지고 실수로 끊긴 방을 줄일 수 있다.

### 2. 리뷰용 hotspot overlay 추가

목표: 클릭 영역 피드백을 감으로 하지 않게 한다.

권장 작업:

- 개발용 토글로 hotspot 사각형과 label 표시.
- 현재 `room_id`, `move_count`, `creature_stage`, 주요 flag를 화면 구석에 표시.
- 릴리즈에서는 숨기거나 debug flag 뒤에 둔다.

효과: "왼쪽 길 클릭 영역이 너무 넓다" 같은 피드백을 바로 코드 수정으로 연결할 수 있다.

### 3. 크리처 타이밍을 방 이동 로직에서 분리

목표: 크리처 연출을 데이터로 조절한다.

권장 작업:

- `creature_beats` 테이블 추가.
- 각 beat에 trigger condition, room id, delay, duration, screen position, alpha/scale, sound/shake를 기록.
- 현재 STOP 표지 뒤 1초 등장을 beat 1로 둔다.
- 이후 등장은 방 흐름 승인 뒤 추가한다.

효과: 연출 타이밍을 코드 수정 없이 조절할 수 있다.

### 4. 2분짜리 플레이를 beat 단위로 설계

목표: 짧은 게임의 밀도를 통제한다.

| Beat | 목표 시간 | 목적 |
| --- | ---: | --- |
| 첫 갈림길 | 10-20초 | STOP, 좌우 선택, 빨간 흔적 인지. |
| 첫 경로 | 15-25초 | 크리처 없이 단서 조사. |
| 복귀 등장 | 5-8초 | STOP 표지 뒤 첫 크리처 등장. |
| 깊은 경로 | 30-45초 | hallway/junction/sign으로 진행. |
| 출구 미끼 | 20-30초 | EXIT sign과 final door. |
| 엔딩 | 10-15초 | 점프/가짜 출구/루프. |

효과: 2분 이내 스코프를 유지할 수 있다.

### 5. 최종 아트는 일괄 적용

목표: 방마다 톤이 흔들리지 않게 한다.

권장 프로세스:

- 모든 방 layout을 블록아웃으로 승인.
- `ROOM_DATA` 기준으로 shot list 작성.
- 같은 스타일 기준으로 모든 배경을 한 번에 생성/교체.
- 파일명은 `bg_start.png`, `bg_left_path.png`처럼 유지.
- 전체 이미지 교체 후 캡션, 오디오, 크리처 위치만 튜닝.

효과: 방별 시각 스타일 편차를 줄인다.

### 6. 배포 전 경량 QA 고정

목표: Pages 배포와 루트 오류를 줄인다.

체크리스트:

- `python3 tools/generate_assets.py`
- `godot --headless --path . --import`
- `godot --headless --path . --export-release Web builds/web/index.html`
- local web build 열기
- 첫 방, 왼쪽 길, 오른쪽 길, 복귀 등장 확인
- `builds/web`를 `gh-pages`에 배포
- 배포된 `index.pck` hash와 local export hash 비교

## 현재 구현 메모

- `src/Game.gd`는 아직 단일 파일 프로토타입이다.
- `ROOM_DATA`가 현재 방 그래프와 hotspot의 중심이다.
- 이미지는 `tools/generate_assets.py`로 생성한다.
- 현재 배경은 개발용 블록아웃 label을 좌상단에 포함한다.
- `hallway`, `junction`, `sign`, `door`, `other`는 존재하지만 현재 첫 루프에서 전체 시퀀스가 자연스럽게 열리지는 않는다. 다음 구현 전에 루트 확정이 필요하다.

## 다음 리뷰 질문

추가 구현 전에 답해야 할 질문:

1. 첫 STOP 갈림길에서 바로 깊은 루트로 진행 가능해야 하는가, 아니면 첫 루프는 teaser인가?
2. 왼쪽과 오른쪽 길 모두 진행 루트인가, 아니면 한쪽은 dead-end/reveal 루트인가?
3. STOP 표지 뒤 크리처 등장 후 무엇이 열리거나 바뀌는가?
4. final door는 명확히 보이는 목표인가, 단서 조사 후 열리는 목표인가?
5. 캡션은 영어로 유지할지, 한국어로 바꿀지, 거의 없앨지?

## 다음 추천 작업 패킷

가장 작은 유효 작업 단위:

1. start에서 ending까지의 playable route graph 확정.
2. 그 route가 실제 `ROOM_DATA`에서 도달 가능하도록 수정.
3. hotspot debug overlay 추가.
4. route validation script 추가.
5. blockout build 재배포 후 리뷰.

이 항목이 승인되기 전까지 최종 배경 작업은 시작하지 않는다.

## Change Log

| Commit | 요약 |
| --- | --- |
| `183c17f` | 상세 배경을 버리고 구조 검토용 블록아웃으로 전환. |
| `acedfef` | reference-style 배경 시도. 이후 블록아웃 결정으로 대체됨. |
| `866c9f9` | STOP 표지 갈림길 피드백과 첫 크리처 등장 지연 반영. |
