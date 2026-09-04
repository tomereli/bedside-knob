# Design — issue #1: DIM, SWITCHES, and the target behind the pill

Mockup: `.aisdlc/run/mockup/index.html`. Open `00-before-after.html` first.

The issue leaves one thing to this pass: **how a single zone is reached on the
DIM card once the chips are gone.** That is answered in §5. Everything else here
is the rest of what a screen needs before it can be built.

---

## 1. The question each screen answers

| Screen | In his words |
|---|---|
| **DIM** | "Less light. Not on her side." |
| **SWITCHES** | "Is the bathroom light still on?" |
| **TARGET** | "Not all of them — just the wave." |

If DIM cannot answer the first one without waking anybody, nothing else on the
card matters.

## 2. What he does here, in order

**DIM**, the resting case, which is most of the uses of this whole device:

1. A hand arrives in the dark and turns. The carousel moves — this is the
   existing invariant on every card and it is not changed here.
2. He taps the face. SET opens; the ring and number go white.
3. He turns. **20 points per detent.** Three detents from 60% to the floor.
   The light moves before Home Assistant is told.
4. Six seconds of stillness, or a tap, and SET closes.

The rare case, reaching one zone:

1. Tap the pill at the bottom of DIM. The TARGET page opens.
2. Turn. The five zones walk past, each showing its own level. **Nothing is
   applied by walking.**
3. Tap. The zone is committed and DIM returns with SET already open, so the next
   turn dims it.

**SWITCHES**: he arrives and taps a chip. That is the whole card. There is no
step two.

## 3. Information hierarchy

Per light, Home Assistant offers: state, brightness 0–255, `color_temp_kelvin`,
supported colour modes, friendly name, last-changed, group membership.

**At a glance, on DIM** — four things, in this reading order:

| Slot | Says | Font, y |
|---|---|---|
| Number | the level of the target | value_60, −50 |
| Sub-line | **the lights this turn will move** | label_18, +8 |
| Ring | the same level, peripherally | r=164 stroke 10 |
| Pill | the target's name, and whether it is lit | label_28, +80 |
| Crescent | the night rule is narrowing this turn | mdi_44, x −72, y −112 |

**On demand**: each zone's own level, on TARGET, revealed by turning past it.

**Not shown, and why:**

- **Colour temperature.** Every bedroom light is `color_temp` only, 2000–6535 K.
  REQUIREMENTS.md wants warmth riding the same dial; this issue does not write
  it. A number on the glass that no gesture can change is worse than no number.
- **Home Assistant's friendly names.** They are machine transliterations —
  `switch.khdr_shynh_rshy_kh_shynh_qryh_shml`. Rendering an entity's own name
  would print garbage at 28 px. Every label on both cards is hand-written in the
  firmware, and this is the reason.
- **Raw brightness 0–255**, `last_changed`, and the group's member list. The
  member list is named as a set in the sub-line and never enumerated.
- **Notifications, repairs, updates, weather.** Refused already in
  REQUIREMENTS.md. Restated because the sub-line is exactly the kind of empty
  slot that attracts them later.

## 4. Default order

**DIM opens on ALL, always.** See finding 1 — `sel_zone` must reset when the
screen sleeps, which it does not do today. The knob a cold hand finds is pointed
at the whole room and covered by the night rule; a single-zone selection is a
deliberate act with a twenty-second life.

TARGET walks in the order `sel_zone` already numbers: ALL, WAVE, BED, TOMER,
MASHA. ALL is first because it is the answer nine times in ten.

SWITCHES has a fixed 2×2 and no order to choose. Top row is the two rooms, bottom
row is the two reading lamps, **and left is left**: `READ L` is
`switch.khdr_shynh_rshy_kh_shynh_qryh_shml` (קריאה שמאל — the left one, Masha's
side), `READ R` is `switch.slvn_vknysh_n15_2`, key N15-2 on his own panel. The
chip on the left of the glass is the lamp on the left of the bed. That is the
only mapping a hand can use without reading, and it is why the layout is a grid
and not a list.

They are labelled by side rather than by name because TARGET already uses TOMER
and MASHA for the two nightstand *strips*. Two different lights called TOMER on
adjacent cards is a bug waiting for a dark room.

## 5. Controls — and the answer the issue asked for

**The zone pill, and TARGET behind it.**

DIM gets exactly one control besides the dial: a **216 × 58 px pill at y +80**,
radius 29, naming the current target. Tapping it opens TARGET, a sub-page at
`ui_level == 2`, alongside the playlist page that already lives at 1.

Why this and not the alternatives the plan listed:

- **Not a hold that cycles.** Hold is already how the selected zone switches off,
  and that separation is load-bearing: because the dial can never reach off, the
  5% floor can be unconditional. Overloading hold would put criteria 7 and 13 on
  the same gesture.
