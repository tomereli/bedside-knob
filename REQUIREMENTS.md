# Bedside knob — requirements

A knob on the nightstand, reachable by one hand from under the duvet, in the
dark, without opening both eyes.

## The constraint that shapes everything

Tomer's side of the bed already has an eight-key Vitrea panel (N15) within
arm's reach:

| Key | Does |
|---|---|
| N15-1 | Movie |
| N15-2 | Reading light (his side) |
| N15-3 | Good Night |
| N15-4 | Good Morning |
| N15-5 | All Off |
| N15-6 | Ambient |
| N15-7 | Ceiling fan — tap speed, hold on/off |
| N15-8 | Fan light |

Discrete scenes are solved. A knob that offers a menu of named scenes is a
worse keypad than the keypad already there.

What the panel cannot do is **continuous**. Nothing at the bedside sets a
brightness, a volume or a temperature — only jumps to preset values. That gap
is the product.

The walk-in closet already has a rotary (TS004F) whose rotation dims the bed
strips, and it works. It is across the room. This is that gesture, at the
right end of it.

## What the knob controls, ranked

### 1. Bed light level — the resting mode

The thing a hand reaches for. Used at least twice every night.

| Entity | Role |
|---|---|
| `light.home_assistant_connect_zbt_2_bedroom_led_strips` | ZHA group "Bed ambience" — daytime target, one multicast |
| `light.tzb210_ue01a0s2_ts0502b` | Under-bed strip |
| `light.tzb210_ue01a0s2_ts0502b_2` | Nightstand Tomer |
| `light.left_nightstand` | Nightstand Masha |
| `light.tzb210_ue01a0s2_ts0502b_3` | Wave — strip behind the panel above the bed |
| `script.bed_strip_step` | The dimming policy, including the night rule |

Every one of these is `color_temp` only, 2000–6535 K. There is no colour in
this room.

**Warmth is not a separate mode — it rides on the same dial.** Turning down
warms the light, turning up cools it. One axis, because nobody half asleep
wants to set 4200 K independently of 40%.

### 2. Goodnight — the hold

Two stages on one gesture, because the second one is large and must not be
reachable by accident.

| Stage | Hold for | Runs |
|---|---|---|
| Room | 1 s | `script.bedroom_good_night` |
| House | 3 s | `script.bedroom_good_night` + `script.house_good_night` |

`script.house_good_night` is the right target rather than `script.house_all_off`:
it leaves the hallway at 10% and the under-bed strip at 15%, and it does not
kill the AC. `house_all_off` is the leaving-the-house script.

### 3. Music volume and transport

Bedroom audio is TV → eARC → WiiM, so the WiiM holds the real volume.

| Entity | Role |
|---|---|
| `media_player.master_bedroom_master_bedroom_wiim` | Music Assistant player — volume lives here |
| `media_player.khdr_shynh_2` | Native WiiM entity for the same speaker |
| `script.room_media_smart_transport` | Routes play/pause to whichever engine owns the room |
| `script.music_stop_all` | Stop everywhere |

Transport must go through `script.room_media_smart_transport`. A direct
`media_player.media_play_pause` on the Music Assistant entity does nothing
during an AirPlay session, which is how the wall buttons came to look dead.

### 4. Bedroom AC

No bedside control exists for this today, and August in Tel Aviv makes it a
3am problem.

| Entity | Role |
|---|---|
| `climate.bedroom_ac` | Target 25.5, current 26, modes off/heat/cool/dry/heat_cool/fan_only |
| `input_number.mbr_ac_timer_minutes` | Sleep timer, 5–240, currently 85 |
| `timer.mbr_ac_countdown` | Runs the timer |

### 5. Front door state — shown, never operated

`lock.main_door` supports `OPEN` only. The knob displays that the door is
unlocked, on wake, and offers no way to change it.

## What a turn, a tap and a hold do

Three modes. Turning never navigates — it always changes the value in front of
you. Tapping is the only thing that changes mode.

| Mode | Turn | Tap | Hold 1 s | Hold 3 s |
|---|---|---|---|---|
| **Light** (resting) | Brightness ±, warmth follows | → Volume | Room goodnight | House goodnight |
| **Volume** | WiiM volume ±2 points | → AC | Play / pause | Stop music everywhere |
| **AC** | Target temp ±0.5 °C | → Light | Restart sleep timer | AC off |

