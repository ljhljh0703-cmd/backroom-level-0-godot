#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
from datetime import datetime
from io import BytesIO
from pathlib import Path
from string import Template

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BUILD_WEB = ROOT / "builds" / "web"
PAGES_BASE_URL = "https://ljhljh0703-cmd.github.io/backroom-level-0-godot"

ASSETS = {
    "fork": ROOT / "assets" / "images" / "bg_fork_stop.png",
    "left": ROOT / "assets" / "images" / "bg_left_path.png",
    "red": ROOT / "assets" / "images" / "bg_stop_back_red.png",
    "exit": ROOT / "assets" / "images" / "bg_true_exit_room.png",
    "blocked": ROOT / "assets" / "images" / "bg_blocked_passage.png",
    "false_end": ROOT / "assets" / "images" / "bg_false_exit_room.png",
}


def deployed_game_version() -> str:
    index_html = BUILD_WEB / "index.html"
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


def data_uri(path: Path, width: int = 1200) -> str:
    with Image.open(path) as source:
        image = source.convert("RGB")
        if image.width > width:
            ratio = width / image.width
            image = image.resize((width, int(image.height * ratio)), Image.Resampling.LANCZOS)

        buffer = BytesIO()
        image.save(buffer, format="WEBP", quality=74, method=6)

    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/webp;base64,{encoded}"