- **Not a smaller second row of chips.** That is the thing the issue is removing.
  Six 29 px-radius targets became four or five slightly larger ones, and a tap
  still would not act — a mode change wearing a button's clothes, again.
- **A sub-page, because turning is the gesture the hand is already making.** It
  is the one input that works with the eyes shut, and this firmware already has
  the exact idiom next door: `page_plist` walks on a turn, commits on a tap,
  leaves on a hold. Reusing a pattern he has already learned costs nothing to
  teach.

TARGET carries, per zone: the name at value_60, its current level at label_18,
`TAP TO SET`, and **five dots** marking position in the ring so "how many more
turns" needs nothing read. Five is not a list and gets no scroll affordance; a
sixth light would go in the firmware, not into a menu that grows.

**No search, sort or filter anywhere.** Five fixed zones and four fixed switches.
Every one of those controls would be clutter charged against attention on every
visit.

**Gesture map for the two new cards and the sub-page:**

| Surface | Turn | Tap face | Tap control | Hold |
|---|---|---|---|---|
| DIM | carousel; in SET, ±20 points | toggle SET | pill → TARGET | toggle selected zone |
| SWITCHES | carousel | refusal buzz | chip → toggle that switch | refusal buzz |
| TARGET | walk the five zones | commit, back to DIM in SET | — | leave unchanged |

A tap on SWITCHES' bare face fires `${fx_refuse}` rather than doing nothing.
There is no value to set on that card, but a gesture that misses should feel like
a miss and not like a dead knob.

## 6. Empty, loading, error and extreme states

| State | DIM | SWITCHES |
|---|---|---|
| Booted, nothing heard yet | `——` in grey, no indicator arc, crescent shown | four grey chips |
| One entity unavailable | `——` in grey if it is the target | that chip grey |
| Everything off | `OFF` in amber, **no indicator arc** | four dark-amber chips, no ring at all |
| One of four lit | the group's own level, which is the mean of its lit members | that chip lit |
| Night, target ALL | crescent, sub-line `BED · TOMER` | unaffected |
| Day, target ALL | no crescent, sub-line `ALL 4 STRIPS` | unaffected |
| Clock not yet synced | identical to night — see below | unaffected |
| Far more than expected | there is no list here that can grow; TARGET is five entries fixed at compile time | four chips fixed at compile time |

Two of these need saying out loud.

**Criterion 14 is satisfied by construction, not by a lambda.** SWITCHES has no
arc at all — it measures nothing, so it carries no gauge, so there is no
full-length ring in the card's hue to draw wrong. On DIM the indicator is 0 when
the target reads off; the dim *track* stays, because the track is the shape of
the control and not a reading.

**The unknown clock gets no screen of its own.** The plan treats an unsynced
clock as night. On the glass that is the crescent and `BED · TOMER` — which is
exactly what a turn will then do, so it is not a lie, and inventing a fourth
state for a condition that lasts a few seconds after boot and behaves identically
to night would be inventing a difference that does not exist.

**The night window is the state this design exists to make visible.** At night a
turn moves two of the four strips and does not write the other two at all. If the
card kept saying `ALL 4 STRIPS` while half the room ignored the dial, the knob
would read as broken at 3am. So the sub-line names **the lights this turn will
move**, never the lights the selection nominally covers, and the crescent marks
*the night rule is narrowing this turn* — not merely that it is night. Select a
single zone and the rule steps aside (criterion 13), so the crescent goes with
it.

One consequence worth having in writing: with the floor at 5% and no off from the
dial, **`OFF` on DIM now always means something else turned the light off** — a
scene, the panel, the hold. It can no longer mean "you wound it down". That is a
narrowing of the word, and it is what makes it worth showing.

## 7. What this design refuses

1. **The six chips, in every form.** They do not come back smaller, and they do
   not come back on a second row.
2. **A ring on SWITCHES.** A card with nothing to measure gets no gauge.
3. **A warmth reading.** Nothing here can change it.
4. **A distinct "clock unknown" screen.** §6.
5. **A BACK button on TARGET.** Every entry is a safe choice and committing one is
   never wrong; tap-commits and hold-leaves are both already learned on the
   playlist page, and the space it would take is where the dots are.
6. **Icons on the toggle chips.** Words instead — which resolves plan step 20:
   `󰾑` and `󰦡` were the CLOSET and BATH card icons and now have no user, so they
   come out of the baked glyph list.
7. **Any scroll affordance on TARGET.** Five is not a list.
8. **Renaming or re-scoping the carousel beyond what the plan settled.** DIM and
   SWITCHES sit adjacent because they are one subject split in two.

---

## Findings

### 1. `sel_zone` must reset to ALL when the screen sleeps — it does not today

This is the important one, and it is not in the acceptance criteria.

