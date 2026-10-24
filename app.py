"""Streamlit cabinet designer. Run: streamlit run app.py"""
import pandas as pd
import streamlit as st

from cabinet import (DRAWER, ITEM_TYPES, ROD, SHELF, build_panels, cut_list, default_col_widths,
                     even_shelves, format_dims, price, price_html)
from style import CSS
from view3d import figure

st.set_page_config(page_title="תכנון ארון | Abanai", layout="wide", initial_sidebar_state="collapsed")
st.markdown(CSS, unsafe_allow_html=True)

COL, TYPE, Z, HEIGHT = "עמודה", "סוג", "גובה מהרצפה (מ\"מ)", "גובה רכיב (מ\"מ)"

st.markdown(
    '<div class="topstrip"></div>'
    '<div class="hdr"><span class="brand">Abanai</span>'
    '<span class="nav"><span>מוצרים</span><span>חדרים</span><span>רעיונות</span><span>שירותים</span></span></div>'
    '<div class="crumbs">מוצרים<span class="sep">›</span>אחסון וארגון<span class="sep">›</span>ארונות'
    '<span class="sep">›</span><span class="cur-page">מתכנן ארון</span></div>',
    unsafe_allow_html=True)

gallery, info = st.columns([3, 2], gap="large")

# ---- buy panel (placeholders are filled once panels are known) ----
with info:
    st.markdown('<span class="badge">בהתאמה אישית</span>', unsafe_allow_html=True)
    head_ph = st.empty()
    price_ph = st.empty()
    st.markdown('<div class="price-note">המחיר כולל חומר ופרזול</div>'
                '<div class="pdesc">ארון בגודל שאתם בוחרים, עם מדפים, מגירות, דלתות ומוטות תלייה. '
                'סובבו את התצוגה כדי לראות כל פרט.</div>'
                '<div class="subhead">בחרו מידות</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    W = c1.number_input("רוחב (מ\"מ)", 300, 5000, 1000, 10)
    H = c2.number_input("גובה (מ\"מ)", 300, 3000, 2000, 10)
    D = c3.number_input("עומק (מ\"מ)", 200, 1000, 600, 10)
    c4, c5, c6 = st.columns(3)
    t = c4.number_input("עובי לוח", 6, 40, 18)
    back_t = c5.number_input("עובי גב", 3, 20, 8)
    n_cols = c6.number_input("מספר עמודות", 1, 8, 2)
    dl_ph = st.empty()
    avail_ph = st.empty()

head_ph.markdown(f'<div class="ptitle">ארון בהתאמה אישית</div>'
                 f'<div class="psub">{format_dims(W, D, H, n_cols)}</div>', unsafe_allow_html=True)

if "items" not in st.session_state:
    st.session_state["items"] = pd.DataFrame(
        [[1, ROD, 1700, None], *[[2, SHELF, z, None] for z in even_shelves(H, t, 3)],
         [2, DRAWER, t, 200], [2, DRAWER, t + 200, 200]],
        columns=[COL, TYPE, Z, HEIGHT])

with gallery:
    plot_ph = st.container()
    show_doors = st.toggle("הצג דלתות וחזיתות", True)

    with st.expander("מידות"):
        cols_df = st.data_editor(
            pd.DataFrame({"רוחב": [round(w, 1) for w in default_col_widths(W, t, n_cols)]},
                         index=range(1, n_cols + 1)),
            key=f"cols_{W}_{t}_{n_cols}", width="stretch")
        inner = W - 2 * t - (n_cols - 1) * t
        st.caption(f"סכום נדרש: {inner:.0f} מ\"מ")

    with st.expander("רכיבים"):
        items_df = st.data_editor(
            st.session_state["items"], key="items_editor", num_rows="dynamic", width="stretch",
            column_config={
                COL: st.column_config.NumberColumn(min_value=1, max_value=n_cols, step=1, required=True),
                TYPE: st.column_config.SelectboxColumn(options=ITEM_TYPES, required=True),
                Z: st.column_config.NumberColumn(min_value=0, required=True),
                HEIGHT: st.column_config.NumberColumn(min_value=0, help="למגירה ודלת בלבד"),
            })
        q1, q2, q3 = st.columns(3)
        q_col = q1.number_input("לעמודה", 1, n_cols, 1)
        q_n = q2.number_input("מספר מדפים", 1, 20, 4)
        q3.markdown("<div style='height:1.7rem'></div>", unsafe_allow_html=True)
        if q3.button("הוסף מדפים במרווח שווה", type="secondary"):
            new = pd.DataFrame([[q_col, SHELF, round(z, 1), None] for z in even_shelves(H, t, q_n)],
                               columns=items_df.columns)
            st.session_state["items"] = pd.concat([items_df, new], ignore_index=True)
            del st.session_state["items_editor"]  # drop stale editor deltas so the new rows show
            st.rerun()

    cut_ph = st.expander("רשימת חיתוך")
    breakdown_ph = st.expander("פירוט מחיר")
    with st.expander("מחירון חומרים"):
        p1, p2 = st.columns(2)
        p_board = p1.number_input("לוח למ\"ר", 0.0, value=120.0)
        p_back = p2.number_input("גב למ\"ר", 0.0, value=40.0)
        p_rail = p1.number_input("זוג מסילות למגירה", 0.0, value=60.0)
        p_hinge = p2.number_input("צירים לדלת", 0.0, value=30.0)

items = [{"col": int(r[COL]), "type": r[TYPE], "z": float(r[Z]), "height": float(r[HEIGHT]) if pd.notna(r[HEIGHT]) else 0.0}
         for _, r in items_df.dropna(subset=[COL, TYPE, Z]).iterrows()]

try:
    panels = build_panels(W, H, D, t, back_t, cols_df["רוחב"].tolist(), items)
except ValueError as e:
    plot_ph.error(str(e))  # plain st.error: message never goes through HTML
    price_ph.markdown('<div class="price"><span class="cur">₪</span>—</div>', unsafe_allow_html=True)
    avail_ph.markdown('<div class="avail"><span class="dot-bad">●</span> לא ניתן לייצר בתצורה הנוכחית</div>',
                      unsafe_allow_html=True)
    st.stop()

pr = price(panels, p_board, p_back, p_rail, p_hinge)
cl = cut_list(panels)
csv_bytes = cl.to_csv(index=False).encode("utf-8-sig")

with plot_ph:
    st.plotly_chart(figure(panels, show_doors), width="stretch")
with cut_ph:
    st.dataframe(cl, width="stretch", hide_index=True)
    st.download_button("הורד רשימת חיתוך (CSV)", csv_bytes, "cut_list.csv", "text/csv",
                       type="secondary", key="dl_secondary")
with breakdown_ph:
    st.markdown(
        f'<div class="rowline"><span>חומר</span><span class="v">₪{pr["material"]:,.0f}</span></div>'
        f'<div class="rowline"><span>פרזול</span><span class="v">₪{pr["hardware"]:,.0f}</span></div>'
        f'<div class="rowline total"><span>סה"כ</span><span class="v">₪{pr["total"]:,.0f}</span></div>'
        f'<div class="small-gray">{pr["board_m2"]:.2f} מ"ר לוח, {pr["back_m2"]:.2f} מ"ר גב</div>',
        unsafe_allow_html=True)

price_ph.markdown(price_html(pr["total"]), unsafe_allow_html=True)
dl_ph.download_button("הורד רשימת חיתוך", csv_bytes, "cut_list.csv", "text/csv",
                      type="primary", width="stretch", key="dl_primary")
avail_ph.markdown('<div class="avail"><span class="dot-ok">●</span> מוכן לייצור בנגריה</div>',
                  unsafe_allow_html=True)
