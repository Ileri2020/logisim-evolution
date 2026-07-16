package com.cburch.logisim.scripting;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

class PythonConsolePanelTest {
  @TempDir Path tempDir;

  @Test
  void runsSelectedScriptFileWhenPathPointsToPythonFile() throws Exception {
    final var scriptPath = tempDir.resolve("demo_script.py");
    final var outputPath = tempDir.resolve("demo_blueprint.json");
    Files.writeString(
        scriptPath,
        "from logisim_py.api import Circuit, Gate\n"
            + "circuit = Circuit('demo')\n"
            + "circuit.add(Gate('and', 'and0'))\n"
            + "circuit.save_to('"
            + outputPath.toString().replace("\\", "\\\\")
            + "')\n");

    final var panel = new PythonConsolePanel(null);
    panel.setScriptPath(scriptPath.toString());
    panel.runCurrentSnippetNow();

    assertTrue(Files.exists(outputPath), "selected script should be executed and write a blueprint");
    assertTrue(panel.getOutputText().contains("[ok]"), panel.getOutputText());
  }

  @Test
  void loadsSelectedScriptIntoEditorWhenRequested() throws Exception {
    final var scriptPath = tempDir.resolve("editor_script.py");
    Files.writeString(scriptPath, "from logisim_py.api import Circuit\n" + "circuit = Circuit('demo')\n");

    final var panel = new PythonConsolePanel(null);
    panel.loadScriptFileAndRun(scriptPath);

    assertTrue(panel.getInputText().contains("Circuit('demo')"), panel.getInputText());
    assertTrue(panel.getOutputText().contains("script"), panel.getOutputText());
  }
}