`sel_zone` is `restore_value: false`, so it resets on boot. It does **not** reset
on sleep: `back_light.on_turn_off` clears `ui_adjust` and `ui_level` and leaves
`sel_zone` alone. So a zone picked at 8pm is still selected at 3am — and
criterion 13 says an explicit selection escapes the night rule. A stale WAVE
selection plus one sleepy turn lights the Wave over a sleeping head, which is
precisely the failure this issue exists to prevent.

**Add `id(sel_zone) = 0;` to the lambda already in `light.back_light.on_turn_off`
that resets `ui_adjust` and `ui_level`.** One line, in a block the developer is
already editing. Without it the night rule has a hole you can drive through, and
no test in the plan would catch it.

### 2. Unavailable and off read the same, on both cards

`val_lt` today prints `OFF` for any state that is not the string `"on"`, so a
light that is off, a light that has dropped off the Zigbee mesh, and a light the
knob has not heard about yet are one picture. The chip borders have the same
problem. He would stand there tapping.

**Two additions, one line each, both beyond the acceptance criteria and both
inside surfaces this issue rewrites anyway:**

- `paint_dim`: grey `——` when the target's state is `unavailable` or empty;
  amber `OFF` only when it is genuinely `off`.
- `paint_toggles`: a third chip colour — border `0x3A3A3A` on background
  `0x1E1E1E` — for a switch reading `unavailable`.

They are named here rather than smuggled in, so the reviewer sees a decision
rather than scope creep. The fuller offline treatment REQUIREMENTS.md asks for —
telling him Home Assistant is unreachable, rather than that one value is unknown
— is a separate issue and is not attempted here.

### 3. A lit chip needs more than a lit border

The shipped chips signal state with `border_color` alone, which is 3 px of colour
across a dark room. `paint_toggles` should set **`bg_color` as well** — `0x3A2606`
lit, `0x241804` dark — on the same `lvgl.widget.update`. Two properties, four
blocks, no new widget ids.

### 4. Left and right on the glass are unverified

`READ L` / `READ R` and the whole SWITCHES layout assume that LVGL's negative x
renders on the viewer's left after `rotation: 180`. The shipped card gives no
evidence either way — its six chips carry no spatial logic. If the frame is
inverted, `READ L` toggles the right-hand lamp, and no config check can see it.

**Hand check, on the device, before this counts as done: tap `READ L` and watch
which lamp lights.** Same check for the two room chips.

### 5. Home Assistant reads were not granted to this session either

The issue directs that `automation.closet_knob_rotate_dims_the_led_strips` and
`script.bed_strip_step` be read before designing. The architect recorded that the
tools were unavailable; they were denied to this session too, as were entity
state reads. **Both artifacts remain unread by anyone on this issue.**

What that leaves unverified, and what it does not:

- The geometry, colours, fonts, offsets and gesture routing above are all taken
  from `firmware/bedside-knob.yaml` and are solid.
- The percentages in the mockup are sample values, not live readings, and are
  labelled as such.
- The design does not depend on a field being populated: every value it shows
  (state, brightness) is one the shipped firmware already reads and paints today.
- What could still surprise the developer is inside `push_zone` — the detail of
  the night rule that the issue body only summarises. **Read both before writing
  it if you have the access.**

### 6. Warmth on the dial is specified and unbuilt

REQUIREMENTS.md is explicit that turning down should warm the light and turning
up should cool it, one axis, 2000 K at 5% to 4000 K at 100%. Nothing in the
firmware writes `color_temp_kelvin` and nothing in this issue adds it. This is
not in scope here and is not attempted; it is recorded because a design pass that
noticed it and said nothing would be the reason it stays unbuilt.

---

## For the developer

The design lands entirely inside the plan's steps 5, 6, 15, 16, 17, 18 and 20,
plus one line in `back_light.on_turn_off` (finding 1). Two things the plan left
open are now decided: the zone-selection mechanism is a pill plus a `ui_level ==
2` sub-page, and the toggle chips are 112 px circles with words, so the two MDI
glyphs come out of the font.

Geometry, all measured against the 172 px safe radius:

| Widget | Size | Position |
|---|---|---|
| DIM pill | 216 × 58, r 29 | y +80 — far corner at r 153 |
| SWITCHES chip | 112 × 112, r 56 | x ±64, y −46 and +72 — far edge at r 152 |
| SWITCHES title | label_28, ls 3 | y −130 |
| TARGET name | value_60 | y −40 |
| TARGET dots | 5 × 8 px, r 4 | y +108, x −48 to +48 step 24 |
| Crescent | mdi_44 | x −72, y −112 (DIM) / y −118 (TARGET) |

The crescent is painted by setting a label's text to the glyph or to `""`, the
trick `sub_fan` already uses, rather than by introducing show/hide.
