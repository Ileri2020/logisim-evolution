package com.cburch.logisim.scripting;

import com.cburch.logisim.proj.Project;
import com.cburch.logisim.util.JFileChoosers;
import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JFileChooser;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;
import javax.swing.filechooser.FileNameExtensionFilter;

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

    scriptPathField.setText("scripts/python/examples/binary_counter.py");
    scriptPathField.setToolTipText("Click to choose a Python script from the built-in examples or another location.");
    scriptPathField.addMouseListener(
        new MouseAdapter() {
          @Override
          public void mouseClicked(MouseEvent e) {
            chooseScriptFile();
          }
        });

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
    SwingUtilities.invokeLater(this::runCurrentSnippetNow);
  }

  void runCurrentSnippetNow() {
    outputArea.append("\n>>> running script...\n");
    try {
      final var scriptFile = resolveScriptFile();
      if (scriptFile != null && Files.isRegularFile(scriptFile)) {
        if (runSelectedScript(scriptFile)) {
          return;
        }
      }

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
  }

  private boolean runSelectedScript(Path scriptFile) throws IOException, InterruptedException {
    final var pythonManager = PythonScriptManager.getInstance();
    if (project != null) {
      pythonManager.setActiveProject(project);
    }
    pythonManager.initialize();
    if (pythonManager.isReady()) {
      outputArea.append("\n>>> executing via embedded Python runtime...\n");
      final var success = pythonManager.runFile(scriptFile.toFile());
      if (success) {
        outputArea.append("\n[ok] embedded script executed: " + scriptFile + "\n");
        return true;
      }
      outputArea.append("\n[error] embedded Python execution failed\n");
      return false;
    }

    final var runner = new PythonCircuitScriptRunner();
    final var result = runner.runScriptAndCapture(scriptFile.toFile(), null);
    outputArea.append(result.output().isBlank() ? "" : result.output());
    if (result.exitCode() == 0) {
      outputArea.append("\n[ok] script executed: " + scriptFile + "\n");
    } else {
      outputArea.append("\n[error] exit code " + result.exitCode() + "\n");
    }
    return true;
  }

  private void chooseScriptFile() {
    final var chooser = createScriptChooser();
    final var choice = chooser.showOpenDialog(this);
    if (choice != JFileChooser.APPROVE_OPTION) {
      return;
    }

    final var selectedFile = chooser.getSelectedFile();
    if (selectedFile == null) {
      return;
    }

    final var displayPath = toDisplayPath(selectedFile);
    scriptPathField.setText(displayPath);

    if (selectedFile.isFile() && selectedFile.getName().endsWith(".py")) {
      loadScriptFileAndRun(selectedFile.toPath());
      return;
    }
  }

  public void loadScriptFileAndRun(Path scriptPath) {
    if (scriptPath == null) {
      return;
    }
    final var resolved = resolvePath(scriptPath.toString());
    if (resolved != null) {
      scriptPathField.setText(toDisplayPath(resolved.toFile()));
    }
    if (Files.isRegularFile(resolved)) {
      try {
        inputArea.setText(Files.readString(resolved, StandardCharsets.UTF_8));
      } catch (IOException ex) {
        outputArea.append("\n[error] could not read selected script: " + ex.getMessage() + "\n");
      }
    }
    runCurrentSnippet();
  }

  public void setScriptPath(String pathText) {
    scriptPathField.setText(pathText == null ? "" : pathText);
  }

  public void saveLinkedPythonFile() {
    final var scriptPath = resolveScriptFile();
    if (scriptPath == null) {
      return;
    }
    try {
      Files.createDirectories(scriptPath.getParent());
      Files.writeString(scriptPath, inputArea.getText(), StandardCharsets.UTF_8);
    } catch (IOException ex) {
      outputArea.append("\n[error] could not save linked script: " + ex.getMessage() + "\n");
    }
  }

  public String getOutputText() {
    return outputArea.getText();
  }

  public String getInputText() {
    return inputArea.getText();
  }

  public void appendOutput(String text) {
    outputArea.append(text);
  }

  private JFileChooser createScriptChooser() {
    final var chooser = JFileChoosers.createSelected(resolveInitialSelection());
    chooser.setDialogTitle("Select Python Script");
    chooser.setFileSelectionMode(JFileChooser.FILES_ONLY);
    chooser.setAcceptAllFileFilterUsed(false);
    chooser.setFileFilter(new FileNameExtensionFilter("Python scripts", "py"));
    return chooser;
  }

  private File resolveInitialSelection() {
    final var pathText = scriptPathField.getText().trim();
    if (!pathText.isBlank()) {
      final var candidate = resolvePath(pathText);
      if (candidate != null && Files.exists(candidate)) {
        return candidate.toFile();
      }
    }

    final var examplesDir = resolveWorkspaceRoot().resolve("scripts/python/examples");
    if (Files.isDirectory(examplesDir)) {
      return examplesDir.toFile();
    }
    return resolveWorkspaceRoot().toFile();
  }

  private Path resolveWorkspaceRoot() {
    return Path.of(System.getProperty("user.dir"));
  }

  private Path resolveScriptFile() {
    final var pathText = scriptPathField.getText().trim();
    if (pathText.isBlank()) {
      return null;
    }
    final var path = resolvePath(pathText);
    if (path == null || !Files.isRegularFile(path)) {
      return null;
    }
    return path;
  }

  private Path resolvePath(String pathText) {
    final var path = Path.of(pathText);
    if (path.isAbsolute()) {
      return path;
    }
    return resolveWorkspaceRoot().resolve(path);
  }

  private String toDisplayPath(File file) {
    final var workspaceRoot = resolveWorkspaceRoot();
    try {
      final var relative = workspaceRoot.relativize(file.toPath().toAbsolutePath());
      return relative.toString().replace('\\', '/');
    } catch (IllegalArgumentException ignored) {
      return file.getAbsolutePath();
    }
  }

  private File resolveOutputFile() {
    final var pathText = scriptPathField.getText().trim();
    if (pathText.isBlank()) {
      return null;
    }
    final var path = resolvePath(pathText);
    if (path == null) {
      return null;
    }
    if (path.getFileName() != null && path.getFileName().toString().endsWith(".py")) {
      final var stem = path.getFileName().toString().replaceFirst("\\.py$", "");
      return path.resolveSibling(stem + "_blueprint.json").toFile();
    }
    return path.toFile();
  }
}
