from pathlib import Path

from .builder import BlueprintBuilder


def build_extended_catalog(output_path: str | Path | None = None):
    builder = BlueprintBuilder("extended_catalog")
    builder.add_floating_point_adder("fpa0")
    builder.add_ram("ram0")
    builder.add_led("led0")
    builder.add_ttl_7400("ttl0")
    builder.add_tcl("tcl0")
    builder.add_bfh_mega_function("mega0")
    builder.add_input_output_extra("ioextra0")
    builder.add_system_on_chip("soc0")
    if output_path is not None:
        builder.save(output_path)
    return builder.circuit.to_dict()
