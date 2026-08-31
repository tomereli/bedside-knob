# Design B — the glass is a map

## The question this screen answers

> "I want the bathroom light — that one, not a menu of lights — and I want it
> before I am properly awake."

## The idea

The round glass is a fixed map of ten addresses. A position on it means a thing,
permanently. **Turn with nothing touched and you have the bed.** Put a thumb on
a place and turn, and you have that thing for as long as the thumb is there. Let
go and you are back on the bed.

There are no modes. Nothing cycles, nothing times out into something else, and
there is nothing to exit. The cost is a layout that has to be learned once. What
it buys is that every target the brief names is one gesture away, from black,
with the eyes shut.

The device's natural grip is already this gesture: on a 66 mm knob with 45 mm of
glass inside a metal ring, the thumb rests on the glass while two fingers turn
the ring. Design B does not invent a posture. It gives the one the hand already
uses a meaning.

## The layout, and the one thing to learn

```
                    THE WAVE
             AC                 FAN
       MASHA        THE BED        MY SIDE
            CLOSET            MUSIC
                    BATHROOM

              the outer edge  =  ALL
```

Five sentences, and they describe a room rather than a list:

- **The middle is the bed.** You are in the middle.
- **The top is the wave**, because the wave is on the wall above your head. The
  air is either side of it: fan on your side, AC on hers.
- **Left and right are the two sides of the bed.** Yours on your side.
- **The bottom is the bathroom** — the way out. Music and the closet either side.
- **The outer edge is everything.**

`MY SIDE` at 3 o'clock and `MASHA` at 9 o'clock assume the knob stands on the
right-hand nightstand seen from the foot of the bed. If it stands on the left,
those two bearings swap. It is a pair of constants and a ten-second check in the
room.

### Why these bearings and not others

Cardinal positions (12, 3, 6, 9) are the ones a blind hand hits reliably, so the
four highest-consequence addresses live there. The diagonals are narrower to
find and carry the four that tolerate a miss. A miss costs nothing anyway:
**touching a zone only addresses it. Nothing in the room changes until you turn,
or lift.**

The hub is 236 px across — 30 mm of a 45.7 mm disc, 43% of the glass area. A
thumb that lands without aiming gets the bed, which is the thing a hand that
landed without aiming wanted.

## What the user does, in order

**The 3 am walk, which is the whole product:**

1. Hand comes out from under the duvet and finds the knob by feel — metal ring
   outside, glass inside.
2. Thumb lands on the bottom of the glass. The backlight starts its 400 ms fade,
   a sharp click fires under the thumb, and `BATHROOM` prints at 60 px.
3. Thumb lifts. The mirror light comes on in the bathroom. The screen now reads
   `MIRROR`.
4. Twenty seconds later the screen is black again.

One gesture, from black. He never read anything; the screen was confirmation,
not instruction.

**The other path, more often:** the ring turns. The bed dims on that same
detent, and the screen comes up already showing the new value.

## Interaction grammar

Four verbs, and each means the same thing at every address.

| Verb | What it does | Never |
|---|---|---|
| **turn**, nothing touched | the bed's level | navigates |
| **touch a place, then turn** | that place's level, while the thumb is down | navigates |
| **tap** (touch and lift) | that place's on/off | changes a level |
| **double tap** | that place's saved level | anything else |
| **hold** | that place's one large action, in visible stages | fire before its first stage |

**A turn wakes and acts on the same detent.** There is no free first detent and
no wake guard. `HARDWARE.md` §3 and §5 specify both; this design does not have
them. Latency is the product, and a hand on this device is a hand that meant it.

**A touch on a dark screen addresses and acts too.** Landing on a place selects
it; lifting commits its tap. Selection alone changes nothing in the room, so the
dangerous half of the gesture is the half that requires a deliberate lift.

**Taps act immediately; a second tap inside 350 ms supersedes the first.** The
alternative is making every single tap wait 350 ms to find out whether it was
half of a double, which is the one cost this device cannot pay. The visible
price: double-tapping a lit light blinks it off and back to its preset. That is
the right trade and it is the only place it shows.

**Releasing returns to the bed.** Always, immediately, with no timeout. The knob
a cold hand finds is the bed knob, exactly as it must be.

**The rim will not accept a turn in its first 250 ms.** It is the one address
whose scope is the house, and it is the one a resting thumb can reach by
accident. A deliberate reach-and-turn takes longer than 250 ms; a thumb that
lands and immediately spins is refused, with the refusal pattern under it.

