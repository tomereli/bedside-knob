# Design — issue #2, the MUSIC card and the playlist sub-page

Two surfaces: `page_music` and `page_plist`. Nothing else on the carousel moves.

---

## 0. What I could and could not read

Both read-only Home Assistant tools available to this session were refused
permission, so **no live entity state was queried**. Everything measured below
comes from three places that do exist here:

- the entity survey in `REQUIREMENTS.md`
- the state facts recorded on the issue by a person: the five playlist names and
  their URIs, the single `input_select` state record across ten days, and
  `supported_features` carrying `VOLUME_MUTE`
- `firmware/bedside-knob.yaml` itself, which is the current screen

What that costs is named in §8. It is one figure, and it does not change any
decision here.

---

## 1. The question each screen answers

**MUSIC** — *"Is it playing, how loud, and how do I make it stop right now?"*

**PLAYLIST** — *"Which of the five do I want, and start it."*

Note what is not in either sentence: what track this is, who made it, how far in
it is. The nightstand asks about the room, not about the music.

---

## 2. What he does here, in order

### The 3 am case, which is the one this issue exists for

Music is playing. The hand comes out, the glass lights on MUSIC. Three things
are wanted and in this order of urgency: **make it quiet, make it stop, make it
softer.** Mute is one tap on a 58 px target near the centre of the row. Pause is
one tap beside it. The dial is under the palm already.

None of that is gated, at any hour, ever. A hand reaching for silence must never
meet a prompt.

### The 3 am case this issue exists to prevent

Nothing is playing. He is winding the carousel to get to LIGHTS and lands on
MUSIC on the way, or a palm settles on the glass. Today either of those starts
music at whatever volume it was left at. After this change:

1. The start attempt **arms** instead. `fx_refuse` fires — a soft fuzz, distinct
   from the sharp click of an accepted press with the eyes shut.
2. The volume drops to at most 20% *at that instant*, so the number on the glass
   is already the number that will play.
3. The play button's ring lights and the state line reads `HOLD PLAY TO START`.
4. A 700 ms hold of that button starts it. Anything else — six seconds, the
   screen sleeping, winding to another card — and the arm is gone.

Two separate acts on a 58 px target. A palm cannot produce that.

### The deliberate case, at any hour

MUSIC → tap the playlist button → the sub-page. Turn: the name walks, one option
per detent, wrapping. Tap the face or the new play button: it starts. At night,
the same arm-then-hold, on the same play button, in the same words.

---

## 3. Information hierarchy

The WiiM entity is a Music Assistant player and offers far more than this card
should carry.

### Shown at a glance — first frame, no gesture

| | Why it is on the glass |
|---|---|
| Volume percent, 60 px | The one continuous thing this device exists to set. |
| The arc | Magnitude with no reading at all, and the only element legible at 60° off normal from a pillow. |
| `PLAYING` / `PAUSED` / `IDLE`, 18 px | Answers half of the card's question in one word. |
| `MUTED` in that same slot | The other half. Silence has two causes and they must not read the same. |
| The armed prompt, in that same slot | An instruction, not a status — so it takes precedence over both above. |
| The four controls | Playlist, play/pause, mute, next. |

### Shown on demand

| | Revealed by |
|---|---|
| The selected playlist name | Opening the sub-page. One gesture, one page, one string. |

### Not shown, and why

| Refused | Why |
|---|---|
| `media_title`, `media_artist`, `media_album_name` | Montserrat is ASCII and LVGL does not shape RTL. A Hebrew title renders as boxes, which teaches him something false. Beyond that it is a readout on a card made of controls. |
| `entity_picture` / `media_image_url` | Artwork is a lit rectangle 150 mm from a sleeping face, and it is the one element that would blow the 120 ms detent budget. |
| `media_position`, `media_duration` | There is nothing on this device that acts on them. |
| `media_content_id` | `library://playlist/9` is a fact about Music Assistant. The name is the fact about the music. This is the field that most wants dumping and most must not be. |
| `shuffle`, `repeat` | `script.play_playlist_by_name` sets shuffle itself before building the queue. A second control over one truth is a second thing to keep true. |
| `source`, `app_name`, `group_members`, `sound_mode`, `supported_features` | Facts about the audio topology. He owns one speaker in this room. |
| `input_select.mbr_playlist_browse` (16 entries) | `REQUIREMENTS.md` already refused it: spinning a 16-item list in the dark is a menu. The bedroom input_select's five are the answer. |
| **A clock** | This issue gives the device wall-clock time for the first time, and the temptation follows immediately. Refused: this is an IPS panel, so dimming the backlight dims the glyphs and the ground together and a "dim clock" is a grey coin glowing beside his head. Idle is off, and off is a feature. |
| **A night badge** — any permanent mark that quiet hours are in force | It would be lit every night from 22:00, and a badge that is always on is not information. The refusal is the teaching moment: it costs one tap, once a night, and it explains itself in words on the spot. |
| A countdown of the six-second arm window | A draining bar teaches him to hurry. The prompt simply stops being there. |

