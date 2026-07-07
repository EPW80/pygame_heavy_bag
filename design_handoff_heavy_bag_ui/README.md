# Handoff: Heavy Bag Training — UI Modernization

## Overview

A complete UI modernization for the **pygame_heavy_bag** repo (`EPW80/pygame_heavy_bag`, Python + Pygame). It covers:

1. **Every existing game state redesigned** at 1920×1080 — Main Menu, Gameplay HUD (two variants: full dashboard and minimal), Pause, Round Complete.
2. **Two new screens** for menu options that currently log "not yet implemented" — Settings and Tutorial/Move List.
3. **A redesigned player character** ("Cel Classic") with a full sprite set: idle + all 7 attacks (jab, cross, hook, uppercut, front kick, roundhouse, low kick).
4. **A combat-feedback animation spec** (jab → cross combo) defining bag physics, impact effects, screen shake, and score feedback timing.

All values were derived from the game's own source (`constants.py`, `menu.py`, `game_manager.py`, `graphics.py`, `heavy_bag.py`, `player.py`) — stamina costs, reach/force stats, scoring rules and copy are the game's real numbers.

## About the Design Files

The files in this bundle are **design references created in HTML** — prototypes showing intended look and behavior, **not production code to copy directly**. The task is to **recreate these designs in the pygame codebase** using its established patterns (the `GraphicsManager` procedural-sprite system, `draw_ui`/`draw_bar` helpers, `Menu` class, etc.).

- Open `UI Redesign.dc.html` in a browser to see all redesigned screens (newest work at top: the combo animation, then character poses, then the three character directions, then the 7 screens).
- Open `Current UI Recreation.dc.html` for a faithful reference of what the game renders today (useful as a diff baseline).

### Resolution note
Designs are at **1920×1080**; the game currently runs at **1000×700** (`SCREEN_WIDTH`/`SCREEN_HEIGHT` in `constants.py`). Either raise the window to 1920×1080 (or 1280×720 at 2/3 scale), or multiply all px values in this doc by your scale factor. All measurements below are in 1920×1080 space unless marked otherwise.

## Fidelity

**High-fidelity.** Colors, typography, spacing and copy are final. Recreate pixel-perfectly (at your chosen scale). The character sprites are specified on the game's existing 80-unit sprite grid and can be ported shape-for-shape into `GraphicsManager._create_player_sprites`.

## Design Tokens

### Colors
| Token | Hex | Use |
|---|---|---|
| bg | `#0B0C10` | screen background |
| scene-bg-top | `#0D0E13` | gym gradient top |
| scene-bg-bottom | `#23242B` | gym gradient bottom |
| floor | `#17181D` | floor band |
| panel | `rgba(13,14,17,0.66–0.8)` | HUD panels (blur 10px behind if possible; otherwise solid `#0D0E11` at 90%) |
| panel-border | `rgba(255,255,255,0.08)` | 1px panel borders |
| card | `rgba(255,255,255,0.03)` w/ border `rgba(255,255,255,0.10)` | stat/settings cards |
| text-primary | `#F2F3F5` | headings, numerals |
| text-dim | `rgba(235,237,240,0.45–0.6)` | labels, hints |
| gold (accent) | `#F0C330` | selection, combo, best score, special |
| stamina green | `#45D483` | stamina meter, in-range, stamina costs |
| power blue | `#3D7BFF` | power meter |
| rage red | `#E5432E` | rage power-up |
| impact yellow | `#F5D90A` | bag damage, impact rings |

### Typography
- **Display / numerals:** Bebas Neue (bundle the TTF; load via `pygame.font.Font("BebasNeue.ttf", size)`). Used for scores, timers, headings, keycaps, combo counter.
- **Body / labels:** Barlow (400/500/600/700). Small caps labels use ~0.25em letter-spacing — pygame has no letter-spacing, so render label chars individually with a fixed advance, or accept default tracking.
- Scale (1080p): giant numerals 96–250, timers 64–110, headings 110–130, menu items 42–44, body 15–22, labels/chips 13–18.