### Timing

| | |
|---|---|
| backlight fade | 400 ms up, 1000 ms down |
| idle to black | 20 s |
| double-tap window | 350 ms |
| hold: room stage | 1000 ms |
| hold: house stage | 3000 ms |
| optimistic state held | 1500 ms, then Home Assistant wins |
| rim turn guard | 250 ms from touch-down |

### Haptics carry the address

The LRA is the confirmation channel, because it works with the eyes closed.
Distinguishing ten effects by feel is not realistic; distinguishing four
**classes** is, and the class is exactly what disambiguates a near miss — you
meant the bathroom at 6 and caught music at 4:30, and the wrong class arrives
under your thumb before you have turned anything.

| Landed on | Feels like |
|---|---|
| hub | one soft bump |
| a cardinal place (12, 3, 6, 9) | one sharp click |
| a diagonal place | two quick clicks |
| the rim | a short buzz |
| each detent | one bump |
| 5% floor, 100% ceiling | double bump |
| refused | two long low buzzes |
| hold armed at ROOM / HOUSE | rising triple, longer at HOUSE |

Night mode uses the same patterns at lower amplitude. An LRA against a hard
nightstand ticks audibly; the device sits on a felt pad.

## Address map to Home Assistant

Every entity below was read from the running system, not from the requirements
document.

| Where | Turn | Tap | Double tap | Hold |
|---|---|---|---|---|
| **hub** — the bed | `script.bed_group_step`, ±20 pp | bed group on/off | saved level | `script.bedroom_good_night` at 1 s; **+** `script.house_good_night` at 3 s |
| **12** — the wave | `script.bed_strip_step` `light: light.tzb210_ue01a0s2_ts0502b_3`, `step: ±20` | that light on/off | saved level | save this level |
| **1:30** — fan | `script.mbr_fan_speed_step` (cycles `switch.khdr_shynh_rshy_kh_shynh_myth_shml_l_mzvhh_2`) | fan on/off | saved speed | `light.master_bedroom_ceiling_fan` on/off |
| **3** — my side | `script.bed_strip_step` `light: light.tzb210_ue01a0s2_ts0502b_2` | on/off | saved level | save this level |
| **4:30** — music | `media_player.volume_set` on `media_player.master_bedroom_master_bedroom_wiim`, capped 0.85 | `script.room_media_smart_transport` | next track | `script.music_stop_all` |
| **6** — bathroom | `script.bath_step`, one rung a detent | rung 1 if dark, else off | saved rung | save this rung |
| **7:30** — closet | *nothing to turn* | `switch.khdr_shynh_rshy_khdr_rvnvt` toggle | — | — |
| **9** — Masha | `script.bed_strip_step` `light: light.left_nightstand` | on/off | saved level | save this level |
| **10:30** — AC | `climate.set_temperature` on `climate.bedroom_ac`, ±0.5 °C, 16–30 | on/off, `cool` at last target | saved target | restart `input_number.mbr_ac_timer_minutes` / `timer.mbr_ac_countdown` |
| **rim** — all lights | `script.all_lights_step` over `light.home_assistant_connect_zbt_2_zbt_all_lights` | *refused* | — | show the map |

The bathroom's three rungs, in order: `..._mrh` (mirror) → `+ ..._mrkz` (centre)
→ `+ ..._spvtym` (spots), all on `switch.khdr_rkhtsh_rshy_kh_rkhtsh_rshy_*`.
Rung 1 is the existing N1-5 "Night" key: mirror only, everything else dark. The
extractor fan `..._vvnth` is on the same panel and is deliberately not on the
knob.

**`ALL` raises only what is already lit.** Turning down dims the house toward
its floor; turning up touches nothing that is off. Without that rule an upward
spin at 3 am lights the kitchen at 5%.

### Findings from the real system

1. **`script.bed_strip_step` already takes a `light:` parameter** and any
   `light` entity satisfies its selector. Seven light targets therefore need no
   new dimming policy — the night rule, the 5% floor and the absolute-target
   computation are reused verbatim, once per address. This is the single biggest
   reason the design fits the existing house.
2. **The bathroom and the closet are relays, not dimmers.** The closet is one
   switch; the bathroom is four. Neither has a level. A knob that could only
   turn would have nothing to offer either of them — which is precisely the
   argument for addressing rather than turning: they get a one-gesture switch,
   which is what they actually need, and the bathroom's relays make a real
   three-rung ladder that the eight-key panel cannot walk.
