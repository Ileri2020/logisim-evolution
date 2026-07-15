import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

output = Path(__file__).with_name("advanced_counter_blueprint.json")
builder = BlueprintBuilder("advanced_counter")
builder.add_gate("xor", "xor0", x=100, y=120, label="XOR0")
builder.add_counter("cnt0", x=260, y=120, label="Counter")
# wire between XOR and counter using coordinates for embedded placement
builder.add_wire("w0", "100,120", "260,120")
builder.save(output)
print(f"wrote {output}")