### Spacing & shape
- Screen margins: 80 px (HUD), 160 px (menu/settings/tutorial content).
- Panel padding: 22–32 px. Card gaps: 18–24 px.
- Corners: square (0) for panels/cards; 6–8 px only on keycaps; toggles fully rounded.
- Keycap: 38–44 px square, 1px border `rgba(255,255,255,0.25)`, fill `rgba(255,255,255,0.05)`, Bebas 22–26.

## Screens / Views

### 1. Main Menu (replaces `menu.py::Menu.draw`)
- Backdrop: gym scene at 50% opacity + left-to-right dark gradient overlay (`rgba(8,9,12)` 0.94 → 0.25).
- Left column at x=160, vertically centered: "PRO EDITION" chip (gold 1px border, 17px, wide tracking) → "HEAVY BAG" (Bebas 190, white) → "TRAINING" (Bebas 190, gold) → menu list (480 wide).
- Menu rows: Bebas 42, padding 16×24. Selected: gold text, 4px gold left bar, `rgba(240,195,48,0.08)` fill, "↵" hint right. Unselected: `rgba(235,237,240,0.55)`.
- Items: START GAME / TUTORIAL / SETTINGS / QUIT (same order as `Menu.options`).
- Bottom-right: save-file stats (BEST SCORE gold, TOTAL PUNCHES, BEST COMBO — from `SaveManager`), label 16px dim + Bebas 64 value.
- Bottom-left: key hints with keycaps (↑ ↓ NAVIGATE · ENTER SELECT).

### 2. Gameplay HUD — Full (replaces `game_manager.py::draw_ui`)
- Top-left (80,56): "SCORE" label → Bebas 96 value → "BEST 3,580" in gold (Bebas 32).
- Top-center: timer Bebas 110 → 360×4 round-progress bar (gold fill = elapsed/180s) → "TRAINING ROUND — 3:00" label.
- Top-right (360 wide panel): STAMINA (green) and POWER (blue) segmented bars, 10px tall, 10 segments (2px `#0D0E11` dividers), numeric value right in Bebas 28. Caption: "SPACE UNLOCKS SPECIAL AT 100". When power = 100, switch bar + value to gold.
- Center: combo — "6×" Bebas 200 gold with soft gold glow, "COMBO" label below, "AMAZING" chip (game rule: combo>5). Floating "+82" Bebas 64 gold near the bag (replaces `FloatingText` styling).
- In-range: green glow strip rising from the floor under the bag (360×180 gradient, 3px green bottom line, ~1.6s opacity pulse) + "IN RANGE" pill chip (green dot, green 1px border, dark blurred fill) — replaces the flat green rect in `_draw_enhanced_range_indicator`.
- Bottom-left panel: control card — two columns: PUNCHES (Z Jab −5, X Cross −8, C Hook −10, V Uppercut −12) and KICKS (Q Front Kick −15, W Roundhouse −18, E Low Kick −12) + gold SPACE Special key. Keycap + name (Barlow 600 18) + green stamina cost.
- Bottom-right chip: "BAG" + 120×6 damage bar (yellow `#F5D90A`) + percent (Bebas 24) — replaces the damage bar drawn above the bag in `heavy_bag.py::_draw_additional_effects`.

### 3. Gameplay HUD — Minimal (alternative; could be a Settings toggle)
- Score Bebas 56 + "BEST" inline (top-left), timer Bebas 64 + 200×2 progress (top-center).
- Bottom-center: two 420×6 slim bars labeled STA / PWR.
- Combo Bebas 160 center. One dim hint line bottom-right: "Z X C V punches · Q W E kicks · SPACE special · ESC pause".
- No panels, no control card — for players who know the moves.

### 4. Pause (replaces `draw_pause_menu`)
- Freeze frame + `rgba(8,9,12,0.85)` overlay (blur if feasible; solid otherwise).
- Left at x=200: "TRAINING ROUND — 02:17 LEFT" label → "PAUSED" Bebas 220 → menu rows RESUME (selected, ESC keycap) / QUIT TO MENU (Q keycap), styled like main menu rows, 520 wide.
- Right: "THIS SESSION" panel (380 wide): Score, Best combo (gold), Punches thrown — label 17px dim left, Bebas 44 value right.

