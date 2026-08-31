# Design A — the knob is the bed light

Everything else is something you wound the ring to, and the ring winds back.

---

## 1. The question this screen answers

> *"How bright is the bed, and can I change it right now without opening my eyes?"*

Every other question this device answers — Masha's lamp, the wave, the volume, the
temperature — is answered on the way back from that one.

---

## 2. What the user does, in order

**The 3 am case, which is 95% of use.** The hand comes out from under the duvet and
turns the ring. The screen lights and the bed dims in the same motion; the first detent
is a real detent. Two or three more clicks, the hand goes back under, the screen fades
out 20 seconds later. Nothing was read.

**The occasional case.** The hand lands flat on the glass instead. After 250 ms the ring
becomes a strip of nine stops. The ring turns, one haptic click per stop, the 60 px word
in the middle naming each one as it arrives. The finger lifts on the one wanted, the word
shrinks to 28 px, that target's level takes the middle at 60 px, and from there it is the
same knob it always was — just pointed somewhere else for as long as the glass stays lit.

**Getting out of it.** Wind anticlockwise until the ring stops turning: that is BED,
found by feel, from anywhere, with a double bump to confirm. Or tap the glass, which
means BED and nothing else. Or do nothing for 20 seconds and let it go dark, which also
means BED.

**Finishing the night.** Palm on the glass, hold. At 1 s the room goodnight. At 3 s the
house follows. Let go before the first break and nothing was called.

---

## 3. Information hierarchy

### Shown at a glance — no gesture, first frame after wake

| | Why it is here |
|---|---|
| The value, 60 px, centre | The one thing this device exists to change. Exactly one per screen. |
| What that value belongs to, 28 px, above | Without it the number is a riddle. It is also the entire mode indicator — there is no separate one. |
| The arc | Magnitude at a glance with no reading at all, and the only element legible at 60° off normal from a pillow. |
| Front door unlocked, on wake only | The one house fact worth a bedside screen. Takes the whole face for 2 s, then gets out of the way. |
| A red dot at the bottom, while Home Assistant is unreachable | The single badge in the design. |

### Shown on demand — one gesture, and only for as long as the gesture lasts

| | Revealed by |
|---|---|
| That the other eight targets exist, and where they sit | A finger resting on the glass for 250 ms. Discovery is by touch, not by memory. |
| A target's current level, before you change it | Selecting it — it sits at 28 px under the name. |
| Track title | Being on MUSIC. It is a hint at what is playing, not a readout. |
| Room temperature, sleep timer remaining | Being on AC. One 28 px line, both facts. |
| Which stage a hold would commit | Holding. The word changes ROOM → HOUSE as the arc crosses the break. |

### Not shown at all

| Refused | Why |
|---|---|
| A clock | This is an IPS panel: dimming the backlight dims the glyphs and the ground together, so a "dim clock" is a grey coin glowing 150 mm from a sleeping face. Idle is off, and off is a feature. |
| Colour temperature in Kelvin | Nobody half asleep sets 4200 K. It rides the brightness dial; the arc's colour hints at it and its length carries the magnitude. |
| Entity names, entity IDs, area names | Nine words, chosen once, in his vocabulary. `light.tzb210_ue01a0s2_ts0502b_2` is a fact about Zigbee. |
| AC mode names — `cool`, `dry`, `heat_cool`, `fan_only` | App decisions, not 3 am decisions. A turn means cool. |
| Playlist, queue, artist, artwork, progress | Resuming what was playing is the whole need. |
| Any other target's state while you are on one | Eight labels around the rim plus a value is a debug page. |
| Notifications, repairs, updates, weather, WiFi bars, uptime | There are 13 open repairs in this Home Assistant and none of them belong on a nightstand. |
| Alarm state | It sits at `armed_home` permanently. A badge that is always on is not information. |
| A hint that the target strip exists | It would have to be lit, permanently, to teach something learned once. The 250 ms touch reveal does the same job and costs nothing while nobody is touching. |

---

## 4. Default state

