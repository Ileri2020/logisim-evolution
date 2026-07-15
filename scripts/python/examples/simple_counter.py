import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.api import Circuit, Counter, Gate, Wire

output = Path(__file__).with_name("simple_counter_blueprint.json")

circuit = Circuit("simple_counter")
circuit.add(Gate("and", "and0", x=100, y=120, label="AND0"))
circuit.add(Counter("cnt0", x=260, y=120, label="Counter"))
# connect AND -> CNT using coordinates for embedded placement
circuit.add(Wire("w0", "100,120", "260,120"))
circuit.save_to(output)
print(f"wrote {output}")
