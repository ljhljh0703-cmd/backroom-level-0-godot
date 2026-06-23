from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DOCS_OUT = ROOT / "docs" / "backroom-portfolio.html"
WEB_OUT = ROOT / "builds" / "web" / "portfolio.html"
REGISTRY_DOCS_OUT = ROOT / "docs" / "backroom-pages-registry.json"
REGISTRY_WEB_OUT = ROOT / "builds" / "web" / "backroom-pages-registry.json"
PAGES_BASE_URL = "https://ljhljh0703-cmd.github.io/backroom-level-0-godot"


IMAGES = {
    "fork": "assets/images/bg_fork_stop.png",
    "left": "assets/images/bg_left_blood_path.png",
    "red": "assets/images/bg_stop_back_red.png",
    "exit": "assets/images/bg_true_exit_room.png",
    "blocked": "assets/images/bg_blocked_passage.png",
    "false": "assets/images/bg_false_exit_room.png",
}


def deployed_game_version() -> str:
    index_html = ROOT / "builds" / "web" / "index.html"
    if not index_html.exists():
        return "latest"
    html = index_html.read_text(encoding="utf-8")
    marker = '"mainPack":"index-'
    start = html.find(marker)
    if start == -1:
        return "latest"
    start += len(marker)
    end = html.find('.pck"', start)
    if end == -1:
        return "latest"
    return html[start:end]


