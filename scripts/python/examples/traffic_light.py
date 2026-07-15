import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

output = Path(__file__).with_name("traffic_light_blueprint.json")

builder = BlueprintBuilder("traffic_light")
builder.add_clock("clk", x=80, y=120, label="CLK")
builder.add_counter("state", x=260, y=120, label="STATE")
builder.add_wire("w0", "80,120", "260,120")
builder.add_led("red", x=420, y=80, label="RED")
builder.add_led("yellow", x=420, y=120, label="YELLOW")
builder.add_led("green", x=420, y=160, label="GREEN")
builder.save(output)
print(f"wrote {output}")
