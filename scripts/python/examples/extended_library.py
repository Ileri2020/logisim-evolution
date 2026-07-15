import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder

output = Path(__file__).with_name("extended_library_blueprint.json")

builder = BlueprintBuilder("extended_library")
# place a small curated selection on a grid for the example
builder.add_pin("pin0", x=60, y=60, label="PIN0")
builder.add_probe("probe0", x=160, y=60, label="PROBE")
builder.add_splitter("split0", x=260, y=60, label="SPLIT")
builder.add_clock("clk0", x=60, y=140, label="CLK")
builder.add_constant("const0", x=160, y=140, label="CONST")
builder.add_power("pwr0", x=260, y=140, label="PWR")
builder.add_ground("gnd0", x=360, y=140, label="GND")
builder.add_not_gate("inv0", x=60, y=220, label="INV")
builder.add_and_gate("and0", x=160, y=220, label="AND")
builder.add_multiplexer("mux0", x=260, y=220, label="MUX")
builder.add_adder("add0", x=360, y=220, label="ADD")
builder.add_counter("cnt0", x=460, y=220, label="CNT")
builder.add_ram("ram0", x=60, y=300, label="RAM")
builder.add_button("btn0", x=160, y=300, label="BTN")
builder.add_led("led0", x=260, y=300, label="LED")
builder.add_dip_switch("sw0", x=360, y=300, label="SW")
builder.add_uart("uart0", x=460, y=300, label="UART")
builder.add_floating_point_adder("fpadder0", x=60, y=380, label="FPADD")
builder.add_register("reg0", x=160, y=380, label="REG")
builder.add_d_flip_flop("dff0", x=260, y=380, label="DFF")
builder.add_ttl_7400("ttl0", x=360, y=380, label="TTL7400")
builder.add_cpu_core("cpu0", x=460, y=380, label="CPU")
builder.save(output)
print(f"wrote {output}")
