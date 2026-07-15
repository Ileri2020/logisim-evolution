import argparse
import json
from pathlib import Path
from typing import Any, Dict

from .api import (
    Absolute,
    Adder,
    AddressDecoder,
    Alu,
    AnalogInput,
    AnalogOutput,
    AndGate,
    ArithmeticUnit,
    BarrelShifter,
    BitAdder,
    BitExtender,
    BitFinder,
    BitSelector,
    BootRom,
    Buffer,
    Bus,
    BusController,
    Button,
    CacheController,
    Circuit,
    Clock,
    ClockController,
    ClockDivider,
    CmosAnd,
    CmosInverter,
    CmosNand,
    CmosNor,
    CmosOr,
    CmosTransistor,
    Comparator,
    ComparatorController,
    ComparatorUnit,
    Constant,
    Console,
    ControlledBuffer,
    ControlledInverter,
    Counter,
    CpuComponent,
    CpuCore,
    DFlipFlop,
    DLatch,
    DmaController,
    Debouncer,
    Decoder,
    Demultiplexer,
    DigitalOscilloscope,
    DipSwitch,
    Divider,
    DividerUnit,
    DoNotConnect,
    DotMatrixDisplay,
    DualPortRam,
    Dram,
    EdgeTriggeredFlipFlop,
    Eeprom,
    EnableGenerator,
    EnabledFlipFlop,
    EvenParityGate,
    Exponentiator,
    FileReader,
    FileWriter,
    FiniteStateMachine,
    FifoQueue,
    FloatingPointAbsoluteValue,
    FloatingPointAdder,
    FloatingPointComparator,
    FloatingPointConstant,
    FloatingPointConverter,
    FloatingPointDivider,
    FloatingPointDisplay,
    FloatingPointExponentExtractor,
    FloatingPointMantissaExtractor,
    FloatingPointMultiplier,
    FloatingPointNegator,
    FloatingPointParser,
    FloatingPointRounder,
    FloatingPointSquareRoot,
    FloatingPointSubtractor,
    FloatingPointToIntegerConverter,
    FloatingPointUnit,
    FrequencyCounter,
    InputOutputExtra,
    BfhMegaFunction,
    SystemOnChip,
    TclComponent,
    Gate,
    GpioController,
    Ground,
    HexDigitDisplay,
    HexKeyboard,
    I2cController,
    I2cInterface,
    IntegerToFloatingPointConverter,
    InterruptController,
    Joystick,
    JkFlipFlop,
    Keyboard,
    Latch,
    LcdDisplay,
    Led,
    LifoStack,
    LogicAnalyzer,
    Maximum,
    MemoryController,
    Microcontroller,
    Minimum,
    Mouse,
    Multiplier,
    MultiplierUnit,
    Multiplexer,
    NandGate,
    Negator,
    NmosTransistor,
    NorGate,
    NotGate,
    NumericKeyboard,
    OddParityGate,
    OpenCollectorOutput,
    OrGate,
    ParallelInput,
    ParallelOutput,
    PeripheralController,
    Pin,
    PipelineComponent,
    Pla,
    Por,
    Power,
    PriorityEncoder,
    Probe,
    Processor,
    PullDown,
    PullResistor,
    PullUp,
    PulseGenerator,
    PmosTransistor,
    Ram,
    Register,
    RegisterBank,
    RegisterFile,
    ResetGenerator,
    RgbLed,
    Rom,
    SRLatch,
    SrFlipFlop,
    SevenSegmentDisplay,
    SerialInput,
    SerialOutput,
    Shifter,
    ShiftRegister,
    SpiController,
    SpiInterface,
    Splitter,
    SquareRoot,
    Sram,
    StateMachine,
    Stopwatch,
    Subtractor,
    Synchronizer,
    SystemBus,
    TFlipFlop,
    TextDisplay,
    TtyTerminal,
    Timer,
    TransmissionGate,
    Transistor,
    TriStateBuffer,
    Tunnel,
    Ttl7400,
    Ttl7402,
    Ttl7404,
    Ttl7408,
    Ttl7432,
    Ttl7486,
    Ttl7474,
    Ttl7476,
    Ttl7490,
    Ttl7493,
    Ttl74161,
    Ttl74163,
    Ttl74173,
    Ttl74175,
    Ttl74194,
    Ttl74150,
    Ttl74151,
    Ttl74153,
    Ttl74157,
    Ttl74138,
    Ttl74139,
    Ttl7442,
    Ttl7483,
    Ttl74283,
    Ttl74181,
    Uart,
    UartController,
    Wire,
    XnorGate,
    XorGate,
)


