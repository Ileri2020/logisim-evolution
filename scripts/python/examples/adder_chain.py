import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

output = Path(__file__).with_name("adder_chain_blueprint.json")

builder = BlueprintBuilder("adder_chain")
builder.add_pin("a", x=80, y=120, label="A")
builder.add_pin("b", x=80, y=180, label="B")
builder.add_adder("add0", x=260, y=150, label="Adder0")
builder.add_wire("w_a", "80,120", "260,140")
builder.add_wire("w_b", "80,180", "260,160")
builder.add_led("sum", x=420, y=150, label="SUM")
builder.save(output)
print(f"wrote {output}")
