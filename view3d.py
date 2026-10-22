"""Render cabinet panels as a rotatable plotly 3D figure."""
import plotly.graph_objects as go

COLORS = {
    "carcass": "#c8a27a", "back": "#8b6b4a", "shelf": "#e0c097",
    "drawer_front": "#6b8fb3", "drawer_box": "#b0c4d8", "door": "#9fb89a", "rod": "#555555",
}
LABELS = {
    "carcass": "גוף", "back": "גב", "shelf": "מדפים", "drawer_front": "חזיתות מגירה",
    "drawer_box": "תיבות מגירה", "door": "דלתות", "rod": "מוטות",
}
# Unit cube vertices + triangles (plotly docs ordering).
CX, CY, CZ = [0, 0, 1, 1, 0, 0, 1, 1], [0, 1, 1, 0, 0, 1, 1, 0], [0, 0, 0, 0, 1, 1, 1, 1]
TI = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
TJ = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
TK = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]


def mesh(group, color, name, opacity=1):
    x, y, z, i, j, k = [], [], [], [], [], []
    for n, p in enumerate(group):
        x += [p.x + c * p.w for c in CX]
        y += [p.y + c * p.d for c in CY]
        z += [p.z + c * p.h for c in CZ]
        i += [v + 8 * n for v in TI]
        j += [v + 8 * n for v in TJ]
        k += [v + 8 * n for v in TK]
    return go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color=color, flatshading=True, opacity=opacity,
                     name=name, showlegend=True, hoverinfo="name")


def figure(panels, show_doors=True, changed=frozenset()):
    fig = go.Figure()
    for kind, color in COLORS.items():
        group = [p for p in panels if p.kind == kind and p not in changed]
        if kind in ("door", "drawer_front") and not show_doors:
            continue
        if group:
            fig.add_trace(mesh(group, color, LABELS[kind], 0.7 if kind == "door" else 1))
    red = [p for p in panels if p in changed and (show_doors or p.kind not in ("door", "drawer_front"))]
    if red:
        fig.add_trace(mesh(red, "#e53935", "שינוי ממתין לאישור"))
    fig.update_layout(
        scene=dict(aspectmode="data", xaxis_title="רוחב", yaxis_title="עומק", zaxis_title="גובה",
                   camera=dict(eye=dict(x=0.6, y=-1.8, z=0.6))),
        margin=dict(l=0, r=0, t=0, b=0), height=650,
    )
    return fig
