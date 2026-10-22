"""Render cabinet panels as a rotatable plotly 3D figure and assembly booklet."""
import html

import plotly.graph_objects as go

from cabinet import step_parts

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
EDGES = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
GHOST = "#e6e6e6"


def _meshes(panels, show_doors=True, opacity=None, color=None, legend=True):
    traces = []
    for kind, kcolor in COLORS.items():
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
        traces.append(go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color=color or kcolor, flatshading=True,
                                opacity=opacity or (0.7 if kind == "door" else 1), name=LABELS[kind],
                                showlegend=legend, hoverinfo="name"))
    return traces


def _edges(panels, color="#222222", width=2):
    x, y, z = [], [], []
    for p in panels:
        for a, b in EDGES:
            for v in (a, b):
                x.append(p.x + CX[v] * p.w)
                y.append(p.y + CY[v] * p.d)
                z.append(p.z + CZ[v] * p.h)
            x.append(None), y.append(None), z.append(None)
    return go.Scatter3d(x=x, y=y, z=z, mode="lines", line=dict(color=color, width=width),
                        showlegend=False, hoverinfo="skip")


def _layout(fig, height):
    fig.update_layout(
        scene=dict(aspectmode="data", xaxis_title="רוחב", yaxis_title="עומק", zaxis_title="גובה",
                   camera=dict(eye=dict(x=0.6, y=-1.8, z=0.6))),
        margin=dict(l=0, r=0, t=0, b=0), height=height,
    )
    return fig


def figure(panels, show_doors=True):
    fig = go.Figure(_meshes(panels, show_doors))
    return _layout(fig, 650)


def step_figure(done, new):
    fig = go.Figure([*_meshes(done, color=GHOST, opacity=0.35, legend=False), _edges(done, "#aaaaaa", 1),
                     *_meshes(new, legend=False), _edges(new)])
    _layout(fig, 550)
    fig.update_layout(showlegend=False, scene_bgcolor="white", paper_bgcolor="white")
    return fig


def assembly_html(steps, title):
    css = ("body{font-family:Arial,sans-serif;background:#fff;color:#000;max-width:900px;margin:0 auto;padding:24px}"
           "h1{border-bottom:3px solid #000;padding-bottom:8px}.step{margin:40px 0;page-break-inside:avoid}"
           ".num{display:inline-block;width:56px;height:56px;line-height:56px;border:3px solid #000;"
           "border-radius:50%;text-align:center;font-size:30px;font-weight:bold;margin-left:14px}"
           "h2{display:flex;align-items:center;font-size:28px;margin:0 0 12px}"
           "table{border-collapse:collapse;margin:8px 0}td,th{border:1px solid #bbb;padding:4px 10px}")
    body, done = [], []
    for n, s in enumerate(steps, 1):
        hw = "".join(f"<li>{html.escape(str(k))}: {html.escape(str(v))}</li>" for k, v in s["hardware"].items())
        fig = step_figure(done, s["panels"]).to_html(full_html=False, include_plotlyjs="cdn" if n == 1 else False)
        body.append(f'<div class="step"><h2><span class="num">{n}</span>{html.escape(s["title"])}</h2>'
                    f'<p>{html.escape(s["text"])}</p><h3>פרזול</h3><ul>{hw}</ul><h3>חלקים</h3>'
                    f'{step_parts(s).to_html(index=False)}{fig}</div>')
        done = done + s["panels"]
    t = html.escape(title)
    return (f'<!DOCTYPE html><html dir="rtl" lang="he"><head><meta charset="utf-8"><title>{t}</title>'
            f'<style>{css}</style></head><body><h1>{t}</h1>{"".join(body)}</body></html>')
