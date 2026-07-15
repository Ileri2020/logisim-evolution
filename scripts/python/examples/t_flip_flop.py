import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

output = Path(__file__).with_name("t_flip_flop_blueprint.json")

builder = BlueprintBuilder("t_flip_flop")
builder.add_clock("clk", x=80, y=120, label="CLK")
builder.add_t_flip_flop("tff0", x=260, y=120, label="TFF0")
builder.add_wire("w0", "80,120", "260,120")
builder.add_led("q", x=420, y=120, label="Q")
builder.save(output)
print(f"wrote {output}")
