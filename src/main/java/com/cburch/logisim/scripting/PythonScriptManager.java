/*
 * Logisim-evolution - digital logic design tool and simulator
 * Copyright by the Logisim-evolution developers
 *
 * https://github.com/logisim-evolution/
 *
 * This is free software released under GNU GPLv3 license
 */

package com.cburch.logisim.scripting;

import com.cburch.logisim.proj.Project;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import org.graalvm.polyglot.Context;
import org.graalvm.polyglot.PolyglotException;
import org.graalvm.polyglot.Source;
import org.graalvm.polyglot.Value;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * PythonScriptManager is the central embedded Python scripting engine for Logisim-evolution.
 *
 * <p>Unlike the original {@link PythonCircuitScriptRunner} which spawns an external OS process,
 * this class embeds a GraalPy Python interpreter directly inside the JVM using the GraalVM
 * Polyglot API. This allows Python scripts to access live Logisim objects (Project, Circuit,
 * Simulator) directly in memory — similar to how Blender's embedded Python interpreter
 * works via {@code bpy}.
 *
 * <p>Usage:
 * <pre>
 *   PythonScriptManager mgr = PythonScriptManager.getInstance();
 *   mgr.setActiveProject(project);
 *   mgr.eval("import logisim; print(logisim.context.circuit_name())");
 *   mgr.runFile(new File("my_circuit.py"));
 * </pre>
 */
public class PythonScriptManager implements AutoCloseable {

  private static final Logger logger = LoggerFactory.getLogger(PythonScriptManager.class);
  private static final String PYTHON = "python";

  /** Singleton instance. */
  private static PythonScriptManager instance;

  /** The embedded GraalPy Polyglot context. */
  private Context polyglotContext;

  /** The currently active project exposed to scripts. */
  private Project activeProject;

  /** The Logisim-Python bindings module exposed into the context. */
  private LogisimPythonBindings bindings;

  /** Whether the engine has been successfully initialized. */
  private boolean initialized = false;

  private PythonScriptManager() {
    // Private constructor – use getInstance()
  }

  /**
   * Returns the singleton instance of PythonScriptManager.
   *
   * @return the singleton instance
   */
  public static synchronized PythonScriptManager getInstance() {
    if (instance == null) {
      instance = new PythonScriptManager();
    }
    return instance;
  }

  /**
   * Initializes the embedded GraalPy polyglot context and injects the {@code logisim}
   * bindings module into the Python namespace.
   *
   * <p>Must be called once at application startup before any scripts are evaluated.
   * Safe to call multiple times – subsequent calls are no-ops.
   */
  public synchronized void initialize() {
    if (initialized) return;
    try {
      logger.info("Initializing embedded GraalPy Python scripting engine...");
      polyglotContext =
          Context.newBuilder(PYTHON)
              .allowAllAccess(true)
              .option("python.PosixModuleBackend", "java")
              .option("python.ForceImportSite", "true")
              .build();

      bindings = new LogisimPythonBindings(this);

      // Inject a top-level 'logisim' object accessible from all scripts.
      final Value pyBindings = polyglotContext.getBindings(PYTHON);
      pyBindings.putMember("logisim", bindings);

      // Verify the engine works by running a simple test.
      polyglotContext.eval(PYTHON, "assert logisim is not None, 'logisim bindings not found'");

      initialized = true;
      logger.info("GraalPy Python scripting engine initialized successfully.");
    } catch (Throwable e) {
      logger.warn("Embedded Python runtime unavailable in this environment; scripting bindings will be disabled. {}", e.getMessage());
      initialized = false;
      if (polyglotContext != null) {
        polyglotContext.close();
        polyglotContext = null;
      }
      bindings = new LogisimPythonBindings(this);
    }
  }

