# Hardware and interaction brief

The device is a knob on a nightstand that controls lights, music and scenes
through Home Assistant. It is operated in the dark, by a hand that found it
without looking, by someone who is not fully awake. Every number below exists
to serve that sentence.

Numbers are marked by where they come from, because they are not equally
trustworthy:

| Mark | Meaning |
|---|---|
| **datasheet** | vendor specification |
| **measured** | observed on the coffee knob, on the glass |
| **computed** | derived here from geometry or optics; arithmetic is sound, inputs are marked |
| **estimate** | best available figure, to be replaced by a bench measurement |

---

## 1. The hardware

**Buy a second Waveshare ESP32-S3-Knob-Touch-LCD-1.8** — the same board the
coffee knob runs on, sold as Guition **JC3636K518C-I-YR1**. $46.99 from
Waveshare, about $53 on Amazon bundled with a 3.7 V 102035 cell.

One board carries the whole device:

| Part | What is on the board | Source |
|---|---|---|
| MCU | ESP32-S3R8, dual LX7 @ 240 MHz, 8 MB octal PSRAM, 16 MB flash | datasheet |
| Second MCU | ESP32-U4WDH — USB-UART only, never flashed | datasheet |
| Display | 1.8 in round IPS, 360 x 360, ST77916 over QSPI, 600 cd/m², 1.2k:1 | datasheet |
| Touch | CST816 capacitive, I²C 0x15 | measured |
| Encoder | SSCM110100, one pulse per detent, A on GPIO8 / B on GPIO7 | measured |
| Haptics | DRV2605 @ 0x5A driving an LRA | measured |
| Backlight | single PWM channel on GPIO47 | measured |
| Power | USB-C, plus a 1.25 mm 2-pin 3.7 V lithium header with onboard charger — **a cell is fitted** | measured |
| Supply sense | ADC1 channel 0 on GPIO1, divide-by-two | measured |
| Body | CNC aluminium, 66 x 22 mm, metal ring rotates around a fixed screen | datasheet |

Unused and left unused: microSD, PCM5100A DAC and 3.5 mm jack, MEMS
microphone, the second encoder (`EC2`, wired to the other MCU).

### The coffee knob's parts are reusable, and so is most of its firmware

Everything below the UI transfers verbatim: the pin map, the display and touch
blocks, the `rotary_encoder_custom` external component pinned at
`KrX3D/WaveShare-Knob-Esp32S3@5e22f98`, the DRV2605 register writes, the
Home Assistant API idiom, and the whole `tools/` preview pipeline, which is
already calibrated for a 360 x 360 round panel.

Two properties of this board are constraints on the design, not defects to fix:

**The knob has no push contact.** `SW2` is a four-pin part — two commons to
ground, A and B out. There is no switch under the knob. Press is a tap on the
glass. The metal ring is the rotate target and the glass inside it is the press
target; in the dark that division is findable by touch, which is why it works
at all. The DRV2605 supplies the click the switch does not.

**There is no accelerometer.** No shake, no tilt, no tap-the-nightstand. The
board has a microphone but not an IMU.

### The alternative, and the one thing that would force it

**LILYGO T-Encoder Pro**, about $38. ESP32-S3-R8, 16 MB / 8 MB PSRAM, 1.2 in
round **AMOLED** 390 x 390, a real encoder push switch, USB-C.

It becomes the correct board the moment an **always-on face** is required — a
clock or a status glyph readable at 3 am without touching anything. An IPS
panel cannot do that: dimming the backlight dims the glyphs and the background
together, so the whole 45 mm disc becomes a faint grey coin floating in a dark
room. On AMOLED an unlit pixel emits nothing, so four glowing digits cost four
digits' worth of light and the rest of the disc stays genuinely black. The same
property makes a deep-red night face actually red, rather than red filtered out
of a white backlight that is still emitting blue.

What it costs, all of it real:

- The display needs `mipi_spi` model `CUSTOM` with a hand-written init
  sequence. There is no built-in ESPHome preset. A working community config
  exists; it is not a product.
- **The screen is a lottery.** Early units ship SH8601A + CHSC5816 touch;
  current units ship CO5300 + CST816. CST816 is a built-in ESPHome component
  and CHSC5816 needs a lightly-tested external one. You cannot tell which you
  bought until it arrives. This is the same class of trap as the K518/W518/K718
  pinout divergence.