### 5. Round Complete (replaces `draw_game_over`)
- Black bg + gold radial glow from top center (`rgba(240,195,48,0.14)` → transparent, ~700×420).
- Centered column: "TRAINING SESSION — 3:00" label → "ROUND COMPLETE" Bebas 130 gold → "FINAL SCORE" label → score Bebas 250 → three 300-wide stat cards (BEST COMBO gold / TOTAL PUNCHES / HIGH SCORE, Bebas 72 values) → all-time strip ("ALL-TIME · 8,214 TOTAL PUNCHES · 15× BEST COMBO", dim 16px) → keycap hints (ENTER Menu · R Restart).

### 6. Settings (new — implements the stubbed menu option)
- Header: "PRO EDITION" eyebrow + "SETTINGS" Bebas 110; "ESC Back to menu" top-right.
- DIFFICULTY: 4 equal cards (EASY/NORMAL/HARD/EXPERT — Bebas 48) with one-line physics description and green stamina-regen stat (+0.5/+0.3/+0.2/+0.1 per sec — from `PLAYER_STAMINA_REGEN_*`). Selected card: gold border, gold title, "SELECTED" tab in the corner (gold fill, dark text).
- GAME: 840-wide stacked rows with pill toggles — Sound, Particle effects, FPS counter (maps to `GameSettings` fields). On: gold pill, dark knob right. Off: `rgba(255,255,255,0.14)` pill, dim knob left.
- Footer hints: ↑↓ Navigate · ←→ Adjust · ENTER Toggle.

### 7. Tutorial / Move List (new — implements the stubbed menu option)
- Header: "TUTORIAL" eyebrow + "MOVE LIST" Bebas 110; ESC hint.
- 4×2 grid of attack cards: keycap + green "−N STA" (from `ATTACK_PROPERTIES.stamina_cost`), name Bebas 44, one-line description, then REACH and FORCE mini-bars (5px) normalized to max reach 50 / max force 5.0 — values from `ATTACK_PROPERTIES`: Jab 35/2.0, Cross 40/3.0, Hook 30/3.5, Uppercut 25/4.0, Front Kick 50/4.5, Roundhouse 45/5.0, Low Kick 40/3.0. FORCE bar gold, REACH bar white.
- 8th cell: SPECIAL card (gold border/tint): SPACE keycap, "Needs full power meter", "+100 points, massive knockback" (−20 STA from `STAMINA_SPECIAL_MOVE`).
- Bottom strip: SCORING (PERFECT +50 — strike while the bag hangs steady; COMBO +20%/hit — chain within one second; SPECIAL +100) and POWER-UPS legend (green Stamina, blue Power, gold 2× Multiplier, red Rage — walk into them).

## Character: "Cel Classic" (replaces `GraphicsManager._create_player_sprites`)

Same identity as the current procedural boxer (white tank, blue shorts, red gloves, brown hair) rebuilt with consistent dark cel outlines (`#241C12`, ~2 units), correct proportions, and a peek-a-boo guard. Drawn on the game's existing **80-unit-wide sprite grid** (feet baseline at y≈110); every shape is a circle/rect/capsule/arc — directly portable to `pygame.draw` calls.

Palette: skin `#F5C89A`, hair `#6B4423`, tank `#EDEAE3` (red hem trim `#D23B2E`), shorts `#3A44B8` + gold waistband `#F0C330` + white side stripes, gloves `#D23B2E` (band `#A32B22`), shoes `#1B1B1F` with off-white sole.