  /**
   * Sets the currently active Logisim {@link Project}. This is called whenever the user switches
   * projects, and the change is immediately visible to any running scripts via
   * {@code logisim.context.project}.
   *
   * @param project the project now active in the main window, or {@code null} if no project
   */
  public synchronized void setActiveProject(Project project) {
    this.activeProject = project;
    if (bindings != null) {
      bindings.updateProject(project);
    }
    logger.debug("Active scripting project set to: {}",
        project != null && project.getLogisimFile() != null ? project.getLogisimFile().getName() : "null");
  }

  /**
   * Returns the currently active project.
   *
   * @return the active {@link Project}, or {@code null}
   */
  public Project getActiveProject() {
    return activeProject;
  }

  /**
   * Evaluates a Python expression or statement block string directly in the embedded interpreter.
   *
   * <p>All Logisim bindings (e.g., {@code logisim.context.circuit_name()}) are available.
   *
   * @param code the Python source code to execute
   * @return the result Value from the polyglot context, or {@code null} on error
   */
  public Value eval(String code) {
    if (!ensureReady()) return null;
    try {
      logger.debug("Evaluating Python code:\n{}", code);
      final var src = Source.newBuilder(PYTHON, code, "<eval>").buildLiteral();
      return polyglotContext.eval(src);
    } catch (PolyglotException e) {
      logger.error("Python error at {}: {}", e.getSourceLocation(), e.getMessage());
      return null;
    } catch (Exception e) {
      logger.error("Unexpected error evaluating Python code: {}", e.getMessage(), e);
      return null;
    }
  }

  /**
   * Loads and runs a Python script file inside the embedded interpreter.
   *
   * <p>Before execution, the script's parent directory is added to Python's {@code sys.path}
   * so it can import sibling modules (e.g., the {@code logisim_py} package in
   * {@code scripts/python/}).
   *
   * @param scriptFile the {@code .py} file to execute
   * @return {@code true} if the script ran without error, {@code false} otherwise
   */
  public boolean runFile(File scriptFile) {
    if (!ensureReady()) return false;
    if (!scriptFile.isFile()) {
      logger.error("Script file not found: {}", scriptFile);
      return false;
    }

    final var outputBuffer = new ByteArrayOutputStream();
    final var captureStream = new PrintStream(outputBuffer, true, StandardCharsets.UTF_8);
    final var originalOut = System.out;
    final var originalErr = System.err;
    try {
      logger.info("Running embedded Python script: {}", scriptFile.getAbsolutePath());
      System.setOut(captureStream);
      System.setErr(captureStream);

      // Add the script's own directory to sys.path.
      final var scriptDir = scriptFile.getParentFile().getAbsolutePath().replace("\\", "\\\\");
      eval("import sys; _sp='" + scriptDir + "'; (sys.path.insert(0,_sp) if _sp not in sys.path else None)");

      // Walk upwards from the script's location to find the scripts/python package root.
      // This is the directory that contains the logisim_py package folder.
      Path packageRoot = resolvePythonPackageRoot(scriptFile.getParentFile().toPath().toAbsolutePath());
      if (packageRoot != null) {
        final var pkgPath = packageRoot.toString().replace("\\", "\\\\");
        eval("import sys; _pp='" + pkgPath + "'; (sys.path.insert(0,_pp) if _pp not in sys.path else None)");
        logger.info("Injected logisim_py package root: {}", packageRoot);
      } else {
        logger.warn("Could not locate logisim_py package root for script: {}", scriptFile);
      }

      final var src =
          Source.newBuilder(PYTHON, scriptFile).mimeType("text/x-python").build();
      polyglotContext.eval(src);
      logger.info("Script completed successfully: {}", scriptFile.getName());
      flushCapturedOutput(outputBuffer);
      return true;
    } catch (PolyglotException e) {
      final var errText = "\nTraceback (most recent call):\n  File \"" + scriptFile.getName() + "\", line " + 
          (e.getSourceLocation() != null ? e.getSourceLocation().getStartLine() : "?") + 
          "\n" + e.getMessage() + "\n";
      logger.error("Python script '{}' failed: {}", scriptFile.getName(), errText);
      if (bindings != null) {
        bindings.writeOutput(errText);
      }
      flushCapturedOutput(outputBuffer);
      return false;
    } catch (IOException e) {
      final var errText = "\n[error] Could not read script file: " + e.getMessage() + "\n";
      logger.error(errText, e);
      if (bindings != null) {
        bindings.writeOutput(errText);
      }
      flushCapturedOutput(outputBuffer);
      return false;
    } finally {
      System.setOut(originalOut);
      System.setErr(originalErr);
      captureStream.close();
    }
  }

