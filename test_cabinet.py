import pytest

from cabinet import (PRESETS, default_items, DOOR, DRAWER, ROD, SHELF, build_panels, cut_list, default_col_widths,
                     even_shelves, price)
from view3d import COLORS, FINISHES, LABELS, figure

W, H, D, T, B = 1000, 2000, 600, 18, 8


def build(n_cols=1, items=()):
    return build_panels(W, H, D, T, B, default_col_widths(W, T, n_cols), list(items))


def test_empty_cabinet_is_carcass_plus_back():
    panels = build()
    assert sorted(p.name for p in panels) == sorted(["דופן", "דופן", "תחתית", "תקרה", "גב"])
    top = next(p for p in panels if p.name == "תקרה")
    assert (top.w, top.d, top.h) == (W - 2 * T, D - B, T)


def test_dividers_per_column_count():
    assert sum(p.name == "מחיצה" for p in build(3)) == 2


def test_shelf_width_matches_column():
    widths = default_col_widths(W, T, 2)
    shelf = [p for p in build(2, [{"col": 2, "type": SHELF, "z": 500, "height": None}]) if p.kind == "shelf"]
    assert len(shelf) == 1 and shelf[0].w == widths[1] and shelf[0].x == T + widths[0] + T


def test_drawer_has_front_and_box():
    names = [p.name for p in build(items=[{"col": 1, "type": DRAWER, "z": 100, "height": 200}])]
    assert names.count("חזית מגירה") == 1 and names.count("צד מגירה") == 2
    assert "גב מגירה" in names and "תחתית מגירה" in names


def test_rod_not_in_cut_list():
    panels = build(items=[{"col": 1, "type": ROD, "z": 1700, "height": None}])
    assert any(p.kind == "rod" for p in panels)
    assert "מוט תלייה" not in set(cut_list(panels)["שם"])


def test_cut_list_groups_identical():
    df = cut_list(build())
    assert df.loc[df["שם"] == "דופן", "כמות"].item() == 2


def test_price():
    panels = build(items=[{"col": 1, "type": DOOR, "z": T, "height": H - 2 * T}])
    r = price(panels, price_m2_board=100, price_m2_back=10, drawer_rail=0, hinge_per_door=30)
    assert r["back_m2"] == pytest.approx(W * H / 1e6)
    assert r["hardware"] == 30
    assert r["total"] == pytest.approx(r["board_m2"] * 100 + r["back_m2"] * 10 + 30)


@pytest.mark.parametrize("item", [
    {"col": 1, "type": SHELF, "z": H, "height": None},
    {"col": 5, "type": SHELF, "z": 500, "height": None},
    {"col": 1, "type": DRAWER, "z": 100, "height": None},
])
def test_invalid_item_raises(item):
    with pytest.raises(ValueError):
        build(items=[item])


def test_bad_col_widths_raise():
    with pytest.raises(ValueError):
        build_panels(W, H, D, T, B, [400, 400], [])


def test_even_shelves_equal_gaps():
    zs = even_shelves(H, T, 3)
    edges = [T] + [e for z in zs for e in (z, z + T)] + [H - T]
    gaps = [edges[i + 1] - edges[i] for i in range(0, len(edges), 2)]
    assert gaps == pytest.approx([gaps[0]] * 4)


@pytest.mark.parametrize("name", list(FINISHES))
def test_finish_colors_carcass_only(name):
    panels = build(items=[{"col": 1, "type": DOOR, "z": T, "height": 500},
                          {"col": 1, "type": DRAWER, "z": 600, "height": 200}])
    color = {t.name: t.color for t in figure(panels, finish=name).data}
    assert color[LABELS["carcass"]] == FINISHES[name]["carcass"]
    assert color[LABELS["back"]] == COLORS["back"]


def test_turntable_drag():
    assert figure(build()).layout.scene.dragmode == "turntable"


def _items(kind, H, n_cols):
    return [dict(zip(("col", "type", "z", "height"), r)) for r in default_items(kind, H, T, n_cols)]


def test_dresser_preset():
    assert ROD not in PRESETS["שידה"]["types"] and PRESETS["שידה"]["H"][1] == 1200


@pytest.mark.parametrize("kind", list(PRESETS))
def test_default_items_build(kind):
    p = PRESETS[kind]
    build_panels(1000, p["H"][2], 600, T, B, default_col_widths(1000, T, p["cols"]),
                 _items(kind, p["H"][2], p["cols"]), p["types"])


def test_dresser_defaults_four_drawers_per_column():
    items = _items("שידה", 800, 2)
    assert {i["type"] for i in items} == {DRAWER} and len(items) == 8
    col1 = [i for i in items if i["col"] == 1]
    assert len(col1) == 4 and col1[-1]["z"] + col1[-1]["height"] == pytest.approx(800 - T, abs=0.5)


def test_wardrobe_defaults_have_rod():
    assert any(i["type"] == ROD and i["z"] == 1700 for i in _items("ארון", 2000, 2))


def test_disallowed_type_raises():
    with pytest.raises(ValueError):
        build_panels(W, H, D, T, B, default_col_widths(W, T, 1),
                     [{"col": 1, "type": ROD, "z": 1700, "height": None}], [SHELF, DRAWER, DOOR])


@pytest.mark.parametrize("h", range(300, 1201))
def test_dresser_defaults_build_at_every_height(h):
    build_panels(1000, h, 450, T, B, default_col_widths(1000, T, 2), _items("שידה", h, 2),
                 PRESETS["שידה"]["types"])
