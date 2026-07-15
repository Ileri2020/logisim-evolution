package com.cburch.logisim.scripting;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class PythonRuntimeManager {
  private static final Logger logger = LoggerFactory.getLogger(PythonRuntimeManager.class);
  private static final PythonRuntimeManager INSTANCE = new PythonRuntimeManager();

  private boolean initialized;
  private String pythonExecutable = "python";

  private PythonRuntimeManager() {}

  public static PythonRuntimeManager get() {
    return INSTANCE;
  }

  public synchronized void initialize() {
    if (initialized) {
      return;
    }

    final var override = System.getenv("PYTHON_EXECUTABLE");
    if (override != null && !override.isBlank()) {
      pythonExecutable = override;
    }

    final var path = resolvePythonExecutable();
    if (path != null) {
      pythonExecutable = path;
    }

    logger.info("Python runtime ready via {}", pythonExecutable);
    initialized = true;
  }

  public String getPythonExecutable() {
    if (!initialized) {
      initialize();
    }
    return pythonExecutable;
  }

  private String resolvePythonExecutable() {
    final var envOverride = System.getenv("PYTHON_EXECUTABLE");
    if (envOverride != null && !envOverride.isBlank()) {
      return envOverride;
    }

    final var candidates = new String[] {"python", "python3", "py"};
    for (final var candidate : candidates) {
      if (isAvailable(candidate)) {
        return candidate;
      }
    }
    return "python";
  }

  private boolean isAvailable(String executable) {
    try {
      final var process = new ProcessBuilder(executable, "--version").redirectErrorStream(true).start();
      final var exitCode = process.waitFor();
      return exitCode == 0;
    } catch (IOException | InterruptedException e) {
      Thread.currentThread().interrupt();
      return false;
    }
  }
}
