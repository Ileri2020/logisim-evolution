package com.cburch.logisim.scripting;

import com.cburch.logisim.proj.Project;
import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.Font;
import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;

public class PythonConsolePanel extends JPanel {
  private static final long serialVersionUID = 1L;
  private final Project project;
  private final JTextArea outputArea = new JTextArea();
  private final JTextArea inputArea = new JTextArea();
  private final JTextField scriptPathField = new JTextField();

  public PythonConsolePanel(Project project) {
    this.project = project;
    buildUi();
  }

  private void buildUi() {
    setLayout(new BorderLayout(6, 6));
    setBorder(BorderFactory.createEmptyBorder(8, 8, 8, 8));

    outputArea.setEditable(false);
    outputArea.setFont(new Font("Monospaced", Font.PLAIN, 12));
    outputArea.setText("Python console ready.\nType Python code to create a blueprint or inspect the current circuit.\n");

    inputArea.setFont(new Font("Monospaced", Font.PLAIN, 12));
    inputArea.setText(
        "from logisim_py.api import Circuit, Gate\n"
            + "circuit = Circuit('demo')\n"
            + "circuit.add(Gate('and', 'and0'))\n"
            + "print('ready')\n");

    scriptPathField.setText("scripts/python/generated_blueprint.json");

    final var controls = new JPanel(new BorderLayout(6, 0));
    controls.add(scriptPathField, BorderLayout.CENTER);
    final var runButton = new JButton("Run");
    runButton.addActionListener(e -> runCurrentSnippet());
    controls.add(runButton, BorderLayout.EAST);

    final var editorPanel = new JPanel(new BorderLayout(6, 6));
    editorPanel.add(inputArea, BorderLayout.CENTER);
    editorPanel.add(controls, BorderLayout.SOUTH);

    final var outputPanel = new JPanel(new BorderLayout());
    outputPanel.add(new JScrollPane(outputArea), BorderLayout.CENTER);

    final var split = new JSplitPane(JSplitPane.VERTICAL_SPLIT, editorPanel, outputPanel);
    split.setResizeWeight(0.6);
    split.setDividerLocation(220);

    add(split, BorderLayout.CENTER);
  }

  private void runCurrentSnippet() {
    SwingUtilities.invokeLater(() -> {
      outputArea.append("\n>>> running snippet...\n");
      try {
        final var tempDir = Files.createTempDirectory("logisim-python-console");
        final var scriptPath = tempDir.resolve("console_script.py");
        Files.writeString(scriptPath, inputArea.getText(), StandardCharsets.UTF_8);
        final var outputFile = resolveOutputFile();
        final var runner = new PythonCircuitScriptRunner();
        final var result = runner.runCode(inputArea.getText(), outputFile);
        outputArea.append(result.output().isBlank() ? "" : result.output());
        if (result.exitCode() == 0) {
          outputArea.append("\n[ok] blueprint written to " + outputFile + "\n");
        } else {
          outputArea.append("\n[error] exit code " + result.exitCode() + "\n");
        }
      } catch (Exception ex) {
        outputArea.append("\n[error] " + ex.getMessage() + "\n");
      }
    });
  }

  private File resolveOutputFile() {
    final var pathText = scriptPathField.getText().trim();
    if (pathText.isBlank()) {
      return null;
    }
    final var path = Path.of(pathText);
    if (!path.isAbsolute()) {
      final var workspaceRoot = Path.of(System.getProperty("user.dir"));
      return workspaceRoot.resolve(path).toFile();
    }
    return path.toFile();
  }
}
