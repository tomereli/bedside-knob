"""Issue #3 — an off AC/FAN card must not show a full-length ring in its hue.

Loads firmware/bedside-knob.yaml with a YAML loader tolerant of ESPHome's own
!lambda / !secret / !include tags, then asserts against the parsed widget and
script structures. These are structural checks on the shape of the fix, not
proof of the visual — no frame is rendered here. Per CLAUDE.md and plan.md's
hand-check table, the change isn't done until it has been turned by hand on
the device in a dark room.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
FIRMWARE_YAML = REPO_ROOT / "firmware" / "bedside-knob.yaml"


class _TolerantLoader(yaml.SafeLoader):
    """A SafeLoader that returns the raw scalar for ESPHome's own tags."""


def _raw_scalar(loader, node):
    return loader.construct_scalar(node)


_TolerantLoader.add_constructor("!lambda", _raw_scalar)
_TolerantLoader.add_constructor("!secret", _raw_scalar)
_TolerantLoader.add_constructor("!include", _raw_scalar)


@pytest.fixture(scope="session")
def config():
    text = FIRMWARE_YAML.read_text(encoding="utf-8")
    return yaml.load(text, Loader=_TolerantLoader)


def _widget(cfg, page_id, widget_id):
    for page in cfg["lvgl"]["pages"]:
        if page.get("id") != page_id:
            continue
        for entry in page["widgets"]:
            for body in entry.values():
                if isinstance(body, dict) and body.get("id") == widget_id:
                    return body
    raise AssertionError(f"widget {widget_id!r} not found on page {page_id!r}")


def _script(cfg, script_id):
    for script in cfg["script"]:
        if script.get("id") == script_id:
            return script
    raise AssertionError(f"script {script_id!r} not found")


def _flatten(obj):
    """Concatenate every string leaf and dict key under obj for substring checks."""
    if isinstance(obj, dict):
        return "\n".join(f"{k}\n{_flatten(v)}" for k, v in obj.items())
    if isinstance(obj, list):
        return "\n".join(_flatten(item) for item in obj)
    return str(obj)


def _update_step(script_body, update_key, widget_id):
    for step in script_body["then"]:
        if isinstance(step, dict) and update_key in step and step[update_key].get("id") == widget_id:
            return step[update_key]
    raise AssertionError(f"no {update_key} step for {widget_id!r} in the script")


def _show_hide_branch(script_body, widget_id):
    """Find the `if:` step in a script's `then:` list that shows/hides widget_id."""
    for step in script_body["then"]:
        if not isinstance(step, dict) or "if" not in step:
            continue
        branch = step["if"]
        text = _flatten(branch)
        if f"lvgl.widget.show\n{widget_id}" in text or f"lvgl.widget.hide\n{widget_id}" in text:
            return branch
    raise AssertionError(f"no if/show/hide branch for {widget_id!r} in the script")


# ---------------------------------------------------------------------------
# 0 — regression gate
# ---------------------------------------------------------------------------