3. **The bedroom ceiling fan has no `fan.` entity.** Speed is a momentary Vitrea
   key that cycles. There is no percentage to set, so the fan's turn steps rungs
   and stops at the top rather than wrapping.
4. **`script.bed_strip_step` sets brightness only.** The 2000 K→4000 K warmth
   curve in `REQUIREMENTS.md` is not implemented anywhere. Because warmth is a
   pure function of level, the gauge's amber depth is correct either way — the
   screen is already right, and stays right when the script gains the line.

### Home Assistant surfaces this needs

Three new scripts, and one lifted from an automation. Each exists because a
policy belongs in Home Assistant rather than in firmware:

- `script.bath_step` — the rung ladder over four relays.
- `script.all_lights_step` — the whole house, raising only what is lit.
- `script.mbr_fan_speed_step` — the key-cycle, rate limited.
- `script.bed_group_step` — the day/night branch (group multicast 06:00–22:00;
  three strips individually otherwise). This logic exists today inside
  `automation.closet_knob_rotate_dims_the_led_strips`. Lifting it into a script
  lets both knobs share one implementation instead of drifting apart.

Saved levels live in Home Assistant, one helper per address, because a reflash
must not erase them.

`allow_service_calls` must be on, or every one of these does nothing, silently.

## Information hierarchy

**At a glance — one thing, 60 px, exactly one per screen:**

The value. While a place is held and nothing has happened yet, its name instead
— the name is on screen only for as long as the thumb is down and idle, and the
first detent or the lift replaces it. This is the only text on the device that
must be legible at 3 am, and it is legible at 600 mm off a pillow.

**On demand — 28 px, inside the hub, nine characters:**

One fact that the value cannot carry: room temperature under an AC setpoint, the
source and transport state under a volume, `NO LINK`. Nothing else earns it.
`HARDWARE.md` puts 28 px at "readable when alert, not when half asleep", so this
line is deliberately dim and deliberately optional.

**The address is not text.** It is the lit wedge, its bearing, and the haptic
class. That is the design: position replaces reading.

**20 px appears on one screen only** — the labelled map, which is a setup card.
Nothing at 3 am is written at 20 px.

**Not shown, and why:**

| Left out | Why |
|---|---|
| which entities a group contains | the wedge is the answer; a list of five entity names is a debug page |
| colour temperature in kelvin | it rides the level and nobody sets it separately |
| what is playing, in full | 28 px buys about 18 characters, and Montserrat has no Hebrew. Strip what cannot be drawn; fall back to the source name rather than to empty boxes |
| brightness of every zone at once | eight numbers around a rim is the debug page `HARDWARE.md` names |
| notifications, repairs, updates, weather, battery | thirteen open repairs, none of which belong on a nightstand |
| a clock | this panel cannot show one without glowing as a whole grey coin 150 mm from a sleeping face |
| the alarm, the garage, the vacuum, the blinds | not reachable, by construction |

## Default state

Black. Not dimmed — off, after 20 s.

The default **address** is the hub: the bed. It is the default because it is what
a hand that did not aim will hit, what a turn with nothing touched addresses,
and what every release returns to. There is no other resting state to get lost
in.

## The face

### Geometry

| Band | Radius | Carries |
|---|---|---|
| type | 0–104 | the 60 px value; the 28 px line at y = +56 |
| gauge | 104–116 | the value as an arc, clockwise from 12 |
| map | 118–150 | eight places |
| rim | 150–172 | all lights; drawn as a 2 px ring at 168 |
| hub touch | r < 118 | the bed |

**Two rings, two questions. The outer ring says which. The inner arc says how
much.** The arc is in the same place whatever is addressed, so the eye never
hunts for it, and a bearing means something everywhere on this device.

Wedges are **drawn** with 5° gaps so the spokes read, and **touched** with no
gaps at all: every point of the glass belongs to exactly one address, assigned
by nearest centre. There are no dead zones to land in.

Type is drawn last and never yields to the map. A 60 px word longer than five
characters crosses the gauge and the wedge outlines; it stays legible because it
is twice their brightness, and the alternative — shrinking it — is worse.

### Night palette

Every colour is RGB565-legal, no channel above `0x80`, and blue is `0x00`
throughout.

