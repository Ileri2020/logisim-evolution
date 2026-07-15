import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

output = Path(__file__).with_name("shift_register_blueprint.json")

builder = BlueprintBuilder("shift_register")
builder.add_clock("clk", x=80, y=120, label="CLK")
builder.add_shift_register("sr0", x=260, y=120, label="ShiftReg")
builder.add_wire("w0", "80,120", "260,120")
builder.add_led("out", x=420, y=120, label="OUT")
builder.save(output)
print(f"wrote {output}")
