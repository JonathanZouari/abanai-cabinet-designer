// Front view of the cabinet with drag & drop (mm). Streamlit calls this again on the SAME parentElement
// on every data change, without cleaning up first: so everything is rebuilt and handlers are
// attached as properties (onX), never addEventListener.
const NS = "http://www.w3.org/2000/svg";
const GAP = 2, EPS = 1e-6, DRAG_STEP = 5, KEY_STEP = 1, KEY_BIG = 10;
const ML = 46, MR = 14, MT = 26, MB = 28; // viewBox margins: height ruler on the left, width label below
const HEX = /^#[0-9a-f]{3,8}$/i;
const KINDS = ["shelf", "drawer", "door", "rod"];
const COLOR_KEYS = ["carcass", "back", "shelf", "drawer_front", "door", "rod"];

const fmt = (v) => String(Math.round(v * 10) / 10);
const snapTo = (z, step) => Math.round(z / step) * step;
const finite = (v) => typeof v === "number" && Number.isFinite(v);
const hasHeight = (k) => k === "drawer" || k === "door";

function el(tag, attrs, parent) {
  const n = document.createElementNS(NS, tag);
  for (const k in attrs) n.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(n);
  return n;
}

export default function ({ data, parentElement, setTriggerValue }) {
  let root = parentElement.querySelector(".fv-root");
  if (!root) {
    root = document.createElement("div");
    root.className = "fv-root";
    parentElement.appendChild(root);
  }
  root._send = setTriggerValue;
  if (root._st && root._st.drag) return; // mid-drag: don't replace the DOM under the pointer
  const items = (data.items || []).filter(
    (i) => Number.isInteger(i.index) && KINDS.includes(i.kind) && finite(i.col) && finite(i.z) &&
      (!hasHeight(i.kind) || (finite(i.h) && i.h > 0)),
  );
  root._st = { d: data, items: items.map((i) => ({ ...i })), sel: root._st ? root._st.sel : null, drag: null };
  render(root);
}

