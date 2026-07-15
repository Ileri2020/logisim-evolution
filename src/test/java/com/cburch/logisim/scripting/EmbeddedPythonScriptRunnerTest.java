package com.cburch.logisim.scripting;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.cburch.logisim.circuit.Circuit;
import com.cburch.logisim.file.LogisimFile;
import com.cburch.logisim.proj.Project;
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
}
