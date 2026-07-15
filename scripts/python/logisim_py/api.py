import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def _is_embedded() -> bool:
    """Return True when running inside the Logisim GraalPy embedded interpreter.

    In embedded mode the Java bridge injects a global named ``logisim`` that
    exposes ``logisim.context`` and ``logisim.ops`` – mirroring Blender's ``bpy``
    module.  When running as a standalone Python script the global is absent and
    we fall back to offline JSON serialisation.
    """
    try:
        return logisim is not None  # noqa: F821  (injected by PythonScriptManager)
    except NameError:
        return False


class CircuitElement:
    def __init__(self, element_type: str, name: str, **kwargs: Any) -> None:
        self.type = element_type
        self.name = name
        self.kwargs = kwargs

    def to_dict(self) -> Dict[str, Any]:
        data = {"type": self.type, "name": self.name}
        data.update(self.kwargs)
        return data


class Gate(CircuitElement):
    def __init__(self, gate_type: str, name: str, **kwargs: Any) -> None:
        super().__init__("gate", name, gate_type=gate_type, **kwargs)


class Splitter(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("splitter", name, **kwargs)


class Pin(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("pin", name, **kwargs)


class Probe(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("probe", name, **kwargs)


class Tunnel(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("tunnel", name, **kwargs)


class PullResistor(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("pull_resistor", name, **kwargs)


class Clock(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("clock", name, **kwargs)


class Por(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("por", name, **kwargs)


class Constant(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("constant", name, **kwargs)


class Power(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("power", name, **kwargs)


class Ground(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ground", name, **kwargs)


class DoNotConnect(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("do_not_connect", name, **kwargs)


class Transistor(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("transistor", name, **kwargs)


class TransmissionGate(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("transmission_gate", name, **kwargs)


class BitExtender(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("bit_extender", name, **kwargs)


class Wire(CircuitElement):
    def __init__(self, name: str, source: str, target: str, **kwargs: Any) -> None:
        super().__init__("wire", name, source=source, target=target, **kwargs)


class Counter(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("counter", name, **kwargs)


class NotGate(Gate):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("not", name, **kwargs)


class Buffer(Gate):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("buffer", name, **kwargs)


class AndGate(Gate):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("and", name, **kwargs)


class OrGate(Gate):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("or", name, **kwargs)


class NandGate(Gate):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("nand", name, **kwargs)


class NorGate(Gate):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("nor", name, **kwargs)


class XorGate(Gate):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("xor", name, **kwargs)


class XnorGate(Gate):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("xnor", name, **kwargs)


class OddParityGate(Gate):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("odd_parity", name, **kwargs)


class EvenParityGate(Gate):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("even_parity", name, **kwargs)


class ControlledBuffer(Gate):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("controlled_buffer", name, **kwargs)


class ControlledInverter(Gate):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("controlled_inverter", name, **kwargs)


class Pla(Gate):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("pla", name, **kwargs)


class Multiplexer(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("multiplexer", name, **kwargs)


class Demultiplexer(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("demultiplexer", name, **kwargs)


class Decoder(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("decoder", name, **kwargs)


class PriorityEncoder(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("priority_encoder", name, **kwargs)


class BitSelector(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("bit_selector", name, **kwargs)


class Adder(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("adder", name, **kwargs)


class Subtractor(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("subtractor", name, **kwargs)


class Multiplier(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("multiplier", name, **kwargs)


class Divider(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("divider", name, **kwargs)


class Negator(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("negator", name, **kwargs)


class Exponentiator(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("exponentiator", name, **kwargs)


class SquareRoot(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("square_root", name, **kwargs)


class Absolute(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("absolute", name, **kwargs)


class Comparator(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("comparator", name, **kwargs)


class Maximum(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("maximum", name, **kwargs)


class Minimum(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("minimum", name, **kwargs)


class Shifter(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("shifter", name, **kwargs)


class BitAdder(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("bit_adder", name, **kwargs)


class BitFinder(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("bit_finder", name, **kwargs)


class FloatingPointConstant(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_constant", name, **kwargs)


class FloatingPointParser(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_parser", name, **kwargs)


class FloatingPointDisplay(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_display", name, **kwargs)


class FloatingPointAdder(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_adder", name, **kwargs)


class FloatingPointSubtractor(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_subtractor", name, **kwargs)


class FloatingPointMultiplier(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_multiplier", name, **kwargs)


class FloatingPointDivider(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_divider", name, **kwargs)


class FloatingPointComparator(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_comparator", name, **kwargs)


class FloatingPointNegator(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_negator", name, **kwargs)


class FloatingPointAbsoluteValue(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_absolute_value", name, **kwargs)


class FloatingPointSquareRoot(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_square_root", name, **kwargs)


class FloatingPointRounder(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_rounder", name, **kwargs)


class FloatingPointConverter(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_converter", name, **kwargs)


class IntegerToFloatingPointConverter(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("integer_to_floating_point_converter", name, **kwargs)


class FloatingPointToIntegerConverter(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_to_integer_converter", name, **kwargs)


class FloatingPointExponentExtractor(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_exponent_extractor", name, **kwargs)


class FloatingPointMantissaExtractor(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_mantissa_extractor", name, **kwargs)


class TclComponent(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("tcl", name, **kwargs)


class BfhMegaFunction(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("bfh_mega_function", name, **kwargs)


class InputOutputExtra(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("input_output_extra", name, **kwargs)


class SystemOnChip(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("system_on_chip", name, **kwargs)


class MemoryElement(CircuitElement):
    def __init__(self, element_type: str, name: str, **kwargs: Any) -> None:
        super().__init__(element_type, name, **kwargs)


class Ram(MemoryElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ram", name, **kwargs)


class Rom(MemoryElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("rom", name, **kwargs)


class Register(MemoryElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("register", name, **kwargs)


class RegisterFile(MemoryElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("register_file", name, **kwargs)


class ShiftRegister(MemoryElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("shift_register", name, **kwargs)


class Eeprom(MemoryElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("eeprom", name, **kwargs)


class Sram(MemoryElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("sram", name, **kwargs)


class Dram(MemoryElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("dram", name, **kwargs)


class FifoQueue(MemoryElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("fifo_queue", name, **kwargs)


class LifoStack(MemoryElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("lifo_stack", name, **kwargs)


class DualPortRam(MemoryElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("dual_port_ram", name, **kwargs)


class Button(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("button", name, **kwargs)


class Led(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("led", name, **kwargs)


class RgbLed(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("rgb_led", name, **kwargs)


class SevenSegmentDisplay(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("seven_segment_display", name, **kwargs)


class HexDigitDisplay(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("hex_digit_display", name, **kwargs)


class DotMatrixDisplay(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("dot_matrix_display", name, **kwargs)


class LcdDisplay(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("lcd_display", name, **kwargs)


class DipSwitch(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("dip_switch", name, **kwargs)


class Joystick(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("joystick", name, **kwargs)


class Keyboard(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("keyboard", name, **kwargs)


class Mouse(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("mouse", name, **kwargs)


class Uart(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("uart", name, **kwargs)


class SerialInput(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("serial_input", name, **kwargs)


class SerialOutput(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("serial_output", name, **kwargs)


class ParallelInput(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("parallel_input", name, **kwargs)


class ParallelOutput(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("parallel_output", name, **kwargs)


class SpiInterface(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("spi_interface", name, **kwargs)


class I2cInterface(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("i2c_interface", name, **kwargs)


class TtyTerminal(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("tty_terminal", name, **kwargs)


class TextDisplay(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("text_display", name, **kwargs)


class Console(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("console", name, **kwargs)


class FileReader(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("file_reader", name, **kwargs)


class FileWriter(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("file_writer", name, **kwargs)


class HexKeyboard(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("hex_keyboard", name, **kwargs)


class NumericKeyboard(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("numeric_keyboard", name, **kwargs)


class Stopwatch(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("stopwatch", name, **kwargs)


class DigitalOscilloscope(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("digital_oscilloscope", name, **kwargs)


class LogicAnalyzer(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("logic_analyzer", name, **kwargs)


class FrequencyCounter(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("frequency_counter", name, **kwargs)


class PulseGenerator(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("pulse_generator", name, **kwargs)


class AnalogInput(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("analog_input", name, **kwargs)


class AnalogOutput(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("analog_output", name, **kwargs)


class Ttl7400(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_7400", name, **kwargs)


class Ttl7402(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_7402", name, **kwargs)


class Ttl7404(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_7404", name, **kwargs)


class Ttl7408(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_7408", name, **kwargs)


class Ttl7432(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_7432", name, **kwargs)


class Ttl7486(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_7486", name, **kwargs)


class Ttl7474(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_7474", name, **kwargs)


class Ttl7476(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_7476", name, **kwargs)


class Ttl7490(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_7490", name, **kwargs)


class Ttl7493(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_7493", name, **kwargs)


class Ttl74161(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_74161", name, **kwargs)


class Ttl74163(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_74163", name, **kwargs)


class Ttl74173(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_74173", name, **kwargs)


class Ttl74175(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_74175", name, **kwargs)


class Ttl74194(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_74194", name, **kwargs)


class Ttl74150(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_74150", name, **kwargs)


class Ttl74151(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_74151", name, **kwargs)


class Ttl74153(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_74153", name, **kwargs)


class Ttl74157(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_74157", name, **kwargs)


class Ttl74138(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_74138", name, **kwargs)


class Ttl74139(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_74139", name, **kwargs)


class Ttl7442(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_7442", name, **kwargs)


class Ttl7483(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_7483", name, **kwargs)


class Ttl74283(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_74283", name, **kwargs)


class Ttl74181(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("ttl_74181", name, **kwargs)


class NmosTransistor(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("nmos_transistor", name, **kwargs)


class PmosTransistor(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("pmos_transistor", name, **kwargs)


class CmosTransistor(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("cmos_transistor", name, **kwargs)


class CmosInverter(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("cmos_inverter", name, **kwargs)


class CmosNand(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("cmos_nand", name, **kwargs)


class CmosNor(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("cmos_nor", name, **kwargs)


class CmosAnd(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("cmos_and", name, **kwargs)


class CmosOr(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("cmos_or", name, **kwargs)


class PullUp(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("pull_up", name, **kwargs)


class PullDown(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("pull_down", name, **kwargs)


class TriStateBuffer(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("tri_state_buffer", name, **kwargs)


class OpenCollectorOutput(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("open_collector_output", name, **kwargs)


class ArithmeticUnit(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("arithmetic_unit", name, **kwargs)


class Alu(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("alu", name, **kwargs)


class BarrelShifter(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("barrel_shifter", name, **kwargs)


class ComparatorUnit(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("comparator_unit", name, **kwargs)


class DividerUnit(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("divider_unit", name, **kwargs)


class MultiplierUnit(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("multiplier_unit", name, **kwargs)


class FloatingPointUnit(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("floating_point_unit", name, **kwargs)


class RegisterBank(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("register_bank", name, **kwargs)


class MemoryController(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("memory_controller", name, **kwargs)


class BusController(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("bus_controller", name, **kwargs)


class InterruptController(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("interrupt_controller", name, **kwargs)


class CpuComponent(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("cpu_component", name, **kwargs)


class PipelineComponent(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("pipeline_component", name, **kwargs)


class CpuCore(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("cpu_core", name, **kwargs)


class Microcontroller(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("microcontroller", name, **kwargs)


class Processor(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("processor", name, **kwargs)


class Bus(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("bus", name, **kwargs)


class SystemBus(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("system_bus", name, **kwargs)


class AddressDecoder(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("address_decoder", name, **kwargs)


class DmaController(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("dma_controller", name, **kwargs)


class Timer(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("timer", name, **kwargs)


class ClockController(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("clock_controller", name, **kwargs)


class UartController(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("uart_controller", name, **kwargs)


class GpioController(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("gpio_controller", name, **kwargs)


class SpiController(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("spi_controller", name, **kwargs)


class I2cController(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("i2c_controller", name, **kwargs)


class CacheController(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("cache_controller", name, **kwargs)


class BootRom(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("boot_rom", name, **kwargs)


class PeripheralController(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("peripheral_controller", name, **kwargs)


class DFlipFlop(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("d_flip_flop", name, **kwargs)


class TFlipFlop(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("t_flip_flop", name, **kwargs)


class JkFlipFlop(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("jk_flip_flop", name, **kwargs)


class SrFlipFlop(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("sr_flip_flop", name, **kwargs)


class EnabledFlipFlop(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("enabled_flip_flop", name, **kwargs)


class EdgeTriggeredFlipFlop(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("edge_triggered_flip_flop", name, **kwargs)


class Latch(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("latch", name, **kwargs)


class DLatch(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("d_latch", name, **kwargs)


class SRLatch(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("sr_latch", name, **kwargs)


class ClockDivider(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("clock_divider", name, **kwargs)


class StateMachine(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("state_machine", name, **kwargs)


class FiniteStateMachine(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("finite_state_machine", name, **kwargs)


class ComparatorController(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("comparator_controller", name, **kwargs)


class EnableGenerator(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("enable_generator", name, **kwargs)


class ResetGenerator(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("reset_generator", name, **kwargs)


class Synchronizer(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("synchronizer", name, **kwargs)


class Debouncer(CircuitElement):
    def __init__(self, name: str, **kwargs: Any) -> None:
        super().__init__("debouncer", name, **kwargs)


class Circuit:
    """Represents a Logisim circuit.

    When running inside the Logisim embedded GraalPy interpreter (``_is_embedded()``
    returns ``True``), calls to :meth:`add` are routed directly to the live Java
    simulation model via ``logisim.ops`` – exactly as Blender routes ``bpy.ops``
    calls into its scene graph.

    When running as a standalone offline script the class behaves as before:
    elements are collected in-memory and serialised to a JSON blueprint file via
    :meth:`save_to`.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.elements: List[CircuitElement] = []
        # Auto-incrementing X position for component placement
        self._x_cursor: int = 100
        self._y_cursor: int = 100
        self._y_step: int = 60

    def add(self, element: "CircuitElement") -> None:
        """Add a circuit element.

        In **embedded** mode the element is placed on the live canvas using
        ``logisim.ops`` so it appears in the GUI immediately.  Each call
        increments the auto-layout cursor so components don't overlap.

        In **offline** mode the element is appended to the in-memory list for
        later JSON serialisation.
        """
        self.elements.append(element)
        if _is_embedded():
            self._place_embedded(element)

    def _place_embedded(self, element: "CircuitElement") -> None:
        """Route an element to the live Java model via the ``logisim.ops`` binding."""
        try:
            ops = logisim.ops  # noqa: F821
            etype = element.type
            gate_type = element.kwargs.get("gate_type", None)
            x = int(element.kwargs.get("x", self._x_cursor))
            y = int(element.kwargs.get("y", self._y_cursor))
            label = element.kwargs.get("label", element.name)

            wiring_types = [
                "splitter", "probe", "tunnel", "pull_resistor", "clock",
                "por", "constant", "power", "ground", "do_not_connect",
                "transistor", "transmission_gate", "bit_extender"
            ]
            plexer_types = [
                "multiplexer", "demultiplexer", "decoder",
                "priority_encoder", "bit_selector"
            ]
            arith_types = [
                "adder", "subtractor", "multiplier", "divider",
                "negator", "exponentiator", "square_root", "absolute",
                "comparator", "maximum", "minimum", "shifter",
                "bit_adder", "bit_finder"
            ]
            fp_arith_mappings = {
                "floating_point_adder": "fpadder",
                "floating_point_subtractor": "fpsubtractor",
                "floating_point_multiplier": "fpmultiplier",
                "floating_point_divider": "fpdivider",
                "floating_point_comparator": "fpcomparator",
                "floating_point_negator": "fpnegator",
                "floating_point_absolute_value": "fpabsolute",
                "floating_point_square_root": "fpsquareroot",
                "floating_point_rounder": "fpround",
                "floating_point_converter": "fptofp",
                "integer_to_floating_point_converter": "inttofp",
                "floating_point_to_integer_converter": "fptoint",
                "floating_point_exponent_extractor": "fpexponentiator",
                "floating_point_mantissa_extractor": "fpclassificator",
            }
            memory_mappings = {
                "ram": "ram",
                "rom": "rom",
                "register": "register",
                "shift_register": "shift_register",
                "dual_port_ram": "dual_ram",
                "counter": "counter",
            }
            io_mappings = {
                "button": "button",
                "led": "led",
                "rgb_led": "rgb_led",
                "seven_segment_display": "seven_segment",
                "hex_digit_display": "hex_digit",
                "dot_matrix_display": "dot_matrix",
                "dip_switch": "dip_switch",
                "joystick": "joystick",
                "keyboard": "keyboard",
                "tty_terminal": "tty",
            }
            extra_io_mappings = {
                "digital_oscilloscope": "digital_oscilloscope",
                "buzzer": "buzzer",
                "slider": "slider",
                "switch": "switch",
                "pla_rom": "pla_rom",
            }

            if etype == "wire":
                source = element.kwargs.get("source")
                target = element.kwargs.get("target")
                if source is not None and target is not None:
                    ops.add_wire(int(source.split(",")[0]), int(source.split(",")[1]), int(target.split(",")[0]), int(target.split(",")[1]))
                else:
                    ops.add_wire(x, y, x + 40, y)
            elif etype == "gate" and gate_type is not None:
                ops.add_gate(gate_type, x, y, label)
            elif etype == "pin":
                is_input = element.kwargs.get("is_input", True)
                ops.add_pin(x, y, is_input, label)
            elif etype in wiring_types:
                ops.add_wiring(etype, x, y)
            elif etype in plexer_types:
                ops.add_plexer(etype, x, y)
            elif etype in arith_types:
                ops.add_arith(etype, x, y)
            elif etype in fp_arith_mappings:
                ops.add_fp_arith(fp_arith_mappings[etype], x, y)
            elif etype in memory_mappings:
                ops.add_memory(memory_mappings[etype], x, y)
            elif etype in io_mappings:
                ops.add_io(io_mappings[etype], x, y)
            elif etype.startswith("ttl_"):
                ops.add_ttl(etype.replace("ttl_", ""), x, y)
            elif etype == "tcl":
                ops.add_tcl("tcl_generic", x, y)
            elif etype == "bfh_mega_function":
                ops.add_bfh("bin_to_bcd", x, y)
            elif etype in extra_io_mappings:
                ops.add_extra_io(extra_io_mappings[etype], x, y)
            elif etype == "system_on_chip":
                ops.add_soc("nios2", x, y)
            else:
                # For component types not yet individually wired up, emit a debug note.
                print(f"[logisim] embedded placement not yet supported for type '{etype}' "
                      f"(name='{element.name}') – recorded offline only.")

            # Advance placement cursor
            self._y_cursor += self._y_step
        except Exception as exc:
            print(f"[logisim] embedded placement error for '{element.name}': {exc}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "elements": [element.to_dict() for element in self.elements],
        }

    def save_to(self, output_path: Any) -> None:
        """Serialise the circuit to a JSON blueprint file (offline mode)."""
        path = Path(output_path)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