- **The encoder push sits on GPIO0**, a boot strapping pin. Holding the knob
  through a power blip puts the device in download mode and it does not come
  back on its own. That is a bad bedside failure.
- 390 px over roughly 30.5 mm is 12.8 px/mm, **63% denser** than the Waveshare
  panel — and the glass is a third smaller. Every font size in section 4 has to
  be multiplied by about 1.63 to stay the same physical height, which leaves
  about 6 characters of primary type across the disc instead of 9. The AMOLED
  wins the black level and loses the physical size, and physical size is what
  legibility is made of.

Do not order it speculatively. Order it when the always-on face is a decided
requirement.

**Elecrow CrowPanel Advance Rotary**, $29 for 1.28 in / 240 x 240 and $35.70 for
2.1 in / 480 x 480, both round IPS with a real knob press, ESP32-S3R8, 8 MB
PSRAM, USB 5 V. The 2.1 in variant has the largest glass of anything here —
53 mm, 9.0 px/mm — which buys about 11 characters at the same physical legibility
instead of 9, and the body is 79 x 79 x 30 mm, which is a large object for a
nightstand.

It loses on the thing that matters most here: **there is no haptic driver.**
Feedback with the eyes closed is the whole interaction model, and an LRA under
the hand is not something a screen can substitute for. It is also still IPS, so
it does not buy the always-on face either. Noted so nobody has to rediscover it;
not recommended.

---

## 2. Talking to Home Assistant

**ESPHome native API, encrypted, over WiFi.** Not MQTT, not REST.

The reason is the first frame after wake. State arrives by subscription —
`sensor`, `text_sensor` and `binary_sensor` on `platform: homeassistant` — so
the values are already in globals before the backlight comes up. A polled
transport would light a screen that says "loading" to someone who reached out
in the dark, which is the one thing a bedside device must never do. There is
no broker in the path and no TLS handshake per call; a service call lands on
a LAN in single-digit to low-tens of milliseconds.

Three rules follow from it:

**Every action is one Home Assistant script call.** The knob calls
`script.bedroom_good_night` and `script.bed_strip_step`; it does not call
`light.turn_off` five times or compute a brightness. A sequence issued from the
device can fail halfway and leave the room half lit, and the knob would then
hold a list of entity IDs and a dimming policy that both drift every time the
room changes. The knob sends intent. Home Assistant owns what the intent means,
and the night rule and the 5% floor live there in one place.

**Hold local intent for about 1.5 s after an action, then let Home Assistant
win.** Optimistic state bounces — the coffee knob sees the machine's power
switch go on, off 4 ms later, and on again 2 s later, from a single press, and
it does the same from the Home Assistant UI. Lights over Zigbee and Matter do
this too. Without the hold, the screen contradicts the hand.

**When Home Assistant is unreachable the knob is lit and inert.** That is
inherent to the architecture and it is worse at 3 am than it is in a kitchen.
Show it as one small persistent mark on the face, never as a modal that has to
be dismissed by someone half asleep. Do not build a local fallback path to the
lights; build the honest indicator.

**`allow_service_calls` defaults to off** when a device is adopted. Every
service call then does nothing, silently, with no error anywhere. Settings →
Devices & Services → ESPHome → Configure.

---

## 3. Power and sleep

**USB-C, with a lithium cell fitted behind it. No deep sleep. The display never
switches off — it falls back to a dim clock.**

Deep sleep costs 1–2 s to wake and re-associate WiFi before the first frame
(**estimate**, community-reported, `fast_connect` and a static IP shave part of
it). A knob that is grabbed in the dark must answer in well under 200 ms. That
alone settles it.

### The cell

**A cell is fitted on the header.** Pulling the USB-C drops the rail from 4.75 V
to 4.14 V and the knob keeps running without leaving the network for a single
second — measured 2026-09-05. 4.14 V is a nearly full lithium cell; the curve in
`firmware/bedside-knob.yaml` reads it as 94%.

Runtime on the cell is unmeasured. The reasoning that argued against fitting one
still stands as a warning rather than as a description: an 800 mAh cell runs an
ESP32-S3 with WiFi associated for a handful of hours (**estimate**), and a
bedside device that is flat at 3 am is the failure this project cannot have. The
knob is not portable; the cell is a ride-through for a pulled plug, not a way to
run untethered.