class BlueprintBuilder:
    def __init__(self, name: str = "generated_circuit") -> None:
        self.circuit = Circuit(name)

    def add(self, element: Any) -> None:
        self.circuit.add(element)

    def add_gate(self, gate_type: str, name: str, **kwargs: Any) -> None:
        self.circuit.add(Gate(gate_type, name, **kwargs))

    def add_wire(self, name: str, source: str, target: str, **kwargs: Any) -> None:
        self.circuit.add(Wire(name, source, target, **kwargs))

    def add_counter(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Counter(name, **kwargs))

    def add_splitter(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Splitter(name, **kwargs))

    def add_pin(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Pin(name, **kwargs))

    def add_probe(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Probe(name, **kwargs))

    def add_tunnel(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Tunnel(name, **kwargs))

    def add_pull_resistor(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(PullResistor(name, **kwargs))

    def add_clock(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Clock(name, **kwargs))

    def add_por(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Por(name, **kwargs))

    def add_constant(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Constant(name, **kwargs))

    def add_power(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Power(name, **kwargs))

    def add_ground(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ground(name, **kwargs))

    def add_do_not_connect(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(DoNotConnect(name, **kwargs))

    def add_transistor(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Transistor(name, **kwargs))

    def add_transmission_gate(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(TransmissionGate(name, **kwargs))

    def add_bit_extender(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(BitExtender(name, **kwargs))

    def add_not_gate(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(NotGate(name, **kwargs))

    def add_buffer(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Buffer(name, **kwargs))

    def add_and_gate(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(AndGate(name, **kwargs))

    def add_or_gate(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(OrGate(name, **kwargs))

    def add_nand_gate(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(NandGate(name, **kwargs))

    def add_nor_gate(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(NorGate(name, **kwargs))

    def add_xor_gate(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(XorGate(name, **kwargs))

    def add_xnor_gate(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(XnorGate(name, **kwargs))

    def add_odd_parity_gate(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(OddParityGate(name, **kwargs))

    def add_even_parity_gate(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(EvenParityGate(name, **kwargs))

    def add_controlled_buffer(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(ControlledBuffer(name, **kwargs))

    def add_controlled_inverter(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(ControlledInverter(name, **kwargs))

    def add_pla(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Pla(name, **kwargs))

    def add_multiplexer(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Multiplexer(name, **kwargs))

    def add_demultiplexer(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Demultiplexer(name, **kwargs))

    def add_decoder(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Decoder(name, **kwargs))

    def add_priority_encoder(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(PriorityEncoder(name, **kwargs))

    def add_bit_selector(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(BitSelector(name, **kwargs))

    def add_adder(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Adder(name, **kwargs))

    def add_subtractor(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Subtractor(name, **kwargs))

    def add_multiplier(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Multiplier(name, **kwargs))

    def add_divider(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Divider(name, **kwargs))

    def add_negator(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Negator(name, **kwargs))

    def add_exponentiator(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Exponentiator(name, **kwargs))

    def add_square_root(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(SquareRoot(name, **kwargs))

    def add_absolute(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Absolute(name, **kwargs))

    def add_comparator(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Comparator(name, **kwargs))

    def add_maximum(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Maximum(name, **kwargs))

    def add_minimum(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Minimum(name, **kwargs))

    def add_shifter(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Shifter(name, **kwargs))

    def add_bit_adder(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(BitAdder(name, **kwargs))

    def add_bit_finder(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(BitFinder(name, **kwargs))

    def add_floating_point_constant(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointConstant(name, **kwargs))

    def add_floating_point_parser(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointParser(name, **kwargs))

    def add_floating_point_display(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointDisplay(name, **kwargs))

    def add_floating_point_adder(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointAdder(name, **kwargs))

    def add_floating_point_subtractor(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointSubtractor(name, **kwargs))

    def add_floating_point_multiplier(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointMultiplier(name, **kwargs))

    def add_floating_point_divider(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointDivider(name, **kwargs))

    def add_floating_point_comparator(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointComparator(name, **kwargs))

    def add_floating_point_negator(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointNegator(name, **kwargs))

    def add_floating_point_absolute_value(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointAbsoluteValue(name, **kwargs))

    def add_floating_point_square_root(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointSquareRoot(name, **kwargs))

    def add_floating_point_rounder(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointRounder(name, **kwargs))

    def add_floating_point_converter(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointConverter(name, **kwargs))

    def add_integer_to_floating_point_converter(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(IntegerToFloatingPointConverter(name, **kwargs))

    def add_floating_point_to_integer_converter(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointToIntegerConverter(name, **kwargs))

    def add_floating_point_exponent_extractor(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointExponentExtractor(name, **kwargs))

    def add_floating_point_mantissa_extractor(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointMantissaExtractor(name, **kwargs))

    def add_tcl(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(TclComponent(name, **kwargs))

    def add_bfh_mega_function(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(BfhMegaFunction(name, **kwargs))

    def add_input_output_extra(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(InputOutputExtra(name, **kwargs))

    def add_system_on_chip(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(SystemOnChip(name, **kwargs))

    def add_ram(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ram(name, **kwargs))

    def add_rom(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Rom(name, **kwargs))

    def add_register(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Register(name, **kwargs))

    def add_register_file(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(RegisterFile(name, **kwargs))

    def add_shift_register(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(ShiftRegister(name, **kwargs))

    def add_eeprom(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Eeprom(name, **kwargs))

    def add_sram(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Sram(name, **kwargs))

    def add_dram(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Dram(name, **kwargs))

    def add_fifo_queue(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FifoQueue(name, **kwargs))

    def add_lifo_stack(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(LifoStack(name, **kwargs))

    def add_dual_port_ram(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(DualPortRam(name, **kwargs))

    def add_button(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Button(name, **kwargs))

    def add_led(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Led(name, **kwargs))

    def add_rgb_led(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(RgbLed(name, **kwargs))

    def add_seven_segment_display(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(SevenSegmentDisplay(name, **kwargs))

    def add_hex_digit_display(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(HexDigitDisplay(name, **kwargs))

    def add_dot_matrix_display(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(DotMatrixDisplay(name, **kwargs))

    def add_lcd_display(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(LcdDisplay(name, **kwargs))

    def add_dip_switch(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(DipSwitch(name, **kwargs))

    def add_joystick(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Joystick(name, **kwargs))

    def add_keyboard(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Keyboard(name, **kwargs))

    def add_mouse(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Mouse(name, **kwargs))

    def add_uart(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Uart(name, **kwargs))

    def add_serial_input(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(SerialInput(name, **kwargs))

    def add_serial_output(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(SerialOutput(name, **kwargs))

    def add_parallel_input(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(ParallelInput(name, **kwargs))

    def add_parallel_output(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(ParallelOutput(name, **kwargs))

    def add_spi_interface(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(SpiInterface(name, **kwargs))

    def add_i2c_interface(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(I2cInterface(name, **kwargs))

    def add_tty_terminal(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(TtyTerminal(name, **kwargs))

    def add_text_display(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(TextDisplay(name, **kwargs))

    def add_console(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Console(name, **kwargs))

    def add_file_reader(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FileReader(name, **kwargs))

    def add_file_writer(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FileWriter(name, **kwargs))

    def add_hex_keyboard(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(HexKeyboard(name, **kwargs))

    def add_numeric_keyboard(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(NumericKeyboard(name, **kwargs))

    def add_stopwatch(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Stopwatch(name, **kwargs))

    def add_digital_oscilloscope(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(DigitalOscilloscope(name, **kwargs))

    def add_logic_analyzer(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(LogicAnalyzer(name, **kwargs))

    def add_frequency_counter(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FrequencyCounter(name, **kwargs))

    def add_pulse_generator(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(PulseGenerator(name, **kwargs))

    def add_analog_input(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(AnalogInput(name, **kwargs))

    def add_analog_output(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(AnalogOutput(name, **kwargs))

    def add_ttl_7400(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl7400(name, **kwargs))

    def add_ttl_7402(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl7402(name, **kwargs))

    def add_ttl_7404(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl7404(name, **kwargs))

    def add_ttl_7408(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl7408(name, **kwargs))

    def add_ttl_7432(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl7432(name, **kwargs))

    def add_ttl_7486(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl7486(name, **kwargs))

    def add_ttl_7474(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl7474(name, **kwargs))

    def add_ttl_7476(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl7476(name, **kwargs))

    def add_ttl_7490(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl7490(name, **kwargs))

    def add_ttl_7493(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl7493(name, **kwargs))

    def add_ttl_74161(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl74161(name, **kwargs))

    def add_ttl_74163(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl74163(name, **kwargs))

    def add_ttl_74173(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl74173(name, **kwargs))

    def add_ttl_74175(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl74175(name, **kwargs))

    def add_ttl_74194(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl74194(name, **kwargs))

    def add_ttl_74150(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl74150(name, **kwargs))

    def add_ttl_74151(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl74151(name, **kwargs))

    def add_ttl_74153(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl74153(name, **kwargs))

    def add_ttl_74157(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl74157(name, **kwargs))

    def add_ttl_74138(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl74138(name, **kwargs))

    def add_ttl_74139(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl74139(name, **kwargs))

    def add_ttl_7442(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl7442(name, **kwargs))

    def add_ttl_7483(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl7483(name, **kwargs))

    def add_ttl_74283(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl74283(name, **kwargs))

    def add_ttl_74181(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Ttl74181(name, **kwargs))

    def add_nmos_transistor(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(NmosTransistor(name, **kwargs))

    def add_pmos_transistor(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(PmosTransistor(name, **kwargs))

    def add_cmos_transistor(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(CmosTransistor(name, **kwargs))

    def add_cmos_inverter(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(CmosInverter(name, **kwargs))

    def add_cmos_nand(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(CmosNand(name, **kwargs))

    def add_cmos_nor(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(CmosNor(name, **kwargs))

    def add_cmos_and(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(CmosAnd(name, **kwargs))

    def add_cmos_or(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(CmosOr(name, **kwargs))

    def add_pull_up(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(PullUp(name, **kwargs))

    def add_pull_down(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(PullDown(name, **kwargs))

    def add_tri_state_buffer(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(TriStateBuffer(name, **kwargs))

    def add_open_collector_output(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(OpenCollectorOutput(name, **kwargs))

    def add_arithmetic_unit(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(ArithmeticUnit(name, **kwargs))

    def add_alu(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Alu(name, **kwargs))

    def add_barrel_shifter(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(BarrelShifter(name, **kwargs))

    def add_comparator_unit(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(ComparatorUnit(name, **kwargs))

    def add_divider_unit(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(DividerUnit(name, **kwargs))

    def add_multiplier_unit(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(MultiplierUnit(name, **kwargs))

    def add_floating_point_unit(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FloatingPointUnit(name, **kwargs))

    def add_register_bank(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(RegisterBank(name, **kwargs))

    def add_memory_controller(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(MemoryController(name, **kwargs))

    def add_bus_controller(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(BusController(name, **kwargs))

    def add_interrupt_controller(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(InterruptController(name, **kwargs))

    def add_cpu_component(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(CpuComponent(name, **kwargs))

    def add_pipeline_component(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(PipelineComponent(name, **kwargs))

    def add_cpu_core(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(CpuCore(name, **kwargs))

    def add_microcontroller(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Microcontroller(name, **kwargs))

    def add_processor(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Processor(name, **kwargs))

    def add_bus(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Bus(name, **kwargs))

    def add_system_bus(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(SystemBus(name, **kwargs))

    def add_address_decoder(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(AddressDecoder(name, **kwargs))

    def add_dma_controller(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(DmaController(name, **kwargs))

    def add_timer(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Timer(name, **kwargs))

    def add_clock_controller(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(ClockController(name, **kwargs))

    def add_uart_controller(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(UartController(name, **kwargs))

    def add_gpio_controller(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(GpioController(name, **kwargs))

    def add_spi_controller(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(SpiController(name, **kwargs))

    def add_i2c_controller(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(I2cController(name, **kwargs))

    def add_cache_controller(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(CacheController(name, **kwargs))

    def add_boot_rom(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(BootRom(name, **kwargs))

    def add_peripheral_controller(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(PeripheralController(name, **kwargs))

    def add_d_flip_flop(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(DFlipFlop(name, **kwargs))

    def add_t_flip_flop(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(TFlipFlop(name, **kwargs))

    def add_jk_flip_flop(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(JkFlipFlop(name, **kwargs))

    def add_sr_flip_flop(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(SrFlipFlop(name, **kwargs))

    def add_enabled_flip_flop(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(EnabledFlipFlop(name, **kwargs))

    def add_edge_triggered_flip_flop(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(EdgeTriggeredFlipFlop(name, **kwargs))

    def add_latch(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Latch(name, **kwargs))

    def add_d_latch(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(DLatch(name, **kwargs))

    def add_sr_latch(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(SRLatch(name, **kwargs))

    def add_clock_divider(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(ClockDivider(name, **kwargs))

    def add_state_machine(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(StateMachine(name, **kwargs))

    def add_finite_state_machine(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(FiniteStateMachine(name, **kwargs))

    def add_comparator_controller(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(ComparatorController(name, **kwargs))

    def add_enable_generator(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(EnableGenerator(name, **kwargs))

    def add_reset_generator(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(ResetGenerator(name, **kwargs))

    def add_synchronizer(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Synchronizer(name, **kwargs))

    def add_debouncer(self, name: str, **kwargs: Any) -> None:
        self.circuit.add(Debouncer(name, **kwargs))

    def build(self) -> Dict[str, Any]:
        return self.circuit.to_dict()

    def save(self, output_path: Any) -> Path:
        path = Path(output_path)
        path.write_text(json.dumps(self.build(), indent=2), encoding="utf-8")
        return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Logisim blueprint from Python")
    parser.add_argument("--name", default="generated_circuit")
    parser.add_argument("--output", default="generated_blueprint.json")
    args = parser.parse_args()

    builder = BlueprintBuilder(args.name)
    builder.add_gate("and", "and0")
    builder.add_counter("cnt0")
    builder.add_wire("w0", "and0.out", "cnt0.in")
    output = builder.save(args.output)
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