Poses (idle + 7 attacks) are defined as reusable parts (head, torso, shorts, standing legs, guard arms, glove) + per-pose arm/leg geometry, mirroring how `graphics.py` composes punch sprites from the idle base. Exact coordinates: open `UI Redesign.dc.html` and inspect the SVG groups `#celPoseIdle`, `#celPoseJab`, `#celPoseCross`, `#celPoseHook`, `#celPoseUppercut`, `#celPoseFrontKick`, `#celPoseRoundhouse`, `#celPoseLowKick` — each `<circle>/<rect>/<path>` maps 1:1 to a `pygame.draw` call on the sprite surface.

Per-pose effect accents (keep from the current game): jab/uppercut white motion lines, cross impact star (yellow), hook/roundhouse gold arc trails, low-kick sweep lines, front-kick impact rays.

Punch sprites are wider than idle (reach extends to ~x=95 on the grid) — use a 120-wide surface for attack poses as the code already does.

## Interactions & Behavior

### Combo animation spec (from the 4a prototype — `combo-anim.jsx`)
- **Sprite swap timing:** punch pose holds ~0.35–0.42s (game currently: `PUNCH_ANIMATION_FRAMES` 15 ≈ 0.25s — keep the game's value; the prototype stretches slightly for readability).
- **Bag swing:** on hit, add a damped impulse: `angle(t) = −A · sin(5.5·dt) · e^(−1.5·dt)` where `dt` = time since impact, A ≈ 9° for a jab, 17° for a cross (scales with force). Swings away from the player, oscillates back. Sum concurrent impulses. (This replaces/augments the existing `heavy_bag.update` integration — the constants above reproduce the prototype's feel.)
- **Impact ring:** at contact point, ring expands r 10→54 over 0.35s while fading out (stroke `#F5D90A` 3.5→1.5) + inner soft flash.
- **Screen shake:** cross only (heavy hits): ±6 px decaying over 0.3s (matches `screen_shake` mechanic).
- **Floating score:** "+N" Bebas 44, gold, rises 70 px over 0.9s while fading (replaces `FloatingText` styling).
- **Combo counter:** appears on first hit, pops (scale 1.35 → 1, ~0.15s decay) on every subsequent hit, fades out 0.4s after the combo window lapses.
- **Idle:** subtle breathing bob, ±2 px at ~1 Hz.

### General
- Menu/pause/settings selection: gold left-bar + tint moves with ↑/↓ (no mouse required, matching current input model).
- Meter behavior: power bar turns gold at 100 (special ready); stamina bar unchanged behavior.
- In-range strip pulses opacity 0.55→1.0 at ~1.6s period while player is in the hit zone.

## State Management

Existing state covers almost everything (`GameState`, `Player`, `HeavyBag`, `GameSettings`). New:
- `hud_variant: "full" | "minimal"` (could live in `GameSettings`; the two HUD designs are alternatives).
- Settings screen: cursor index + editing of existing `GameSettings` fields; persist via `SaveManager`.
- Tutorial screen: static render from `ATTACK_PROPERTIES` (no new state).

## Assets

- **Fonts:** Bebas Neue (1 weight) and Barlow (400/500/600/700) — free on Google Fonts, download TTFs into the repo (e.g. `assets/fonts/`).
- No raster images: every visual (gym backdrop, bag, character, effects) is procedural shapes, consistent with the codebase's `GraphicsManager` approach. The gym scene layers: vertical gradient, 3 ceiling light glows + fixtures, mirror strips, weight-rack silhouette, floor band with 96px mat grid, chain (8px + 2px highlight, links every ~110px), bag (rounded rect, leather gradient `#5A2C16→#33150A`, seam lines, gold "HEAVY" branding, left highlight, floor shadow ellipses).

## Files

- `UI Redesign.dc.html` — all redesigned screens + character sheet + animation (open in a browser; pan/zoom). Screens are labeled 1a–1g, character options 2a–2c, pose sheet 3a/3b, animation 4a.
- `Current UI Recreation.dc.html` — pixel-faithful recreation of the current pygame UI (baseline for comparison).
- `combo-anim.jsx` — animation engine + the combo scene source (timing/physics constants live in the `HITS` array and `damped()`).
- `support.js` — runtime required by the two `.dc.html` files; keep it next to them.