`sensor.bedside_knob_supply_voltage` reads ADC1 channel 0 — GPIO1 — through a
divide-by-two. **Not the divide-by-three in Waveshare's own note for this
board**, which puts the same rail at 7.18 V; the coffee knob runs identical
hardware and has been calibrated at 2.0 since it was built.

The sense point sits on the system rail, after the charger, so **the cell cannot
be read while the USB-C is connected** — the ADC then measures the charger's
output near 4.75 V, above the top of the lithium curve, and any percentage
derived from it clamps to 100 and means nothing. Charge state is only observable
unplugged.

So:

| Awake, always | Idle |
|---|---|
| MCU, WiFi associated, API connected, entity subscriptions live, backlight, LVGL | backlight dimmed to 20%, or 3% while the Good Night key is on |

Idle path: after the timeout the backlight drops and `page_clock` takes the
glass — the coffee knob's `screentime` script, retimed and rerouted. Wake on an
encoder pulse or a touch. Wake latency is the backlight ramp and nothing else.

**The backlight no longer turns off, so `back_light.on_turn_off` no longer
fires.** The UI state resets that used to live there — `ui_adjust`, `ui_level`
and `sel_zone` — moved into `screentime`'s idle branch. Putting them back in the
handler silently reopens the night-rule hole: a zone selected in the evening
escapes the night rule and would still be selected at 3 am.

Retimed for the bedroom, with the coffee knob's value beside it so the
difference is deliberate:

| | Coffee | Bedside | Why |
|---|---|---|---|
| Idle timeout | 5 min | **20 s** | five minutes of glow beside a sleeping person |
| Backlight fade | 30 ms | **400 ms up, 1000 ms down** | a snap to light reads as a flash in a dark room |
| Boot brightness | 60% | **0%, dark** | a power cut at 2 am must not light the room |
| Wake guard after backlight-on | 600 ms | **800 ms** | a half-asleep hand is slower and lands wider |

**The first detent after wake must not change a value.** On the coffee knob,
rotating wakes the screen and moves the carousel in the same motion. Here that
means a sleeve brushing the knob dims the bedroom lights. Rotation on a dark
screen wakes and arms the current context; the value moves from the second
detent onward. One detent of dead zone is imperceptible in use.

**PWM: set `frequency: 19531Hz`.** The ESPHome `ledc` default is 1 kHz, which
is visible as flicker to dark-adapted peripheral vision and on saccades. 19531
Hz maps to 12-bit duty, 4096 steps (**datasheet**, ESPHome ledc table) — ample
resolution at the bottom of the range. The real floor is the backlight driver:
below some duty it simply stops lighting. **Measure that floor on the bench and
write it here**, because the night brightness must sit just above it.

**Dim in two places at once.** Backlight duty and foreground colour multiply.
A 12% grey glyph at 4% backlight emits far less than either alone and steps
below the PWM floor without reaching it. See the night palette in section 4.

**Nothing may make a sound.** The board has no fitted speaker; leave the DAC
and the jack unpopulated. The LRA is the only feedback channel, and against a
hard nightstand an LRA still ticks audibly — use a lower-amplitude effect in
night mode, and put a felt pad under the device.

**Brightness comes from Home Assistant**, from
`sensor.lumi_lumi_motion_ac02_illuminance`, read at the moment the display
wakes rather than tracked continuously. Between 22:00 and 06:00 a hard ceiling
overrides whatever that sensor says — a lamp switched on across the room must
not license a bright knob. If Home Assistant is unreachable, or the sensor is
stale, the knob uses the night ceiling. **The safe default is dark.**

---

## 4. What a screen design must respect

### Canvas

- **360 x 360 pixels, and the panel is a circle.** Anything outside radius 180
  is not clipped, it is not there.
- **Safe radius 172 px.** The bezel curves and a glyph touching the true edge
  reads as broken while still technically inside. Real content stays inside 172.
- **Rotation 180 belongs on the `lvgl:` block**, not `display:`. LVGL rejects a
  rotated display and rotates touch input itself.
- **Pixel pitch 7.87 px/mm, 0.127 mm per pixel, about 200 PPI** (**computed**
  from a 45.72 mm active diameter). Waveshare sells the same 360 x 360 panel on
  a board it calls 1.85 in, so the true diameter is somewhere in 45.7–47.0 mm.
  The figure used here is the denser end, which makes every type size below
  conservative. **One caliper measurement of the visible glass settles it**, and
  the whole type scale scales linearly off it.