**BED, at whatever the bed is currently at.** Not the last thing used, not what the
sensors suggest, not the most likely thing given the hour — the same target, every time.

The invariant is stronger than a default, and it is the load-bearing idea in this design:

> **When the glass is dark, the knob is the bed light. State is allowed to exist only
> while it is legible on the glass.**

So there is no target timeout to specify and no second timer to model. The screen sleeps
20 s after the last input; sleeping *is* the reset. If the knob is currently Masha's
lamp, the word MASHA is on the glass saying so, and it will be until the light goes out.

"BED" is not one entity. Between 06:00 and 22:00 it is one multicast to the ZHA group,
wave included. Between 22:00 and 06:00 it is his nightstand, Masha's nightstand and the
under-bed strip stepped individually with the wave left dark. The user's intent is "the
bed light" at both hours and the face says the same word at both hours;
`script.bed_strip_step` owns the difference, and the knob never learns it.

---

## 5. The interaction grammar

### The three verbs, each with exactly one meaning

| Verb | Means | Everywhere |
|---|---|---|
| **Turn** | more / less of the value in front of you | Never navigates. Wakes and acts on the same motion — no guard window, no free first detent. |
| **Touch and turn** | walk the target strip | The only way a target is ever chosen. |
| **Tap** | back to BED | Calls no service, from any state, at any time. |
| **Hold** | "I'm done with this" | Staged, visible, and released early it does nothing. |

### One finger down has exactly three futures

Put a finger on the glass and one of three things happens, decided by what the hand does
next, with no timeout you have to beat:

- **Turn** → the ring becomes the strip and you are choosing a target. A hold that has
  become a selection cannot become a hold again until the finger lifts.
- **Lift** (before 700 ms, no detent) → tap. Back to BED.
- **Stay still** → the hold arc starts filling at 700 ms and commits at 1 s.

There is no fourth outcome and nothing is ambiguous. That is the whole vocabulary.

### The strip

Nine stops. **It does not wrap.**

```
 wall                                                              wall
  |                                                                 |
 BED  ·  ME  ·  MASHA  ·  WAVE  ·  ALL  ·  CLOSET  ·  BATHROOM  ·  MUSIC  ·  AC
  ^                                                                        ^
 anticlockwise to the stop                              clockwise to the stop
```

Both ends are hard stops with a double haptic bump. That is the whole recovery story and
it needs no eyes and no counting: **wind it back and you are on the bed light; wind it
forward all the way and you are on the AC.** Those are the two things wanted at 3 am and
they are the two that can be found without counting. The seven in between are counted,
and they are the seven used in daylight, which is exactly the trade this design is making.

The strip is drawn on the rim as nine ticks in a 320° span with a 40° gap at the bottom.
The gap is the wall, drawn as a wall — a ring with a hole in it does not invite a spin
past the end. The same geometry carries every value arc, so 0% and 16 °C sit against the
same wall the strip does.

**No velocity acceleration on the strip.** One detent, one stop, always — a flick that
skips two stops destroys counting, which is the only way the middle seven are reachable.
Acceleration is on volume and temperature, where the ranges are long and the steps are
small, and off brightness, where a step is already 20 points.

### Every gesture, and what it calls