---

## 4. Default state — what is on the glass before anyone touches anything

**MUSIC:** the current volume, the current transport word, four unlit controls.
Identical at 03:00 and at noon while something is playing — AC-8 is a visual
requirement as much as a behavioural one. If a prompt appeared over playing
music the card would have two night faces to learn instead of none.

**PLAYLIST:** whatever Home Assistant currently has selected, verbatim. The knob
holds no copy of the list and does not remember a "last" one. That property is
already in the file and the fixed walk is what finally honours it.

---

## 5. Controls

### The row on `page_music`

Four controls do not fit at the current 66 px. Worst corner of a 66 px button at
`x: ±111, y: 70` sits at r = 177, outside the 172 safe radius. So the row adopts
the geometry the LIGHTS card already uses for its zone chips — **58 px on a 70 px
pitch** — extended by one:

```
   PLAYLIST        PLAY         MUTE         NEXT
     x -105        x -35        x +35       x +105          y 70, 58 px, radius 29
```

Worst corner r = 167, inside 172. Gap between neighbours 12 px, byte-identical to
the LIGHTS row. This is not a new size or a new spacing; it is the file's own row
with a fourth chip on it.

| Control | Question it answers | Notes |
|---|---|---|
| PLAYLIST `mdi:playlist-music` | "Something else." | Left end, where it already is. |
| PLAY `mdi:play-pause` | "Start / stop." | Moves 35 px left of centre — the smallest displacement four-across allows. |
| MUTE `mdi:volume-high` → `mdi:volume-off` | "Silence, now." | New. Placed just right of centre, because it is the most urgent control on the card and it belongs under the thumb. |
| NEXT `mdi:skip-next` | "Not this one." | Right end, where it already is. |

Only PLAY and MUTE occupy new positions, and PLAY moves by half a button width.

**Why mute rather than pause is the urgent control.** `REQUIREMENTS.md` records
that a direct `media_player.media_play_pause` on the Music Assistant entity does
nothing during an AirPlay session — "which is how the wall buttons came to look
dead." Mute is the control that silences the room whatever is driving the
speaker. That is why it gets the better seat. See §8, finding 4.

### The dial on `page_music`

One detent, one deliberate turn: **5 percentage points**, climbing **5 → 8 → 12 →
18** as a spin sustains, streak window **450 ms**, fast flick doubles, capped at
**20 pp per detent**. Twenty detents crosses the range deliberately; ten crosses
it in a spin. The LIGHTS ladder keeps its own constants verbatim — the two
branches share globals and must stop sharing a tuning.

Ungated at every hour. A hand winding the volume down is the same hand reaching
for silence.

### `page_plist`

The sub-page gains a play control beside its BACK button:

```
        BACK              PLAY
        x -44             x +44             y 104, 66 px, radius 33
```

Worst corner r = 157, inside 172. Both stay 66 px — there are only two.

It earns its place for one reason: **the confirm gesture needs a target a palm
cannot land on.** A hold of the open face already means BACK here and must keep
meaning it. In daylight the button is a second, harmless way to do what the face
tap already does.

Moving BACK off centre is normally a cost. Here it is not: the issue records that
`input_select.bedroom_playlist` has one state record across ten days, so this
page has never been walked successfully by anyone. There is no muscle memory to
protect.

### One confirm gesture, in one place

**A 700 ms hold of the play control.** Nothing else confirms, on either surface.

- It reuses `long_press_time: 700ms`, already configured, and `on_long_press`,
  already the idiom on `btn_read` and the zone chips.