def build_html(version: str, assets: dict[str, str]) -> str:
    generated = datetime.now().strftime("%Y-%m-%d")
    template = Template(
        r"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>BackRoom Level 0 | Short Backrooms Horror Game</title>
  <meta name="description" content="BackRoom Level 0 is a short Godot Web horror game about a STOP sign, looping rooms, and three endings." />
  <meta property="og:title" content="BackRoom Level 0 | Portfolio Case Study" />
  <meta property="og:description" content="A short Backrooms-inspired horror game. Enter the space behind the STOP sign, read the room changes, and find one of three endings." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="$base_url" />
  <meta name="theme-color" content="#f5f1e8" />
  <style>
    :root {
      color-scheme: light;
      --paper: #f5f1e8;
      --ink: #161410;
      --muted: #625d53;
      --soft: #e8e1d2;
      --line: #c9bfae;
      --panel: #fffaf0;
      --night: #111111;
      --danger: #b9241f;
      --amber: #c2871a;
      --blue: #0064ff;
      --green: #4d6f54;
      --radius: 8px;
      --maxw: 1120px;
      --shadow: 0 18px 44px rgba(22, 20, 16, .14);
      font-family: "IBM Plex Sans KR", "Noto Sans KR", Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }

    * {
      box-sizing: border-box;
    }

    html {
      scroll-behavior: smooth;
      background: var(--paper);
    }

    body {
      margin: 0;
      color: var(--ink);
      background:
        linear-gradient(90deg, rgba(22, 20, 16, .045) 1px, transparent 1px),
        linear-gradient(180deg, rgba(22, 20, 16, .035) 1px, transparent 1px),
        var(--paper);
      background-size: 96px 96px, 96px 96px, auto;
      line-height: 1.6;
      overflow-x: hidden;
    }

    a {
      color: inherit;
      text-decoration: none;
    }

    img {
      display: block;
      max-width: 100%;
    }

    .progress {
      position: fixed;
      z-index: 90;
      top: 0;
      left: 0;
      width: 100%;
      height: 3px;
      background: rgba(22, 20, 16, .08);
    }

    .progress-bar {
      width: 0;
      height: 100%;
      background: linear-gradient(90deg, var(--danger), var(--amber));
    }

    .site-nav {
      position: sticky;
      z-index: 80;
      top: 0;
      border-bottom: 1px solid rgba(22, 20, 16, .12);
      background: rgba(245, 241, 232, .88);
      backdrop-filter: blur(18px);
    }

    .nav-inner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      width: min(calc(100% - 32px), var(--maxw));
      margin: 0 auto;
      padding: 12px 0;
    }

    .brand {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      min-width: max-content;
      font-weight: 800;
      letter-spacing: 0;
    }

    .brand-mark {
      width: 14px;
      height: 14px;
      border: 2px solid var(--ink);
      background: var(--danger);
      box-shadow: 4px 4px 0 var(--amber);
      transform: rotate(45deg);
    }

    .nav-links {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 4px;
      flex-wrap: wrap;
      max-width: 100%;
      font-size: 13px;
      color: var(--muted);
    }

    .nav-links a {
      padding: 7px 10px;
      border-radius: 999px;
    }

    .nav-links a:hover {
      background: rgba(22, 20, 16, .08);
      color: var(--ink);
    }

    .nav-cta {
      color: #fff !important;
      background: var(--ink) !important;
    }

    .hero {
      position: relative;
      isolation: isolate;
      min-height: 80svh;
      display: grid;
      align-items: end;
      overflow: hidden;
      color: #fff7e8;
      background: var(--night);
    }

    .hero::before {
      content: "";
      position: absolute;
      inset: 0;
      z-index: -2;
      background:
        linear-gradient(90deg, rgba(17, 17, 17, .94) 0%, rgba(17, 17, 17, .78) 39%, rgba(17, 17, 17, .24) 100%),
        linear-gradient(180deg, rgba(17, 17, 17, .1) 0%, rgba(17, 17, 17, .92) 100%),
        url("$fork") center / cover no-repeat;
      transform: scale(1.02);
    }

    .hero::after {
      content: "";
      position: absolute;
      inset: 0;
      z-index: -1;
      opacity: .2;
      background:
        linear-gradient(90deg, rgba(255, 255, 255, .18) 1px, transparent 1px),
        linear-gradient(180deg, rgba(255, 255, 255, .15) 1px, transparent 1px);
      background-size: 72px 72px;
      mix-blend-mode: screen;
    }

    .hero-inner {
      width: min(calc(100% - 32px), var(--maxw));
      margin: 0 auto;
      padding: 86px 0 54px;
    }

    .eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 16px;
      color: #f7cf74;
      font: 700 12px/1 "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
      text-transform: uppercase;
      letter-spacing: 0;
    }

    .eyebrow::before {
      content: "";
      width: 38px;
      height: 1px;
      background: currentColor;
    }

    h1 {
      max-width: 850px;
      margin: 0;
      font-size: clamp(46px, 8vw, 108px);
      line-height: .92;
      letter-spacing: 0;
      overflow-wrap: anywhere;
    }

    .hero-copy {
      max-width: 680px;
      margin: 24px 0 0;
      color: rgba(255, 247, 232, .86);
      font-size: clamp(17px, 2vw, 22px);
      overflow-wrap: anywhere;
    }

    .hero-brief {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 1px;
      max-width: 860px;
      margin-top: 28px;
      border: 1px solid rgba(255, 247, 232, .24);
      background: rgba(255, 247, 232, .2);
    }

    .hero-brief div {
      min-width: 0;
      min-height: 128px;
      padding: 18px;
      background: rgba(17, 17, 17, .7);
    }

    .hero-brief span {
      color: #f7cf74;
      font: 800 12px/1 "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
      text-transform: uppercase;
    }

    .hero-brief strong {
      display: block;
      margin-top: 10px;
      color: #fff7e8;
      font-size: 20px;
      line-height: 1.25;
      overflow-wrap: anywhere;
    }

    .hero-brief p {
      margin: 9px 0 0;
      color: rgba(255, 247, 232, .72);
      font-size: 14px;
      overflow-wrap: anywhere;
    }

    .hero-actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 30px;
    }

    .button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      min-height: 44px;
      padding: 10px 15px;
      border: 1px solid currentColor;
      border-radius: var(--radius);
      font-weight: 800;
      line-height: 1.1;
    }

    .button.primary {
      color: var(--night);
      border-color: #f7cf74;
      background: #f7cf74;
    }

    .button.secondary {
      color: #fff7e8;
      border-color: rgba(255, 247, 232, .46);
      background: rgba(255, 247, 232, .06);
    }

    .hero-strip {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 1px;
      margin-top: 52px;
      border: 1px solid rgba(255, 247, 232, .22);
      background: rgba(255, 247, 232, .2);
    }

    .hero-stat {
      min-height: 100px;
      padding: 18px;
      background: rgba(17, 17, 17, .68);
    }

    .hero-stat strong {
      display: block;
      font: 800 32px/1 "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
      color: #fff7e8;
      overflow-wrap: anywhere;
    }

    .hero-stat span {
      display: block;
      margin-top: 8px;
      color: rgba(255, 247, 232, .72);
      font-size: 13px;
    }

    .quick-read {
      display: grid;
      grid-template-columns: .78fr 1.22fr;
      gap: 18px;
      align-items: stretch;
    }

    .brief-card {
      padding: 22px;
    }

    .brief-card h3,
    .signal-card h3,
    .path-card h3 {
      margin: 0;
      font-size: 22px;
      line-height: 1.18;
      letter-spacing: 0;
    }

    .brief-card p,
    .signal-card p,
    .path-card p {
      margin: 10px 0 0;
      color: var(--muted);
      font-size: 15px;
      overflow-wrap: anywhere;
    }

    .brief-card .tag,
    .signal-card .tag,
    .path-card .tag {
      display: inline-flex;
      margin-bottom: 14px;
      color: var(--blue);
      font: 800 12px/1 "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
      text-transform: uppercase;
    }

    .fact-list {
      display: grid;
      margin: 0;
      padding: 0;
      list-style: none;
    }

    .fact-list li {
      display: grid;
      grid-template-columns: 150px 1fr;
      gap: 20px;
      padding: 15px 18px;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 250, 240, .74);
    }

    .fact-list li:first-child {
      border-top-left-radius: var(--radius);
      border-top-right-radius: var(--radius);
    }

    .fact-list li:last-child {
      border-bottom: 0;
      border-bottom-left-radius: var(--radius);
      border-bottom-right-radius: var(--radius);
    }

    .fact-list strong {
      font-size: 14px;
    }

    .fact-list span {
      color: var(--muted);
      font-size: 14px;
    }

    main {
      overflow: hidden;
    }

    section {
      padding: 92px 0;
      border-top: 1px solid rgba(22, 20, 16, .1);
    }

    .wrap {
      width: min(calc(100% - 32px), var(--maxw));
      margin: 0 auto;
    }

    .section-head {
      display: grid;
      grid-template-columns: minmax(0, .85fr) minmax(280px, .45fr);
      gap: 42px;
      align-items: end;
      margin-bottom: 34px;
    }

    .kicker {
      margin: 0 0 9px;
      color: var(--danger);
      font: 800 12px/1.1 "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
      text-transform: uppercase;
    }

    h2 {
      margin: 0;
      font-size: clamp(31px, 4.5vw, 56px);
      line-height: 1.02;
      letter-spacing: 0;
      overflow-wrap: anywhere;
    }

    .section-head p,
    .lead {
      margin: 0;
      color: var(--muted);
      font-size: 17px;
      overflow-wrap: anywhere;
    }

    .grid {
      display: grid;
      gap: 16px;
    }

    .grid.three {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .grid.two {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .card {
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: rgba(255, 250, 240, .72);
      box-shadow: 0 1px 0 rgba(255, 255, 255, .7) inset;
    }

    .metric-card {
      padding: 20px;
    }

    .metric-card .label {
      color: var(--muted);
      font-size: 13px;
    }

    .metric-card strong {
      display: block;
      margin-top: 8px;
      font-size: 29px;
      line-height: 1.05;
    }

    .metric-card p {
      margin: 12px 0 0;
      color: var(--muted);
      font-size: 14px;
    }

    .signal-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
      margin-top: 16px;
    }

    .signal-card,
    .path-card {
      padding: 20px;
    }

    .path-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
      margin-top: 18px;
    }

    .path-card {
      min-height: 210px;
    }

    .path-card .room {
      display: block;
      margin-top: 14px;
      color: var(--muted);
      font: 700 12px/1.4 "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
    }

    .media-grid {
      display: grid;
      grid-template-columns: 1.1fr .9fr;
      gap: 18px;
      align-items: stretch;
    }

    .frame {
      position: relative;
      min-height: 430px;
      overflow: hidden;
      border-radius: var(--radius);
      background: var(--night);
      box-shadow: var(--shadow);
    }

    .frame.small {
      min-height: 206px;
    }

    .frame img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      filter: saturate(.95) contrast(1.05);
    }

    .frame figcaption {
      position: absolute;
      left: 16px;
      right: 16px;
      bottom: 16px;
      padding: 10px 12px;
      border: 1px solid rgba(255, 247, 232, .22);
      border-radius: var(--radius);
      color: #fff7e8;
      background: rgba(17, 17, 17, .72);
      font-size: 13px;
    }

    .caption-stack {
      display: grid;
      gap: 18px;
    }

    .route-list {
      display: grid;
      gap: 10px;
      margin: 0;
      padding: 0;
      list-style: none;
    }

    .route-list li {
      display: grid;
      grid-template-columns: 42px 1fr;
      gap: 14px;
      align-items: start;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: rgba(255, 250, 240, .74);
    }

    .route-list b {
      display: grid;
      place-items: center;
      width: 42px;
      height: 42px;
      border: 1px solid var(--ink);
      border-radius: 50%;
      color: var(--paper);
      background: var(--ink);
      font: 800 15px/1 "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
    }

    .route-list strong {
      display: block;
      line-height: 1.2;
    }

    .route-list span {
      display: block;
      margin-top: 4px;
      color: var(--muted);
      font-size: 14px;
    }

    .evidence-band {
      color: #fff7e8;
      background: #111;
    }

    .evidence-band .section-head p,
    .evidence-band .lead {
      color: rgba(255, 247, 232, .76);
    }

    .evidence-band .kicker {
      color: #f7cf74;
    }

    .pipeline {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 1px;
      border: 1px solid rgba(255, 247, 232, .22);
      background: rgba(255, 247, 232, .18);
    }

    .pipeline-step {
      min-height: 180px;
      padding: 20px;
      background: #171717;
    }

    .pipeline-step span {
      color: #f7cf74;
      font: 800 12px/1 "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
    }

    .pipeline-step strong {
      display: block;
      margin-top: 14px;
      font-size: 20px;
      line-height: 1.2;
    }

    .pipeline-step p {
      margin: 10px 0 0;
      color: rgba(255, 247, 232, .68);
      font-size: 14px;
    }

    .dark-facts {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 1px;
      margin-top: 18px;
      border: 1px solid rgba(255, 247, 232, .22);
      background: rgba(255, 247, 232, .18);
    }

    .dark-facts div {
      min-height: 120px;
      padding: 18px;
      background: #171717;
    }

    .dark-facts strong {
      display: block;
      color: #fff7e8;
      font-size: 19px;
      line-height: 1.22;
    }

    .dark-facts span {
      display: block;
      margin-top: 8px;
      color: rgba(255, 247, 232, .68);
      font-size: 14px;
    }

    .table-wrap {
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: rgba(255, 250, 240, .78);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 720px;
    }

    th,
    td {
      padding: 15px 16px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }

    th {
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
    }

    td {
      font-size: 14px;
    }

    tr:last-child th,
    tr:last-child td {
      border-bottom: 0;
    }

    code {
      font-family: "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
      font-size: .94em;
    }

    .note {
      margin-top: 16px;
      padding: 16px;
      border-left: 4px solid var(--danger);
      background: rgba(185, 36, 31, .08);
      color: var(--muted);
    }

    .note strong {
      color: var(--ink);
    }

    .claim-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      margin-top: 18px;
    }

    .claim-card {
      padding: 18px;
      border-left: 4px solid var(--blue);
    }

    .claim-card strong {
      display: block;
      font-size: 18px;
      line-height: 1.25;
    }

    .claim-card span {
      display: block;
      margin-top: 8px;
      color: var(--muted);
      font-size: 14px;
    }

    .proof-list {
      display: grid;
      gap: 12px;
      margin: 0;
      padding: 0;
      list-style: none;
    }

    .proof-list li {
      display: flex;
      justify-content: space-between;
      gap: 20px;
      padding: 14px 0;
      border-bottom: 1px solid rgba(22, 20, 16, .12);
    }

    .proof-list li:last-child {
      border-bottom: 0;
    }

    .proof-list span {
      color: var(--muted);
    }

    .mono {
      font-family: "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
    }

    .registry {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
    }

    .registry a,
    .registry div {
      min-height: 160px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: rgba(255, 250, 240, .74);
    }

    .registry strong {
      display: block;
      font-size: 19px;
    }

    .registry span {
      display: block;
      margin-top: 10px;
      color: var(--muted);
      font-size: 14px;
    }

    footer {
      padding: 34px 0 48px;
      border-top: 1px solid rgba(22, 20, 16, .12);
      color: var(--muted);
      font-size: 13px;
    }

    .footer-inner {
      display: flex;
      justify-content: space-between;
      gap: 18px;
      flex-wrap: wrap;
      width: min(calc(100% - 32px), var(--maxw));
      margin: 0 auto;
    }

    .reveal {
      opacity: 0;
      transform: translateY(16px);
      transition: opacity .55s ease, transform .55s ease;
    }

    .reveal.is-visible {
      opacity: 1;
      transform: translateY(0);
    }

    @media (max-width: 900px) {
      .nav-inner {
        align-items: flex-start;
        flex-direction: column;
      }

      .hero {
        min-height: 78svh;
      }

      .hero-strip,
      .hero-brief,
      .quick-read,
      .grid.three,
      .grid.two,
      .signal-grid,
      .media-grid,
      .section-head,
      .pipeline,
      .dark-facts,
      .path-grid,
      .claim-grid,
      .registry {
        grid-template-columns: 1fr;
      }

      .frame,
      .frame.small {
        min-height: 280px;
      }
    }

    @media (max-width: 560px) {
      .nav-links {
        justify-content: flex-start;
      }

      section {
        padding: 68px 0;
      }

      h1 {
        font-size: 38px;
        line-height: 1;
      }

      .hero-copy {
        font-size: 16px;
      }

      .hero-copy,
      .hero-brief strong,
      .hero-brief p,
      .brief-card p,
      .signal-card p,
      .path-card p,
      .section-head p,
      h2 {
        word-break: break-all;
      }

      .hero-inner {
        width: calc(100vw - 32px);
        max-width: calc(100vw - 32px);
        padding-top: 62px;
      }

      .hero-copy,
      .hero-brief,
      .hero-actions,
      .hero-strip {
        width: 100%;
        max-width: 100%;
      }

      .hero-actions {
        align-items: stretch;
        flex-direction: column;
      }

      .button {
        width: 100%;
      }

      .hero-stat {
        min-height: 82px;
      }

      .proof-list li {
        align-items: flex-start;
        flex-direction: column;
        gap: 4px;
      }

      .fact-list li {
        grid-template-columns: 1fr;
        gap: 5px;
      }
    }

    @media (prefers-reduced-motion: reduce) {
      *,
      *::before,
      *::after {
        scroll-behavior: auto !important;
        transition: none !important;
      }

      .reveal {
        opacity: 1;
        transform: none;
      }
    }
  </style>
