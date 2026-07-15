/*
 * Logisim-evolution - digital logic design tool and simulator
 * Copyright by the Logisim-evolution developers
 *
 * https://github.com/logisim-evolution/
 *
 * This is free software released under GNU GPLv3 license
 */

package com.cburch.logisim.scripting;

import com.cburch.logisim.circuit.Circuit;
import com.cburch.logisim.circuit.CircuitMutation;
import com.cburch.logisim.circuit.SplitterFactory;
import com.cburch.logisim.circuit.Wire;
import com.cburch.logisim.comp.Component;
import com.cburch.logisim.comp.ComponentFactory;
import com.cburch.logisim.data.AttributeOption;
import com.cburch.logisim.data.Location;
import com.cburch.logisim.instance.InstanceFactory;
import com.cburch.logisim.instance.StdAttr;
import com.cburch.logisim.proj.Project;
import com.cburch.logisim.soc.Soc;
import com.cburch.logisim.std.arith.ArithmeticLibrary;
import com.cburch.logisim.std.arith.floating.FPArithmeticLibrary;
import com.cburch.logisim.std.bfh.BfhLibrary;
import com.cburch.logisim.std.gates.GatesLibrary;
import com.cburch.logisim.std.io.IoLibrary;
import com.cburch.logisim.std.io.extra.ExtraIoLibrary;
import com.cburch.logisim.std.memory.MemoryLibrary;
import com.cburch.logisim.std.plexers.PlexersLibrary;
import com.cburch.logisim.std.tcl.TclLibrary;
import com.cburch.logisim.std.ttl.TtlLibrary;
import com.cburch.logisim.std.wiring.Clock;
import com.cburch.logisim.std.wiring.Constant;
import com.cburch.logisim.std.wiring.DoNotConnect;
import com.cburch.logisim.std.wiring.Ground;
import com.cburch.logisim.std.wiring.Pin;
import com.cburch.logisim.std.wiring.Power;
import com.cburch.logisim.std.wiring.PowerOnReset;
import com.cburch.logisim.std.wiring.Probe;
import com.cburch.logisim.std.wiring.PullResistor;
import com.cburch.logisim.std.wiring.Tunnel;
import com.cburch.logisim.std.wiring.WiringLibrary;
import com.cburch.logisim.tools.AddTool;
import com.cburch.logisim.tools.Library;
import com.cburch.logisim.util.StringGetter;
import com.cburch.logisim.data.Attribute;
import com.cburch.logisim.tools.SetAttributeAction;
import java.util.HashMap;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * LogisimPythonBindings is the Java-side bridge injected as the {@code logisim} global into every
 * embedded Python script.
 *
 * <p>This mirrors Blender's {@code bpy} module. Scripts access live Logisim objects via:
 * <pre>
 *   logisim.context.circuit_name()   # read the active circuit
 *   logisim.ops.add_gate("and", 100, 200, "g0")   # place a gate on canvas
 *   logisim.ops.add_wiring("splitter", 40, 60)     # place a wiring element
 *   logisim.ops.add_plexer("mux", 200, 100)        # place a plexer
 *   logisim.ops.add_arith("adder", 300, 100)       # place an arithmetic unit
 * </pre>
 *
 * <p><b>Coverage:</b>
 * <ul>
 *   <li>Wiring: splitter, pin, probe, tunnel, pull_resistor, clock, por, constant,
 *       power, ground, do_not_connect (+ transistor/transmission_gate/bit_extender via library)</li>
 *   <li>Gates: all 13 gates from GatesLibrary (and, or, not, nand, nor, xor, xnor,
 *       odd_parity, even_parity, buffer, controlled_buffer, controlled_inverter, pla)</li>
 *   <li>Plexers: multiplexer, demultiplexer, decoder, priority_encoder, bit_selector</li>
 *   <li>Arithmetic: adder, subtractor, multiplier, divider, negator, exponentiator,
 *       square_root, absolute, comparator, minmax, shifter, bit_adder, bit_finder</li>
 * </ul>
 *
 * <p><b>Not yet covered (missing Java factories / separate libs):</b>
 * Floating-point arithmetic, Memory, I/O, TTL, TCL, BFH mega-functions, SoC.
 */
public class LogisimPythonBindings {

  private static final Logger logger = LoggerFactory.getLogger(LogisimPythonBindings.class);

  // ── Factory maps built once from the library APIs ──────────────────────────

  /** Gate factories keyed by lower-case short name (e.g. "and", "not"). */
  private static final Map<String, ComponentFactory> GATE_MAP = new HashMap<>();

  /** Wiring factories keyed by short name (e.g. "splitter", "clock"). */
  private static final Map<String, ComponentFactory> WIRING_MAP = new HashMap<>();

  /** Plexer factories keyed by short name (e.g. "mux", "decoder"). */
  private static final Map<String, ComponentFactory> PLEXER_MAP = new HashMap<>();

  /** Arithmetic factories keyed by short name (e.g. "adder", "shifter"). */
  private static final Map<String, ComponentFactory> ARITH_MAP = new HashMap<>();

  private static final Map<String, ComponentFactory> FP_ARITH_MAP = new HashMap<>();
  private static final Map<String, ComponentFactory> MEMORY_MAP = new HashMap<>();
  private static final Map<String, ComponentFactory> IO_MAP = new HashMap<>();
  private static final Map<String, ComponentFactory> TTL_MAP = new HashMap<>();
  private static final Map<String, ComponentFactory> TCL_MAP = new HashMap<>();
  private static final Map<String, ComponentFactory> BFH_MAP = new HashMap<>();
  private static final Map<String, ComponentFactory> EXTRA_IO_MAP = new HashMap<>();
  private static final Map<String, ComponentFactory> SOC_MAP = new HashMap<>();