### Colour

- **RGB565, 16 bits.** 32 levels of red, 64 of green, 32 of blue. The darkest
  non-black step is about 3% — near-black gradients band visibly. Design in
  flat blocks. The panel itself is 262K-capable and `pixel_mode: 18bit` exists,
  at a cost in bus bandwidth; do not spend it on a gradient.
- **Background is #000000.** Always, on every screen, day and night.
- **Night palette: amber and red only.** No channel above 0x80. No blue above
  0x20. Rods are largely insensitive above 620 nm, so red preserves dark
  adaptation, and melatonin suppression peaks at 460–480 nm, which is exactly
  the blue to keep off a bedroom screen. On this IPS panel a red screen is a
  white backlight through a red filter, so it is much better than white but not
  blue-free — another reason the backlight is the primary dimmer.
- **Lit area is a budget, not an afterthought.** In a dark room the eye responds
  to total emitted flux, so a bright element the size of the disc is a flash
  whatever its colour. **At night, no more than 15% of the disc's pixels may sit
  above 30% grey.** A large dim field and a small bright glyph are not
  interchangeable.
- Day mode may use full white and saturated accents.
- **The warmth arc cannot be drawn in the light's own colour at night.** The
  bedroom lights are colour-temperature only, and the top of the dimming curve
  is a near-white with real blue content — precisely the colour the night
  palette exists to keep off the glass. At night, map the whole warmth range on
  to an amber ramp, deep at the bottom and pale at the top, and let arc *length*
  carry the magnitude. Day mode may render the true colour temperature.

### Refresh

- LVGL drives the flush; the display is `update_interval: never`. Draw buffer
  is 24% of the frame, so a full screen renders in about four chunks.
- **Budget one full-screen repaint per ~50 ms** (**estimate**, from bus
  arithmetic and the observed behaviour below). Partial updates are far cheaper.
- **A panel flush steals most of a 100 ms slot.** On the coffee knob a 100 ms
  interval coalesces whenever the display is flushing, badly enough that a
  stopwatch built by counting ticks read low and biased the logged shot times
  short (**measured**). Two consequences: derive all timing from `millis()`,
  never from tick counts; and any animation that must stay smooth has to touch a
  small area.
- **The 120 ms detent budget forbids a page rebuild.** A detent must repaint the
  value and the arc and nothing else. There is room for that inside 120 ms and
  no room for a full-screen redraw plus a round trip to Home Assistant, which is
  why the value on screen is predicted locally and reconciled when the reported
  state arrives.

### Type

Fonts are compiled in at fixed pixel sizes. **Only the sizes declared in the
config exist** — there is no "slightly smaller". Each added size costs flash and
a full rebuild.

**Two distances, and they are not the same number.** The screen sits about
150 mm from a sleeping face — that is the light-pollution distance, and it is
why the idle state is off rather than dim. The *reading* distance is eye to
nightstand with a head on a pillow: **400–500 mm**, because a hand comes out
from under the duvet but the head does not follow it.

Cap height in arc minutes (**computed**; Montserrat cap height is 0.70 of
nominal size):

| Font size | Cap height | @300 mm | @400 mm | @500 mm | @600 mm |
|---|---|---|---|---|---|
| 16 px | 1.42 mm | 16.3' | 12.2' | 9.8' | 8.1' |
| 20 px | 1.78 mm | 20.4' | 15.3' | 12.2' | 10.2' |
| 28 px | 2.49 mm | 28.5' | 21.4' | 17.1' | 14.3' |
| 40 px | 3.56 mm | 40.7' | 30.6' | 24.4' | 20.4' |
| **48 px** | 4.27 mm | 48.9' | 36.7' | **29.3'** | 24.4' |
| **60 px** | 5.33 mm | 61.1' | **45.8'** | **36.7'** | 30.6' |
| 76 px | 6.76 mm | 77.4' | 58.1' | 46.5' | 38.7' |

Comfortable reading is 20–22 arc minutes. A dark-adapted eye at low luminance,
in someone who has just woken, loses roughly a factor of two — **30 arc minutes
is the line to design to**, not 20.

**The bedside type scale:**