</head>
<body>
  <div class="progress" aria-hidden="true"><div class="progress-bar"></div></div>
  <nav class="site-nav" aria-label="Portfolio sections">
    <div class="nav-inner">
      <a class="brand" href="#top" aria-label="BackRoom Level 0">
        <span class="brand-mark" aria-hidden="true"></span>
        <span>BackRoom Level 0</span>
      </a>
      <div class="nav-links">
        <a href="#case">Game</a>
        <a href="#design">Rules</a>
        <a href="#pipeline">Making Of</a>
        <a href="#after">Case Study</a>
        <a href="#registry">Play Links</a>
        <a class="nav-cta" href="./?v=$version">Play</a>
      </div>
    </div>
  </nav>

  <header class="hero" id="top">
    <div class="hero-inner">
      <div class="eyebrow">Short Backrooms Horror Game</div>
      <h1>BackRoom Level 0</h1>
      <p class="hero-copy">
        이곳에 도사리고 있는 비밀을 밝혀야 합니다. 과연 이 공간에서 무사히 집으로 돌아갈 수 있을까요?
      </p>
      <div class="hero-brief">
        <div>
          <span>Your Goal</span>
          <strong>집으로 돌아갈 단서를 찾아야 합니다.</strong>
          <p>표지판 뒤 공간, 전등 버튼, 막힌 길이 서로 어떻게 연결되는지 읽어야 합니다.</p>
        </div>
        <div>
          <span>The Rule</span>
          <strong>같은 공간도 다시 들어가면 다른 의미를 가집니다.</strong>
          <p>방은 이전 선택을 기억합니다. 돌아갈 타이밍을 틀리면 출구는 실패 지점으로 바뀝니다.</p>
        </div>
      </div>
      <div class="hero-actions">
        <a class="button primary" href="./?v=$version">지금 플레이</a>
        <a class="button secondary" href="#case">게임 소개 보기</a>
      </div>
      <div class="hero-strip" aria-label="Game details">
        <div class="hero-stat"><strong>1인용</strong><span>single player</span></div>
        <div class="hero-stat"><strong>짧은 공포</strong><span>short horror</span></div>
        <div class="hero-stat"><strong>3개 엔딩</strong><span>A / B / C</span></div>
        <div class="hero-stat"><strong>브라우저</strong><span>playable demo</span></div>
      </div>
    </div>
  </header>

  <main>
    <section id="case">
      <div class="wrap">
        <div class="section-head reveal">
          <div>
            <p class="kicker">01 / About This Game</p>
            <h2>STOP 표지판 뒤에는, 돌아오지 말아야 할 공간이 있습니다.</h2>
          </div>
          <p>
            BackRoom Level 0은 좁은 갈림길을 반복해서 통과하는 클릭 공포 어드벤처입니다. 플레이어는 달라진 색, 막힌 길, 재진입 경고를 읽고 진짜 출구가 열리는 순서를 찾아야 합니다.
          </p>
        </div>
        <div class="quick-read">
          <article class="card brief-card reveal">
            <span class="tag">Premise</span>
            <h3>처음에는 단순한 통로처럼 보입니다.</h3>
            <p>하지만 STOP 표지판 뒤로 한 번 들어간 뒤부터, 같은 갈림길은 이전과 다른 반응을 보이기 시작합니다.</p>
          </article>
          <ul class="fact-list reveal" aria-label="Project facts">
            <li><strong>Genre</strong><span>1인용 백룸 공포 클릭 어드벤처</span></li>
            <li><strong>Goal</strong><span>단서와 방 상태를 읽고 집으로 돌아갈 길을 찾습니다.</span></li>
            <li><strong>Twist</strong><span>방은 이전 선택을 기억하고, 재진입 순서가 결말을 바꿉니다.</span></li>
            <li><strong>Build</strong><span>Godot 4.6 Web export, browser playable demo</span></li>
          </ul>
        </div>
        <div class="grid three">
          <article class="card metric-card reveal">
            <span class="label">Feature</span>
            <strong>Looping Space</strong>
            <p>처음 지나간 갈림길로 돌아오지만, 방은 같은 방식으로 반응하지 않습니다.</p>
          </article>
          <article class="card metric-card reveal">
            <span class="label">Feature</span>
            <strong>Three Endings</strong>
            <p>탈출, 가짜 출구, 재진입 실패. 같은 공간에서 세 결말로 갈라집니다.</p>
          </article>
          <article class="card metric-card reveal">
            <span class="label">Feature</span>
            <strong>Playable Web Build</strong>
            <p>설치 없이 브라우저에서 바로 시작할 수 있습니다.</p>
          </article>
        </div>
        <div class="signal-grid">
          <article class="card signal-card reveal">
            <span class="tag">Explore</span>
            <h3>표지판 뒤로 들어갑니다.</h3>
            <p>중앙 STOP 표지판은 단순한 배경이 아니라 첫 진입 지점입니다.</p>
          </article>
          <article class="card signal-card reveal">
            <span class="tag">Observe</span>
            <h3>붉게 변한 공간을 읽습니다.</h3>
            <p>스위치를 누른 뒤 돌아오면 같은 방이 다른 상태로 돌아옵니다.</p>
          </article>
          <article class="card signal-card reveal">
            <span class="tag">Avoid</span>
            <h3>같은 행동을 반복하지 마세요.</h3>
            <p>위험한 재진입은 별도 엔딩으로 이어집니다.</p>
          </article>
          <article class="card signal-card reveal">
            <span class="tag">Escape</span>
            <h3>진짜 출구 조건을 맞춥니다.</h3>
            <p>막힌 길의 경고를 우회해야 진짜 출구에 도달할 수 있습니다.</p>
          </article>
        </div>
      </div>
    </section>

    <section id="design">
      <div class="wrap">
        <div class="section-head reveal">
          <div>
            <p class="kicker">02 / Play Experience</p>
            <h2>선택은 작지만, 방은 그 선택을 기억합니다.</h2>
          </div>
          <p>
            좁은 갈림길 안에서 반복, 단서, 재진입의 압박을 만듭니다. 플레이어는 더 많은 장소가 아니라 달라진 상태를 읽으며 앞으로 나아갑니다.
          </p>
        </div>
        <div class="media-grid">
          <figure class="frame reveal">
            <img src="$left" alt="BackRoom left door scene" loading="lazy" />
            <figcaption>왼쪽과 오른쪽 문은 현재 룰을 얼마나 이해했는지 시험합니다.</figcaption>
          </figure>
          <div class="caption-stack">
            <figure class="frame small reveal">
              <img src="$red" alt="BackRoom red room scene" loading="lazy" />
              <figcaption>붉은 조명은 세계 상태가 바뀌었다는 즉각적인 신호입니다.</figcaption>
            </figure>
            <figure class="frame small reveal">
              <img src="$blocked" alt="BackRoom blocked exit scene" loading="lazy" />
              <figcaption>막힌 길은 돌아가기 전에 경고를 읽으라는 압박으로 작동합니다.</figcaption>
            </figure>
            <figure class="frame small reveal">
              <img src="$false_end" alt="BackRoom false exit scene" loading="lazy" />
              <figcaption>거짓 출구는 안도감이 실패로 바뀌는 엔딩 장면입니다.</figcaption>
            </figure>
          </div>
        </div>
        <div class="path-grid">
          <article class="card path-card reveal">
            <span class="tag">Start</span>
            <h3>STOP 갈림길</h3>
            <p>처음에는 표지판 뒤가 가장 수상합니다. 이후 중앙 클릭은 단순 이동이 아니라 새 진입 조건이 됩니다.</p>
            <span class="room">room: fork_stop</span>
          </article>
          <article class="card path-card reveal">
            <span class="tag">Left</span>
            <h3>전등 버튼</h3>
            <p>왼쪽 길에서 전등 버튼을 찾습니다. 버튼을 누르면 STOP 뒤 공간이 붉게 바뀝니다.</p>
            <span class="room">flag: light_switch_pressed</span>
          </article>
          <article class="card path-card reveal">
            <span class="tag">Right</span>
            <h3>막다른 길</h3>
            <p>오른쪽 길은 단서와 경고를 남깁니다. 경고를 무시하고 문을 다시 누르면 가짜 출구 루트로 밀려납니다.</p>
            <span class="room">event: right_door</span>
          </article>
          <article class="card path-card reveal">
            <span class="tag">Loop</span>
            <h3>연속 재진입</h3>
            <p>STOP 뒤 공간에서 나온 뒤 바로 다시 들어가면, 기다리고 있던 존재와 마주칩니다.</p>
            <span class="room">flag: stop_back_reentry_armed</span>
          </article>
        </div>
        <ul class="route-list" style="margin-top:18px">
          <li class="reveal"><b>A</b><span><strong>진짜 탈출</strong>전등 버튼 이후 붉어진 STOP 뒤 공간을 확인하고, 진짜 출구의 문을 눌러 집으로 돌아갑니다.</span></li>
          <li class="reveal"><b>B</b><span><strong>가짜 탈출</strong>오른쪽 막다른 길에서 경고를 무시하면, 막힌 길 너머의 가짜 출구로 끌려갑니다.</span></li>
          <li class="reveal"><b>C</b><span><strong>재진입 사망</strong>STOP 뒤 공간에 바로 다시 들어가면, 재진입을 기다리던 존재에게 붙잡힙니다.</span></li>
        </ul>
      </div>
    </section>

    <section class="evidence-band" id="pipeline">
      <div class="wrap">
        <div class="section-head reveal">
          <div>
            <p class="kicker">03 / How It Works</p>
            <h2>공포는 작은 상태 변화에서 만들어집니다.</h2>
          </div>
          <p>
            플레이 뒤에는 구조를 확인할 수 있습니다. 방 그래프, 클릭 이벤트, 상태 플래그, 엔딩 루트는 프로젝트 파일에 남아 있고 같은 기준으로 다시 검증됩니다.
          </p>
        </div>
        <div class="pipeline">
          <article class="pipeline-step reveal">
            <span>01</span>
            <strong>Room Graph</strong>
            <p>8개 방과 이동 경로를 <code>data/rooms.json</code>에서 관리합니다.</p>
          </article>
          <article class="pipeline-step reveal">
            <span>02</span>
            <strong>State Flags</strong>
            <p>전등, 재진입, 단서 확인은 flag로 분리합니다.</p>
          </article>
          <article class="pipeline-step reveal">
            <span>03</span>
            <strong>Ending Flow</strong>
            <p>A/B/C 엔딩 루트는 실제 클릭 순서로 재검증합니다.</p>
          </article>
          <article class="pipeline-step reveal">
            <span>04</span>
            <strong>Web Build</strong>
            <p>Godot Web export로 브라우저 플레이 빌드를 제공합니다.</p>
          </article>
        </div>
        <div class="dark-facts">
          <div class="reveal">
            <strong>8 rooms / 12 flags / 9 events</strong>
            <span>방 구조와 이벤트 범위는 데이터 파일에서 확인할 수 있습니다.</span>
          </div>
          <div class="reveal">
            <strong>A/B/C route QA</strong>
            <span>엔딩 흐름은 Godot headless에서 실제 클릭 순서로 확인합니다.</span>
          </div>
          <div class="reveal">
            <strong>Repo-built page</strong>
            <span>이 HTML은 repo-local builder로 다시 만들 수 있습니다.</span>
          </div>
        </div>
      </div>
    </section>

    <section id="after">
      <div class="wrap">
        <div class="section-head reveal">
          <div>
            <p class="kicker">04 / Pipeline Case Study</p>
            <h2>원본을 보존한 채, 룰 구조를 분리해 검증했습니다.</h2>
          </div>
          <p>
            공개 플레이 기준선은 그대로 두고, 리폼 실험은 격리 사본에서만 진행했습니다. 아래 수치는 Before와 After를 같은 QA 기준으로 비교한 결과입니다.
          </p>
        </div>
        <div class="table-wrap reveal">
          <table>
            <thead>
              <tr>
                <th>Axis</th>
                <th>Before</th>
                <th>After pipeline run</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Rule logic location</td>
                <td><code>src/Game.gd</code>가 상태와 룰을 함께 처리</td>
                <td><code>src/GameEngine.gd</code> autoload가 상태와 룰을 소유</td>
              </tr>
              <tr>
                <td>Measured LOC</td>
                <td><code>Game.gd</code> 1440 LOC</td>
                <td><code>Game.gd</code> 1329 LOC + <code>GameEngine.gd</code> 425 LOC</td>
              </tr>
              <tr>
                <td>Render to rule coupling</td>
                <td>렌더 노드의 직접 룰/상태 변이 15 lines</td>
                <td>렌더 노드 직접 룰 판정 0, 룰 변이는 engine으로 이동</td>
              </tr>
              <tr>
                <td>Add one room or event</td>
                <td>코드 분기 수정 필요</td>
                <td>A3 probe에서 리소스 추가만으로 검증, 코드 hash 유지</td>
              </tr>
              <tr>
                <td>Testability</td>
                <td>씬과 렌더 상태에 강하게 결합</td>
                <td>엔진 snapshot과 state_changed 기준으로 headless 검증 가능</td>
              </tr>
              <tr>
                <td>Behavior parity</td>
                <td><code>validate_routes</code> 8/8 + A/B/C PASS</td>
                <td>A2a, A2b, A3 모두 8/8 + A/B/C PASS</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="note reveal">
          <strong>해석:</strong> 이 비교는 게임의 매력을 과장하는 문구가 아니라, 원본을 망가뜨리지 않고 룰과 화면 코드를 분리할 수 있는지 확인한 개발 기록입니다.
        </div>
        <div class="claim-grid">
          <article class="card claim-card reveal">
            <strong>구조적으로 확인한 점</strong>
            <span>After 구조는 화면이 snapshot을 그리고, 룰 결정은 engine이 맡는 형태로 검증했습니다.</span>
          </article>
          <article class="card claim-card reveal">
            <strong>공개 페이지에서 선을 긋는 점</strong>
            <span>현재 플레이 링크는 원본 계열 기준입니다. 리폼 결과는 격리 사본에서 검증한 개발 실험으로 구분합니다.</span>
          </article>
        </div>
      </div>
    </section>

    <section id="proof">
      <div class="wrap">
        <div class="section-head reveal">
          <div>
            <p class="kicker">05 / Proof</p>
            <h2>플레이 화면 뒤의 근거도 남겼습니다.</h2>
          </div>
          <p>
            게임 컨셉만 말하지 않습니다. 방 그래프, 상태 문서, route validator, A/B/C QA를 함께 연결해 실제 구현 범위를 확인할 수 있게 했습니다.
          </p>
        </div>
        <div class="grid two">
          <figure class="frame reveal">
            <img src="$exit" alt="BackRoom true exit scene" loading="lazy" />
            <figcaption>진짜 출구는 A 엔딩 직전 목표 지점입니다.</figcaption>
          </figure>
          <article class="card metric-card reveal">
            <ul class="proof-list">
              <li><strong>8-room graph</strong><span><code>data/rooms.json</code></span></li>
              <li><strong>State and route map</strong><span><code>docs/CODEGRAPH.md</code></span></li>
              <li><strong>A/B/C flow QA</strong><span><code>tools/qa_game_flow.gd</code></span></li>
              <li><strong>Route validator</strong><span><code>tools/validate_routes.py</code></span></li>
              <li><strong>Portfolio builder</strong><span><code>tools/build_portfolio_html.py</code></span></li>
            </ul>
          </article>
        </div>
        <div class="claim-grid">
          <article class="card claim-card reveal">
            <strong>확인 가능한 범위</strong>
            <span>Godot Web 플레이 빌드, 8개 방 route graph, A/B/C 엔딩, route validation, headless QA, repo-generated portfolio HTML.</span>
          </article>
          <article class="card claim-card reveal">
            <strong>말하지 않는 것</strong>
            <span>대규모 상용 게임, 자동화가 QA를 대체했다는 주장, 검증하지 않은 성과 수치, 최종 실사풍 아트 완성.</span>
          </article>
        </div>
      </div>
    </section>

    <section id="registry">
      <div class="wrap">
        <div class="section-head reveal">
          <div>
            <p class="kicker">06 / Play & Notes</p>
            <h2>바로 플레이하거나, 개발 노트를 확인할 수 있습니다.</h2>
          </div>
          <p>
            첫 방문자는 게임부터 시작하면 됩니다. 구조와 검증 기준이 궁금하면 이 페이지의 개발 노트와 근거 섹션을 확인하면 됩니다.
          </p>
        </div>
        <div class="registry">
          <a class="reveal" href="./?v=$version">
            <strong>Play Build</strong>
            <span>브라우저에서 현재 Web export를 바로 실행합니다.</span>
          </a>
          <a class="reveal" href="./portfolio.html">
            <strong>Game Detail Page</strong>
            <span>게임 소개, 플레이 구조, 개발 근거를 함께 정리한 페이지입니다.</span>
          </a>
          <div class="reveal">
            <strong>Version</strong>
            <span class="mono">$version</span>
            <span>Generated on $generated by repo-local builder.</span>
          </div>
        </div>
      </div>
    </section>
  </main>

  <footer>
    <div class="footer-inner">
      <span>BackRoom Level 0 - short Backrooms horror game</span>
      <span>Playable build and developer notes generated from <code>tools/build_portfolio_html.py</code></span>
    </div>
  </footer>

  <script>
    const progressBar = document.querySelector(".progress-bar");
    const updateProgress = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const ratio = max > 0 ? window.scrollY / max : 0;
      progressBar.style.width = (Math.min(1, Math.max(0, ratio)) * 100).toFixed(3) + "%";
    };
    updateProgress();
    window.addEventListener("scroll", updateProgress, { passive: true });

    const observer = new IntersectionObserver((entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      }
    }, { threshold: 0.12 });

    for (const element of document.querySelectorAll(".reveal")) {
      observer.observe(element);
    }
  </script>
