"""Cabinet geometry, cut list and price. Pure logic, no Streamlit.

Axes (mm): x = width (left->right), y = depth (front=0 -> back), z = height (floor=0).
"""
from dataclasses import dataclass
import math

import pandas as pd

SHELF, DRAWER, DOOR, ROD = "מדף", "מגירה", "דלת", "מוט תלייה"
ITEM_TYPES = [SHELF, DRAWER, DOOR, ROD]

NEEDS = ["עמידות ללחות", "עומס כבד", "תקציב נמוך", "מראה עץ טבעי", "גימור צבע",
         "עמידות לשריטות ושימוש אינטנסיבי"]


def _w(pros, cons, *scores):
    return {"pros": pros, "cons": cons, "scores": dict(zip(NEEDS, scores))}


# scores per NEEDS order: 3 = fits well, 2 = OK, 1 = poor
WOODS = {
    "סנדוויץ' (לבידי)": _w(
        ["חזק וקל יחסית", "עמיד סביר ללחות", "מחזיק ברגים היטב"],
        ["מחיר בינוני-גבוה", "קצוות שכבות גלויים", "איכות משתנה בין יצרנים"], 2, 3, 2, 2, 2, 2),
    "MDF": _w(
        ["משטח חלק מושלם לצבע", "מחיר נוח", "יציב, בלי פיתולים"],
        ["מתנפח במגע עם מים", "כבד", "אין מראה עץ", "מחזיק ברגים פחות טוב"], 1, 2, 3, 1, 3, 2),
    "MDF עמיד מים (ירוק)": _w(
        ["עמיד ללחות יותר מ-MDF רגיל", "משטח חלק לצבע", "מתאים למטבח ושירותים"],
        ["יקר מ-MDF רגיל", "כבד", "אין מראה עץ"], 3, 2, 2, 1, 3, 2),
    "סיבית מצופה מלמין": _w(
        ["זול", "מגיע מצופה בצבעים ודוגמאות", "קל לניקוי"],
        ["רגיש ללחות בקצוות", "נכנע תחת עומס על מדפים ארוכים", "אי אפשר לצבוע", "קצוות פגיעים"],
        1, 1, 3, 2, 1, 2),
    "אורן מלא": _w(
        ["עץ אמיתי במחיר סביר", "קל לעיבוד", "ניתן לצבוע או להשחין"],
        ["רך ונשרט בקלות", "נוטה לתזוזה ולעיוות", "בעל סיבים וקשרים"], 1, 2, 2, 3, 2, 1),
    "אלון מלא": _w(
        ["חזק וקשה מאוד", "מראה עץ יפה ועמיד", "עמיד לשריטות ולשימוש רב"],
        ["יקר", "כבד", "קשה יותר לעיבוד"], 2, 3, 1, 3, 2, 3),
    "אגוז אמריקאי מלא": _w(
        ["גוון כהה ויוקרתי", "חזק ויציב", "מראה עץ טבעי מרשים"],
        ["יקר מאוד", "לא מתאים לצביעה", "רך מאלון, נשרט יותר"], 2, 3, 1, 3, 1, 2),
}


def wood_tips(wood, needs):
    if wood not in WOODS:
        raise ValueError(f"סוג עץ לא מוכר: {wood}")
    tips = []
    for need in needs:
        if need not in NEEDS:
            raise ValueError(f"דרישה לא מוכרת: {need}")
        score = WOODS[wood]["scores"][need]
        best = ", ".join(w for w, d in WOODS.items() if w != wood and d["scores"][need] == 3)
        if score == 1:
            tips.append(f"⚠️ {wood} פחות מתאים ל{need}. עדיף: {best}")
        elif score == 2:
            tips.append(f"ℹ️ {wood} סביר ל{need}" + (f", אבל {best} יתאים יותר" if best else ""))
        else:
            tips.append(f"✅ {wood} מתאים מאוד ל{need}")
    if "עומס כבד" in needs:
        tips.append("💡 מדף ארוך מ-800 מ\"מ דורש תמיכה אמצעית/מחיצה או לוח עבה יותר")
    return tips


RAIL_GAP = 13      # side clearance per drawer rail, mm
DRAWER_BACK_GAP = 20  # clearance between drawer box and cabinet back, mm
ROD_SIZE = 25


@dataclass(frozen=True)
class Panel:
    name: str
    x: float
    y: float
    z: float
    w: float  # along x
    d: float  # along y
    h: float  # along z
    kind: str  # carcass/shelf/drawer_front/drawer_box/door/back/rod
    material: str  # board/back/none


def even_shelves(height, t, n):
    """Bottom-face heights of n shelves evenly spaced inside the carcass."""
    gap = (height - 2 * t - n * t) / (n + 1)
    return [t + i * gap + (i - 1) * t for i in range(1, n + 1)]


def default_col_widths(width, t, n):
    return [(width - 2 * t - (n - 1) * t) / n] * n