- A button's short-click does not fire when a long-press did, so the arm-tap and
  the confirm-hold cannot both land from one touch.
- **A hold of the open face never confirms** — it arms, or re-arms. This is the
  refinement that makes the guard real: a palm settling on the glass reports one
  centroid, and only a centroid inside a 58 px circle at `(-35, 70)` would even
  reach the control. A palm produces a face event, and a face event can only ever
  arm.

The accidental path is therefore two separate deliberate touches on a small
target inside six seconds. Nothing a sleeping arm does looks like that.

---

## 6. States

### Armed

| Where | Rest | Armed |
|---|---|---|
| `page_music` play button border | `0x4A2432` | `0xF06292` |
| `page_music` state line | `PLAYING` / `PAUSED` / `IDLE` / `MUTED` | `HOLD PLAY TO START`, colour `0xF06292` |
| `page_music` value + arc | the live volume | the capped value, ≤ 20 |
| `page_plist` play button border | `0x4A2432` | `0xF06292` |
| `page_plist` hint line | `TAP TO PLAY` | `HOLD PLAY TO START`, colour `0xF06292` |

The prompt is at `0xF06292`, not the `0x8C4A62` the state line normally uses. At
25% backlight — which is exactly when this prompt appears, because `screentime`
dims to `0.25` while the house goodnight key is on — the dim rose is the faintest
ink on the card, and the one line he must read must not be the faintest thing
on the glass.

The prompt is ASCII English, like every other string on this device, because the
compiled font is Montserrat and LVGL does not shape RTL. `HOLD PLAY TO START`
measures ≈ 200 px at `label_18` against a chord well over 340 px at that height.

**The value must be true when it is shown.** Showing `70%` under a prompt whose
confirm will play at 20% is a lie he would act on. The cheapest way to make the
number honest is to make it real: cap the volume *at the moment of arming*, not
at the moment of starting. Nothing is playing, so setting a silent speaker's
volume is inaudible; if he abandons the arm the volume is left low, which at 3 am
is the safe direction. It also removes the race the plan hedged against with a
400 ms delay — the cap has been applied for seconds by the time the play call
goes out. Keep the cap in the start path as well; it costs nothing and covers a
window that opens across 22:00.

**The arm clears on:** six seconds, the screen sleeping, a successful start, and
**leaving MUSIC for another carousel card**. That last one is a decision, not an
oversight: winding the carousel is abandoning the thought. `page_music` and
`page_plist` are one surface for this purpose — moving between them keeps the arm,
which is what lets a playlist chosen on the sub-page be confirmed on the sub-page.

Six seconds is `adjust_timeout`'s number. One constant for "you have six seconds
to finish a thought" is one thing to learn, and it is comfortably shorter than
the 20 s screen timeout, so an arm always dies while the glass is still lit to
show it dying.

### Muted

Three channels, because AC-5 asks for the state and one channel is not enough at
25% backlight:

| | |
|---|---|
| The mute button glyph | `mdi:volume-high` → `mdi:volume-off` — a 44 px shape change, the strongest signal on the card |
| The mute button border | `0x4A2432` → `0xF06292`, the file's own "this thing is active" convention from `paint_lights` |
| The arc indicator | drops to the track colour `0x3A1E2A`, so the ring reads as empty |
| The state line | `MUTED` |

The volume number stays. The level is still real and the dial still sets it — the
arc going dead beside a live number is precisely "there is a level, and nothing
is coming out of it."

**Muted and armed at once:** the arc obeys mute (nothing coming out is the more
urgent truth) and the line obeys the prompt (it is an instruction). Both states
remain independently legible on their own buttons. This is the only precedence
rule on the card and it is why mute needs three channels rather than one.

**Starting playback clears mute.** He asked for music; delivering silence and a
`PLAYING` label is two states reading the same, which is the failure this repo
has already paid for once. The mute button un-lights in the same frame. This
applies to any start from the knob, not only at night.

### Everything else