| | Hex | Max channel | Use |
|---|---|---|---|
| background | `#000000` | — | always, day and night |
| map | `#200c00` | 12% | dormant wedge outlines |
| field | `#381400` | 22% | the addressed wedge, the gauge fill |
| label | `#481800` | 28% | the 28 px line |
| hub ring | `#582000` | 35% | the hub, addressed |
| value | `#804000` | 50% | the 60 px primary, and the needle |
| alert | `#802000` | 50% | the door, faults |

**Lit-area budget.** At night no more than 15% of the disc may sit above 30%
grey. Only `value`, `alert` and `hub ring` clear that line. On the brightest
ordinary screen — a four-character value, the needle, and the hub ring — that is
2 241 + 60 + 1 659 = **3 960 px² of 92 941, or 4.3%**. The worst screen on the
device is the door alert at **6.1%**. The map, the fill and the 28 px line are
all below the line and cost nothing against it.

The map is therefore nearly invisible at the night ceiling, and that is correct:
at 3 am the hand already knows it. The map is ink for the learning weeks and for
daylight, and it brightens with the backlight.

### Repaint budget

A detent repaints **the numeral's box and the gauge's newly swept arc. Nothing
else.** The map, the hub ring, the rim ring and the 28 px line are static, and
the addressed wedge cannot change while a thumb is down. There is no page
rebuild on the detent path, which is what the 120 ms budget requires.

A grab repaints more — one wedge fills and a name prints — but a grab is not on
the detent path and has the 400 ms backlight fade to hide behind.

## States

| State | Face |
|---|---|
| **idle** | black |
| **wake by turn** | hub ring lit, arc at the bed's level, the value at 60 px |
| **place held, nothing done yet** | that wedge filled, its name at 60 px |
| **turning** | the value at 60 px, arc and needle following |
| **hold in progress** | the arc becomes the hold: the room stage is the first third, marked with a break; the house stage closes the circle. Dim means not yet, bright means armed, and the haptic rises at each |
| **AC off** | `OFF` at 60 px, `ROOM 26` under it. The first detent turns it on in `cool` at the last target |
| **nothing playing and nothing paused** | `PLAY` at 60 px and the source under it — what a lift would do, not a dead `n/a`. A turn is refused with the refusal pattern rather than adjusting a silent speaker |
| **door unlocked at wake** | `UNLOCKED` at 60 px in alert red, `FRONT DOOR` under it, map suppressed. It is the only thing on the glass, ahead of any value |
| **Home Assistant unreachable** | the arc goes dashed — permanently, quietly, no modal. The number is the knob's guess, not the house's answer. Every gesture gets the refusal pattern, so a hand with the eyes shut learns immediately |
| **a light is off** | `OFF`, and a turn up wakes it at 5% between 22:00 and 06:00, per the existing script. A turn down never wakes anything |

## What this design refuses

- **A menu, a list, a carousel, and any mode that has to be entered or left.**
  The brief says a menu that must be read is a failure. Every alternative that
  cycles through targets is a menu with the labels taken away.
- **A tap on the rim.** Everything is the one address whose accidental toggle
  would be felt in five rooms. It has a level and a map, and no switch.
- **`script.house_all_off`, from any gesture.** It is the leaving-the-house
  script. The 3 s hold runs `script.house_good_night`, which leaves the hallway
  at 10% and the under-bed strip lit.
- **Anything that opens the front door, touches the alarm, the garage or the
  vacuum.** Not guarded — not addressable. There is no bearing that reaches them.
- **A latch after release.** A "stay on this target for four seconds" would make
  the one-handed case marginally easier and would put a mode back in, with a
  timeout, which is the thing this design exists to not have.
- **An idle clock.** Not a preference — this panel cannot draw one without
  lighting the whole disc.
- **Colour on the warmth arc at night.** The top of the dimming curve is a
  near-white with real blue in it. The arc ramps through amber and length
  carries the magnitude.

## Before this is built

Three measurements, all cheap, all of which move numbers on this page:

1. **Which side of the bed the knob stands on.** It decides two constants.
2. **The bearings of the bathroom and closet doors from the pillow.** The rule
   is "point where it is"; the mockup shows 6 o'clock and 7:30.
3. **The lowest backlight duty that still lights**, on this unit. The night
   ceiling sits just above it, and the map's `#200c00` is the first thing that
   disappears below it.

## Mockup

`mockup/index.html` is all twelve states side by side. Each is also a standalone
file, rendered at 360 × 360 on black, in the night palette, with real values read
from the running house — the WiiM paused on the TV source at volume 25, the AC
cooling to 25.5 in a room at 26.
