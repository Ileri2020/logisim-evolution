import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

output = Path(__file__).with_name("nor_gate_flip_flop_blueprint.json")

builder = BlueprintBuilder("nor_gate_flip_flop")
builder.add_pin("set", x=80, y=120, label="SET")
builder.add_pin("reset", x=80, y=180, label="RESET")
builder.add_nor_gate("nor0", x=260, y=140, label="NOR0")
builder.add_nor_gate("nor1", x=260, y=200, label="NOR1")
builder.add_wire("w_set", "80,120", "260,140")
builder.add_wire("w_reset", "80,180", "260,200")
builder.add_led("q", x=420, y=140, label="Q")
builder.add_led("q_bar", x=420, y=200, label="Q_BAR")
builder.save(output)
print(f"wrote {output}")
