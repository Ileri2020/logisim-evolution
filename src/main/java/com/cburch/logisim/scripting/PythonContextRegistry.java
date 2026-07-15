package com.cburch.logisim.scripting;

import com.cburch.logisim.comp.Component;
import com.cburch.logisim.gui.main.Frame;
import com.cburch.logisim.proj.Project;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public final class PythonContextRegistry {
  private static final PythonContextRegistry INSTANCE = new PythonContextRegistry();

  private volatile Project project;
  private volatile Frame frame;

  private PythonContextRegistry() {}

  public static PythonContextRegistry get() {
    return INSTANCE;
  }

  public void bind(Project project, Frame frame) {
    this.project = project;
    this.frame = frame;
  }

  public void writeContextFile(Path outputPath) throws IOException {
    if (outputPath == null) {
      return;
    }
    Files.writeString(outputPath, toJson(), StandardCharsets.UTF_8);
  }

  public String toJson() {
    return toJson(snapshot());
  }

  public Map<String, Object> snapshot() {
    final var data = new LinkedHashMap<String, Object>();
    data.put("project", buildProjectData());
    data.put("circuit", buildCircuitData());
    data.put("selected_components", buildSelectionData());
    data.put("active_tool", buildToolData());
    return data;
  }

  private Map<String, Object> buildProjectData() {
    final var projectData = new LinkedHashMap<String, Object>();
    projectData.put("name", project != null ? "active-project" : "none");
    projectData.put("has_frame", frame != null);
    projectData.put("has_circuit", project != null && project.getCurrentCircuit() != null);
    return projectData;
  }

  private Map<String, Object> buildCircuitData() {
    final var circuitData = new LinkedHashMap<String, Object>();
    if (project != null && project.getCurrentCircuit() != null) {
      final var circuit = project.getCurrentCircuit();
      circuitData.put("name", circuit.getName());
      circuitData.put("component_count", circuit.getNonWires().size());
    } else {
      circuitData.put("name", "none");
      circuitData.put("component_count", 0);
    }
    return circuitData;
  }

  private List<String> buildSelectionData() {
    if (frame == null || frame.getCanvas() == null) {
      return List.of();
    }
    final var selection = frame.getCanvas().getSelection();
    if (selection == null || selection.isEmpty()) {
      return List.of();
    }
    return selection.getComponents().stream().map(this::describeComponent).toList();
  }

  private String buildToolData() {
    if (project == null || project.getTool() == null) {
      return "none";
    }
    return project.getTool().getName();
  }

  private String describeComponent(Component component) {
    return component == null ? "<null>" : component.getFactory().getName();
  }

  private String toJson(Object value) {
    if (value == null) {
      return "null";
    }
    if (value instanceof String text) {
      return '"' + escape(text) + '"';
    }
    if (value instanceof Number || value instanceof Boolean) {
      return value.toString();
    }
    if (value instanceof Map<?, ?> map) {
      final var builder = new StringBuilder("{");
      var first = true;
      for (final var entry : map.entrySet()) {
        if (!first) {
          builder.append(',');
        }
        first = false;
        builder.append('"').append(escape(String.valueOf(entry.getKey()))).append('"').append(':').append(toJson(entry.getValue()));
      }
      builder.append('}');
      return builder.toString();
    }
    if (value instanceof Iterable<?> iterable) {
      final var builder = new StringBuilder("[");
      var first = true;
      for (final var item : iterable) {
        if (!first) {
          builder.append(',');
        }
        first = false;
        builder.append(toJson(item));
      }
      builder.append(']');
      return builder.toString();
    }
    return '"' + escape(String.valueOf(value)) + '"';
  }

  private String escape(String text) {
    return text.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", "\\n");
  }
}
