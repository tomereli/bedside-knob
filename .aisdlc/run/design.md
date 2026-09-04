# Design — an off card must not show a full ring

Issue: https://github.com/tomereli/bedside-knob/issues/3 (`size:S`, `needs:ux`)
Surfaces: `page_ac` / `page_fan`, `arc_ac` / `arc_fan`, `paint_ac` / `paint_fan`.
Mockup: `.aisdlc/run/mockup/index.html`

## The question this screen answers

**"Is it on, and how high?"** — from the pillow, at arm's length, in the dark,
answered before any text is read.

Today the card answers the second half and lies about the first.

## The rule

> **A track is only ever drawn under an indicator.**

The dark ring is not a decoration and not a frame. It exists for one purpose:
to give the bright ring a scale to be a fraction of. Draw it alone and it stops
being a track and becomes a claim — a full-length ring, in the card's hue, at
the card's radius, in a room where hue and shape arrive at the eye long before
`OFF` does.

So: **off draws no ring at all**, and **on draws both rings, with the indicator
floored to a length that cannot be mistaken for absence.** Off and on differ in
presence. On differs from on by length. Neither reading needs the number.

This rule is written to outlive the issue. LIGHTS, BATH, CLOSET and MUSIC carry
the same defect and are out of scope here; whatever the lights redesign puts on
those cards should inherit this sentence rather than re-derive it.

## What the user does here

1. **Sees the card arrive.** A turn brought them here from the neighbouring
   card. The first thing that lands is the shape at the rim: a ring means the
   thing is running, no ring means it is not. Icon and hue say which card.
2. **Reads the middle**, only if the answer to "is it on" was yes, and only if
   they care about the exact figure. `23.0`, `4`.
3. **Reaches for the gesture.** Hold toggles power. Tap opens SET and the ring
   and number turn white; a turn then moves the value on the spot.

Step 1 is the one this issue is about, and it is the only step that happens
every single visit.

## Information hierarchy

Home Assistant offers far more about a climate and a fan entity than a 360 px
circle should ever accept. The census below is the `climate` / `fan` domain
attribute sets plus what `bedside-knob.yaml` already binds; the live entities
were not queried from this session, so treat the "offered" column as the domain
contract rather than a reading of these two entities.

### AC card — `climate.bedroom_ac`

| Field | Rank | Where |
|---|---|---|
| on / off | **at a glance** | Presence of the ring. Nothing else. |
| `temperature` (target) | **at a glance** | Length of the indicator, and the 60 px figure. |
| `current_temperature` | **on demand** | `ROOM 26`, 28 px, below the figure. Answers "is it getting there", which is a second question and gets second billing. |
| `hvac_mode` beyond on/off (`cool`, `dry`, `fan_only`, `heat`, `auto`, `heat_cool`) | **not shown** | Which mode it is running in is an app decision, not a 3 am decision. Collapsed to the one bit the ring carries. |
| `hvac_action` (`cooling` / `idle`) | **not shown** | Flickers on the compressor's own cycle. A rim that changes while nobody touched it teaches the eye to distrust the rim. |
| `fan_mode`, `swing_mode` | **not shown** | The FAN card is one detent away and is about air moving. Two fan controls on one strip is worse than one. |
| `min_temp` / `max_temp` | **not shown** | Already spent — they are the two walls of the sweep. Printing them would be printing the ring in words. |
| `preset_mode`, `humidity`, `friendly_name` | **not shown** | Never set from here, and the card is titled by being the AC card. |

### FAN card — `fan.master_bedroom_ceiling_fan`

| Field | Rank | Where |
|---|---|---|
| on / off | **at a glance** | Presence of the ring. |
| `percentage`, as step 1–6 | **at a glance** | Length of the indicator, and the figure. |
| the scale | **on demand** | `OF 6`, 28 px, and only while on — an off fan is not "0 of 6", it is off. |
| `oscillating`, `direction` | **not shown** | Set twice a year, from a phone. |
| `preset_mode`, `percentage_step` | **not shown** | The six steps *are* the step size, made visible as six lengths. |