  static {
    buildGateMap();
    buildWiringMap();
    buildPlexerMap();
    buildArithMap();
    buildFpArithMap();
    buildMemoryMap();
    buildIoMap();
    buildTtlMap();
    buildTclMap();
    buildBfhMap();
    buildExtraIoMap();
    buildSocMap();
  }

  // ── Gate map ───────────────────────────────────────────────────────────────
  private static void buildGateMap() {
    for (final var tool : new GatesLibrary().getTools()) {
      if (tool instanceof AddTool addTool
          && addTool.getFactory() instanceof ComponentFactory f) {
        // Factory names: "AND Gate", "OR Gate", "NOT Gate", "Buffer", "PLA", ...
        final var raw = f.getName().toLowerCase()
            .replace(" gate", "")
            .replace("controlled ", "controlled_")
            .replace("odd parity", "odd_parity")
            .replace("even parity", "even_parity")
            .trim();
        GATE_MAP.put(raw, f);
        logger.trace("GateMap: '{}' -> {}", raw, f.getName());
      }
    }
  }

  // ── Wiring map ─────────────────────────────────────────────────────────────
  private static void buildWiringMap() {
    // Splitter lives in circuit package, not wiring; add manually.
    WIRING_MAP.put("splitter", SplitterFactory.instance);

    // All WiringLibrary tools (PIN, PROBE, TUNNEL, PULL_RESISTOR, CLOCK, POR, CONSTANT,
    //   POWER, GROUND, DO_NOT_CONNECT, TRANSISTOR, TRANSMISSION_GATE, BIT_EXTENDER)
    for (final var tool : new WiringLibrary().getTools()) {
      if (tool instanceof AddTool addTool
          && addTool.getFactory() instanceof ComponentFactory f) {
        final var key = f.getName().toLowerCase()
            .replace(" ", "_")
            .replace("power-on_reset", "por")
            .replace("power_on_reset", "por")
            .trim();
        WIRING_MAP.put(key, f);
        logger.trace("WiringMap: '{}' -> {}", key, f.getName());
      }
    }

    // Convenience aliases
    alias(WIRING_MAP, "pin", "pin");
    alias(WIRING_MAP, "probe", "probe");
    alias(WIRING_MAP, "tunnel", "tunnel");
    alias(WIRING_MAP, "clock", "clock");
    alias(WIRING_MAP, "constant", "constant");
    alias(WIRING_MAP, "ground", "ground");
    alias(WIRING_MAP, "power", "power");
    alias(WIRING_MAP, "do_not_connect", "do_not_connect");
    alias(WIRING_MAP, "pull_resistor", "pull_resistor");
    alias(WIRING_MAP, "bit_extender", "bit_extender");
    alias(WIRING_MAP, "transistor", "transistor");
    alias(WIRING_MAP, "transmission_gate", "transmission_gate");
  }

  // ── Plexer map ─────────────────────────────────────────────────────────────
  private static void buildPlexerMap() {
    for (final var tool : new PlexersLibrary().getTools()) {
      if (tool instanceof AddTool addTool
          && addTool.getFactory() instanceof ComponentFactory f) {
        final var key = f.getName().toLowerCase()
            .replace(" ", "_")
            .trim();
        PLEXER_MAP.put(key, f);
        logger.trace("PlexerMap: '{}' -> {}", key, f.getName());
      }
    }
    // Aliases for convenience
    alias(PLEXER_MAP, "mux",  "multiplexer");
    alias(PLEXER_MAP, "demux", "demultiplexer");
    alias(PLEXER_MAP, "priority_encoder", "priority_encoder");
    alias(PLEXER_MAP, "bit_selector", "bit_selector");
  }

  // ── Arithmetic map ─────────────────────────────────────────────────────────
  private static void buildArithMap() {
    for (final var tool : new ArithmeticLibrary().getTools()) {
      if (tool instanceof AddTool addTool
          && addTool.getFactory() instanceof ComponentFactory f) {
        final var key = f.getName().toLowerCase()
            .replace(" ", "_")
            .trim();
        ARITH_MAP.put(key, f);
        logger.trace("ArithMap: '{}' -> {}", key, f.getName());
      }
    }
    // Aliases
    alias(ARITH_MAP, "abs",    "absolute");
    alias(ARITH_MAP, "cmp",    "comparator");
    alias(ARITH_MAP, "sqrt",   "square_root");
    alias(ARITH_MAP, "exp",    "exponentiator");
    alias(ARITH_MAP, "neg",    "negator");
    alias(ARITH_MAP, "mul",    "multiplier");
    alias(ARITH_MAP, "div",    "divider");
    alias(ARITH_MAP, "sub",    "subtractor");
    alias(ARITH_MAP, "add",    "adder");
    alias(ARITH_MAP, "shift",  "shifter");
    alias(ARITH_MAP, "minmax", "min/max");
    alias(ARITH_MAP, "min_max", "min/max");
    alias(ARITH_MAP, "maximum", "min/max");
    alias(ARITH_MAP, "minimum", "min/max");
    alias(ARITH_MAP, "bit_add", "bit_adder");
    alias(ARITH_MAP, "bit_find", "bit_finder");
  }