def _carcass(W, H, D, t, back_t, col_widths):
    panels = [
        Panel("דופן", 0, 0, 0, t, D, H, "carcass", "board"),
        Panel("דופן", W - t, 0, 0, t, D, H, "carcass", "board"),
        Panel("תחתית", t, 0, 0, W - 2 * t, D, t, "carcass", "board"),
        Panel("תקרה", t, 0, H - t, W - 2 * t, D, t, "carcass", "board"),
        Panel("גב", 0, D, 0, W, back_t, H, "back", "back"),
    ]
    x = t
    for w in col_widths[:-1]:
        x += w
        panels.append(Panel("מחיצה", x, 0, t, t, D, H - 2 * t, "carcass", "board"))
        x += t
    return panels


def _col_x(t, col_widths):
    xs, x = [], t
    for w in col_widths:
        xs.append(x)
        x += w + t
    return xs


def _drawer(cx, cw, z, h, D, t, back_t):
    box_w, box_d, box_h = cw - 2 * RAIL_GAP, D - DRAWER_BACK_GAP, h - 40
    bx = cx + RAIL_GAP
    return [
        Panel("חזית מגירה", cx, -t, z, cw, t, h, "drawer_front", "board"),
        Panel("צד מגירה", bx, 0, z + 10, t, box_d, box_h, "drawer_box", "board"),
        Panel("צד מגירה", bx + box_w - t, 0, z + 10, t, box_d, box_h, "drawer_box", "board"),
        Panel("גב מגירה", bx + t, box_d - t, z + 10, box_w - 2 * t, t, box_h, "drawer_box", "board"),
        Panel("תחתית מגירה", bx, 0, z + 10, box_w, box_d, back_t, "drawer_box", "back"),
    ]


def _validate(item, n_cols, H, t):
    col, typ, z, h = item["col"], item["type"], item["z"], item["height"]
    if typ not in ITEM_TYPES:
        raise ValueError(f"סוג רכיב לא מוכר: {typ}")
    if not (1 <= col <= n_cols):
        raise ValueError(f"{typ}: עמודה {col} לא קיימת (יש {n_cols})")
    if typ in (DRAWER, DOOR) and not (h and h > 0):
        raise ValueError(f"{typ} בעמודה {col}: חסר גובה")
    top = z + (t if typ == SHELF else ROD_SIZE if typ == ROD else h)
    if not (z >= t and top <= H - t):
        raise ValueError(f"{typ} בעמודה {col}: גובה {z} חורג מגבולות הארון")


def build_panels(width, height, depth, t, back_t, col_widths, items):
    """items: iterable of dicts {col (1-based), type, z (mm from floor), height (mm)}."""
    if any(not (w > 0) for w in col_widths):
        raise ValueError("רוחב עמודה חייב להיות חיובי")
    inner = width - 2 * t - (len(col_widths) - 1) * t
    if abs(sum(col_widths) - inner) > 1:
        raise ValueError(f"סכום רוחבי העמודות ({sum(col_widths):.0f}) חייב להיות {inner:.0f} מ\"מ")

    D = depth - back_t  # usable depth in front of the back panel
    panels = _carcass(width, height, D, t, back_t, col_widths)
    xs = _col_x(t, col_widths)
    for item in items:
        _validate(item, len(col_widths), height, t)
        cx, cw = xs[item["col"] - 1], col_widths[item["col"] - 1]
        typ, z, h = item["type"], item["z"], item["height"]
        if typ == SHELF:
            panels.append(Panel("מדף", cx, 0, z, cw, D, t, "shelf", "board"))
        elif typ == DRAWER:
            panels.extend(_drawer(cx, cw, z, h, D, t, back_t))
        elif typ == DOOR:
            panels.append(Panel("דלת", cx, -t, z, cw, t, h, "door", "board"))
        else:
            panels.append(Panel("מוט תלייה", cx, D / 2, z, cw, ROD_SIZE, ROD_SIZE, "rod", "none"))
    return panels


def _dims(p):
    return sorted((round(p.w, 1), round(p.d, 1), round(p.h, 1)), reverse=True)


def cut_list(panels):
    rows = [(p.name, *_dims(p)) for p in panels if p.material != "none"]
    df = pd.DataFrame(rows, columns=["שם", "אורך", "רוחב", "עובי"])
    return df.groupby(["שם", "אורך", "רוחב", "עובי"], as_index=False).size().rename(columns={"size": "כמות"})


def price(panels, price_m2_board, price_m2_back, drawer_rail, hinge_per_door):
    def area(material):
        return sum(math.prod(_dims(p)[:2]) for p in panels if p.material == material) / 1e6

    board_m2, back_m2 = area("board"), area("back")
    material = board_m2 * price_m2_board + back_m2 * price_m2_back
    hardware = (sum(p.kind == "drawer_front" for p in panels) * drawer_rail
                + sum(p.kind == "door" for p in panels) * hinge_per_door)
    return {"board_m2": board_m2, "back_m2": back_m2, "material": material,
            "hardware": hardware, "total": material + hardware}
