import pytest

from cabinet import (DOOR, DRAWER, ROD, SHELF, build_panels, cut_list, default_col_widths,
                     even_shelves, price, resolve_col_widths)

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


def test_resolve_no_overrides_equals_default():
    assert resolve_col_widths(W, T, 3, {}) == default_col_widths(W, T, 3)


def test_resolve_one_override_splits_rest():
    w = resolve_col_widths(W, T, 3, {2: 300})
    inner = W - 2 * T - 2 * T
    assert w[1] == 300 and w[0] == w[2] == (inner - 300) / 2 and sum(w) == pytest.approx(inner)


def test_resolve_ignores_out_of_range_key():
    assert resolve_col_widths(W, T, 2, {5: 100, 0: 50}) == default_col_widths(W, T, 2)


def test_resolve_all_overridden_as_is():
    assert resolve_col_widths(W, T, 2, {1: 400, 2: 500}) == [400, 500]


def test_resolve_feeds_build_panels():
    assert build_panels(W, H, D, T, B, resolve_col_widths(W, T, 3, {1: 200}), [])
