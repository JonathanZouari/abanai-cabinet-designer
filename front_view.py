"""Interactive (draggable) front view as a Streamlit v2 component. The HTML/CSS/JS are fixed files;
user data reaches the browser only as `data` (JSON) and comes back only as validated events."""
import math
from pathlib import Path

import streamlit as st

from cabinet import DOOR, DRAWER, ROD, ROD_SIZE, SHELF

_DIR = Path(__file__).parent
_component = st.components.v2.component(
    "front_view",
    html='<div class="fv-root"></div>',
    css=(_DIR / "front_view.css").read_text(encoding="utf-8"),
    js=(_DIR / "front_view.js").read_text(encoding="utf-8"),
)
_KINDS = {SHELF: "shelf", DRAWER: "drawer", DOOR: "door", ROD: "rod"}


def front_view(W, H, t, col_widths, rows, colors, key="front"):
    """Render the front view. Returns ("move"|"delete", payload) when the user acted, else None.

    rows: ALL table rows as dicts {col, type, z, height}, in table order. Rows with invalid cells are
    not drawn, but `index` stays the row position so events map back to the right row.
    """
    items = []
    for i, r in enumerate(rows):
        kind = _KINDS.get(r["type"])
        try:
            col, z = int(r["col"]), float(r["z"])
            h = float(r["height"]) if kind in ("drawer", "door") else None
        except (TypeError, ValueError):
            continue
        if kind is None or not 1 <= col <= len(col_widths) or not math.isfinite(z):
            continue
        if kind in ("drawer", "door") and not (math.isfinite(h) and h > 0):
            continue
        items.append({"index": i, "kind": kind, "label": r["type"], "col": col, "z": z, "h": h})
    res = _component(
        key=key,
        data={"W": float(W), "H": float(H), "t": float(t), "col_widths": [float(w) for w in col_widths],
              "rod": ROD_SIZE, "items": items, "colors": dict(colors)},
        on_move_change=lambda: None,
        on_delete_change=lambda: None,
    )
    for kind in ("move", "delete"):
        if res.get(kind) is not None:
            return kind, res[kind]
    return None