def test_esphome_config_validates(tmp_path):
    """The pin map, widget tree and external component still validate.

    Runs against a throwaway copy of the firmware YAML with a dummy
    secrets.yaml in a scratch directory — never firmware/secrets.yaml, which
    per aisdlc.yml a crew must never read, write, or commit.
    """
    shutil.copy(FIRMWARE_YAML, tmp_path / "bedside-knob.yaml")
    (tmp_path / "secrets.yaml").write_text(
        'wifi_ssid: "test-network"\nwifi_password: "test-password"\n',
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-m", "esphome", "config", "bedside-knob.yaml"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Configuration is valid!" in result.stderr


# ---------------------------------------------------------------------------
# 1 — fan off draws no ring
# ---------------------------------------------------------------------------


def test_fan_arc_starts_hidden(config):
    widget = _widget(config, "page_fan", "arc_fan")
    assert widget.get("hidden") is True


def test_fan_paint_shows_and_hides_the_ring(config):
    script = _script(config, "paint_fan")
    branch = _show_hide_branch(script, "arc_fan")
    assert "fan_step" in _flatten(branch["condition"])
    assert "lvgl.widget.show\narc_fan" in _flatten(branch.get("then"))
    assert "lvgl.widget.hide\narc_fan" in _flatten(branch.get("else"))


# ---------------------------------------------------------------------------
# 2 — AC off (and unavailable) draws no ring
# ---------------------------------------------------------------------------


def test_ac_arc_starts_hidden(config):
    widget = _widget(config, "page_ac", "arc_ac")
    assert widget.get("hidden") is True


def test_ac_paint_shows_and_hides_the_ring(config):
    script = _script(config, "paint_ac")
    branch = _show_hide_branch(script, "arc_ac")
    assert "ac_on" in _flatten(branch["condition"])
    assert "lvgl.widget.show\narc_ac" in _flatten(branch.get("then"))
    assert "lvgl.widget.hide\narc_ac" in _flatten(branch.get("else"))


def test_ac_on_predicate_is_a_closed_whitelist(config):
    """The on/off predicate must positively match HA's closed HVACMode enum,
    so an unmapped state (unavailable, unknown, pre-link "") fails closed to
    the off appearance instead of reading as on."""
    script = _script(config, "paint_ac")
    predicate_step = script["then"][0]
    predicate_text = _flatten(predicate_step)

    assert "ac_on" in predicate_text
    for mode in ("cool", "heat", "dry", "fan_only", "auto", "heat_cool"):
        assert f'"{mode}"' in predicate_text

    # A blacklist reading (`!= "off" && != "unavailable"`) would read "off"
    # and "unknown" states as on. Assert it's gone so a future edit can't
    # quietly swap the whitelist back for one.
    assert '!= "off"' not in predicate_text
    assert '!= "unavailable"' not in predicate_text


def test_ac_label_and_arc_share_the_on_predicate(config):
    """The value label, the arc's value, and the arc's visibility must all
    key off the same id(ac_on) global rather than re-testing the state
    string, or they can drift apart again."""
    script = _script(config, "paint_ac")

    label = _update_step(script, "lvgl.label.update", "val_ac")
    arc = _update_step(script, "lvgl.arc.update", "arc_ac")
    visibility = _show_hide_branch(script, "arc_ac")

    assert "id(ac_on)" in label["text"]
    assert "id(ac_on)" in arc["value"]
    assert "id(ac_on)" in _flatten(visibility["condition"])


# ---------------------------------------------------------------------------
# 3 — on is distinguishable from off by length or presence alone
# ---------------------------------------------------------------------------


def test_on_state_floor_is_visible(config):
    floor = int(config["substitutions"]["min_on"])
    assert floor >= 5

    ac_widget = _widget(config, "page_ac", "arc_ac")
    fan_widget = _widget(config, "page_fan", "arc_fan")
    assert floor > ac_widget["min_value"]
    assert floor > fan_widget["min_value"]

    ac_value = _update_step(_script(config, "paint_ac"), "lvgl.arc.update", "arc_ac")["value"]
    fan_value = _update_step(_script(config, "paint_fan"), "lvgl.arc.update", "arc_fan")["value"]
    assert "min_on" in ac_value
    assert "min_on" in fan_value


# ---------------------------------------------------------------------------
# 4 — the ring stays readable as a value indicator across its whole range
# ---------------------------------------------------------------------------


def test_ring_stays_readable_across_the_full_range(config):
    for page_id, widget_id in (("page_ac", "arc_ac"), ("page_fan", "arc_fan")):
        widget = _widget(config, page_id, widget_id)
        assert widget["min_value"] == 0
        assert widget["max_value"] == 100

    ac_value = _update_step(_script(config, "paint_ac"), "lvgl.arc.update", "arc_ac")["value"]
    assert "16.0f" in ac_value  # 16.0 degC is the bottom of the AC's on-range, mapped to the floor
    assert "14.0f" in ac_value  # 30.0 - 16.0: the span the mapping divides by, reaching 100 at 30.0 degC

    fan_value = _update_step(_script(config, "paint_fan"), "lvgl.arc.update", "arc_fan")["value"]
    assert "100 / 6" in fan_value  # step 6 of 6 maps to the full scale