| Role | Size | Rule |
|---|---|---|
| Primary | **60 px** | Exactly one per screen. 45.8' at 400 mm, 36.7' at 500 mm, and still 30.6' at 600 mm if the bed turns out to be further than measured. |
| Secondary | **28 px** | The one word naming what the primary is. 21.4' at 400 mm — readable when alert, not when half asleep. |
| Tertiary | **20 px** | Setup and configuration only. Nothing here may need reading at 3 am. |

**16 px does not exist on this device.**

The coffee knob's scale is 16 / 20 / 48. It was drawn for a lit kitchen at
arm's-over-the-counter distance and does not transfer intact: 48 px sits on the
line rather than above it, and 16 px is texture rather than text.

**Measure the actual eye-to-knob distance before drawing to this.** If it comes
back above 550 mm, the primary goes to 76 px and the widest line drops from
about 9 characters to about 7.

### The screen will be viewed on the slant

A nightstand top sits near mattress height and so do the eyes of someone lying
on it. The glass will be seen from perhaps 45–60 degrees off its normal, and a
circle at 60 degrees is an ellipse half as tall (**computed**): a 60 px line
subtends 30 px of retina, and the legibility table above quietly halves.

**Tilt the device toward the bed, about 35 degrees, on a printed wedge.** It is
the cheapest fix available, it recovers the whole factor, it settles which way
is up for the `rotation: 180` setting, and it puts the glass where a hand
expects to find it. Designing for a flat-lying panel instead means doubling
every type size, which the disc has no room for.

### How much fits

Horizontal room is not the screen width, it is the chord at that height:
`half_width(dy) = sqrt(172² − dy²)`. A label that fits at the centre is cut in
half near the rim, and nothing in the toolchain says so — LVGL lays it out, the
compiler is happy, and the defect appears only on the glass.

The limit is set by the **outer corner** of the text box, so a tall line loses
room faster than its baseline suggests. Line box is **1.22 x the font size**
(Montserrat ascender 968 + descender 251 per 1000 em), and average advance is
**0.585 x the font size** (**estimate**, from the coffee knob's measured font
table; deliberately generous, so the linter errs toward caution).

Maximum text-box width, and characters at average advance (**computed**):

| Vertical offset | 60 px | 28 px | 20 px |
|---|---|---|---|
| y = 0 | 336 px, 9 ch | 342 px, 20 ch | 343 px, 29 ch |
| y = ±40 | 308 px, 8 ch | 325 px, 19 ch | 328 px, 28 ch |
| y = ±70 | 270 px, 7 ch | 297 px, 18 ch | 302 px, 25 ch |
| y = ±100 | 209 px, 5 ch | 252 px, 15 ch | 261 px, 22 ch |
| y = ±120 | 142 px, 4 ch | 208 px, 12 ch | 220 px, 18 ch |
| y = ±130 | 86 px, 2 ch | 178 px, 10 ch | 194 px, 16 ch |
| y = ±140 | does not fit | 140 px, 8 ch | 160 px, 13 ch |
| y = ±155 | does not fit | does not fit | 81 px, 6 ch |

**60 px type cannot live outside y = ±135**, and only reaches 4 characters by
y = ±120. The primary value belongs at the centre and there is room for one of
it. An arc around the rim and a 28 px word above or below it is the whole
budget.

### Other things that only show up on the glass

- **Labels do not wrap.** A long string is one long line running off both edges.
  Any label written at runtime needs `width:` *and* `long_mode:` — `DOTS` to
  ellipsise, `SCROLL_CIRCULAR` to move.
- **Montserrat carries ASCII only. No Hebrew.** This device shows a track title,
  so it will meet Hebrew, and a Hebrew title is currently a row of empty boxes.
  A font with the glyphs can be compiled in, but LVGL does not shape
  right-to-left text — that is a project, not a setting. Reduce rather than
  mangle: strip what cannot be drawn and say so, the way the coffee knob reports
  "non-latin name" for a bean it cannot render. At 28 px and about 18 characters
  the title is a hint at what is playing, not a readout; when it cannot be drawn
  at all, fall back to the source name rather than to blanks.
- **Icon fonts carry an explicit glyph list.** A glyph used but not listed
  renders as nothing — no error, no box, no warning. Adding one forces a full
  rebuild.
- **The declared `text:` on a widget is a placeholder.** Content comes from
  whatever writes it at runtime, and a paint routine may drop a label to a
  smaller size for one item. Reading the declared text tells you nothing about
  what is on screen.