| Stop | Turn | Service called | Hold 1 s | Hold 3 s |
|---|---|---|---|---|
| **BED** | ±20 pp | `script.bed_strip_step` (`target: bed`) → group `light.home_assistant_connect_zbt_2_bedroom_led_strips` by day; `light.tzb210_ue01a0s2_ts0502b`, `light.left_nightstand`, `light.tzb210_ue01a0s2_ts0502b_2` individually by night | `script.bedroom_good_night` | + `script.house_good_night` |
| **ME** | ±20 pp | `script.bed_strip_step` (`target: me`) → `light.tzb210_ue01a0s2_ts0502b_2` | that light off / on | — |
| **MASHA** | ±20 pp | `script.bed_strip_step` (`target: masha`) → `light.left_nightstand` | that light off / on | — |
| **WAVE** | ±20 pp | `script.bed_strip_step` (`target: wave`) → `light.tzb210_ue01a0s2_ts0502b_3` | that light off / on | — |
| **ALL** | ±20 pp | `script.bed_strip_step` (`target: all`) → the five bedroom lights, wave and under-bed included | those lights off / on | — |
| **CLOSET** | ±20 pp | `script.bed_strip_step` (`target: closet`) → **entity not surveyed, see §7** | that light off / on | — |
| **BATHROOM** | ±20 pp | `script.bed_strip_step` (`target: bath`) → **entity not surveyed, see §7** | that light off / on | — |
| **MUSIC** | ±2 points, capped 0.85 | `media_player.volume_set` on `media_player.master_bedroom_master_bedroom_wiim` | `script.room_media_smart_transport` (`ma_player: media_player.master_bedroom_master_bedroom_wiim`, `native_player: media_player.khdr_shynh_2`) | `script.music_stop_all` |
| **AC** | ±0.5 °C, bounded 16–30 | `climate.set_temperature` on `climate.bedroom_ac`; from off, `climate.set_hvac_mode: cool` at the last target | restart `timer.mbr_ac_countdown` from `input_number.mbr_ac_timer_minutes` | — |
| *any* | **tap** | nothing — the face returns to BED | | |

Never called from any gesture: `script.house_all_off`, anything touching `lock.main_door`,
`alarm_control_panel.home_alarm`, `cover.garage_door`, `vacuum.kitchen_saros_10`.

### Haptics, which are the primary channel

| Event | Effect |
|---|---|
| Value detent | one click, quieter amplitude at night |
| 5% floor, 100%, volume cap 85, 16 °C, 30 °C | double bump |
| Strip stop | one softer click |
| **Either wall of the strip** | double bump — this is the "you are home" signal |
| Hold crossing 1 s, then 3 s | rising pattern, heavier at the second |
| Tap accepted | one click |
| **Gesture refused** (offline, silent speaker) | one long buzz — distinguishable from a click with the eyes shut |

---

## 6. Idle, wake, empty, error, extreme

| State | Face |
|---|---|
| **Idle** | Nothing. Black. Backlight zero, LVGL paused, no clock. |
| **Wake by turn** | The new value, already changed. This face has no separate "wake" frame. |
| **Wake by touch** | The current value at 60 px, its name at 28 px, the arc. |
| **Wake, door unlocked** | `FRONT DOOR` / `UNLOCKED` in red, whole face, 2 s or until the next gesture. No arc, because nothing here can be set. |
| **Home Assistant unreachable** | `OFFLINE` in the name slot, last known value greyed to `#3a2400`, a red dot at the bottom that persists, and a refusal buzz on every detent. No modal. Nothing to dismiss. |
| **MUSIC with nothing playing or paused** | `MUSIC` / `SILENT`. A turn is refused rather than adjusting a silent speaker — but hold still resumes, which is the whole point of the stop. It is not a dead screen. |
| **AC off** | `AC` / `OFF`. The first detent turns it on in `cool` at its last target rather than nudging a setpoint nothing is chasing. |
| **Track title unrenderable** | The source name instead — `AIRPLAY`. Montserrat is ASCII, LVGL does not shape RTL, and boxes or blanks teach the user something false. |
| **A strip already off, turned down** | Stays off. The 5% floor and the never-switch-off rule live in `script.bed_strip_step`, so they apply identically to every stop. |
| **Longest string on the glass** | `BATHROOM`, 8 characters at 60 px, against a 9-character chord at y = 0. Nothing on this device can be longer except the track title, which is width-bounded and ellipsised. |
| **Boot** | Backlight 0%. A power cut at 2 am must not light the room. |

---

## 7. What this design refuses, and the argument for each

**A mode carousel.** There is no Light / Volume / AC to be in, so there is nothing to
lose track of. Music and the AC are stops on the same strip as the lamps, reached by the
same gesture, drawn on the same page. One selection axis instead of two means one thing
to learn and one thing to recover from, and the recovery is the same motion in both cases.

