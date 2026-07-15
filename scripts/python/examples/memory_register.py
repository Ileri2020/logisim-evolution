import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

output = Path(__file__).with_name("memory_register_blueprint.json")

builder = BlueprintBuilder("memory_register")
builder.add_pin("data", x=80, y=120, label="DATA")
builder.add_clock("clk", x=80, y=180, label="CLK")
builder.add_register("reg0", x=260, y=150, label="REG0")
# connect DATA -> REG and CLK -> REG using coordinates
builder.add_wire("w_data", "80,120", "260,140")
builder.add_wire("w_clk", "80,180", "260,160")
builder.add_led("q", x=420, y=150, label="Q")
builder.save(output)
print(f"wrote {output}")
