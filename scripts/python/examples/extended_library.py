import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

output = Path(__file__).with_name("extended_library_blueprint.json")

builder = BlueprintBuilder("extended_library")
builder.add_pin("pin0")
builder.add_probe("probe0")
builder.add_splitter("split0")
builder.add_clock("clk0")
builder.add_constant("const0")
builder.add_power("pwr0")
builder.add_ground("gnd0")
builder.add_not_gate("inv0")
builder.add_and_gate("and0")
builder.add_multiplexer("mux0")
builder.add_adder("add0")
builder.add_counter("cnt0")
builder.add_ram("ram0")
builder.add_button("btn0")
builder.add_led("led0")
builder.add_dip_switch("sw0")
builder.add_uart("uart0")
builder.add_floating_point_adder("fpadder0")
builder.add_register("reg0")
builder.add_d_flip_flop("dff0")
builder.add_ttl_7400("ttl0")
builder.add_cpu_core("cpu0")
builder.save(output)
print(f"wrote {output}")
