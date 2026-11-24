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


def figure(panels, show_doors=True):
    fig = go.Figure()
    for kind, color in COLORS.items():
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
    body = [p for p in panels if p.kind not in ("door", "drawer_front")]
    x0, x1 = min(p.x for p in body), max(p.x + p.w for p in body)
    y0, y1 = min(p.y for p in body), max(p.y + p.d for p in body)
    z0, z1 = min(p.z for p in body), max(p.z + p.h for p in body)
    span = max(x1 - x0, y1 - y0, z1 - z0)
    fig.add_trace(go.Scatter3d(
        x=[(x0 + x1) / 2, x0 - 0.12 * span, x1 + 0.05 * span],
        y=[y0 - 0.12 * span, y0, (y0 + y1) / 2],
        z=[z0 - 0.03 * span, (z0 + z1) / 2, z0],
        mode="text", text=[f'רוחב {x1 - x0:.0f} מ"מ', f'גובה {z1 - z0:.0f} מ"מ', f'עומק {y1 - y0:.0f} מ"מ'],
        textfont=dict(size=13, color="#222"),
        textposition=["bottom center", "middle left", "bottom center"],  # grow away from the body
        showlegend=False, hoverinfo="skip"))
    axis = dict(showbackground=False, gridcolor="#e5e5e5", showticklabels=False, zeroline=False, title="")
    fig.update_layout(
        scene=dict(aspectmode="data", camera=dict(eye=dict(x=1.3, y=-2.4, z=1.0)),
                   xaxis=axis, yaxis=axis, zaxis=axis),
        legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="center", x=0.5),
        paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=0, b=0), height=600,
    )
    return fig