  private Path resolvePythonPackageRoot(Path searchDir) {
    while (searchDir != null) {
      if (Files.isDirectory(searchDir.resolve("logisim_py"))) {
        return searchDir;
      }
      final var candidate = searchDir.resolve("scripts").resolve("python");
      if (Files.isDirectory(candidate.resolve("logisim_py"))) {
        return candidate;
      }
      searchDir = searchDir.getParent();
    }

    final var appHome = getAppHome();
    if (appHome != null) {
      final var candidates = List.of(
          appHome.resolve("scripts/python"),
          appHome.getParent() != null ? appHome.getParent().resolve("scripts/python") : null,
          appHome.getParent() != null && appHome.getParent().getParent() != null
              ? appHome.getParent().getParent().resolve("scripts/python")
              : null
      );
      for (final var candidate : candidates) {
        if (candidate != null && Files.isDirectory(candidate.resolve("logisim_py"))) {
          return candidate;
        }
      }
    }
    return null;
  }

  private Path getAppHome() {
    try {
      final var codeSource = PythonScriptManager.class
          .getProtectionDomain()
          .getCodeSource();
      if (codeSource != null && codeSource.getLocation() != null) {
        final var jarPath = Path.of(codeSource.getLocation().toURI()).toAbsolutePath();
        final var parentDir = jarPath.getParent();
        if (parentDir != null) {
          return parentDir;
        }
      }
    } catch (Exception ignored) {
    }
    return Path.of(System.getProperty("user.dir"));
  }

  private void flushCapturedOutput(ByteArrayOutputStream outputBuffer) {
    if (outputBuffer == null) {
      return;
    }
    final var outputText = outputBuffer.toString(StandardCharsets.UTF_8);
    if (outputText != null && !outputText.isBlank() && bindings != null) {
      bindings.writeOutput(outputText);
    }
  }

  /**
   * Returns {@code true} if the embedded Python engine is ready to execute scripts.
   */
  public boolean isReady() {
    return initialized && polyglotContext != null;
  }

  /**
   * Checks readiness and logs a warning if not ready.
   */
  private boolean ensureReady() {
    if (!isReady()) {
      logger.warn("Python scripting engine is not initialized. Call initialize() first.");
      return false;
    }
    return true;
  }

  /**
   * Shuts down the embedded polyglot context and releases resources.
   */
  @Override
  public synchronized void close() {
    if (polyglotContext != null) {
      logger.info("Closing embedded Python scripting engine.");
      polyglotContext.close();
      polyglotContext = null;
    }
    initialized = false;
    instance = null;
  }

  /**
   * Notifies any running embedded scripts that the design has changed. If a
   * top-level Python function named `on_design_update` is defined it will be
   * invoked. Exceptions from the script are logged but do not propagate.
   */
  public synchronized void notifyDesignChanged() {
    if (!ensureReady()) return;
    try {
      final String code = "f = globals().get('on_design_update')\n" +
          "if callable(f):\n" +
          "  f()\n";
      polyglotContext.eval(PYTHON, code);
    } catch (PolyglotException e) {
      logger.error("Error while running on_design_update(): {}", e.getMessage());
    } catch (Exception e) {
      logger.error("Unexpected error notifying design change: {}", e.getMessage(), e);
    }
  }
}
