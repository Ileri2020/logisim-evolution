import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

output = Path(__file__).with_name("sr_latch_blueprint.json")

builder = BlueprintBuilder("sr_latch")
builder.add_pin("s", x=80, y=120, label="S")
builder.add_pin("r", x=80, y=180, label="R")
builder.add_sr_latch("latch0", x=260, y=150, label="SR_LATCH")
builder.add_wire("w_s", "80,120", "260,140")
builder.add_wire("w_r", "80,180", "260,160")
builder.add_led("q", x=420, y=140, label="Q")
builder.add_led("q_bar", x=420, y=180, label="Q_BAR")
builder.save(output)
print(f"wrote {output}")