**A wrapping ring.** Wrapping would put every stop three clicks from every other stop and
would remove the only thing on this device you can locate blind. A wall you can feel is
worth more than a shortcut you have to count.

**Remembering the last target.** The most seductive feature here and the one that breaks
the promise: a knob that remembers is a knob whose behaviour depends on something that
happened hours ago, to a person who is now asleep. Reaching in the dark and dimming
Masha's lamp because that is where you left it is exactly the failure this design exists
to prevent. The target lives only while the glass is lit and naming it.

**A second timer for the target.** One timeout, 20 s, doing both jobs. Two timers is two
mental models and a window in which the screen is lit and the state has already changed
underneath it.

**Double tap.** LVGL has no double-click, so it costs a ~350 ms window on *every single
tap* — and in this design the tap is the recovery gesture, the one thing that must land
instantly under a confused hand. That is the worst possible place on the device to spend
latency. Three touch gestures are already distinct and already free: tap, hold-1 s,
hold-3 s.

**Tap position — left half / right half of the glass.** It is free in hardware and it is
the wrong kind of free. A positional tap is remembered, not felt, and a miss is silent:
you meant Masha's side, you hit the middle, and nothing tells you. Every selection in
this design is confirmed by a detent you can feel and a word you could read if you opened
an eye.

**Press-and-turn as a second value axis.** The gesture is spent on target selection, and
it can only mean one thing. A palm resting on the glass while the ring turns must never
mean "and also change the track".

**An AC-off gesture.** Turning the air conditioning off by accident on a 34 °C Tel Aviv
night is the worst thing this device could do to him, and the smart-cycle automations
already decide when to stop cooling. The hold restarts the 85-minute sleep timer, which
is the real off switch. The knob can turn the AC on and cannot turn it off; that
asymmetry is deliberate and it points the safe way.

**Play/pause on the tap.** It would be the obvious convenience and it would cost the
universal meaning of the tap. Transport is on the hold, where "I'm done with this" already
lives.

**A local fallback path to the lights when Home Assistant is down.** It would duplicate
the dimming policy — the night rule, the 5% floor, the warmth curve — in a second place
that drifts. The honest indicator is the correct feature.

**Guards on the first gesture after wake.** None. The device behaves identically whether
the glass was lit or dark, which is one less thing to know at 3 am. This is affordable
here only because nothing on the knob is irreversible: the destructive services were
refused at design time rather than gated at runtime. A goodnight leaves the under-bed
strip lit and the AC running; a lamp toggles back; the lock, the alarm and the garage are
not reachable at all.

**Anything that has to be read.** Nine words exist on this device and eight of them are
room names he chose. The one screen with prose on it is the front-door banner, and it
appears when the front door is open.

---

## 8. Findings against the data that actually exists

**Two of the seven light targets have no surveyed entity.** `REQUIREMENTS.md` names every
bedroom light, the WiiM pair, the climate entities and the lock. It names no entity for
the closet room and none for the bathroom — the only closet device in the survey is the
TS004F rotary, which is a controller, not a light. `CLOSET` and `BATHROOM` are drawn on
the strip and their positions are fixed, but they cannot be wired until those two
`entity_id`s are surveyed. **This blocks two of the nine stops and nothing else** — the
strip's geometry does not change when they arrive.

**`script.bed_strip_step` needs a `target` field.** It currently *is* the bed policy;
seven targets need seven policies, and they must not move into firmware or the night rule
and the 5% floor end up in two places. One field, defaulting to `bed`, keeps every
existing caller working and keeps the dimming policy where `HARDWARE.md` insists it lives.
The hold's off/on for a single lamp goes through the same script for the same reason.

**"All lights together" is ambiguous.** Read here as every dimmable light in the bedroom —
the five, wave and under-bed included — because closet and bathroom are listed separately
beside it. If he meant every light in the house, that is a different stop and a different
script, and it should be said before it is built.

**Montserrat Medium, not Regular.** The ESPHome default weight reads thin at 60 px on
black at low backlight. One extra compiled weight, one rebuild.

---

## 9. The open decisions, answered

