import pytest

from cabinet import (DOOR, DRAWER, ROD, SHELF, apply_event, build_panels, clamp_move, cut_list,
                     default_col_widths, even_shelves, price)

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


@pytest.mark.parametrize("args, expected", [
    ((SHELF, 500.4, None, T, H, 2, 1.2), (1, 500)),        # snaps to 1 mm, col rounds
    ((SHELF, -50, None, T, H, 2, 9), (2, T)),              # below floor panel, col clamped
    ((SHELF, 5000, None, T, H, 2, 1), (1, H - 2 * T)),     # shelf top must stay <= H - t
    ((ROD, 5000, None, T, H, 1, 1), (1, H - T - 25)),      # rod is 25 mm tall
    ((DRAWER, 5000, 200, T, H, 1, 1), (1, H - T - 200)),
    ((DOOR, 0, H - 2 * T, T, H, 1, 0), (1, T)),            # full-height door can only sit at t
    ((DOOR, 500, 3000, T, H, 1, 1), (1, T)),               # taller than the cabinet: pinned to t
])
def test_clamp_move(args, expected):
    assert clamp_move(*args) == expected


@pytest.mark.parametrize("args", [
    (SHELF, float("nan"), None, T, H, 2, 1),
    (SHELF, float("inf"), None, T, H, 2, 1),
    (SHELF, True, None, T, H, 2, 1),
    (SHELF, "500", None, T, H, 2, 1),
    (SHELF, 500, None, T, H, 2, None),
    (SHELF, 500, None, T, H, 2, float("nan")),
    (DRAWER, 500, None, T, H, 2, 1),                       # missing height
    (DOOR, 500, 0, T, H, 2, 1),
    (DRAWER, 500, float("nan"), T, H, 2, 1),
    ("x", 500, 100, T, H, 2, 1),
])
def test_clamp_move_invalid(args):
    assert clamp_move(*args) is None


ROWS = [
    {"col": 1, "type": SHELF, "z": 300, "height": None},
    {"col": 2, "type": DRAWER, "z": T, "height": 200},
    {"col": 2, "type": DOOR, "z": T, "height": 900},
]


def event(kind, payload):
    return apply_event(ROWS, kind, payload, T, H, 2)


def test_apply_move_changes_only_target_row():
    out = event("move", {"index": 1, "col": 1, "z": 703.2})
    assert out[1] == {"col": 1, "type": DRAWER, "z": 703, "height": 200}
    assert out[0] == ROWS[0] and out[2] == ROWS[2]


def test_apply_move_clamps_and_accepts_integer_float_index():
    assert event("move", {"index": 2.0, "col": 5, "z": 9999})[2]["z"] == H - T - 900
    assert event("move", {"index": 2.0, "col": 5, "z": 9999})[2]["col"] == 2


def test_apply_delete_removes_row_and_keeps_order():
    assert event("delete", {"index": 1}) == [ROWS[0], ROWS[2]]


def test_apply_does_not_mutate_input():
    before = [dict(r) for r in ROWS]
    event("move", {"index": 0, "col": 2, "z": 100})
    event("delete", {"index": 0})
    assert ROWS == before


@pytest.mark.parametrize("kind, payload", [
    ("move", {"index": True, "col": 1, "z": 100}),
    ("move", {"index": 1.5, "col": 1, "z": 100}),
    ("move", {"index": 3, "col": 1, "z": 100}),
    ("move", {"index": -1, "col": 1, "z": 100}),
    ("move", {"index": "1", "col": 1, "z": 100}),
    ("move", {"col": 1, "z": 100}),
    ("move", {"index": 0, "col": 1, "z": float("nan")}),
    ("move", {"index": 0, "col": 1, "z": "100"}),
    ("delete", {"index": 9}),
    ("delete", {"index": True}),
    ("resize", {"index": 0}),
    ("move", None),
    ("move", [0, 1, 100]),
])
def test_apply_event_invalid_returns_none(kind, payload):
    assert event(kind, payload) is None


def test_apply_move_on_row_with_invalid_cells_is_ignored():
    rows = [{"col": None, "type": DRAWER, "z": None, "height": None}]
    assert apply_event(rows, "move", {"index": 0, "col": 1, "z": 100}, T, H, 2) is None
    assert apply_event(rows, "delete", {"index": 0}, T, H, 2) == []
