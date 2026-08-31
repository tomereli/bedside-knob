# What the owner asked for

Stated 2026-08-30. This overrides anything in `REQUIREMENTS.md` that
disagrees with it.

## Duplication with the Vitrea panel is fine

The eight-key panel at the bedside is not a reason to leave something off
the knob. Existing keys may be refactored later; do not design around
avoiding overlap.

## Must control, in this order

1. **Lights, per group** — each of these is a separate target:
   - the wave
   - his bedside LED
   - Masha's bedside LED
   - both bedsides together with the under-bed strip
   - all lights together
   - the closet room
   - the bathroom
2. **Music**
3. **AC and fan**

## The design problem this creates

Seven light targets, plus music, plus climate, on a device with **no
physical button** — turn, touch tap, touch hold — operated in the dark,
half asleep, at 45–60° off normal from a pillow, with a 120 ms detent
budget that forbids rebuilding a page while the dial moves.

Selecting a target is now the hard part, and it is the part to solve. A
menu that must be read is a failure: the eyes are closed or unfocused, and
the hand arrives before the attention does.
