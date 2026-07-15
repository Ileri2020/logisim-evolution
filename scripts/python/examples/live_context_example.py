"""
live_context_example.py
=======================
Demonstrates querying the live Logisim runtime from embedded Python.

When run inside the Logisim GraalPy interpreter (via the Python Console
tab), this script reads the current project state through `logisim.context`
and lists all components currently placed on the active circuit via
`logisim.ops.list_components()`.

When run as a standalone offline script, it falls back to printing a
summary from the JSON context file (if LOGISIM_CONTEXT_PATH is set).

Usage (embedded, from the Python Console panel):
    Run this script using the "Run" button in the Python tab.

Usage (offline):
    python live_context_example.py
"""

import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from logisim_py import get_context_summary

def _is_embedded() -> bool:
    try:
        return logisim is not None  # noqa: F821
    except NameError:
        return False


def run():
    print("=" * 60)
    print("  Logisim-evolution  –  Live Context Inspector")
    print("=" * 60)

    # ── Offline mode: JSON context summary ────────────────────────────────
    print("\n[context summary]")
    print(get_context_summary())

    if not _is_embedded():
        print("\n[note] Running offline – connect via the Python Console tab")
        print("       for live component introspection.")
        return

    # ── Embedded mode: query live Java objects ────────────────────────────
    ctx = logisim.context  # noqa: F821
    ops = logisim.ops      # noqa: F821

    print(f"\n[project]  circuit = '{ctx.circuit_name()}'")
    print(f"           component count = {ctx.component_count()}")
    print(f"           active tool     = {ctx.active_tool()}")

    print("\n[components on canvas]")
    comps = ops.list_components()
    if not comps:
        print("  (none — add some components first)")
    else:
        for i, c in enumerate(comps, 1):
            print(f"  {i:3d}.  {c}")

    print("\n[selected components]")
    sel = ctx.selected_components() if hasattr(ctx, "selected_components") else []
    if not sel:
        print("  (nothing selected)")
    else:
        for s in sel:
            print(f"  • {s}")

    print("\n[attribute inspection – first component]")
    if comps:
        first_label = comps[0].split(" (")[0]   # strip factory name
        attrs = ops.get_component_attributes(first_label)
        if attrs:
            for k, v in attrs.items():
                print(f"  {k:20s} = {v}")
        else:
            print(f"  (no attributes found for '{first_label}')")

    print("\n" + "=" * 60)


run()
