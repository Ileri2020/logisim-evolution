# Python scripting support for Logisim

This folder contains a lightweight Python API for describing circuits in a Blender-like scripting style.

## Layout
- `logisim_py/` - Python package providing circuit objects, a builder helper, and JSON serialization.
- `examples/` - Example scripts that create simple circuits.
- `run_example.py` - Convenience script for generating a blueprint through the local Python runtime.

## Quick start--

```powershell
python scripts/python/run_example.py --name demo --output scripts/python/generated_blueprint.json
```

You can also run one of the bundled example scripts:

```powershell
python scripts/python/examples/simple_counter.py
python scripts/python/examples/advanced_counter.py
```
