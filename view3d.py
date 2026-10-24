"""Render cabinet panels as a rotatable plotly 3D figure."""
import plotly.graph_objects as go

COLORS = {
    "carcass": "#EDE6DA", "back": "#D9CCB8", "shelf": "#E3D5BE",
    "drawer_front": "#F4F4F4", "drawer_box": "#CFC6B8", "door": "#FFFFFF", "rod": "#8A8A8A",
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
                                opacity=0.85 if kind == "door" else 1,
                                lighting=dict(ambient=0.6, diffuse=0.8, specular=0.1), name=LABELS[kind],
                                showlegend=True, hoverinfo="name"))
    ax = dict(showbackground=False, showgrid=True, gridcolor="#E4E4E4", zeroline=False, showline=False)
    fig.update_layout(
        scene=dict(aspectmode="data", xaxis_title="רוחב", yaxis_title="עומק", zaxis_title="גובה",
                   xaxis=ax, yaxis=ax, zaxis=ax, bgcolor="#F5F5F5",
                   camera=dict(eye=dict(x=0.6, y=-1.8, z=0.6))),
        paper_bgcolor="#F5F5F5", plot_bgcolor="#F5F5F5",
        font=dict(family="Noto Sans Hebrew, sans-serif", color="#111111"),
        legend=dict(orientation="h", yanchor="bottom", y=0, xanchor="center", x=0.5),
        margin=dict(l=0, r=0, t=0, b=0), height=650,
    )
    return fig
