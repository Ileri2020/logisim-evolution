package com.cburch.logisim.scripting;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PythonCircuitScriptRunner {
  private static final Logger logger = LoggerFactory.getLogger(PythonCircuitScriptRunner.class);

  public record ExecutionResult(int exitCode, String output) {}

  public int runScript(File scriptFile, File outputFile) throws IOException, InterruptedException {
    return runScriptAndCapture(scriptFile, outputFile).exitCode();
  }

  public ExecutionResult runScriptAndCapture(File scriptFile, File outputFile)
      throws IOException, InterruptedException {
    if (!scriptFile.isFile()) {
      throw new IOException("Python script not found: " + scriptFile);
    }

    final var scriptDir = scriptFile.getParentFile();
    final var command = buildCommand(scriptFile, outputFile);
    logger.info("Running Python script: {}", String.join(" ", command));

    final var processBuilder = new ProcessBuilder(command);
    processBuilder.directory(scriptDir);
    processBuilder.redirectErrorStream(true);
    configureEnvironment(processBuilder.environment());
    final var process = processBuilder.start();

    final var output = new StringBuilder();
    try (var reader = process.inputReader()) {
      reader.lines().forEach(line -> output.append(line).append('\n'));
    }

    final var exitCode = process.waitFor();
    if (exitCode == 0 && outputFile != null && outputFile.exists()) {
      logger.info("Python script generated blueprint at {}", outputFile);
    } else if (exitCode != 0) {
      logger.error("Python script failed with exit code {}: {}", exitCode, output);
    }
    return new ExecutionResult(exitCode, output.toString());
  }

  public ExecutionResult runCode(String code, File outputFile) throws IOException, InterruptedException {
    final var tempDir = Files.createTempDirectory("logisim-python-console");
    final var scriptPath = tempDir.resolve("console_script.py");
    Files.writeString(scriptPath, code, StandardCharsets.UTF_8);
    final var contextPath = tempDir.resolve("logisim_context.json");
    PythonContextRegistry.get().writeContextFile(contextPath);
    final var result = runScriptAndCapture(scriptPath.toFile(), outputFile, contextPath);
    return new ExecutionResult(result.exitCode(), result.output());
  }

  public ExecutionResult runScriptAndCapture(File scriptFile, File outputFile, Path contextPath)
      throws IOException, InterruptedException {
    if (!scriptFile.isFile()) {
      throw new IOException("Python script not found: " + scriptFile);
    }

    final var scriptDir = scriptFile.getParentFile();
    final var command = buildCommand(scriptFile, outputFile);
    logger.info("Running Python script with context: {}", contextPath);

    final var processBuilder = new ProcessBuilder(command);
    processBuilder.directory(scriptDir);
    processBuilder.redirectErrorStream(true);
    configureEnvironment(processBuilder.environment(), contextPath);
    final var process = processBuilder.start();

    final var output = new StringBuilder();
    try (var reader = process.inputReader()) {
      reader.lines().forEach(line -> output.append(line).append('\n'));
    }

    final var exitCode = process.waitFor();
    if (exitCode == 0 && outputFile != null && outputFile.exists()) {
      logger.info("Python script generated blueprint at {}", outputFile);
    }
    return new ExecutionResult(exitCode, output.toString());
  }

  private List<String> buildCommand(File scriptFile, File outputFile) {
    final var command = new ArrayList<String>();
    command.add(resolvePythonExecutable());
    command.add(scriptFile.getAbsolutePath());
    if (outputFile != null) {
      command.add("--output");
      command.add(outputFile.getAbsolutePath());
    }
    return command;
  }

  private void configureEnvironment(java.util.Map<String, String> environment) {
    configureEnvironment(environment, null);
  }

  private void configureEnvironment(java.util.Map<String, String> environment, Path contextPath) {
    final var pythonPath = resolvePythonPath();
    final var currentPath = environment.getOrDefault("PYTHONPATH", "");
    final var newPath = currentPath.isBlank() ? pythonPath : currentPath + File.pathSeparator + pythonPath;
    environment.put("PYTHONPATH", newPath);
    environment.put("PYTHON_EXECUTABLE", resolvePythonExecutable());
    if (contextPath != null) {
      environment.put("LOGISIM_CONTEXT_PATH", contextPath.toString());
    }
  }

  private String resolvePythonPath() {
    final var configuredPath = System.getProperty("logisim.python.path", "scripts/python");
    final var path = Path.of(configuredPath);
    if (path.isAbsolute()) {
      return path.normalize().toString();
    }
    return Path.of(System.getProperty("user.dir", ".")).resolve(path).normalize().toString();
  }

  private String resolvePythonExecutable() {
    return PythonRuntimeManager.get().getPythonExecutable();
  }
}

