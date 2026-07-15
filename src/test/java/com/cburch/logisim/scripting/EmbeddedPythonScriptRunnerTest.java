package com.cburch.logisim.scripting;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.cburch.logisim.circuit.Circuit;
import com.cburch.logisim.comp.Component;
import com.cburch.logisim.comp.EndData;
import com.cburch.logisim.data.AttributeSet;
import com.cburch.logisim.data.BitWidth;
import com.cburch.logisim.data.Location;
import com.cburch.logisim.file.LogisimFile;
import com.cburch.logisim.instance.InstanceFactory;
import com.cburch.logisim.instance.Port;
import com.cburch.logisim.instance.StdAttr;
import com.cburch.logisim.proj.Project;
import com.cburch.logisim.util.StringGetter;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class EmbeddedPythonScriptRunnerTest {

  private PythonScriptManager manager;

  @BeforeEach
  void setUp() {
    manager = PythonScriptManager.getInstance();
    manager.initialize();
  }

  @AfterEach
  void tearDown() {
    manager.close();
  }

  @Test
  void testEngineInitializationAndBindings() {
    assertTrue(manager.isReady(), "scripting manager should be ready after initialization");
    final var logisimObj = manager.eval("logisim");
    assertNotNull(logisimObj, "logisim global object should be bound in context");
  }

  @Test
  void testProjectContextProxying() {
    final var project = mock(Project.class);
    final var logisimFile = mock(LogisimFile.class);

    when(logisimFile.getName()).thenReturn("test_project_file.circ");
    when(project.getLogisimFile()).thenReturn(logisimFile);

    manager.setActiveProject(project);

    final var result = manager.eval("logisim.context.project_name()");
    assertNotNull(result, "should get result from project_name()");
    assertEquals("test_project_file.circ", result.asString(), "project name should match mocked project");
  }

  @Test
  void testComponentCreation() {
    final var project = mock(Project.class);
    final var circuit = mock(Circuit.class);
    when(project.getCurrentCircuit()).thenReturn(circuit);

    manager.setActiveProject(project);

    final var gateResult = manager.eval("logisim.ops.add_gate('and', 100, 200, 'g0')");
    assertNotNull(gateResult);
    assertTrue(gateResult.asBoolean(), "add_gate should succeed");

    final var wiringResult = manager.eval("logisim.ops.add_wiring('probe', 100, 200)");
    assertNotNull(wiringResult);
    assertTrue(wiringResult.asBoolean(), "add_wiring should succeed");

    final var plexerResult = manager.eval("logisim.ops.add_plexer('decoder', 100, 200)");
    assertNotNull(plexerResult);
    assertTrue(plexerResult.asBoolean(), "add_plexer should succeed");

    final var arithResult = manager.eval("logisim.ops.add_arith('adder', 100, 200)");
    assertNotNull(arithResult);
    assertTrue(arithResult.asBoolean(), "add_arith should succeed");

    final var fpArithResult = manager.eval("logisim.ops.add_fp_arith('fpadder', 100, 200)");
    assertNotNull(fpArithResult);
    assertTrue(fpArithResult.asBoolean(), "add_fp_arith should succeed");

    final var memoryResult = manager.eval("logisim.ops.add_memory('ram', 100, 200)");
    assertNotNull(memoryResult);
    assertTrue(memoryResult.asBoolean(), "add_memory should succeed");

    final var ioResult = manager.eval("logisim.ops.add_io('led', 100, 200)");
    assertNotNull(ioResult);
    assertTrue(ioResult.asBoolean(), "add_io should succeed");

    final var ttlResult = manager.eval("logisim.ops.add_ttl('7400', 100, 200)");
    assertNotNull(ttlResult);
    assertTrue(ttlResult.asBoolean(), "add_ttl should succeed");

    final var tclResult = manager.eval("logisim.ops.add_tcl('tcl_generic', 100, 200)");
    assertNotNull(tclResult);
    assertTrue(tclResult.asBoolean(), "add_tcl should succeed");

    final var bfhResult = manager.eval("logisim.ops.add_bfh('bin_to_bcd', 100, 200)");
    assertNotNull(bfhResult);
    assertTrue(bfhResult.asBoolean(), "add_bfh should succeed");

    final var extraIoResult = manager.eval("logisim.ops.add_extra_io('buzzer', 100, 200)");
    assertNotNull(extraIoResult);
    assertTrue(extraIoResult.asBoolean(), "add_extra_io should succeed");

    final var socResult = manager.eval("logisim.ops.add_soc('nios2', 100, 200)");
    assertNotNull(socResult);
    assertTrue(socResult.asBoolean(), "add_soc should succeed");
  }

  @Test
  void testPlacementAndWireHelpers() {
    final var project = mock(Project.class);
    final var circuit = mock(Circuit.class);
    when(project.getCurrentCircuit()).thenReturn(circuit);

    manager.setActiveProject(project);

    final var placementResult = manager.eval("logisim.ops.place_component('gate:and', 120, 240, 'g1')");
    assertNotNull(placementResult);
    assertTrue(placementResult.asBoolean(), "place_component should succeed");

    final var wireResult = manager.eval("logisim.ops.add_wire(120, 240, 220, 240)");
    assertNotNull(wireResult);
    assertTrue(wireResult.asBoolean(), "add_wire should succeed");
  }

  @Test
  void testPortBasedConnectionHelpers() {
    final var project = mock(Project.class);
    final var circuit = mock(Circuit.class);
    final var sourceAttrs = mock(AttributeSet.class);
    final var targetAttrs = mock(AttributeSet.class);
    final var source = mock(Component.class);
    final var target = mock(Component.class);

    when(project.getCurrentCircuit()).thenReturn(circuit);
    when(circuit.getNonWires()).thenReturn(Set.of(source, target));
    when(source.getAttributeSet()).thenReturn(sourceAttrs);
    when(target.getAttributeSet()).thenReturn(targetAttrs);
    when(sourceAttrs.containsAttribute(StdAttr.LABEL)).thenReturn(true);
    when(targetAttrs.containsAttribute(StdAttr.LABEL)).thenReturn(true);
    when(sourceAttrs.getValue(StdAttr.LABEL)).thenReturn("src");
    when(targetAttrs.getValue(StdAttr.LABEL)).thenReturn("dst");
    final var sourceOut = new EndData(Location.create(10, 10, false), BitWidth.UNKNOWN, EndData.INPUT_OUTPUT);
    final var sourceIn = new EndData(Location.create(20, 10, false), BitWidth.UNKNOWN, EndData.INPUT_OUTPUT);
    final var targetIn = new EndData(Location.create(40, 10, false), BitWidth.UNKNOWN, EndData.INPUT_OUTPUT);
    final var targetOut = new EndData(Location.create(50, 10, false), BitWidth.UNKNOWN, EndData.INPUT_OUTPUT);
    when(source.getEnds()).thenReturn(List.of(sourceOut, sourceIn));
    when(target.getEnds()).thenReturn(List.of(targetIn, targetOut));
    when(source.getEnd(0)).thenReturn(sourceOut);
    when(source.getEnd(1)).thenReturn(sourceIn);
    when(target.getEnd(0)).thenReturn(targetIn);
    when(target.getEnd(1)).thenReturn(targetOut);

    manager.setActiveProject(project);

    final var connectionResult = manager.eval("logisim.ops.connect_ports('src', 'out', 'dst', 'in')");
    assertNotNull(connectionResult);
    assertTrue(connectionResult.asBoolean(), "connect_ports should succeed");
  }

  @Test
  void testComponentSpecificPortMetadataResolution() {
    final var project = mock(Project.class);
    final var circuit = mock(Circuit.class);
    final var attrs = mock(AttributeSet.class);
    final var component = mock(Component.class);
    final var factory = mock(InstanceFactory.class);
    final var portIn0 = new Port(0, 0, Port.INPUT, 1);
    final var portIn1 = new Port(0, 10, Port.INPUT, 1);
    final var portOut = new Port(0, 20, Port.OUTPUT, 1);
    portIn0.setToolTip(new StringGetter() {
      @Override
      public String toString() {
        return "in0";
      }
    });
    portIn1.setToolTip(new StringGetter() {
      @Override
      public String toString() {
        return "in1";
      }
    });
    portOut.setToolTip(new StringGetter() {
      @Override
      public String toString() {
        return "out";
      }
    });

    when(project.getCurrentCircuit()).thenReturn(circuit);
    when(circuit.getNonWires()).thenReturn(Set.of(component));
    when(component.getAttributeSet()).thenReturn(attrs);
    when(component.getFactory()).thenReturn(factory);
    when(factory.getName()).thenReturn("Adder");
    when(factory.getPorts()).thenReturn(List.of(portIn0, portIn1, portOut));
    when(attrs.containsAttribute(StdAttr.LABEL)).thenReturn(true);
    when(attrs.getValue(StdAttr.LABEL)).thenReturn("adder");

    final var out = new EndData(Location.create(10, 10, false), BitWidth.UNKNOWN, EndData.INPUT_OUTPUT);
    final var in0 = new EndData(Location.create(20, 10, false), BitWidth.UNKNOWN, EndData.INPUT_OUTPUT);
    final var in1 = new EndData(Location.create(30, 10, false), BitWidth.UNKNOWN, EndData.INPUT_OUTPUT);
    when(component.getEnds()).thenReturn(List.of(out, in0, in1));
    when(component.getEnd(0)).thenReturn(out);
    when(component.getEnd(1)).thenReturn(in0);
    when(component.getEnd(2)).thenReturn(in1);

    manager.setActiveProject(project);

    final var result = manager.eval("logisim.ops.connect_ports('adder', 'in0', 'adder', 'out')");
    assertNotNull(result);
    assertTrue(result.asBoolean(), "component-specific port metadata should resolve correctly");
  }
}
