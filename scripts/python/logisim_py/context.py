import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class RuntimeContext:
    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:
        self.data = data or {}

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.data)


def resolve_context_path(path: Optional[str | Path] = None) -> Optional[Path]:
    if path is None:
        env_path = os.getenv("LOGISIM_CONTEXT_PATH")
        if not env_path:
            return None
        path = env_path
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = Path.cwd() / resolved
    return resolved


def load_context(path: Optional[str | Path] = None) -> RuntimeContext:
    resolved = resolve_context_path(path)
    if resolved is None or not resolved.exists():
        return RuntimeContext({})
    with resolved.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return RuntimeContext(data)


def get_context(path: Optional[str | Path] = None) -> Dict[str, Any]:
    return load_context(path).to_dict()


def get_context_summary(path: Optional[str | Path] = None) -> str:
    context = load_context(path)
    project = context.get("project", {})
    circuit = context.get("circuit", {})
    selected = context.get("selected_components", [])
    project_name = project.get("name", "none") if isinstance(project, dict) else "none"
    circuit_name = circuit.get("name", "none") if isinstance(circuit, dict) else "none"
    selection_count = len(selected) if isinstance(selected, list) else 0
    return f"project={project_name}; circuit={circuit_name}; selected={selection_count}"