</body>
</html>
"""
    )
    return template.safe_substitute(
        base_url=PAGES_BASE_URL,
        version=version,
        generated=generated,
        fork=assets["fork"],
        left=assets["left"],
        red=assets["red"],
        exit=assets["exit"],
        blocked=assets["blocked"],
        false_end=assets["false_end"],
    )


def build_registry(version: str) -> dict[str, object]:
    generated = datetime.now().isoformat(timespec="seconds")
    return {
        "project": "BackRoom Level 0",
        "generated_at": generated,
        "base_url": PAGES_BASE_URL,
        "deployed_game_version": version,
        "pages": [
            {
                "id": "play",
                "title": "Play BackRoom Level 0",
                "url": f"{PAGES_BASE_URL}/",
                "description": "Godot Web export entrypoint for the playable horror prototype.",
                "evidence": ["project.godot", "export_presets.cfg", "docs/PROGRESS.md"],
            },
            {
                "id": "portfolio",
                "title": "BackRoom Level 0 Game Detail Page",
                "url": f"{PAGES_BASE_URL}/portfolio.html",
                "description": "Self-contained game detail page for a short Godot Web Backrooms horror game, with developer notes and QA evidence.",
                "evidence": [
                    "tools/build_portfolio_html.py",
                    "data/rooms.json",
                    "tools/validate_routes.py",
                    "tools/qa_game_flow.gd",
                    "docs/CODEGRAPH.md",
                    "docs/PROGRESS.md",
                ],
            },
        ],
    }


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    BUILD_WEB.mkdir(parents=True, exist_ok=True)

    version = deployed_game_version()
    embedded_assets = {name: data_uri(path) for name, path in ASSETS.items()}
    html = build_html(version, embedded_assets)
    registry = build_registry(version)
    registry_text = json.dumps(registry, ensure_ascii=False, indent=2) + "\n"

    outputs = {
        DOCS / "backroom-portfolio.html": html,
        BUILD_WEB / "portfolio.html": html,
        DOCS / "backroom-pages-registry.json": registry_text,
        BUILD_WEB / "backroom-pages-registry.json": registry_text,
    }

    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} ({len(text):,} chars)")


if __name__ == "__main__":
    main()