| State | The card |
|---|---|
| **Nothing playing, daylight** | `IDLE`. A tap of play starts it. No prompt exists outside quiet hours. |
| **Paused at 03:00** | `PAUSED`, no prompt. The first tap of play arms — paused is not running, so AC-6 covers it. |
| **Playing at 03:00** | Exactly the noon card. No prompt, no badge, no dimmed control. |
| **Home Assistant time not yet valid** | Treated as quiet, and it shows the *same* prompt. There is no third face to learn, and the one guess that costs anything is guessing "not quiet". |
| **Home Assistant unreachable** | The card is what it was; the state line goes empty as it does today, and the refusal haptic is what a press earns. Adding an OFFLINE face is a change to all seven cards and belongs to its own issue. |
| **`is_volume_muted` absent from the attributes** | Read as unmuted. An empty string must not become a third mute state that shows nothing on the glass. |
| **Volume before HA answers** | `0%`, as today. |
| **Playlist name before HA answers** | `--`, as today. |
| **Longest real playlist name** | `KPop Demon Hunters` ≈ 280 px at `label_28` against `name_pl`'s `width: 300`. It fits, with about 20 px to spare, and it is the only one of the five that is close. Anything past ~19 characters ellipsises on `long_mode: DOT` rather than overflowing. |
| **One playlist option** | A turn produces a detent click and no change — honest, and indistinguishable from the bug being fixed here. The design assumes two or more. |
| **Many playlist options** | The walk is one detent per option. Past about eight it stops being reasonable and becomes the menu `REQUIREMENTS.md` refused. That ceiling is an `input_select` edit in Home Assistant, not a firmware limit. |
| **Boot** | Backlight 0%, unchanged. A power cut at 2 am must not light the room, and it must not arm anything either — the armed flag starts false and is cleared by the backlight's `on_turn_off`. |

---

## 7. What this design refuses

**A confirmation dialog.** No modal, no "are you sure", no OK/CANCEL. The prompt
is an instruction in the state line and the answer is a gesture. A dialog is a
page, the carousel is flat, and something you must dismiss at 3 am is worse than
the thing it was protecting you from.

**Making the confirm gesture a turn.** It was the tempting answer — a resting
palm cannot turn a knob, and winding up from zero would set the start volume in
the same motion. It is wrong for one reason: if he armed by accident and then
turns to leave the card, the turn starts the music. The recovery gesture must
never be the commit gesture.

**Letting a face hold confirm.** A face hold is what a palm produces. It arms and
only arms, on both surfaces.

**A double tap.** LVGL has no double-click, so it costs a ~350 ms window on every
tap on the card, including the mute tap that must land instantly under a hand
reaching for silence. That is the worst place on this device to spend latency.

**Gating anything while playback runs.** Pause, next, mute and the dial are free
at every hour with no extra gesture and no changed appearance. This is AC-8 and
it is also the reason the guard is acceptable at all.

**Capping the dial at 20% during quiet hours.** The cap belongs to the *start*,
which is the moment he cannot predict. Once music is playing he can hear exactly
what he is doing, and a dial that refuses to go up is a dial that feels broken.

**Repeating the playlist name on the MUSIC card while armed.** He read it at
28 px one second earlier on a page whose entire job was to show it. Repeating it
costs the state line, which is carrying the instruction.

**A fade-in ramp on the night start.** A volume that climbs on its own is a
volume he has to chase. 20% is a number; a ramp is a negotiation.

**Removing NEXT to make room for MUTE.** It is on the card today and this issue
did not ask for it to go. Four controls is a geometry problem and it was solved
as one.

**Any change to the LIGHTS, AC, FAN, SCENES, CLOSET or BATH cards**, including
the LIGHTS dial ramp, which shares `last_step_ms` and `spin_streak` with the
volume ramp and must keep its own constants exactly.

---

## 8. Findings against the data that exists

**1. No live Home Assistant read was possible from this session.** Both
`ha_get_state` and `ha_get_history` were refused permission. Everything above is
measured against `REQUIREMENTS.md`, the firmware, and the state facts a person
recorded on the issue.

**2. What that actually costs is one figure: the volume he leaves it at.** I
cannot say whether 20% is a small step down from his resting volume or a large
one, so I cannot say how surprising the capped start will feel. It does not
change any decision here — AC-7 fixes the cap at 20 — but it is the first thing
to look at during the hand check, and if 20% turns out to be inaudible against
the room, `night_vol_cap` is one substitution line.

**3. This page has never worked.** `input_select.bedroom_playlist` holds one
state record across ten days. Every design decision on `page_plist` is therefore
free of muscle memory, which is why BACK can move off centre.

