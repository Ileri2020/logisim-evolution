package com.cburch.logisim.scripting;

import com.cburch.logisim.proj.Project;
import com.cburch.logisim.util.JFileChoosers;
import java.awt.BorderLayout;
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
    initializeScriptFile();
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

    final var exampleCombo = new javax.swing.JComboBox<String>(new String[] {
      "Select Example...",
      "adder_chain.py",
      "advanced_counter.py",
      "binary_counter.py",
      "bjt_oscillator.py",
      "d_flip_flop.py",
      "extended_library.py",
      "live_context_example.py",
      "memory_register.py",
      "nor_gate_flip_flop.py",
      "shift_register.py",
      "simple_counter.py",
      "sr_latch.py",
      "t_flip_flop.py",
      "traffic_light.py"
    });
    exampleCombo.setFont(new Font("SansSerif", Font.PLAIN, 11));
    exampleCombo.addActionListener(e -> {
      final var selected = (String) exampleCombo.getSelectedItem();
      if (selected == null || selected.equals("Select Example...")) {
        return;
      }
      final var examplesDir = resolveWorkspaceRoot().resolve("scripts/python/examples");
      final var exampleFile = examplesDir.resolve(selected).toFile();
      if (exampleFile.exists()) {
        scriptPathField.setText(toDisplayPath(exampleFile));
        try {
          inputArea.setText(Files.readString(exampleFile.toPath(), StandardCharsets.UTF_8));
        } catch (IOException ex) {
          outputArea.append("\n[error] Could not read example script: " + ex.getMessage() + "\n");
        }
      }
    });

    final var comboPanel = new JPanel(new BorderLayout(6, 0));
    comboPanel.add(new javax.swing.JLabel("Examples:"), BorderLayout.WEST);
    comboPanel.add(exampleCombo, BorderLayout.CENTER);

    final var controls = new JPanel(new BorderLayout(6, 0));
    controls.add(scriptPathField, BorderLayout.CENTER);
    final var runButton = new JButton("Run");
    runButton.addActionListener(e -> runCurrentSnippet());
    controls.add(runButton, BorderLayout.EAST);

    final var controlPanel = new JPanel(new BorderLayout(0, 6));
    controlPanel.add(comboPanel, BorderLayout.NORTH);
    controlPanel.add(controls, BorderLayout.SOUTH);

    final var editorPanel = new JPanel(new BorderLayout(6, 6));
    editorPanel.add(new JScrollPane(inputArea), BorderLayout.CENTER);
    editorPanel.add(controlPanel, BorderLayout.SOUTH);

    final var outputPanel = new JPanel(new BorderLayout());
    outputPanel.add(new JScrollPane(outputArea), BorderLayout.CENTER);

    final var split = new JSplitPane(JSplitPane.VERTICAL_SPLIT, editorPanel, outputPanel);
    split.setResizeWeight(0.6);
    split.setDividerLocation(220);

    add(split, BorderLayout.CENTER);
  }

  private void runCurrentSnippet() {
    final var pathText = scriptPathField.getText().trim();
    if (pathText.isBlank()) {
      outputArea.append("\n[error] No script file linked.\n");
      return;
    }

    final var file = resolvePath(pathText).toFile();
    outputArea.append("\n>>> running script: " + file.getName() + "...\n");

    // Run on a background thread so the GUI stays responsive.
    new Thread(() -> {
      try {
        // Write editor content to the linked file so what you see is what runs.
        final var parent = file.getParentFile();
        if (parent != null && !parent.exists()) {
          parent.mkdirs();
        }
        Files.writeString(file.toPath(), inputArea.getText(), StandardCharsets.UTF_8);

        // Ensure the embedded Python engine has this project bound.
        final var mgr = PythonScriptManager.getInstance();
        mgr.initialize();
        mgr.setActiveProject(project);

        // Redirect Python stdout/stderr into the output panel.
        mgr.eval(
            "import sys\n" +
            "class _LogisimIO:\n" +
            "    def write(self, s):\n" +
            "        logisim.writeOutput(s)\n" +
            "    def flush(self):\n" +
            "        pass\n" +
            "_io = _LogisimIO()\n" +
            "sys.stdout = _io\n" +
            "sys.stderr = _io\n"
        );

        final var success = mgr.runFile(file);
        SwingUtilities.invokeLater(() -> {
          if (success) {
            outputArea.append("\n[ok] script finished.\n");
          } else {
            outputArea.append("\n[error] script execution failed — see output above.\n");
          }
        });
      } catch (Exception ex) {
        SwingUtilities.invokeLater(() ->
            outputArea.append("\n[error] " + ex.getMessage() + "\n"));
      }
    }, "logisim-python-runner").start();
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

    final var examplesDir = resolveWorkspaceRoot().resolve("scripts/python/examples");
    if (Files.isDirectory(examplesDir)) {
      return examplesDir.toFile();
    }
    return resolveWorkspaceRoot().toFile();
  }

  private Path resolveWorkspaceRoot() {
    var current = Path.of(System.getProperty("user.dir", ".")).toAbsolutePath();
    while (current != null) {
      if (Files.isDirectory(current.resolve("scripts/python"))) {
        return current.normalize();
      }
      current = current.getParent();
    }
    return Path.of(System.getProperty("user.dir", "."));
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
    return resolvePath(pathText).toFile();
  }

  private void initializeScriptFile() {
    final var mainFile = project.getLogisimFile().getLoader().getMainFile();
    if (mainFile == null) {
      try {
        final var documentsDir = new File(System.getProperty("user.home"), "Documents");
        if (!documentsDir.exists()) {
          documentsDir.mkdirs();
        }
        var pyFile = new File(documentsDir, "untitled.py");
        int counter = 1;
        while (pyFile.exists()) {
          pyFile = new File(documentsDir, "untitled_" + counter + ".py");
          counter++;
        }
        pyFile.createNewFile();
        
        final var code = LogisimPythonBindings.generatePythonCode(project.getCurrentCircuit());
        Files.writeString(pyFile.toPath(), code, StandardCharsets.UTF_8);
        
        scriptPathField.setText(pyFile.getAbsolutePath().replace('\\', '/'));
        inputArea.setText(code);
      } catch (IOException e) {
        outputArea.append("\n[error] Could not create new python file in Documents: " + e.getMessage() + "\n");
      }
    } else {
      final var circPath = mainFile.getAbsolutePath();
      final var pyPath = circPath.substring(0, circPath.lastIndexOf('.')) + ".py";
      final var pyFile = new File(pyPath);
      scriptPathField.setText(pyPath.replace('\\', '/'));
      
      try {
        if (pyFile.exists()) {
          inputArea.setText(Files.readString(pyFile.toPath(), StandardCharsets.UTF_8));
        } else {
          final var code = LogisimPythonBindings.generatePythonCode(project.getCurrentCircuit());
          Files.writeString(pyFile.toPath(), code, StandardCharsets.UTF_8);
          inputArea.setText(code);
        }
      } catch (IOException e) {
        outputArea.append("\n[error] Could not read or create python file: " + e.getMessage() + "\n");
      }
    }
  }

  public void updatePythonCode(com.cburch.logisim.circuit.Circuit circuit) {
    if (circuit == null) return;
    final String pyCode = LogisimPythonBindings.generatePythonCode(circuit);
    SwingUtilities.invokeLater(() -> {
      inputArea.setText(pyCode);
    });
  }

  public void setScriptPath(String path) {
    if (path != null) {
      SwingUtilities.invokeLater(() -> {
        scriptPathField.setText(path.replace('\\', '/'));
      });
    }
  }

  public void saveLinkedPythonFile() {
    final var pathText = scriptPathField.getText().trim();
    if (pathText.isBlank()) {
      return;
    }
    final var path = resolvePath(pathText);
    if (path != null) {
      try {
        final var parent = path.getParent();
        if (parent != null) {
          Files.createDirectories(parent);
        }
        Files.writeString(path, inputArea.getText(), StandardCharsets.UTF_8);
        outputArea.append("\n[ok] Saved Python script to " + path + "\n");
      } catch (IOException e) {
        outputArea.append("\n[error] Could not save Python script: " + e.getMessage() + "\n");
      }
    }
  }

  public void appendOutput(String text) {
    if (text != null) {
      SwingUtilities.invokeLater(() -> {
        outputArea.append(text);
      });
    }
  }
}
