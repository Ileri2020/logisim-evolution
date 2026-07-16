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
    SwingUtilities.invokeLater(this::runCurrentSnippetInternal);
  }

  public void runCurrentSnippetNow() {
    if (SwingUtilities.isEventDispatchThread()) {
      runCurrentSnippetInternal();
    } else {
      try {
        SwingUtilities.invokeAndWait(this::runCurrentSnippetInternal);
      } catch (Exception ex) {
        outputArea.append("\n[error] " + ex.getMessage() + "\n");
      }
    }
  }

  private void runCurrentSnippetInternal() {
    outputArea.append("\n>>> running snippet...\n");
    try {
      final var selectedScript = resolvePath(scriptPathField.getText().trim());
      if (selectedScript != null && selectedScript.toFile().isFile() && selectedScript.toString().endsWith(".py")) {
        runScriptFile(selectedScript.toFile());
        return;
      }

      final var tempDir = Files.createTempDirectory("logisim-python-console");
      final var scriptPath = tempDir.resolve("console_script.py");
      Files.writeString(scriptPath, inputArea.getText(), StandardCharsets.UTF_8);

      final var manager = PythonScriptManager.getInstance();
      if (manager.isReady()) {
        final var success = manager.runFile(scriptPath.toFile());
        if (success) {
          outputArea.append("\n[ok] embedded Python snippet executed\n");
        } else {
          outputArea.append("\n[error] embedded Python snippet execution failed\n");
        }
        return;
      }

      if (PythonScriptManager.isForceEmbedded()) {
        outputArea.append("\n[error] embedded Python runtime required but unavailable\n");
        return;
      }

      final var outputFile = tempDir.resolve("generated_blueprint.json").toFile();
      final var runner = new PythonCircuitScriptRunner();
      final var result = runner.runCode(inputArea.getText(), outputFile);
      outputArea.append(result.output().isBlank() ? "" : result.output());
      if (result.exitCode() == 0) {
        outputArea.append("\n[ok] generated blueprint written to " + outputFile + "\n");
      } else {
        outputArea.append("\n[error] exit code " + result.exitCode() + "\n");
      }
    } catch (Exception ex) {
      outputArea.append("\n[error] " + ex.getMessage() + "\n");
    }
  }

  private void runScriptFile(File scriptFile) {
    final var manager = PythonScriptManager.getInstance();
    if (manager.isReady()) {
      final var success = manager.runFile(scriptFile);
      if (success) {
        outputArea.append("\n[ok] embedded Python script executed: " + scriptFile + "\n");
      } else {
        outputArea.append("\n[error] embedded Python script execution failed: " + scriptFile + "\n");
      }
      return;
    }

    if (PythonScriptManager.isForceEmbedded()) {
      outputArea.append("\n[error] embedded Python runtime required but unavailable\n");
      return;
    }

    final var runner = new PythonCircuitScriptRunner();
    try {
      final var result = runner.runScriptAndCapture(scriptFile, null);
      outputArea.append(result.output().isBlank() ? "" : result.output());
      if (result.exitCode() == 0) {
        outputArea.append("\n[ok] external Python script executed: " + scriptFile + "\n");
      } else {
        outputArea.append("\n[error] exit code " + result.exitCode() + "\n");
      }
    } catch (Exception ex) {
      outputArea.append("\n[error] " + ex.getMessage() + "\n");
    }
  }

  public void setScriptPath(String scriptPath) {
    if (scriptPath == null || scriptPath.isBlank()) {
      return;
    }
    scriptPathField.setText(scriptPath.replace('\\', '/'));
  }

  public void saveLinkedPythonFile() {
    final var targetPath = resolvePath(scriptPathField.getText().trim());
    if (targetPath == null) {
      return;
    }
    try {
      final var parentDir = targetPath.getParent();
      if (parentDir != null) {
        Files.createDirectories(parentDir);
      }
      Files.writeString(targetPath, inputArea.getText(), StandardCharsets.UTF_8);
      outputArea.append("\n[saved] linked Python file: " + targetPath + "\n");
    } catch (IOException ex) {
      outputArea.append("\n[error] could not save linked Python file: " + ex.getMessage() + "\n");
    }
  }

  public void appendOutput(String text) {
    if (text != null && !text.isBlank()) {
      outputArea.append(text);
    }
  }

  public void loadScriptFileAndRun(Path scriptPath) {
    if (scriptPath == null) {
      return;
    }
    final var resolvedPath = scriptPath.toAbsolutePath();
    setScriptPath(resolvedPath.toString());
    try {
      inputArea.setText(Files.readString(resolvedPath, StandardCharsets.UTF_8));
      outputArea.append("\n[script] loaded " + resolvedPath + "\n");
    } catch (IOException ex) {
      outputArea.append("\n[error] could not read script file: " + ex.getMessage() + "\n");
    }
  }

  public String getOutputText() {
    return outputArea.getText();
  }

  public String getInputText() {
    return inputArea.getText();
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
      try {
        inputArea.setText(Files.readString(selectedFile.toPath(), StandardCharsets.UTF_8));
      } catch (IOException ex) {
        outputArea.append("\n[error] could not read selected script: " + ex.getMessage() + "\n");
      }
    }
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

    final var examplesDir = resolveExamplesDirectory();
    if (Files.isDirectory(examplesDir)) {
      return examplesDir.toFile();
    }
    return resolveWorkspaceRoot().toFile();
  }

  private Path resolveWorkspaceRoot() {
    return Path.of(System.getProperty("user.dir"));
  }

  private Path resolveAppHome() {
    try {
      final var codeSource = PythonConsolePanel.class.getProtectionDomain().getCodeSource();
      if (codeSource != null && codeSource.getLocation() != null) {
        final var jarPath = Path.of(codeSource.getLocation().toURI()).toAbsolutePath();
        final var parentDir = jarPath.getParent();
        if (parentDir != null) {
          return parentDir;
        }
      }
    } catch (Exception ignored) {
    }
    return resolveWorkspaceRoot();
  }

  private Path resolveExamplesDirectory() {
    final var workspaceExamples = resolveWorkspaceRoot().resolve("scripts/python/examples");
    if (Files.isDirectory(workspaceExamples)) {
      return workspaceExamples;
    }

    final var appExamples = resolveAppHome().resolve("scripts/python/examples");
    if (Files.isDirectory(appExamples)) {
      return appExamples;
    }

    final var appHomeExamples = resolveAppHome().getParent() != null
        ? resolveAppHome().getParent().resolve("scripts/python/examples")
        : null;
    if (appHomeExamples != null && Files.isDirectory(appHomeExamples)) {
      return appHomeExamples;
    }
    return resolveWorkspaceRoot();
  }

  private Path resolvePath(String pathText) {
    if (pathText == null || pathText.isBlank()) {
      return null;
    }
    final var path = Path.of(pathText);
    if (path.isAbsolute()) {
      return path;
    }

    final var workspaceCandidate = resolveWorkspaceRoot().resolve(path);
    if (Files.exists(workspaceCandidate)) {
      return workspaceCandidate;
    }

    final var appHome = resolveAppHome();
    final var appCandidate = appHome.resolve(path);
    if (Files.exists(appCandidate)) {
      return appCandidate;
    }

    final var appParent = appHome.getParent();
    if (appParent != null) {
      final var parentCandidate = appParent.resolve(path);
      if (Files.exists(parentCandidate)) {
        return parentCandidate;
      }
    }

    return workspaceCandidate;
  }

  private String toDisplayPath(File file) {
    final var absolute = file.toPath().toAbsolutePath();
    try {
      final var workspaceRoot = resolveWorkspaceRoot();
      final var relative = workspaceRoot.relativize(absolute);
      if (!relative.toString().startsWith("..")) {
        return relative.toString().replace('\\', '/');
      }
    } catch (IllegalArgumentException ignored) {
      // ignore and try app-relative display
    }

    try {
      final var appHome = resolveAppHome();
      final var relative = appHome.relativize(absolute);
      if (!relative.toString().startsWith("..")) {
        return relative.toString().replace('\\', '/');
      }
      final var appParent = appHome.getParent();
      if (appParent != null) {
        final var relativeToParent = appParent.relativize(absolute);
        if (!relativeToParent.toString().startsWith("..")) {
          return relativeToParent.toString().replace('\\', '/');
        }
      }
    } catch (IllegalArgumentException ignored) {
      // no-op
    }

    return absolute.toString();
  }

  private File resolveOutputFile() {
    final var pathText = scriptPathField.getText().trim();
    if (pathText.isBlank()) {
      return null;
    }
    return resolvePath(pathText).toFile();
  }
}