**4. The transport path may make the confirm gesture lie, and this is the one
finding worth stopping on.** `REQUIREMENTS.md` records that a direct
`media_player.media_play_pause` on the Music Assistant entity does nothing during
an AirPlay session, and names that as how the wall buttons came to look dead. The
plan splits that call into `media_pause` / `media_play` but keeps it direct. If
that finding still holds, then at 3 am the guard arms, he holds, the card shows
`PLAYING`, and no sound arrives — a screen asserting a state that is not true,
which is exactly what this repo has already paid for once. **This is a bench
check for the Developer, not a design change:** confirm on the device that
`media_player.media_play` starts audio on
`media_player.master_bedroom_master_bedroom_wiim`, and if it does not, say so
rather than shipping a prompt that promises something it cannot deliver.
`script.room_media_smart_transport` exists for this and is already surveyed.

**5. The 0.85 volume cap in `REQUIREMENTS.md` is not in the shipped firmware.**
`value_move` clamps at 100. That is a real gap between a written requirement and
the device, it is not in this issue's acceptance criteria, and this design does
not close it. Recording it so it is not lost.

---

## 9. Glyphs

MDI glyphs are baked in at compile time and an unlisted one renders as nothing.
Three names must be added to the `mdi_44` `glyphs:` list:

| MDI name | Codepoint | Used by |
|---|---|---|
| `mdi:volume-high` | `U+F057E` | the mute control at rest |
| `mdi:volume-off` | `U+F0581` | the mute control while muted |
| `mdi:play` | `U+F040A` | the new play control on `page_plist` |

Verify each against materialdesignicons.com and paste the literal character —
this file never uses escapes. **Check the codepoint, not a character copied out
of this table.** The mockup renders all three from the MDI webfont by class name,
so what he looks at is self-verifying.

Already baked and unchanged: `mdi:playlist-music`, `mdi:play-pause`,
`mdi:skip-next`, `mdi:arrow-left`.

---

## 10. Numbers this design has to survive

**Geometry, against the 172 px safe radius.**

| Element | Worst corner | r |
|---|---|---|
| MUSIC row, 58 px at `x ±105, y 70` | (134, 99) | 167 ✓ |
| MUSIC row at 66 px, `x ±111` — why it was rejected | (144, 103) | 177 ✗ |
| PLAYLIST pair, 66 px at `x ±44, y 104` | (77, 137) | 157 ✓ |

**Strings.**

| String | Font | Width | Slot |
|---|---|---|---|
| `HOLD PLAY TO START` | `label_18` | ≈ 200 px | chord > 340 px at y = -6 ✓ |
| `KPop Demon Hunters` | `label_28` | ≈ 280 px | `name_pl` `width: 300` ✓ |
| `MUTED` | `label_18` | ≈ 62 px | ✓ |

**Repaint.** Every state here is a `label.update`, an `arc.update` and two
`widget.update`s on borders — the same shape as `paint_lights`, which already
runs on the LIGHTS dial. **No page is rebuilt while the dial moves**, which is
what keeps the 120 ms detent budget a budget rather than a hope.

**Haptics, all existing effects.** Arm → `fx_refuse` (13, soft fuzz — a buzz, not
a click, and distinguishable with the eyes shut). Confirm → `fx_power` (4, sharp
click 100%). Mute → `fx_power`. Detent → `fx_detent` (9), unchanged. No new
effect is introduced.

---

## 11. The mockup

`.aisdlc/run/mockup/` — 360 × 360 at 1:1, the firmware's own palette, and the
five real playlist names. Before and after, side by side, is the argument.

| | |
|---|---|
| `index.html` | Everything, before beside after |
| `01-music-before.html` | The card as it ships today — three buttons, no mute, no guard |
| `02-music-after.html` | Playing at 23:40. Four controls, and nothing else different |
| `03-music-armed.html` | 23:41, nothing playing, one tap of play: capped and asking |
| `04-music-muted.html` | Dead arc, live number, swapped glyph |
| `05-plist-before.html` | The sub-page today — one BACK button, a name that never moves |
| `06-plist-after.html` | BACK and PLAY, the walk working |
| `07-plist-armed.html` | The same prompt, the same words, on the sub-page |
| `08-plist-longest.html` | `KPop Demon Hunters` against the 300 px slot |