The mode returns to Light after 20 s of stillness. The knob a cold hand finds
is always the light knob — no exceptions, no context guessing.

`tap` and `hold` are **touchscreen** events. The Waveshare K518 encoder has no
push contact; `SW2` is a four-pin part with two grounds and A/B out.

## What it must show

The screen is 15 cm from a sleeping face. Its default state is **off**, not
dimmed.

| When | Shows |
|---|---|
| Idle | Nothing. Black. |
| Waking | The current mode's value, large, at a brightness derived from `sensor.lumi_lumi_motion_ac02_illuminance` |
| Light | Percent, and an arc whose colour is the warmth about to be set |
| Volume | Volume, and the track title if Music Assistant has one, else the source |
| AC | Target temperature large, room temperature small, sleep timer if `timer.mbr_ac_countdown` is running |
| Holding | A filling arc with a visible break at the room and house stages |
| On wake, if `lock.main_door` is not `locked` | That, above everything else |

It shows no notifications, no repairs, no firmware updates, no weather, and no
battery warnings. There are 13 open repairs in this Home Assistant and none of
them belong on a nightstand.

Haptics are the primary feedback channel, because they work with eyes closed:
one bump per detent, a double bump at the 5% floor and at 100%, and a rising
pattern as the hold arc crosses each stage.

## Acceptance criteria

### Dimming

- WHEN the knob is turned in Light mode THE SYSTEM SHALL call
  `script.bed_strip_step` with a step of ±20 percentage points, and SHALL NOT
  compute the resulting brightness in firmware.
- WHEN the local time is between 06:00 and 22:00 THE SYSTEM SHALL address the
  group `light.home_assistant_connect_zbt_2_bedroom_led_strips` as a single
  multicast.
- WHEN the local time is between 22:00 and 06:00 THE SYSTEM SHALL step
  `light.tzb210_ue01a0s2_ts0502b`, `light.left_nightstand` and
  `light.tzb210_ue01a0s2_ts0502b_2` individually, and SHALL NOT address
  `light.tzb210_ue01a0s2_ts0502b_3`.
- WHEN the knob is turned down THE SYSTEM SHALL NOT bring any light below 5%,
  and SHALL NOT switch any light off.
- WHEN the knob is turned down and a strip is already off THE SYSTEM SHALL
  leave that strip off.
- WHEN a detent is registered THE SYSTEM SHALL render the new value within
  120 ms without waiting for Home Assistant, and SHALL reconcile to the
  reported state when it arrives.
- WHEN brightness is set to 5% THE SYSTEM SHALL set colour temperature to
  2000 K; WHEN brightness is set to 100% THE SYSTEM SHALL set 4000 K; and
  intermediate values SHALL interpolate linearly.

### Goodnight

- WHEN the screen is held for 1 s in Light mode THE SYSTEM SHALL run
  `script.bedroom_good_night`.
- WHEN the hold continues to 3 s THE SYSTEM SHALL additionally run
  `script.house_good_night`.
- WHEN a hold is released before 1 s THE SYSTEM SHALL take no action.
- WHILE a hold is in progress THE SYSTEM SHALL show which stage the current
  duration would commit.
- THE SYSTEM SHALL NOT call `script.house_all_off` from any gesture.
- THE SYSTEM SHALL NOT leave the bedroom with every light off; after any
  goodnight the under-bed strip SHALL be lit.

### Music

- WHEN a transport action is issued THE SYSTEM SHALL call
  `script.room_media_smart_transport` with
  `ma_player: media_player.master_bedroom_master_bedroom_wiim` and
  `native_player: media_player.khdr_shynh_2`.
- WHEN the knob is turned in Volume mode THE SYSTEM SHALL set the volume of
  `media_player.master_bedroom_master_bedroom_wiim` and SHALL cap it at 0.85.
- WHEN nothing is playing and nothing is paused in the bedroom THE SYSTEM SHALL
  show Volume mode as unavailable rather than adjusting a silent speaker.

### AC

- WHEN the knob is turned in AC mode THE SYSTEM SHALL set the target
  temperature of `climate.bedroom_ac` in 0.5 °C steps, bounded to 16–30 °C.
- WHEN `climate.bedroom_ac` is off THE SYSTEM SHALL show it as off, and a turn
  SHALL turn it on in `cool` at the last target rather than adjusting a
  setpoint nothing is chasing.

### The screen