  private static void buildFpArithMap() {
    for (final var tool : new FPArithmeticLibrary().getTools()) {
      if (tool instanceof AddTool addTool && addTool.getFactory() instanceof ComponentFactory f) {
        final var key = f.getName().toLowerCase().replace(" ", "_").replace("/", "_").trim();
        FP_ARITH_MAP.put(key, f);
      }
    }

    // Canonical keys used by the Java library (for example: fp_adder, fp_subtractor, ...).
    alias(FP_ARITH_MAP, "fp_abs", "fp_absolute");
    alias(FP_ARITH_MAP, "fp_cmp", "fp_comparator");
    alias(FP_ARITH_MAP, "fp_sqrt", "fp_square_root");
    alias(FP_ARITH_MAP, "fp_exp", "fp_exponentiator");
    alias(FP_ARITH_MAP, "fp_neg", "fp_negator");
    alias(FP_ARITH_MAP, "fp_mul", "fp_multiplier");
    alias(FP_ARITH_MAP, "fp_div", "fp_divider");
    alias(FP_ARITH_MAP, "fp_sub", "fp_subtractor");
    alias(FP_ARITH_MAP, "fp_add", "fp_adder");
    alias(FP_ARITH_MAP, "fp_minmax", "fp_min_max");
    alias(FP_ARITH_MAP, "fp_maximum", "fp_min_max");
    alias(FP_ARITH_MAP, "fp_minimum", "fp_min_max");
    alias(FP_ARITH_MAP, "fp_absolute", "fp_absolute");
    alias(FP_ARITH_MAP, "fp_comparator", "fp_comparator");
    alias(FP_ARITH_MAP, "fp_square_root", "fp_square_root");
    alias(FP_ARITH_MAP, "fp_exponentiator", "fp_exponentiator");
    alias(FP_ARITH_MAP, "fp_negator", "fp_negator");
    alias(FP_ARITH_MAP, "fp_multiplier", "fp_multiplier");
    alias(FP_ARITH_MAP, "fp_divider", "fp_divider");
    alias(FP_ARITH_MAP, "fp_subtractor", "fp_subtractor");
    alias(FP_ARITH_MAP, "fp_adder", "fp_adder");
    alias(FP_ARITH_MAP, "floating_point_adder", "fp_adder");
    alias(FP_ARITH_MAP, "floating_point_subtractor", "fp_subtractor");
    alias(FP_ARITH_MAP, "floating_point_multiplier", "fp_multiplier");
    alias(FP_ARITH_MAP, "floating_point_divider", "fp_divider");
    alias(FP_ARITH_MAP, "floating_point_comparator", "fp_comparator");
    alias(FP_ARITH_MAP, "floating_point_negator", "fp_negator");
    alias(FP_ARITH_MAP, "floating_point_absolute_value", "fp_absolute");
    alias(FP_ARITH_MAP, "floating_point_square_root", "fp_square_root");
    alias(FP_ARITH_MAP, "floating_point_rounder", "fp_round");
    alias(FP_ARITH_MAP, "floating_point_converter", "fp_to_fp");
    alias(FP_ARITH_MAP, "integer_to_floating_point_converter", "int_to_fp");
    alias(FP_ARITH_MAP, "floating_point_to_integer_converter", "fp_to_int");
    alias(FP_ARITH_MAP, "floating_point_exponent_extractor", "fp_exponentiator");
    alias(FP_ARITH_MAP, "floating_point_mantissa_extractor", "fp_classificator");

    // Shorthand names used by the Python examples/tests.
    alias(FP_ARITH_MAP, "fpadder", "fp_adder");
    alias(FP_ARITH_MAP, "fpsubtractor", "fp_subtractor");
    alias(FP_ARITH_MAP, "fpmultiplier", "fp_multiplier");
    alias(FP_ARITH_MAP, "fpdivider", "fp_divider");
    alias(FP_ARITH_MAP, "fpcomparator", "fp_comparator");
    alias(FP_ARITH_MAP, "fpnegator", "fp_negator");
    alias(FP_ARITH_MAP, "fpabsolute", "fp_absolute");
    alias(FP_ARITH_MAP, "fpsquareroot", "fp_square_root");
    alias(FP_ARITH_MAP, "fpround", "fp_round");
    alias(FP_ARITH_MAP, "fptofp", "fp_to_fp");
    alias(FP_ARITH_MAP, "inttofp", "int_to_fp");
    alias(FP_ARITH_MAP, "fptoint", "fp_to_int");
    alias(FP_ARITH_MAP, "fpexponentiator", "fp_exponentiator");
    alias(FP_ARITH_MAP, "fpclassificator", "fp_classificator");
  }

  private static void buildMemoryMap() {
    for (final var tool : new MemoryLibrary().getTools()) {
      if (tool instanceof AddTool addTool && addTool.getFactory() instanceof ComponentFactory f) {
        final var key = f.getName().toLowerCase().replace(" ", "_").replace("-", "_").trim();
        MEMORY_MAP.put(key, f);
      }
    }
    alias(MEMORY_MAP, "jk_flip_flop", "j_k_flip_flop");
    alias(MEMORY_MAP, "sr_flip_flop", "s_r_flip_flop");
    alias(MEMORY_MAP, "dual_ram", "dual_port_ram");
  }

  private static void buildIoMap() {
    for (final var tool : new IoLibrary().getTools()) {
      if (tool instanceof AddTool addTool && addTool.getFactory() instanceof ComponentFactory f) {
        final var key = f.getName().toLowerCase().replace(" ", "_").replace("-", "_").replace("/", "_").trim();
        IO_MAP.put(key, f);
      }
    }
    alias(IO_MAP, "led_bar", "led_light_bar");
    alias(IO_MAP, "seven_segment", "7_segment_display");
    alias(IO_MAP, "hex_digit", "hex_digit_display");
    alias(IO_MAP, "port_io", "i_o_port");
    alias(IO_MAP, "pio", "i_o_port");
    alias(IO_MAP, "real_time_clock", "real_time_clock");
    alias(IO_MAP, "video", "vga_component");
    alias(IO_MAP, "vga", "vga_component");
  }