Nothing free-text reaches either card. Nothing arrives on the glass that the
hand cannot act on from the glass.

## Default order

Not a list, but the equivalent question — what is on screen before anyone
touches a control — has an answer that this issue changes, and it is the
important one:

**Before Home Assistant has spoken, the card shows no ring.**

`on_boot` runs `paint_all` two seconds in, and `api.on_client_connected` runs
it again two seconds after the link comes up. Between those, `ha_ac_mode.state`
is the empty string and `ac_target` is its initial `24.0`. Today that draws a
57 % blue ring and the figure `24.0` — the card stating, with total confidence,
a value nothing has told it. `hidden: true` on the widget alone does not fix
this, because `paint_all` runs and shows it.

An unknown state gets the off appearance, because "no ring" is the honest
picture of "the knob has not been told." A knob that has lost Wi-Fi should look
like it knows nothing, not like the room is cold.

**This requires the on-test to be a whitelist, not a blacklist.** `state != "off"`
is true for `""`, `"unknown"` and every future surprise, and every one of those
failures draws a ring. HA's `HVACMode` is a closed enum, so a positive test is
complete:

```
cool · heat · dry · fan_only · auto · heat_cool   →  on, draw the ring
everything else, including "", "off", "unavailable", "unknown"  →  no ring
```

Fail closed. If this list is ever wrong, a running AC shows no ring — visible,
annoying, and the safe direction. The other direction is the bug being fixed.

## The states

Every face below is in the mockup. Colours, radius, stroke, angles, fonts and
text positions are the values in `bedside-knob.yaml` today and are unchanged by
this design.

| State | Ring | Middle | Sub |
|---|---|---|---|
| AC off | none | `OFF` | empty |
| AC unavailable | none | `OFF` | empty — `ha_ac_current` goes NaN with the entity, and `sub_ac` already returns `""` on NaN |
| AC unknown / pre-link | none | `--` | empty |
| AC on 16.0 °C | track + **8 %** stub | `16.0` | `ROOM 26` |
| AC on 23.0 °C | track + 54 % | `23.0` | `ROOM 26` |
| AC on 30.0 °C | track + 100 % | `30.0` | `ROOM 26` |
| FAN off | none | `OFF` | empty |
| FAN step 1 | track + 16 % | `1` | `OF 6` |
| FAN step 6 | track + 100 % | `6` | `OF 6` |

### The floor

**`MIN_ON = 8`** on the 0–100 scale, named once and applied to both cards.

- 8 % of the 320° sweep is **25.6°**.
- At r = 159 that is **71 px** of arc, against a 10 px stroke — seven times its
  own thickness. It is a segment of a ring, not a dot, not a rounding artefact,
  and not something the eye files under "nothing there".
- Against the full sweep's 888 px it is 8 %. Nobody reads 71 px as 888 px.

A shorter floor was considered and rejected: 5 (16°, 44 px) survives on a
monitor and does not survive being glanced at, out of focus, from a pillow.

**AC** remaps its on-range onto the floor: `8 + (t − 16) × 92 / 14`, clamped
0–100. 16.0 °C is the shortest on-state, 30.0 °C is full, and each 0.5 °C detent
moves 3.29 units — 10.5° of sweep, 29 px. Every detent is visibly a detent.

**FAN** keeps `fan_step × 100 / 6` and applies the same clamp as a floor, not a
mapping. Step 1 already yields 16, so the clamp never fires and no on-state
moves. It is written anyway so the rule reads identically on both cards — and
deliberately *as a floor*, because that expression is the same one sent to
`fan.set_percentage`. Remapping the arc would let the ring and the fan drift
apart, which the existing comment at line 964 exists to prevent.

### Transitions

Ordering matters and is part of the design, not an implementation detail:

- **Turning on:** set the value, *then* show. Never a frame of a stale length.
- **Turning off:** hide. The whole ring leaves at once.
- **FAN spun down 1 → 0 inside SET:** the fan turns off by rotation, so the ring
  vanishes on that detent while the figure goes `1` → `OFF` and the sub-line
  empties. Three things change together on one click of the wrist. That is the
  loudest confirmation this face can give, and turning the fan off with a spin
  is exactly the moment that deserves it.
- **Spun back up 0 → 1:** the ring returns at 16 %, from nothing.

### SET is untouched

Tap turns the figure and the indicator white. White is not the card's hue, so
an off card cannot be reached in SET and made to draw a hue ring; and a white
ring at a length is unambiguous about being a value being edited. No change.

## What this design refuses

**A neutral-grey track on an off card.** It satisfies the letter of the
acceptance criteria — not "in the card's hue" — and fails the intent. A
full-length ring at the rim is a ring first and a colour second. Shape arrives
before hue, hue arrives before text, and the fix has to work at the first of
those, not the second.

**A dot, tick or ghost mark at the start of the sweep on an off card**, to keep
the sense that a scale exists. It costs a widget on two pages, and it competes
with the 8 % stub for the same reading — "there is a small mark near the start"
is precisely the on-state at minimum. Two states must not read the same. The
affordance is not lost: the hand already knows this is a knob, and every
neighbouring card shows a ring.

**Any new number, label, mode name or icon.** The issue is that the card says
too much with a shape, not that it says too little.

**Touching the other five cards.** Out of scope by the issue. The rule at the
top is the thing to carry over, not this diff.

## Findings

Three, in the order they matter. The first is inside this issue; the other two
are not, and are recorded rather than fixed.

**1. `unavailable` and unknown are not currently off, and they must be.**
`paint_ac`'s label already treats `off` and `unavailable` as OFF; the arc value
lambda tests only `"off"`. So an unavailable AC draws a ring at the last known
target, and a pre-link AC draws one at `24.0`. One predicate has to serve the
label, the arc value and the visibility, or they drift apart again — they have
drifted apart once already, which is how half of this bug got in.

**2. The FAN card cannot know it is unavailable.** Its on/off truth is
`fan_step > 0`, derived from the `percentage` attribute; when the entity goes
away that attribute goes NaN, the guard at line 364 keeps the last value, and
the card keeps showing a ring at the last known step. The AC has a text_sensor
on its own state and the fan does not, so the firmware genuinely cannot tell
"unavailable" from "still running at 4". The rule above already covers it if a
`text_sensor` on `${fan_ent}` is ever added — six lines — but adding an entity
binding is more than this issue asked for. **Worth its own issue.**

**3. Inside SET on an off card, a turn moves nothing on the glass.** On the AC,
tapping into SET while off and turning changes `ac_target` and calls
`climate.set_temperature` on a unit that is off: the figure still reads `OFF`,
and after this change there is no ring either. The hand feels a detent, the face
does not answer. This predates the issue — the ring was already frozen at 0 —
and this design does not make it worse, but it does remove the last moving pixel
from that path, so it should be named. The cheap shape of a fix, for whoever
picks it up: while `ui_adjust` is open on the AC card, show the figure and a
white ring at the pending target even when off, since white is the SET colour
and not the card's hue. **Out of scope here.**

## Note on the mockup

The "today" faces are **redrawn from the YAML's own constants**, not photographed
from the device — the knob is not attached to this session. Every colour, radius,
angle and text position in them comes from `firmware/bedside-knob.yaml` lines
1402–1501, and every arc length from the value lambdas at lines 623–626 and 652,
so the redraw is checkable against the file. The two 44 px MDI glyphs are
substituted with hand-drawn SVG of the same weight and colour, because the icon
font is not available to a browser; their position and size are the real ones.

Nothing in this design is proven by a mockup. Per `CLAUDE.md` it is not done
until it has been turned by hand in a dark room, and the state table above is
the checklist for that.