- WHEN no touch and no rotation has occurred for 20 s THE SYSTEM SHALL turn the
  display off entirely and return the mode to Light.
- WHEN the display wakes THE SYSTEM SHALL set its backlight from
  `sensor.lumi_lumi_motion_ac02_illuminance`, and between 22:00 and 06:00 SHALL
  NOT exceed the night ceiling whatever that sensor reports.
- WHEN `lock.main_door` is not `locked` at the moment the display wakes THE
  SYSTEM SHALL show that state before the mode value.
- THE SYSTEM SHALL NOT display persistent notifications, repair issues,
  update availability, or weather.

### Not breaking the room

- THE SYSTEM SHALL NOT call any service that changes `lock.main_door`,
  `alarm_control_panel.home_alarm`, `cover.garage_door` or `vacuum.kitchen_saros_10`.
- WHEN Home Assistant is unreachable THE SYSTEM SHALL show that it is
  unreachable and SHALL NOT silently absorb gestures.

## Out of scope

| Rejected | Why |
|---|---|
| Colour | Every bedroom light reports `supported_color_modes: ["color_temp"]`. There is no colour to control. |
| Locking or unlocking the front door | `lock.main_door` supports `OPEN`. A half-asleep hand on a device with no physical press must not be able to open the house. Status only. |
| Arming or disarming the alarm | `alarm_control_panel.home_alarm` has no `code_format`, so a stray gesture really would disarm it. It also sits at `armed_home` permanently, so a badge would be constant noise. |
| Blinds and curtains | `cover.master_bedroom_vylvn_hplh` has no position support — open, close, stop only, over fire-and-forget RF sent three times. A knob turn has nothing to express. Keys N19-3 and N19-4 are already at the bedside. |
| Ceiling fan speed | N15-7 is tap-for-speed, hold-for-on/off, an arm's length away. |
| Picking a playlist | `input_select.mbr_playlist_browse` has 16 entries. Spinning a 16-item list in the dark is a menu. Resuming what was playing is the whole need. |
| Picking which light | Five dimmable lights and two reading relays. Choosing among them at 3am is a menu; the panel already addresses them individually. |
| Robot vacuum | `vacuum.kitchen_saros_10` has a do-not-disturb window of 22:00–08:00 configured. The house has already answered this. |
| Garage | `cover.garage_door` reads `unknown` and has a lockout state machine and an emergency-stop script. Anything with an emergency stop does not go on a nightstand. |
| TV control | The audio path is the WiiM, not the TV's own volume. The TV has a remote. |
| An alarm clock or wake routine | A wake alarm needs a schedule, a snooze and a sound source. That is a product, not a mode on a dial. `script.house_wake_up` and `scene.mbr_good_morning` already exist for the morning. |
| Masha's side | One knob, one nightstand. Panel N2 is hers. |
| Anything health-related | Different product, same house. |

## Affected surfaces

- New ESPHome device on the Waveshare ESP32-S3-Knob-Touch-LCD-1.8 (Guition
  JC3636K518C-I-YR1), same board as `tomereli/coffee-knob`.
- No new Home Assistant scripts. The knob calls `script.bed_strip_step`,
  `script.bedroom_good_night`, `script.house_good_night`,
  `script.room_media_smart_transport` and `script.music_stop_all` as they
  stand. The dimming policy — the night rule, the 5% floor, the absolute-target
  computation — lives in one place and stays there.
- `allow_service_calls` must be enabled on the ESPHome device or every call
  fails silently.
- First flash over USB-A → USB-C. A C→C cable picks which of the two chips you
  reach at random.

## Decisions needed

1. **The encoder has no push contact.** Tap and hold are specified as
   touchscreen gestures. Confirm that, or name the hardware if a knob with a
   real press is being sourced instead.
2. **House goodnight turns off Romi's spots.** `script.house_good_night`
   includes `light.home_assistant_connect_zbt_2_romi_lights_spots`. Should the
   3-second hold be able to darken a child's room, or should stage 2 skip the
   kids' lights?
3. **The warmth curve.** 2000 K at 5% to 4000 K at 100%. Too warm at the top,
   or right?
4. **A clock while idle.** The screen is specified as fully off. A permanently
   dim clock is the obvious alternative and the obvious light-pollution risk.
5. **AC mode's hold.** Restarting the 85-minute sleep timer, or switching the
   AC off outright? The smart-cycle automations already decide when to stop
   cooling.
