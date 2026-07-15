import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py.builder import BlueprintBuilder


def build_example(name: str, output: Path) -> None:
    builder = BlueprintBuilder(name)
    builder.add_gate("and", "and0")
    builder.add_counter("cnt0")
    builder.add_wire("w0", "and0.out", "cnt0.in")
    builder.save(output)
    print(f"wrote {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Logisim blueprint from Python")
    parser.add_argument("--name", default="generated_circuit")
    parser.add_argument("--output", default=str(ROOT / "generated_blueprint.json"))
    args = parser.parse_args()
    build_example(args.name, Path(args.output))