- **Show one thing large.** Eight labels around the rim plus a value plus a hint
  is a debug page. On the coffee knob the screens that worked showed a single
  number; at bedside that is not a preference, it is the spec.
- **A dead screen is worse than a missing one.** An item reading "n/a" in the
  mode you are actually in is a stop on the nightly path that answers nothing.

### Before anything is flashed

**Never flash a layout that has not been seen rendered** — rendered from the
config about to be flashed, including its ugly states: longest possible string,
data unavailable, the mode where an item reads "n/a". A hand-drawn mock is an
argument for a design; a render is evidence about one. The coffee knob's
`tools/` pipeline does this and ports directly: geometry lint, export, build
simulator, drive a browser and screenshot every screen. Update `FONT_ADV` and
`FONT_HEIGHT` for the new sizes when porting — and note that `FONT_HEIGHT`
currently holds the nominal size rather than the 1.22x line box, which
under-reports vertical overflow near the rim.

---

## 5. Interaction primitives

The full vocabulary on this board is **turn, tap, hold**. Three verbs, and each
gets exactly one meaning:

- **turn** changes the value in front of you. Never navigates.
- **tap** changes mode. Never changes a value.
- **hold** commits the mode's one large action, in visible stages.

**Hold means "act" here, and on the coffee knob it means "leave".** That is a
deliberate difference and it should survive contact with anyone who knows the
other device. Hold means leave when there is somewhere to leave *to* — nested
pages, a settings tree, a rating flow you can abandon. This knob has three peer
modes and no hierarchy, so "leave" has no referent and the gesture is free.

The rule that made hold mean leave still applies in its real form: **the gesture
people reach for blindly must not reach anything destructive by accident.**
Staged holds satisfy that only if the staging is honest — a hold released before
the first stage does nothing, each stage is visible before it commits, and hold
is inert while the screen is dark or inside the wake guard. A three-second hold
that darkens rooms other people are in is exactly the case the original rule was
protecting, and it earns its guards.

| Primitive | Available | Firmware cost | Notes |
|---|---|---|---|
| **Rotate** | yes | none, exists | `rotary_encoder_custom`. One clean pulse per detent, direction by which channel fires. ESPHome's stock `rotary_encoder` reads **zero** on this board — it is not quadrature in the PCNT sense. |
| **Tap** | yes | none, exists | Touchscreen short click. No switch under the knob. |
| **Hold** | yes | none, exists | `long_press_time: 700ms` on the `touchscreens:` block. |
| **Rotate fast** (velocity) | yes | **low** | Timestamp deltas between pulses; a global and a few lines. High value at bedside: one flick covers the whole range, so brightness never needs 40 detents. |
| **Press-and-turn** | yes | **medium** | A `touch_held` global set in `on_touch` / `on_release`, read in the encoder handler. Buys a second axis for free — turn is volume, press-and-turn is track. Risk: a palm resting on the glass while the ring turns reads as press-and-turn. Gate it on a touch that began before the first pulse. |
| **Double tap** | yes | **medium**, and it is felt | LVGL has no double-click. A global holding the last click's `millis()` and a ~350 ms window. The cost is not code, it is that every single tap must now wait 350 ms before it can act. On a device sold on instant response, spend this only if the action is worth it. |
| **Physical push** | **no** | — | No switch on this board. Forcing one means the T-Encoder Pro. |
| **Shake / tap the nightstand** | **no** | — | No accelerometer. Adding an external IMU over the Qwiic-adjacent I²C bus is possible and is a mechanical project. |
| **Voice / clap wake** | hardware yes | **high**, and it is a policy question | The MEMS microphone exists. I²S plus energy detection plus a threshold that does not fire on a partner turning over. A bedside device listening all night is Tomer's call, not a firmware decision. |

### Bedside rules on top of the three verbs

**A press on a dark screen only wakes it.** The panel is dark most of the day
and night. The first press lands on a screen that cannot be read, and without a
guard it activates whatever is under the finger. Stamp `millis()` when the
backlight comes up and ignore input for the guard window (800 ms here).

**The first detent after wake only wakes.** Section 3.

**Nothing irreversible is reachable while dark or inside the guard.** Not
"confirm before doing it" — not reachable at all.

**Destructive and room-changing actions get two deliberate taps on their own
screen, with the armed state visible.** In night colours, at 60 px.