def data_uri(path: str, width: int = 1120, quality: int = 78) -> str:
    source = ROOT / path
    image = Image.open(source).convert("RGB")
    if image.width > width:
        ratio = width / image.width
        image = image.resize((width, int(image.height * ratio)), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True, progressive=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def build_registry(version: str) -> dict:
    return {
        "version": "1.0.0",
        "kind": "github-pages-multi-html-registry",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": "ljhljh0703-cmd/backroom-level-0-godot",
        "pages_base_url": PAGES_BASE_URL,
        "documents": {
            "playable_game": {
                "path": "index.html",
                "url": f"{PAGES_BASE_URL}/?v={version}",
                "role": "Godot Web export, playable prototype",
                "source": "builds/web/index.html",
            },
            "portfolio_case_study": {
                "path": "portfolio.html",
                "url": f"{PAGES_BASE_URL}/portfolio.html?v={version}",
                "role": "portfolio record as one HTML file",
                "source": "docs/backroom-portfolio.html",
            },
        },
    }


def html(version: str, assets: dict[str, str]) -> str:
    generated = datetime.now().strftime("%Y-%m-%d")
    return f"""<!doctype html>
<!--
HTML Publish L0
visual thesis: A restrained case-study page that turns a short Backrooms prototype into proof of design, implementation, QA, and web deployment.
content plan: opener -> design evidence -> route/ending system -> production pipeline -> deployment registry.
system declaration: Single-file HTML, monochrome/yellow/red palette, system fonts, actual game frames embedded as compressed data URIs.
-->
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BackRoom Level 0 - Godot Portfolio Case Study</title>
  <meta name="description" content="2분 내외 포인트앤클릭 백룸 호러 프로토타입의 기획, 구현, 품질 검증(QA), GitHub Pages 배포 기록.">
  <meta property="og:title" content="BackRoom Level 0 - Godot Portfolio Case Study">
  <meta property="og:description" content="짧은 클릭/터치 백룸 호러 프로토타입의 기획, 구현, 검증, 배포 기록.">
  <meta property="og:type" content="website">
  <style>
    :root {{
      color-scheme: dark;
      --bg: black;
      --paper: white;
      --ink: white;
      --muted: silver;
      --dim: gray;
      --line: color-mix(in srgb, white 18%, transparent);
      --panel: color-mix(in srgb, black 76%, white 8%);
      --panel-strong: color-mix(in srgb, black 62%, goldenrod 10%);
      --signal: gold;
      --warning: darkred;
      --warning-soft: color-mix(in srgb, darkred 52%, black);
      --floor: color-mix(in srgb, goldenrod 12%, black);
      --radius: 8px;
      --max: 1180px;
      --font: "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", system-ui, sans-serif;
    }}

    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }}
    body {{
      margin: 0;
      font-family: var(--font);
      background: var(--bg);
      color: var(--ink);
      word-break: keep-all;
      overflow-wrap: anywhere;
    }}
    a {{ color: inherit; text-decoration: none; }}
    img {{ display: block; max-width: 100%; }}
    .shell {{ width: min(var(--max), calc(100% - 40px)); margin: 0 auto; }}

    .hero {{
      min-height: 82svh;
      display: grid;
      align-items: end;
      position: relative;
      background-image: url("{assets['fork']}");
      background-size: cover;
      background-position: center;
      isolation: isolate;
      border-bottom: 1px solid var(--line);
    }}
    .hero::before {{
      content: "";
      position: absolute;
      inset: 0;
      background: color-mix(in srgb, black 56%, transparent);
      z-index: -1;
    }}
    .hero::after {{
      content: "";
      position: absolute;
      inset: auto 0 0 0;
      height: 30%;
      background: color-mix(in srgb, black 72%, transparent);
      z-index: -1;
    }}
    .hero-inner {{
      padding: 84px 0 54px;
      display: grid;
      gap: 28px;
    }}
    .kicker {{
      display: inline-flex;
      width: fit-content;
      align-items: center;
      gap: 10px;
      color: var(--signal);
      font-size: 13px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .kicker::before {{
      content: "";
      width: 10px;
      height: 10px;
      background: var(--warning);
      border-radius: 2px;
      box-shadow: 0 0 18px var(--warning);
    }}
    h1 {{
      margin: 0;
      max-width: 920px;
      font-size: clamp(44px, 8vw, 112px);
      line-height: 0.98;
      letter-spacing: 0;
    }}
    .lead {{
      max-width: 760px;
      margin: 0;
      color: color-mix(in srgb, white 82%, goldenrod 10%);
      font-size: clamp(18px, 2.2vw, 25px);
      line-height: 1.55;
      font-weight: 520;
    }}
    .actions {{ display: flex; flex-wrap: wrap; gap: 12px; }}
    .button {{
      display: inline-flex;
      min-height: 44px;
      align-items: center;
      justify-content: center;
      padding: 12px 18px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      font-weight: 800;
      background: color-mix(in srgb, black 72%, white 7%);
    }}
    .button.primary {{
      color: black;
      background: var(--signal);
      border-color: var(--signal);
    }}

    section {{ padding: 82px 0; border-bottom: 1px solid var(--line); }}
    .section-head {{
      display: grid;
      grid-template-columns: minmax(0, 0.72fr) minmax(280px, 0.28fr);
      gap: 32px;
      align-items: end;
      margin-bottom: 32px;
    }}
    .eyebrow {{
      margin: 0 0 12px;
      color: var(--signal);
      font-size: 12px;
      font-weight: 900;
      text-transform: uppercase;
    }}
    h2 {{
      margin: 0;
      font-size: clamp(30px, 5vw, 62px);
      line-height: 1.05;
      letter-spacing: 0;
    }}
    .section-copy {{
      margin: 0;
      color: var(--muted);
      font-size: 16px;
      line-height: 1.75;
    }}

    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 18px;
      background: var(--panel);
      min-height: 128px;
    }}
    .metric b {{
      display: block;
      font-size: clamp(28px, 4vw, 50px);
      line-height: 1;
      color: var(--signal);
      margin-bottom: 10px;
    }}
    .metric span {{ color: var(--muted); line-height: 1.55; }}

    .frames {{
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 16px;
      align-items: stretch;
    }}
    .frame {{
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--panel);
    }}
    .frame img {{ width: 100%; height: 100%; object-fit: cover; aspect-ratio: 16 / 9; }}
    .frame figcaption {{
      padding: 13px 14px 15px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }}
    .frame.tall img {{ aspect-ratio: 16 / 18.5; }}

    .route {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 10px;
      align-items: stretch;
    }}
    .node {{
      min-height: 138px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 16px;
      background: var(--panel);
      position: relative;
    }}
    .node::after {{
      content: "→";
      position: absolute;
      right: -14px;
      top: 50%;
      translate: 0 -50%;
      color: var(--signal);
      font-weight: 900;
    }}
    .node:last-child::after {{ content: ""; }}
    .node.danger {{ background: var(--warning-soft); }}
    .node strong {{ display: block; margin-bottom: 10px; font-size: 18px; }}
    .node p {{ margin: 0; color: var(--muted); font-size: 14px; line-height: 1.55; }}

    .split {{
      display: grid;
      grid-template-columns: minmax(0, 0.95fr) minmax(320px, 1.05fr);
      gap: 22px;
      align-items: center;
    }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 24px;
      background: var(--panel-strong);
    }}
    .panel h3 {{ margin: 0 0 16px; font-size: 24px; }}
    .panel ul {{ display: grid; gap: 12px; margin: 0; padding: 0; list-style: none; }}
    .panel li {{ color: var(--muted); line-height: 1.65; }}
    .panel li::before {{ content: "■"; color: var(--signal); margin-right: 10px; font-size: 10px; }}

    .registry {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}
    .registry a {{
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 20px;
      background: var(--panel);
    }}
    .registry strong {{ display: block; margin-bottom: 8px; color: var(--signal); }}
    .registry span {{ display: block; color: var(--muted); line-height: 1.6; }}

    footer {{
      padding: 34px 0;
      color: var(--dim);
      font-size: 13px;
    }}
    footer .shell {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }}

    @media (max-width: 860px) {{
      .shell {{ width: min(100% - 28px, var(--max)); }}
      .hero {{ min-height: 76svh; }}
      .hero-inner {{ padding: 70px 0 42px; }}
      .section-head, .frames, .split, .registry {{ grid-template-columns: 1fr; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .route {{ grid-template-columns: 1fr; }}
      .node::after {{ right: 18px; top: auto; bottom: -20px; rotate: 90deg; }}
      .node:last-child::after {{ content: ""; }}
      section {{ padding: 58px 0; }}
    }}
    @media (max-width: 520px) {{
      .metrics {{ grid-template-columns: 1fr; }}
      h1 {{ font-size: clamp(40px, 15vw, 68px); }}
      .lead {{ font-size: 17px; }}
    }}
  </style>
</head>
<body>
  <header class="hero" id="top">
    <div class="shell hero-inner">
      <div class="kicker">Godot Web Prototype · Portfolio Case Study</div>
      <h1>BackRoom Level 0</h1>
      <p class="lead">짧은 클릭/터치 호러 게임을 끝까지 닫은 기록이다. 갈림길, STOP 표지판, 세 갈래 엔딩을 데이터로 관리하고, Godot Web export와 GitHub Pages 배포까지 연결했다.</p>
      <nav class="actions" aria-label="Primary links">
        <a class="button primary" href="./?v={version}">플레이하기</a>
        <a class="button" href="https://github.com/ljhljh0703-cmd/backroom-level-0-godot" target="_blank" rel="noopener">GitHub</a>
        <a class="button" href="./backroom-pages-registry.json">배포 레지스트리</a>
      </nav>
    </div>
  </header>

  <main>
    <section>
      <div class="shell">
        <div class="section-head">
          <div>
            <p class="eyebrow">Scope</p>
            <h2>짧은 게임을 끝까지 닫았다.</h2>
          </div>
          <p class="section-copy">이 페이지는 결과 화면보다 제작 과정을 보여준다. 게임 디자인 문서(GDD), 방 그래프, 클릭 판정, A/B/C 엔딩 품질 검증(QA), Godot Web export, GitHub Pages 배포를 한 작업 단위로 묶었다.</p>
        </div>
        <div class="metrics">
          <div class="metric"><b>8</b><span>8개 방. 좌측 단서, 우측 막다른 길, STOP 뒤 공간, 진짜 출구 방을 JSON 데이터로 관리한다.</span></div>
          <div class="metric"><b>3</b><span>A 진짜 탈출, B 가짜 탈출 후 백룸, C 크리처 사망 엔딩.</span></div>
          <div class="metric"><b>2분</b><span>2분 내외. 가벼운 클릭/터치 플레이 안에서 판단 불안을 만든다.</span></div>
          <div class="metric"><b>QA</b><span>Godot headless 테스트로 A/B/C 대표 루트를 실제 클릭 좌표 기준으로 검증한다.</span></div>
        </div>
      </div>
    </section>

    <section>
      <div class="shell">
        <div class="section-head">
          <div>
            <p class="eyebrow">Player Experience</p>
            <h2>위험해 보이는 길에 이유를 둔다.</h2>
          </div>
          <p class="section-copy">복잡한 조작 대신 선택 압박을 설계했다. 안전해 보이는 오른쪽은 막다른 길이고, 위험해 보이는 왼쪽은 전등 버튼으로 이어진다.</p>
        </div>
        <div class="frames">
          <figure class="frame">
            <img alt="STOP 표지판 갈림길" src="{assets['fork']}">
            <figcaption>첫 갈림길. STOP 뒤 공간, 핏자국이 있는 왼쪽 길, 깨끗해 보이는 오른쪽 길을 한 화면에 둔다.</figcaption>
          </figure>
          <figure class="frame tall">
            <img alt="핏자국을 따라 이어지는 왼쪽 길" src="{assets['left']}">
            <figcaption>왼쪽 길. 위험 신호처럼 보이는 핏자국이 실제 진행 단서가 된다.</figcaption>
          </figure>
        </div>
      </div>
    </section>

    <section>
      <div class="shell">
        <div class="section-head">
          <div>
            <p class="eyebrow">Route Logic</p>
            <h2>엔딩은 상태로 갈린다.</h2>
          </div>
          <p class="section-copy">방 이동은 `data/rooms.json`에 두고, 상태 판정은 `src/Game.gd`에서 처리한다. 루트를 바꿀 때는 데이터부터 수정하고, 회귀는 headless QA로 확인한다.</p>
        </div>
        <div class="route" aria-label="A ending route">
          <div class="node"><strong>왼쪽 길</strong><p>핏자국을 따라 전등 버튼 방으로 들어간다.</p></div>
          <div class="node"><strong>스위치</strong><p>버튼을 누르면 STOP 뒤 공간의 상태가 바뀐다.</p></div>
          <div class="node danger"><strong>STOP 뒤</strong><p>처음에는 어둡고, 스위치 이후 붉게 밝아진다.</p></div>
          <div class="node"><strong>진짜 출구 방</strong><p>밝아진 공간을 누르면 문이 있는 방으로 이동한다.</p></div>
          <div class="node"><strong>A 엔딩</strong><p>마지막으로 문을 클릭해야 탈출한다.</p></div>
        </div>
      </div>
    </section>

    <section>
      <div class="shell split">
        <div>
          <p class="eyebrow">Ending Pressure</p>
          <h2>B 엔딩은 오답 처벌보다 압박에 가깝다.</h2>
          <p class="section-copy">오른쪽 막다른 길의 문은 첫 클릭에서 경고만 준다. 경고를 무시하고 다시 누르면 길목 차단 전환으로 이어진다. 실패 판정보다, 공간과 크리처 압박에 밀려 들어가는 경험을 목표로 했다.</p>
        </div>
        <figure class="frame">
          <img alt="길목이 차단되는 B 엔딩 전환 화면" src="{assets['blocked']}">
          <figcaption>B 엔딩 전환. 길목이 막히고 추격 압박이 시작된다.</figcaption>
        </figure>
      </div>
    </section>

    <section>
      <div class="shell">
        <div class="section-head">
          <div>
            <p class="eyebrow">Production System</p>
            <h2>문서와 코드가 같은 방 그래프를 본다.</h2>
          </div>
          <p class="section-copy">기획 변경은 게임 디자인 문서(GDD), 개발 요구사항, CodeGraph, Progress에 남겼다. 실제 구현은 `data/rooms.json`과 headless QA가 따라가게 했다.</p>
        </div>
        <div class="split">
          <figure class="frame">
            <img alt="붉게 밝아진 STOP 뒤 공간" src="{assets['red']}">
            <figcaption>스위치 이후 STOP 뒤 공간. 텍스트 힌트가 아니라 화면 상태 변화로 다음 행동을 유도한다.</figcaption>
          </figure>
          <div class="panel">
            <h3>검증 루틴</h3>
            <ul>
              <li>`tools/validate_routes.py`로 방, 이동 대상(target), 이벤트(event), 상태 플래그(flag) 누락을 확인한다.</li>
              <li>`tools/qa_game_flow.gd`로 로비, A/B/C 엔딩, 우측 경고 쪽지 흐름을 실제 클릭 좌표로 검증한다.</li>
              <li>`tools/prepare_web_build.py`로 커밋 버전이 붙은 `.pck`를 만들어 GitHub Pages 캐시 문제를 줄인다.</li>
              <li>배포 후 원격 `.pck` SHA-256을 로컬 빌드와 비교한다.</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <section>
      <div class="shell split">
        <div>
          <p class="eyebrow">Final Interaction</p>
          <h2>출구는 마지막 클릭으로 닫는다.</h2>
          <p class="section-copy">밝아진 공간을 눌러도 바로 엔딩이 뜨지 않는다. 먼저 진짜 출구 방으로 이동하고, 그 안의 문을 눌렀을 때 A 엔딩이 열린다.</p>
        </div>
        <figure class="frame">
          <img alt="진짜 출구 방" src="{assets['exit']}">
          <figcaption>true_exit_room. 문 클릭이 A 엔딩의 마지막 입력이다.</figcaption>
        </figure>
      </div>
    </section>

    <section>
      <div class="shell">
        <div class="section-head">
          <div>
            <p class="eyebrow">Deployment Registry</p>
            <h2>한 Pages 배포에 HTML 두 개를 올렸다.</h2>
          </div>
          <p class="section-copy">`gh-pages` 루트에는 게임용 `index.html`과 포트폴리오용 `portfolio.html`이 함께 있다. 같은 저장소와 같은 Pages 배포를 쓰되, URL 경로를 분리해 충돌을 피했다.</p>
        </div>
        <div class="registry">
          <a href="./?v={version}">
            <strong>index.html</strong>
            <span>플레이 가능한 Godot Web export. 버전이 붙은 `.pck`로 브라우저 캐시를 분리한다.</span>
          </a>
          <a href="./portfolio.html?v={version}">
            <strong>portfolio.html</strong>
            <span>기획, 구현, 검증, 배포 과정을 정리한 단일 HTML 파일 사례 기록.</span>
          </a>
        </div>
      </div>
    </section>
  </main>

  <footer>
    <div class="shell">
      <span>BackRoom Level 0 · generated {generated}</span>
      <span>game pack {version}</span>
    </div>
  </footer>
</body>
</html>
"""


def main() -> None:
    version = deployed_game_version()
    assets = {
        name: data_uri(path, width=1280 if name == "fork" else 1000)
        for name, path in IMAGES.items()
    }
    rendered = html(version, assets)
    DOCS_OUT.parent.mkdir(parents=True, exist_ok=True)
    WEB_OUT.parent.mkdir(parents=True, exist_ok=True)
    DOCS_OUT.write_text(rendered, encoding="utf-8")
    WEB_OUT.write_text(rendered, encoding="utf-8")

    registry = build_registry(version)
    REGISTRY_DOCS_OUT.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    REGISTRY_WEB_OUT.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {DOCS_OUT.relative_to(ROOT)}")
    print(f"Wrote {WEB_OUT.relative_to(ROOT)}")
    print(f"Wrote {REGISTRY_DOCS_OUT.relative_to(ROOT)}")
    print(f"Wrote {REGISTRY_WEB_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
