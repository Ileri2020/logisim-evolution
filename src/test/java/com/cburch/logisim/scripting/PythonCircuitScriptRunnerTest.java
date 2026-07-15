package com.cburch.logisim.scripting;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class PythonCircuitScriptRunnerTest {
  @TempDir Path tempDir;

  @Test
  void runsPythonScriptAndWritesBlueprint() throws Exception {
    final var scriptPath = tempDir.resolve("demo_script.py");
    final var outputPath = tempDir.resolve("demo_blueprint.json");
    Files.writeString(
        scriptPath,
        """
from logisim_py.api import Circuit, Gate, Wire, Counter

circuit = Circuit(\"demo\")
circuit.add(Gate(\"and\", \"and0\"))
circuit.add(Wire(\"w0\", \"and0.out\", \"led0\"))
circuit.add(Counter(\"cnt0\"))
circuit.save_to(\"""
            + outputPath
            + "\")
""");

    final var runner = new PythonCircuitScriptRunner();
    final var exitCode = runner.runScript(scriptPath.toFile(), outputPath.toFile());

    assertEquals(0, exitCode, "python script should complete successfully");
    assertTrue(Files.exists(outputPath), "output blueprint file should be created");
    final var contents = Files.readString(outputPath);
    assertTrue(contents.contains("\"name\": \"demo\""), contents);
    assertTrue(contents.contains("\"type\": \"and\""), contents);
  }

  @Test
  void runsSnippetCodeAndCapturesOutput() throws Exception {
    final var outputPath = tempDir.resolve("console_blueprint.json");
    final var runner = new PythonCircuitScriptRunner();
    final var result = runner.runCode(
        "from logisim_py.api import Circuit, Gate\n"
            + "circuit = Circuit('console_demo')\n"
            + "circuit.add(Gate('not', 'inv0'))\n"
            + "circuit.save_to('"
            + outputPath
            + "')\n",
        outputPath.toFile());

    assertEquals(0, result.exitCode(), "console snippet should complete successfully");
    assertTrue(Files.exists(outputPath), "output blueprint file should be created");
    assertTrue(result.output().contains("wrote") || result.output().isBlank(), result.output());
  }

  @Test
  void runsBuilderCoverageForExtendedElementFamilies() throws Exception {
    final var scriptPath = tempDir.resolve("extended_catalog_script.py");
    final var outputPath = tempDir.resolve("extended_catalog_blueprint.json");
    Files.writeString(
        scriptPath,
        """
from logisim_py.builder import BlueprintBuilder

builder = BlueprintBuilder('extended_catalog')
builder.add_floating_point_adder('fpa0')
builder.add_ram('ram0')
builder.add_led('led0')
builder.add_ttl_7400('ttl0')
builder.add_tcl('tcl0')
builder.add_bfh_mega_function('mega0')
builder.add_input_output_extra('ioextra0')
builder.add_system_on_chip('soc0')
builder.save(output_path)
""".replace("output_path", "'" + outputPath + "'"));

    final var runner = new PythonCircuitScriptRunner();
    final var exitCode = runner.runScript(scriptPath.toFile(), outputPath.toFile());

    assertEquals(0, exitCode, "extended catalog builder should complete successfully");
    assertTrue(Files.exists(outputPath), "extended catalog blueprint should be created");
    final var contents = Files.readString(outputPath);
    assertTrue(contents.contains("fpa0"), contents);
    assertTrue(contents.contains("soc0"), contents);
  }
}