**Haptics carry confirmation, because the switch does not.** Fire an LRA effect
on every accepted tap and every detent, so the hand knows the input landed
without the eye checking. Use a quieter effect in night mode.

**An edit indicator is quieter than the content.** A hard white ring around a
black screen is the brightest thing on the panel and it is only saying "you are
editing".

---

## 6. Flashing and provisioning

Unchanged from the coffee knob, and each line is here because it cost a day:

- **16 MB flash means the first flash is over USB.** A partition table change
  cannot be applied over the air. Flash once via web.esphome.io, then everything
  after is OTA.
- **Use a USB-A to USB-C cable.** On this board the cable *orientation* selects
  which of the two chips you talk to; with C-to-C it is a coin flip.
- **The YAML must contain zero backslashes.** Content written through the
  ESPHome dashboard API gets backslashes doubled in transit, and a glyph written
  as an escape arrives as a literal ten-character string. Store MDI glyphs as
  literal characters.
- **LVGL text lambdas must return `const char*`.** A single-expression lambda
  gets inlined, skipping the `std::string` conversion, and `.c_str()` is called
  on the result. Use a multi-statement lambda writing into a `static char[]`.
- **Do not use the community DRV2605 component.** It reads the status register
  first thing in `setup()`; the chip acknowledges its address and NAKs register
  reads, so the component bails before setting LRA mode and marks itself FAILED.
  Effects still fire, on ERM defaults, into an LRA motor — a buzz, and the wrong
  one. Write the registers directly: `0x01`=0x00, `0x1A`=0x80, `0x03`=0x06, then
  `0x04`/`0x05`/`0x0C` per effect.
- **`esphome run`, never `esphome upload`.** Upload ships whatever binary is in
  the build directory without recompiling.
- **`ESPHOME_ESP_IDF_PREFIX` must be short** (`C:\ei`). The toolchain nests
  about 245 characters deep and blows past Windows' 260-character limit,
  surfacing as `bits/c++config.h: No such file or directory`, which looks like a
  compiler bug and is not.
- **Run the build from PowerShell, not Git Bash.** ESP-IDF refuses to build
  under MSys and says so only deep in a traceback.
- **Never generate a new secret for an already-flashed device.** A fresh API key
  means Home Assistant cannot decrypt and every entity goes unavailable; a fresh
  OTA password means the next flash must be over USB. Clear
  `.esphome/storage/*.yaml.json` after any secrets change — ESPHome caches the
  validated config and will not re-read them.

The bootloader, the flashing path and the pairing state are on the
not-all-things list. Anything touching them needs a way back out first.

---

## 7. What the hardware settles

Answers to the open questions in `REQUIREMENTS.md` that are decided by the
board rather than by taste.

**The encoder has no push contact, and tap and hold are touchscreen events.**
Confirmed against the schematic and against the running coffee knob: `SW2` is a
four-pin part, two commons to ground and A/B out. A press can only be bought by
changing boards, and both boards that offer one cost more than they return:
the T-Encoder Pro puts its switch on GPIO0, where holding the knob through a
power blip strands the device in download mode, and the Elecrow rotary panels
have no haptic driver at all. Haptics are the primary feedback channel for a
device used with the eyes closed, so trading an LRA for a switch is a bad trade.
A tap on 45 mm of glass inside a metal ring is a large, findable target in the
dark. Keep the touchscreen gestures and let the LRA supply the click the switch
would have.

**A permanently dim idle clock is not available on this panel.** Backlight
dimming attenuates the glyphs and the background together, so a dim clock is a
whole grey disc glowing 150 mm from a sleeping face, not four glowing digits.
Idle stays fully off. If the clock is wanted badly enough to spend hardware on,
it is the one requirement that justifies the AMOLED board in section 1, and it
should be decided before anything is ordered rather than after.

**Colour temperature cannot be shown in its own colour at night.** See the
warmth arc note in section 4; the arc ramps through amber and carries magnitude
by length.

Three things the hardware does not settle, and which want a bench answer before
the first screen is drawn:

1. **The visible glass diameter, with a caliper.** Every type size scales off it.
2. **The lowest backlight duty that still lights**, on this specific unit. The
   night brightness sits just above it, and it cannot be guessed from the
   datasheet.
3. **The eye-to-knob distance from the pillow**, with a tape measure, and
   whether the wedge that fixes the viewing angle changes it.