  private static void buildTtlMap() {
    for (final var tool : new TtlLibrary().getTools()) {
      if (tool instanceof AddTool addTool && addTool.getFactory() instanceof ComponentFactory f) {
        final var key = f.getName().toLowerCase().trim();
        TTL_MAP.put(key, f);
        TTL_MAP.put("ttl_" + key, f);
        TTL_MAP.put("ttl" + key, f);
      }
    }
  }

  private static void buildTclMap() {
    for (final var tool : new TclLibrary().getTools()) {
      if (tool instanceof AddTool addTool && addTool.getFactory() instanceof ComponentFactory f) {
        final var key = f.getName().toLowerCase().replace(" ", "_").trim();
        TCL_MAP.put(key, f);
      }
    }
    alias(TCL_MAP, "tcl_generic", "tclgeneric");
    alias(TCL_MAP, "tcl_generic_component", "tclgeneric");
    alias(TCL_MAP, "tclconsole", "tclconsolereds");
    alias(TCL_MAP, "tcl_console", "tclconsolereds");
  }

  private static void buildBfhMap() {
    for (final var tool : new BfhLibrary().getTools()) {
      if (tool instanceof AddTool addTool && addTool.getFactory() instanceof ComponentFactory f) {
        final var key = f.getName().toLowerCase().replace(" ", "_").trim();
        BFH_MAP.put(key, f);
      }
    }
    alias(BFH_MAP, "bin_to_bcd", "binary_to_bcd_converter");
    alias(BFH_MAP, "bcd_to_seven_segment", "bcd_to_7_segment_decoder");
    alias(BFH_MAP, "binary_to_bcd_converter", "binary_to_bcd_converter");
    alias(BFH_MAP, "bcd_to_7_segment_decoder", "bcd_to_7_segment_decoder");
    alias(BFH_MAP, "bin2bcd", "binary_to_bcd_converter");
    alias(BFH_MAP, "bcd2sevensegment", "bcd_to_7_segment_decoder");
  }

  private static void buildExtraIoMap() {
    for (final var tool : new ExtraIoLibrary().getTools()) {
      if (tool instanceof AddTool addTool && addTool.getFactory() instanceof ComponentFactory f) {
        final var key = f.getName().toLowerCase().replace(" ", "_").trim();
        EXTRA_IO_MAP.put(key, f);
      }
    }
  }

  private static void buildSocMap() {
    for (final var tool : new Soc().getTools()) {
      if (tool instanceof AddTool addTool && addTool.getFactory() instanceof ComponentFactory f) {
        final var key = f.getName().toLowerCase().replace(" ", "_").trim();
        SOC_MAP.put(key, f);
      }
    }
    alias(SOC_MAP, "rv32im_riscv", "rv32im");
  }

  /** Inserts {@code alias → map[canonical]} if the canonical key exists. */
  private static void alias(Map<String, ComponentFactory> map, String alias, String canonical) {
    final var f = map.get(canonical);
    if (f != null) map.putIfAbsent(alias, f);
  }

  // ── Instance fields ────────────────────────────────────────────────────────

  private final PythonScriptManager manager;

  /** {@code logisim.context} – read-only live application state. */
  public final ContextProxy context;

  /** {@code logisim.ops} – undoable circuit mutations. */
  public final OpsProxy ops;

  LogisimPythonBindings(PythonScriptManager manager) {
    this.manager = manager;
    this.context = new ContextProxy();
    this.ops = new OpsProxy();
  }

