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


def figure(panels, show_doors=True, carcass_color=None):
    fig = go.Figure()
    colors = {**COLORS, "carcass": carcass_color or COLORS["carcass"]}
    for kind, color in colors.items():
        group = [p for p in panels if p.kind == kind]
        if kind in ("door", "drawer_front") and not show_doors:
            continue
        if not group:
            continue
        x, y, z, i, j, k = [], [], [], [], [], []
        for n, p in enumerate(group):
            x += [p.x + c * p.w for c in CX]
            y += [p.y + c * p.d for c in CY]
            z += [p.z + c * p.h for c in CZ]
            i += [v + 8 * n for v in TI]
            j += [v + 8 * n for v in TJ]
            k += [v + 8 * n for v in TK]
        fig.add_trace(go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color=color, flatshading=True,
                                opacity=0.7 if kind == "door" else 1, name=LABELS[kind],
                                showlegend=True, hoverinfo="name"))
    fig.update_layout(
        scene=dict(aspectmode="data", xaxis_title="רוחב", yaxis_title="עומק", zaxis_title="גובה",
                   camera=dict(eye=dict(x=0.6, y=-1.8, z=0.6))),
        margin=dict(l=0, r=0, t=0, b=0), height=650,
    )
    return fig