function render(root) {
  const st = root._st, { W, H, t } = st.d;
  const cw = st.d.col_widths, cols = Array.isArray(cw) ? cw.length : 0;
  if (![W, H, t, st.d.rod].every(finite) || cols < 1 || !cw.every((v) => finite(v) && v > 0)) return;
  const colors = {};
  for (const k of COLOR_KEYS) {
    const c = st.d.colors && st.d.colors[k];
    colors[k] = typeof c === "string" && HEX.test(c) ? c : "#c8a27a";
  }
  const xs = []; // left edge of each column, same as _col_x in cabinet.py
  for (let x = t, i = 0; i < cols; x += cw[i] + t, i++) xs.push(x);
  const s = Math.min(0.6, 600 / H, 520 / W);
  const VW = ML + W * s + MR, VH = MT + H * s + MB;
  const X = (x) => ML + x * s, Y = (z) => MT + (H - z) * s;
  const ih = (it) => (it.kind === "shelf" ? t : it.kind === "rod" ? st.d.rod : it.h);

  const clampTo = (it, c, z, step) => [
    Math.min(Math.max(Math.round(c), 1), cols),
    Math.min(Math.max(snapTo(z, step), t), Math.max(t, H - t - ih(it))),
  ];
  // doors cover other items by design, so only non-door items in the same column can collide
  const clashes = (it, c, z) => it.kind !== "door" &&
    st.items.some((o) => o !== it && o.kind !== "door" && o.col === c && z < o.z + ih(o) - EPS && o.z < z + ih(it) - EPS);

  const a = root.getRootNode().activeElement;
  const focusIdx = a && root.contains(a) ? a.getAttribute("data-index") : null;

  const svg = el("svg", { viewBox: `0 0 ${VW} ${VH}`, role: "group", "aria-label": "חזית הארון" });
  const rect = (x0, x1, z0, z1, cls, fill) =>
    el("rect", { x: X(x0), y: Y(z1), width: (x1 - x0) * s, height: (z1 - z0) * s, class: cls, fill }, svg);

  rect(t, W - t, t, H - t, "back", colors.back);
  for (let i = 0; i < cols - 1; i++) rect(xs[i] + cw[i], xs[i] + cw[i] + t, t, H - t, "edge", colors.carcass);
  rect(0, t, 0, H, "edge", colors.carcass);
  rect(W - t, W, 0, H, "edge", colors.carcass);
  rect(t, W - t, H - t, H, "edge", colors.carcass);
  rect(t, W - t, 0, t, "edge", colors.carcass);

  // height ruler: tick every 100 mm, number every 500
  const rule = el("g", { class: "rule" }, svg);
  el("line", { x1: ML - 8, x2: ML - 8, y1: Y(0), y2: Y(H) }, rule);
  for (let v = 0; v <= H; v += 100) {
    const big = v % 500 === 0;
    el("line", { x1: ML - 8 - (big ? 6 : 3), x2: ML - 8, y1: Y(v), y2: Y(v) }, rule);
    if (big) el("text", { x: ML - 17, y: Y(v) }, rule).textContent = String(v);
  }
  el("text", { class: "dim", x: X(W / 2), y: VH - 8 }, svg).textContent = fmt(W) + " מ\"מ";

  const place = (g, it, c, z) => {
    const x0 = xs[c - 1], w = cw[c - 1], h = ih(it), P = g._p;
    if (it.kind === "drawer") {
      P.body.setAttribute("x", X(x0 + GAP)); P.body.setAttribute("y", Y(z + h - GAP));
      P.body.setAttribute("width", (w - 2 * GAP) * s); P.body.setAttribute("height", (h - 2 * GAP) * s);
      const hz = z + h - Math.min(50, h / 2);
      P.handle.setAttribute("x", X(x0 + w / 2 - 60)); P.handle.setAttribute("y", Y(hz + 6));
      P.handle.setAttribute("width", 120 * s); P.handle.setAttribute("height", 12 * s);
    } else {
      P.body.setAttribute("x", X(x0)); P.body.setAttribute("y", Y(z + h));
      P.body.setAttribute("width", w * s); P.body.setAttribute("height", h * s);
    }
    const hh = Math.max(h * s, 16); // comfortable grab area even for a thin shelf
    P.hit.setAttribute("x", X(x0)); P.hit.setAttribute("width", w * s);
    P.hit.setAttribute("y", Y(z + h / 2) - hh / 2); P.hit.setAttribute("height", hh);
    P.del.setAttribute("transform", "translate(" + (X(x0 + w) - 12) + " " + Y(z + h / 2) + ")");
    const bad = clashes(it, c, z);
    P.lab.setAttribute("x", X(x0 + w / 2)); P.lab.setAttribute("y", Y(z + h) - 6);
    P.lab.textContent = bad ? "מתנגש (" + fmt(z) + ")" : fmt(z);
    g.classList.toggle("clash", bad);
    g.setAttribute("aria-label", it.label + ", עמודה " + c + ", גובה " + fmt(z) + " מ\"מ" + (bad ? ", מתנגש" : ""));
  };
  const select = (idx) => {
    st.sel = idx;
    svg.querySelectorAll(".item").forEach((n) => n.classList.toggle("sel", Number(n.getAttribute("data-index")) === idx));
  };
  const send = (kind, payload) => root._send && root._send(kind, payload);
  const colAt = (xmm) => { // column under the pointer; boundaries lie in the middle of each divider
    let c = 1;
    while (c < cols && xmm >= xs[c] - t / 2) c++;
    return c;
  };
  const toMm = (e) => {
    const p = svg.createSVGPoint();
    p.x = e.clientX; p.y = e.clientY;
    const q = p.matrixTransform(svg.getScreenCTM().inverse());
    return { x: (q.x - ML) / s, z: H - (q.y - MT) / s };
  };
  const removeItem = (it) => {
    send("delete", { index: it.index });
    st.items = st.items.filter((o) => o !== it);
    for (const o of st.items) if (o.index > it.index) o.index -= 1; // rows after the deleted one shift up
    st.sel = null;
    render(root);
  };

  // doors first so they sit behind shelves/drawers/rods, which therefore stay grabbable
  const order = [...st.items].sort((p, q) => (q.kind === "door") - (p.kind === "door"));
  for (const it of order) {
    const g = el("g", { class: "item " + it.kind, tabindex: "0", role: "button", "data-index": it.index }, svg);
    const hit = el("rect", { class: "hit" }, g);
    const body = el("rect", { class: "body", fill: colors[it.kind === "drawer" ? "drawer_front" : it.kind] }, g);
    const handle = it.kind === "drawer" ? el("rect", { class: "handle", fill: colors.rod }, g) : null;
    const del = el("g", { class: "del", role: "button", "aria-label": "מחיקת הרכיב" }, g);
    el("circle", { r: 8 }, del);
    el("text", {}, del).textContent = "×";
    const lab = el("text", { class: "lab" }, g);
    g._p = { hit, body, handle, del, lab };
    place(g, it, it.col, it.z);

    g.onfocus = () => select(it.index);
    g.onblur = (e) => { if (!st.rendering && !st.drag && !root.contains(e.relatedTarget)) select(null); };
    del.onpointerdown = (e) => { e.stopPropagation(); e.preventDefault(); };
    del.onclick = (e) => { e.stopPropagation(); removeItem(it); };

    g.onpointerdown = (e) => {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      e.preventDefault();
      e.stopPropagation(); // keep it from reaching the background (which clears the selection)
      g.setPointerCapture(e.pointerId);
      g.focus({ preventScroll: true });
      select(it.index);
      st.drag = { id: e.pointerId, dz: toMm(e).z - it.z, col: it.col, z: it.z };
      g.classList.add("drag");
    };
    g.onpointermove = (e) => {
      const d = st.drag;
      if (!d || d.id !== e.pointerId) return;
      const p = toMm(e);
      [d.col, d.z] = clampTo(it, colAt(p.x), p.z - d.dz, DRAG_STEP);
      place(g, it, d.col, d.z);
    };
    const finish = (e, commit) => {
      const d = st.drag;
      if (!d || d.id !== e.pointerId) return;
      st.drag = null;
      g.classList.remove("drag");
      if (commit && (d.col !== it.col || d.z !== it.z)) {
        it.col = d.col; it.z = d.z;
        send("move", { index: it.index, col: it.col, z: it.z });
        render(root);
      } else {
        place(g, it, it.col, it.z);
      }
    };
    g.onpointerup = (e) => finish(e, true);
    g.onpointercancel = (e) => finish(e, false);

    g.onkeydown = (e) => {
      const step = e.shiftKey ? KEY_BIG : KEY_STEP; // Shift = 10 mm, otherwise 1 mm
      let dc = 0, dz = 0;
      if (e.key === "ArrowUp") dz = step;
      else if (e.key === "ArrowDown") dz = -step;
      else if (e.key === "ArrowRight") dc = 1; // right on screen = higher column (x grows rightward)
      else if (e.key === "ArrowLeft") dc = -1;
      else if (e.key === "Delete" || e.key === "Backspace") { e.preventDefault(); removeItem(it); return; }
      else if (e.key === "Escape") { g.blur(); return; }
      else return;
      e.preventDefault();
      const [c, z] = clampTo(it, it.col + dc, it.z + dz, 1);
      if (c === it.col && z === it.z) return;
      it.col = c; it.z = z;
      send("move", { index: it.index, col: c, z });
      render(root);
    };
  }

  svg.onpointerdown = () => select(null); // clicking the background clears the selection
  st.rendering = true;
  root.replaceChildren(svg);
  st.rendering = false;
  select(st.sel);
  if (focusIdx !== null) {
    const f = svg.querySelector('.item[data-index="' + focusIdx + '"]');
    if (f) f.focus({ preventScroll: true });
  }
}