  void updateProject(Project project) {
    context.project = project;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // logisim.context
  // ═══════════════════════════════════════════════════════════════════════════

  /** Read-only live context – mirrors Blender's {@code bpy.context}. */
  public class ContextProxy {
    private Project project;
    private ContextProxy() {}

    public String project_name() {
      return project == null ? "(none)" : project.getLogisimFile().getName();
    }

    public String circuit_name() {
      if (project == null) return "(none)";
      final var c = project.getCurrentCircuit();
      return c == null ? "(none)" : c.getName();
    }

    public int component_count() {
      if (project == null) return 0;
      final var c = project.getCurrentCircuit();
      return c == null ? 0 : c.getNonWires().size();
    }

    public String[] all_circuit_names() {
      if (project == null) return new String[0];
      return project.getLogisimFile().getCircuits().stream()
          .map(Circuit::getName)
          .toArray(String[]::new);
    }

    public boolean has_project() { return project != null; }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // logisim.ops
  // ═══════════════════════════════════════════════════════════════════════════

  /** Circuit-mutation operations – mirrors Blender's {@code bpy.ops}. */
  public class OpsProxy {
    private OpsProxy() {}

    // ── Wiring ──────────────────────────────────────────────────────────────

    /**
     * Place a wiring element on the active circuit canvas.
     *
     * <p>Supported {@code elementType} values (case-insensitive):
     * {@code splitter, pin, probe, tunnel, pull_resistor, clock, por, constant,
     * power, ground, do_not_connect, transistor, transmission_gate, bit_extender}.
     *
     * <p>For {@code pin} use {@link #add_pin(int, int, boolean, String)} instead to
     * also set the direction; this convenience overload creates an input pin.
     *
     * @return {@code true} on success
     */
    public boolean add_wiring(String elementType, int x, int y) {
      return placeFrom(WIRING_MAP, elementType, x, y, "wiring");
    }

    /**
     * Add an input or output Pin component.
     *
     * @param isInput {@code true} → input pin, {@code false} → output pin
     */
    public boolean add_pin(int x, int y, boolean isInput, String label) {
      final var proj = context.project;
      if (!checkProject(proj, "add_pin")) return false;
      final var circuit = proj.getCurrentCircuit();
      if (!checkCircuit(circuit, "add_pin")) return false;

      final var factory = Pin.FACTORY;
      final var loc = Location.create(x, y, false);
      final var attrs = factory.createAttributeSet();
      attrs.setValue(Pin.ATTR_TYPE, isInput ? Pin.INPUT : Pin.OUTPUT);
      final var comp = factory.createComponent(loc, attrs);

      doMutation(circuit, proj, comp, "Script: add " + (isInput ? "input" : "output") + " pin");
      logger.info("add_pin: {} pin at ({},{}) circuit='{}'",
          isInput ? "input" : "output", x, y, circuit.getName());
      return true;
    }

    // ── Gates ────────────────────────────────────────────────────────────────

    /**
     * Place a logic gate on the active circuit canvas.
     *
     * <p>Supported {@code gateType} values:
     * {@code and, or, not, nand, nor, xor, xnor, buffer,
     * odd_parity, even_parity, controlled_buffer, controlled_inverter, pla}.
     *
     * @return {@code true} on success
     */
    public boolean add_gate(String gateType, int x, int y, String label) {
      return placeFrom(GATE_MAP, gateType, x, y, "gate");
    }

    /** Place a component at an explicit coordinate and optionally assign a name. */
    public boolean place_component(String componentType, int x, int y, String label) {
      final var key = componentType == null ? "" : componentType.toLowerCase().trim();
      if (key.startsWith("gate:")) {
        return add_gate(key.substring(5), x, y, label);
      }
      if (key.startsWith("wiring:")) {
        return add_wiring(key.substring(7), x, y);
      }
      if (key.startsWith("plexer:")) {
        return add_plexer(key.substring(7), x, y);
      }
      if (key.startsWith("arith:")) {
        return add_arith(key.substring(6), x, y);
      }
      if (key.startsWith("fp:")) {
        return add_fp_arith(key.substring(3), x, y);
      }
      if (key.startsWith("memory:")) {
        return add_memory(key.substring(7), x, y);
      }
      if (key.startsWith("io:")) {
        return add_io(key.substring(3), x, y);
      }
      if (key.startsWith("ttl:")) {
        return add_ttl(key.substring(4), x, y);
      }
      if (key.startsWith("tcl:")) {
        return add_tcl(key.substring(4), x, y);
      }
      if (key.startsWith("bfh:")) {
        return add_bfh(key.substring(4), x, y);
      }
      if (key.startsWith("extra_io:")) {
        return add_extra_io(key.substring(9), x, y);
      }
      if (key.startsWith("soc:")) {
        return add_soc(key.substring(4), x, y);
      }
      return false;
    }

    /** Create a simple wire between two coordinate points. */
    public boolean add_wire(int x1, int y1, int x2, int y2) {
      final var proj = context.project;
      if (!checkProject(proj, "add_wire")) return false;
      final var circuit = proj.getCurrentCircuit();
      if (!checkCircuit(circuit, "add_wire")) return false;

      final var loc0 = Location.create(x1, y1, false);
      final var loc1 = Location.create(x2, y2, false);
      final var wire = Wire.create(loc0, loc1);
      final var mut = new CircuitMutation(circuit);
      mut.add(wire);
      final var action = mut.toAction(new StringGetter() {
        @Override public String toString() { return "Script: add wire"; }
      });
      proj.doAction(action);
      logger.info("Placed wire from ({},{}) to ({},{})", x1, y1, x2, y2);
      return true;
    }

    /** Connect a source component's named port to a target component's named port. */
    public boolean connect_ports(String sourceName, String sourcePort, String targetName, String targetPort) {
      final var proj = context.project;
      if (!checkProject(proj, "connect_ports")) return false;
      final var circuit = proj.getCurrentCircuit();
      if (!checkCircuit(circuit, "connect_ports")) return false;

      final var sourceComp = findComponentByLabel(circuit, sourceName);
      final var targetComp = findComponentByLabel(circuit, targetName);
      if (sourceComp == null || targetComp == null) {
        logger.warn("connect_ports failed: unknown component name (source='{}', target='{}')", sourceName, targetName);
        return false;
      }

      final var sourceEnd = findPort(sourceComp, sourcePort);
      final var targetEnd = findPort(targetComp, targetPort);
      if (sourceEnd == null || targetEnd == null) {
        logger.warn("connect_ports failed: unknown port (source='{}:{}', target='{}:{}')", sourceName, sourcePort, targetName, targetPort);
        return false;
      }

      final var wire = Wire.create(sourceEnd.getLocation(), targetEnd.getLocation());
      final var mut = new CircuitMutation(circuit);
      mut.add(wire);
      final var action = mut.toAction(new StringGetter() {
        @Override public String toString() { return "Script: connect ports"; }
      });
      proj.doAction(action);
      logger.info("Connected {}:{} to {}:{}", sourceName, sourcePort, targetName, targetPort);
      return true;
    }

    // ── Plexers ──────────────────────────────────────────────────────────────

    /**
     * Place a plexer element on the active circuit canvas.
     *
     * <p>Supported {@code plexerType} values:
     * {@code multiplexer (mux), demultiplexer (demux), decoder,
     * priority_encoder, bit_selector}.
     *
     * @return {@code true} on success
     */
    public boolean add_plexer(String plexerType, int x, int y) {
      return placeFrom(PLEXER_MAP, plexerType, x, y, "plexer");
    }

    // ── Arithmetic ───────────────────────────────────────────────────────────

    /**
     * Place an arithmetic component on the active circuit canvas.
     *
     * <p>Supported {@code arithType} values:
     * {@code adder (add), subtractor (sub), multiplier (mul), divider (div),
     * negator (neg), exponentiator (exp), square_root (sqrt), absolute (abs),
     * comparator (cmp), minmax/min_max, shifter (shift), bit_adder (bit_add),
     * bit_finder (bit_find)}.
     *
     * @return {@code true} on success
     */
    public boolean add_arith(String arithType, int x, int y) {
      return placeFrom(ARITH_MAP, arithType, x, y, "arithmetic");
    }

    public boolean add_fp_arith(String fpArithType, int x, int y) {
      return placeFrom(FP_ARITH_MAP, fpArithType, x, y, "floating-point arithmetic");
    }

    public boolean add_memory(String memoryType, int x, int y) {
      return placeFrom(MEMORY_MAP, memoryType, x, y, "memory");
    }

    public boolean add_io(String ioType, int x, int y) {
      return placeFrom(IO_MAP, ioType, x, y, "input/output");
    }

    public boolean add_ttl(String ttlType, int x, int y) {
      return placeFrom(TTL_MAP, ttlType, x, y, "ttl");
    }

    public boolean add_tcl(String tclType, int x, int y) {
      return placeFrom(TCL_MAP, tclType, x, y, "tcl");
    }

    public boolean add_bfh(String bfhType, int x, int y) {
      return placeFrom(BFH_MAP, bfhType, x, y, "bfh");
    }

    public boolean add_extra_io(String extraIoType, int x, int y) {
      return placeFrom(EXTRA_IO_MAP, extraIoType, x, y, "input/output extra");
    }

    public boolean add_soc(String socType, int x, int y) {
      return placeFrom(SOC_MAP, socType, x, y, "soc");
    }

    /**
     * List components in the active circuit as "label (Factory Name)" strings.
     */
    public String[] list_components() {
      final var proj = context.project;
      if (!checkProject(proj, "list_components")) return new String[0];
      final var circuit = proj.getCurrentCircuit();
      if (!checkCircuit(circuit, "list_components")) return new String[0];
      return circuit.getNonWires().stream()
          .map(c -> {
            final var lab = c.getAttributeSet().containsAttribute(StdAttr.LABEL)
                ? String.valueOf(c.getAttributeSet().getValue(StdAttr.LABEL)) : "";
            return (lab == null || lab.isBlank()) ? c.getFactory().getName() : (lab + " (" + c.getFactory().getName() + ")");
          })
          .toArray(String[]::new);
    }

    /**
     * Get attributes for a named component (by label). Returns a map of attribute name -> value.
     */
    public java.util.Map<String, Object> get_component_attributes(String componentLabel) {
      final var proj = context.project;
      final var map = new java.util.LinkedHashMap<String, Object>();
      if (!checkProject(proj, "get_component_attributes")) return map;
      final var circuit = proj.getCurrentCircuit();
      if (!checkCircuit(circuit, "get_component_attributes")) return map;
      final var comp = findComponentByLabel(circuit, componentLabel);
      if (comp == null) return map;
      final var attrs = comp.getAttributeSet();
      final var list = attrs.getAttributes();
      if (list == null) return map;
      for (final var attr : list) {
        try {
          map.put(attr.getName(), attrs.getValue(attr));
        } catch (Throwable ignored) {
        }
      }
      return map;
    }

    /**
     * Set a single attribute on a component identified by its label. Value is provided as string
     * and parsed by the Attribute.parse(...) implementation.
     */
    public boolean set_component_attribute(String componentLabel, String attributeName, String valueStr) {
      final var proj = context.project;
      if (!checkProject(proj, "set_component_attribute")) return false;
      final var circuit = proj.getCurrentCircuit();
      if (!checkCircuit(circuit, "set_component_attribute")) return false;
      final var comp = findComponentByLabel(circuit, componentLabel);
      if (comp == null) {
        logger.warn("set_component_attribute: unknown component '{}'", componentLabel);
        return false;
      }

      final var attrs = comp.getAttributeSet();
      final var list = attrs.getAttributes();
      if (list == null) {
        logger.warn("set_component_attribute: component has no attribute list: {}", componentLabel);
        return false;
      }

      Attribute<?> target = null;
      for (final var a : list) {
        if (a.getName().equalsIgnoreCase(attributeName) || a.getDisplayName().equalsIgnoreCase(attributeName)) {
          target = a;
          break;
        }
      }
      if (target == null) {
        logger.warn("set_component_attribute: attribute '{}' not found on component '{}'", attributeName, componentLabel);
        return false;
      }

      Object parsedValue;
      try {
        parsedValue = target.parse(valueStr);
      } catch (Exception e) {
        logger.warn("set_component_attribute: failed to parse value '{}' for attribute '{}': {}", valueStr, attributeName, e.getMessage());
        return false;
      }

      final var action = new SetAttributeAction(circuit, new StringGetter() {
        @Override
        public String toString() {
          return "Script: set " + attributeName + " on " + componentLabel;
        }
      });
      action.set(comp, target, parsedValue);
      proj.doAction(action);
      return true;
    }

    // ── Discovery helpers ─────────────────────────────────────────────────────

    /** Returns all known gate type keys. */
    public String available_gates() {
      return String.join(", ", GATE_MAP.keySet());
    }

    /** Returns all known wiring element type keys. */
    public String available_wiring() {
      return String.join(", ", WIRING_MAP.keySet());
    }

    /** Returns all known plexer type keys. */
    public String available_plexers() {
      return String.join(", ", PLEXER_MAP.keySet());
    }

    /** Returns all known arithmetic type keys. */
    public String available_arith() {
      return String.join(", ", ARITH_MAP.keySet());
    }

    public String available_fp_arith() {
      return String.join(", ", FP_ARITH_MAP.keySet());
    }

    public String available_memory() {
      return String.join(", ", MEMORY_MAP.keySet());
    }

    public String available_io() {
      return String.join(", ", IO_MAP.keySet());
    }

    public String available_ttl() {
      return String.join(", ", TTL_MAP.keySet());
    }

    public String available_tcl() {
      return String.join(", ", TCL_MAP.keySet());
    }

    public String available_bfh() {
      return String.join(", ", BFH_MAP.keySet());
    }

    public String available_extra_io() {
      return String.join(", ", EXTRA_IO_MAP.keySet());
    }

    public String available_soc() {
      return String.join(", ", SOC_MAP.keySet());
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Internal helpers
  // ═══════════════════════════════════════════════════════════════════════════

  /**
   * Generic placement helper: look up a factory from the given map, create a
   * component at (x,y), and push it as an undoable action.
   */
  private boolean placeFrom(
      Map<String, ComponentFactory> map, String typeKey, int x, int y, String category) {
    final var proj = context.project;
    if (!checkProject(proj, "add_" + category)) return false;
    final var circuit = proj.getCurrentCircuit();
    if (!checkCircuit(circuit, "add_" + category)) return false;

    final var key = typeKey == null ? "" : typeKey.toLowerCase().trim();
    final var factory = map.get(key);
    if (factory == null) {
      logger.error("Unknown {} type: '{}'. Known keys: {}", category, typeKey, map.keySet());
      return false;
    }

    final var loc = Location.create(x, y, false);
    final var attrs = factory.createAttributeSet();
    final var comp = factory.createComponent(loc, attrs);

    final var actionName = "Script: add " + typeKey + " (" + category + ")";
    doMutation(circuit, proj, comp, actionName);
    logger.info("Placed '{}' at ({},{}) in circuit '{}'", typeKey, x, y, circuit.getName());
    return true;
  }

  /** Creates a single-component CircuitMutation and executes it via Project.doAction(). */
  private static void doMutation(
      com.cburch.logisim.circuit.Circuit circuit,
      Project proj,
      com.cburch.logisim.comp.Component comp,
      String actionLabel) {
    final var mut = new CircuitMutation(circuit);
    mut.add(comp);
    proj.doAction(mut.toAction(new StringGetter() {
      @Override public String toString() { return actionLabel; }
    }));
  }

  private static boolean checkProject(Project proj, String op) {
    if (proj == null) { logger.warn("{} called but no project is active.", op); return false; }
    return true;
  }

  private static boolean checkCircuit(com.cburch.logisim.circuit.Circuit circuit, String op) {
    if (circuit == null) { logger.warn("{} called but no circuit is active.", op); return false; }
    return true;
  }

  private static Component findComponentByLabel(com.cburch.logisim.circuit.Circuit circuit, String label) {
    if (circuit == null || label == null || label.isBlank()) return null;
    for (final var comp : circuit.getNonWires()) {
      final var attrs = comp.getAttributeSet();
      if (attrs != null && attrs.containsAttribute(StdAttr.LABEL)) {
        final var compLabel = attrs.getValue(StdAttr.LABEL);
        if (label.equals(compLabel)) return comp;
      }
    }
    return null;
  }

  private static com.cburch.logisim.comp.EndData findPort(Component comp, String portName) {
    if (comp == null || portName == null || portName.isBlank()) return null;

    final var normalized = portName.trim().toLowerCase();
    for (int index = 0; index < comp.getEnds().size(); index++) {
      final var end = comp.getEnd(index);
      final var aliases = buildPortAliases(normalized, comp, index);
      for (final var alias : aliases) {
        if (normalized.equals(alias)) return end;
      }
    }

    final var fallback = switch (normalized) {
      case "in", "input", "i", "a", "left", "0" -> 0;
      case "out", "output", "o", "b", "right", "1" -> 1;
      case "clk", "clock", "c" -> 0;
      case "en", "enable", "e" -> 0;
      case "sel", "select", "s" -> 0;
      default -> -1;
    };
    if (fallback >= 0 && fallback < comp.getEnds().size()) {
      return comp.getEnd(fallback);
    }
    return null;
  }

  private static java.util.List<String> buildPortAliases(String normalized, Component comp, int index) {
    final var aliases = new java.util.ArrayList<String>();
    aliases.add(normalized);

    if (comp.getFactory() instanceof InstanceFactory factory) {
      final var ports = factory.getPorts();
      if (index >= 0 && index < ports.size()) {
        final var port = ports.get(index);
        final var tooltip = port == null ? null : port.getToolTip();
        if (tooltip != null && !tooltip.isBlank()) {
          addAliasVariants(aliases, tooltip);
        }
      }
    }

    final var factoryName = comp.getFactory() == null ? "" : comp.getFactory().getName().toLowerCase();
    if (factoryName.contains("gate") || factoryName.contains("buffer") || factoryName.contains("not")) {
      aliases.addAll(java.util.List.of("in", "out", "a", "b"));
    } else if (factoryName.contains("adder") || factoryName.contains("subtractor") || factoryName.contains("multiplier") || factoryName.contains("divider")) {
      aliases.addAll(java.util.List.of("a", "b", "out", "cin", "cout", "in0", "in1", "sum", "carry"));
    } else if (factoryName.contains("mux") || factoryName.contains("multiplexer") || factoryName.contains("demux") || factoryName.contains("demultiplexer")) {
      aliases.addAll(java.util.List.of("in", "out", "sel", "select"));
    } else if (factoryName.contains("pin")) {
      aliases.addAll(java.util.List.of("in", "out", "input", "output"));
    }

    return java.util.stream.StreamSupport.stream(new java.util.HashSet<>(aliases).spliterator(), false)
        .toList();
  }

  private static void addAliasVariants(java.util.List<String> aliases, String raw) {
    final var cleaned = raw.toLowerCase().trim();
    aliases.add(cleaned);
    aliases.add(cleaned.replace(" ", "_"));
    aliases.add(cleaned.replace(" ", ""));
    aliases.add(cleaned.replace("-", ""));
    aliases.add(cleaned.replace("_", ""));

    for (final var token : cleaned.split("[^a-z0-9]+")) {
      if (!token.isBlank()) aliases.add(token);
    }
  }

  public record ComponentInfo(String category, String type) {}

  public static ComponentInfo getComponentInfo(ComponentFactory factory) {
    if (factory == null) return null;
    for (final var entry : GATE_MAP.entrySet()) {
      if (entry.getValue() == factory) {
        return new ComponentInfo("gate", entry.getKey());
      }
    }
    for (final var entry : WIRING_MAP.entrySet()) {
      if (entry.getValue() == factory) {
        return new ComponentInfo("wiring", entry.getKey());
      }
    }
    for (final var entry : PLEXER_MAP.entrySet()) {
      if (entry.getValue() == factory) {
        return new ComponentInfo("plexer", entry.getKey());
      }
    }
    for (final var entry : ARITH_MAP.entrySet()) {
      if (entry.getValue() == factory) {
        return new ComponentInfo("arith", entry.getKey());
      }
    }
    for (final var entry : FP_ARITH_MAP.entrySet()) {
      if (entry.getValue() == factory) {
        return new ComponentInfo("fp_arith", entry.getKey());
      }
    }
    for (final var entry : MEMORY_MAP.entrySet()) {
      if (entry.getValue() == factory) {
        return new ComponentInfo("memory", entry.getKey());
      }
    }
    for (final var entry : IO_MAP.entrySet()) {
      if (entry.getValue() == factory) {
        return new ComponentInfo("io", entry.getKey());
      }
    }
    for (final var entry : TTL_MAP.entrySet()) {
      if (entry.getValue() == factory) {
        return new ComponentInfo("ttl", entry.getKey());
      }
    }
    for (final var entry : TCL_MAP.entrySet()) {
      if (entry.getValue() == factory) {
        return new ComponentInfo("tcl", entry.getKey());
      }
    }
    for (final var entry : BFH_MAP.entrySet()) {
      if (entry.getValue() == factory) {
        return new ComponentInfo("bfh", entry.getKey());
      }
    }
    for (final var entry : EXTRA_IO_MAP.entrySet()) {
      if (entry.getValue() == factory) {
        return new ComponentInfo("extra_io", entry.getKey());
      }
    }
    for (final var entry : SOC_MAP.entrySet()) {
      if (entry.getValue() == factory) {
        return new ComponentInfo("soc", entry.getKey());
      }
    }
    return null;
  }

  public static String generatePythonCode(Circuit circuit) {
    if (circuit == null) {
      return "";
    }
    final var sb = new StringBuilder();
    sb.append("from logisim_py.api import *\n\n");
    sb.append("circuit = Circuit('").append(circuit.getName()).append("')\n\n");

    final var counters = new java.util.HashMap<String, Integer>();
    
    for (final var comp : circuit.getNonWires()) {
      final var factory = comp.getFactory();
      final var info = getComponentInfo(factory);
      
      String type = (info != null) ? info.type() : factory.getName().toLowerCase().replace(" ", "_").replace("gate", "").trim();
      String category = (info != null) ? info.category() : "wiring";
      
      final var labelAttr = comp.getAttributeSet().getValue(StdAttr.LABEL);
      String label = (labelAttr != null && !labelAttr.toString().isBlank()) ? labelAttr.toString() : "";
      
      String pyName;
      if (!label.isEmpty()) {
        pyName = label.replaceAll("[^a-zA-Z0-9_]", "_");
      } else {
        final var count = counters.getOrDefault(type, 0);
        pyName = type + count;
        counters.put(type, count + 1);
      }
      
      final var loc = comp.getLocation();
      final var x = loc.getX();
      final var y = loc.getY();
      
      sb.append("circuit.add(");
      if ("gate".equals(category)) {
        sb.append("Gate('").append(type).append("', '").append(pyName).append("', x=").append(x).append(", y=").append(y);
      } else {
        final var className = toCamelCase(type);
        sb.append(className).append("('").append(pyName).append("', x=").append(x).append(", y=").append(y);
      }
      
      if (factory == Pin.FACTORY) {
        final var typeVal = comp.getAttributeSet().getValue(Pin.ATTR_TYPE);
        final var isInput = (typeVal == null || typeVal == Pin.INPUT);
        sb.append(", is_input=").append(isInput ? "True" : "False");
      }
      
      if (!label.isEmpty()) {
        sb.append(", label='").append(label.replace("'", "\\'")).append("'");
      }
      sb.append("))\n");
    }
    
    sb.append("\n");
    
    var wireCount = 0;
    for (final var wire : circuit.getWires()) {
      final var e0 = wire.getEnd0();
      final var e1 = wire.getEnd1();
      sb.append("circuit.add(Wire('wire").append(wireCount++)
        .append("', source='").append(e0.getX()).append(",").append(e0.getY())
        .append("', target='").append(e1.getX()).append(",").append(e1.getY())
        .append("'))\n");
    }
    
    return sb.toString();
  }
  
  private static String toCamelCase(String s) {
    if (s == null || s.isEmpty()) return "";
    if ("por".equals(s)) return "Por";
    final var parts = s.split("[_-]");
    final var sb = new StringBuilder();
    for (final var part : parts) {
      if (!part.isEmpty()) {
        sb.append(Character.toUpperCase(part.charAt(0)));
        sb.append(part.substring(1));
      }
    }
    return sb.toString();
  }
}
