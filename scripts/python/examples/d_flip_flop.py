import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

output = Path(__file__).with_name("d_flip_flop_blueprint.json")

builder = BlueprintBuilder("d_flip_flop")
builder.add_pin("d", x=80, y=120, label="D")
builder.add_clock("clk", x=80, y=180, label="CLK")
builder.add_d_flip_flop("dff0", x=260, y=150, label="DFF0")
builder.add_wire("w_d", "80,120", "260,140")
builder.add_wire("w_clk", "80,180", "260,160")
builder.add_led("q", x=420, y=150, label="Q")
builder.save(output)
print(f"wrote {output}")