| # | Answer |
|---|---|
| 1. Encoder push | Settled by the board. Tap and hold are touchscreen events; the LRA supplies the click. |
| 2. House goodnight and Romi's spots | **Stage 2 skips the kids' lights.** A knob at his bedside must not darken a room with a child in it, and the 3 s hold is exactly the gesture a half-asleep hand overshoots into. Add the exclusion to `script.house_good_night`, or a `skip_kids` field — either way the policy stays in Home Assistant. |
| 3. Warmth curve, 2000 K → 4000 K | Keep it. 100% is a daytime value; the top of the curve is never seen at 3 am. |
| 4. An idle clock | **Refused.** On this panel a dim clock is a whole grey disc glowing 150 mm from a sleeping face, not four glowing digits. Idle is off. |
| 5. AC's hold | **Restart the sleep timer.** There is no AC-off gesture — see §7. |

---

## 10. What he configures

The strip is a list, not a layout. Position 0 is BED and the far end is AC — those two are
structural, because they are the two ends you find by feel. **Everything between them is
one ordered list he edits**, and adding a stop, reordering the middle, or pointing a stop
at a scene instead of a light changes nothing on the glass except the words that appear
while a finger is down. Nine stops is what the strip holds comfortably at 40° apart; more
than that and the ticks stop being countable, which is the real limit.

---

## 11. The numbers this design has to survive

**Geometry.** One ring at r = 160, stroke 8 → outer edge 164, inside the 172 safe radius.
Three text slots and no more: 28 px centred at y = 102, 60 px centred at y = 180, 28 px
centred at y = 260. Against the chord table: the 60 px slot allows 9 characters and the
longest string on the device is `BATHROOM` at 8; the 28 px slots allow ~15 characters at
`letter_space: 2` and the longest are `FRONT DOOR` at 10 and `ROOM 26 · 85M` at 13. The
track title is the one runtime string and carries `width:` and `long_mode: DOTS`.

**Night lit-area budget.** Worst case on the glass is BED at 80%: arc 715 px × 8 px stroke
= 5 720 px², plus `80%` at 60 px ≈ 1 540 px² of ink, plus `BED` at 28 px ≈ 340 px².
Total ≈ 7 600 px² against a 101 788 px² disc — **7.5%**, against a 15% ceiling. The
selection screen is lighter still: nine 20 px ticks and one word.

**Night palette.** `#805000` primary, `#5e3a00` labels, `#241500` arc track, `#800000`
warnings, amber ramp `#601400` → `#806018` standing in for 2000 K → 4000 K. No channel
above `0x80`, no blue above `0x20`, background `#000000` on every screen. Day mode uses
white and a true colour-temperature arc.

**Repaint budget.** Every stop draws the same page: one ring, three text slots. A detent
repaints the number and the arc — **there is no page to rebuild, in any mode, ever**,
which is what makes 120 ms a budget rather than a hope. The two ring modes (value arc,
strip) are a single widget with different geometry, swapped by one partial repaint at
250 ms of contact.

---

## 12. The mockup

`mockup/index.html` — every state side by side, with the strip drawn and the grammar on
one line each. Individual states, 360 × 360 at 1:1:

| | |
|---|---|
| `01-idle.html` | Nothing. Black. |
| `02-wake-bed.html` | Woken by touch: BED, 60%, night palette |
| `03-door-unlocked.html` | The front door is not locked |
| `04-light-adjusting.html` | One detent up, 80%, arc warming |
| `05-target-select.html` | Finger down, wound two clicks to MASHA — the strip and both walls |
| `06-target-armed.html` | Lifted on MASHA: the same page, a different word |
| `07-hold-goodnight.html` | Held 1.4 s, past the first break, ROOM armed |
| `08-music.html` | Volume 32, title, the 85 cap as the arc's wall |
| `09-climate.html` | 25.5 target, room 26, 85 minutes left |
| `10-offline.html` | Lit and inert, and saying so |
| `11-day-bed.html` | 14:00, white type, true-colour arc |
| `12-music-unrenderable.html` | A Hebrew title, fallen back to the source name |
