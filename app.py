"""Streamlit cabinet designer. Run: streamlit run app.py"""
import pandas as pd
import streamlit as st

from cabinet import (DRAWER, ITEM_TYPES, ROD, SHELF, build_panels, cut_list, even_shelves, price, resolve_col_widths)
from view3d import figure

st.set_page_config(page_title="תכנון ארון", layout="wide")
st.markdown("<style>.stApp, [data-testid='stSidebar'] {direction: rtl; text-align: right;}</style>",
            unsafe_allow_html=True)
st.title("🪚 תכנון ארון")

COL_WIDTH = "רוחב עמודה"
COL, TYPE, Z, HEIGHT, WIDTH = "עמודה", "סוג", "גובה מהרצפה (מ\"מ)", "גובה רכיב (מ\"מ)", "רוחב (מ\"מ)"

with st.sidebar:
    st.header("מידות (מ\"מ)")
    W = st.number_input("רוחב", 300, 5000, 1000, 10)
    H = st.number_input("גובה", 300, 3000, 2000, 10)
    D = st.number_input("עומק", 200, 1000, 600, 10)
    t = st.number_input("עובי לוח", 6, 40, 18)
    back_t = st.number_input("עובי גב", 3, 20, 8)
    n_cols = st.number_input("מספר עמודות", 1, 8, 2)
    st.header("מחירים (₪)")
    p_board = st.number_input("לוח למ\"ר", 0.0, value=120.0)
    p_back = st.number_input("גב למ\"ר", 0.0, value=40.0)
    p_rail = st.number_input("זוג מסילות למגירה", 0.0, value=60.0)
    p_hinge = st.number_input("צירים לדלת", 0.0, value=30.0)

if "items" not in st.session_state:
    st.session_state["items"] = pd.DataFrame(
        [[1, ROD, 1700, None, None], *[[2, SHELF, z, None, None] for z in even_shelves(H, t, 3)],
         [2, DRAWER, t, 200, None], [2, DRAWER, t + 200, 200, None]],
        columns=[COL, TYPE, Z, HEIGHT, WIDTH])

left, right = st.columns([2, 3])
with left:
    st.subheader("טבלת ארון")
    items_df = st.data_editor(
        st.session_state["items"], key="items_editor", num_rows="dynamic", width="stretch",
        column_config={
            COL: st.column_config.NumberColumn(min_value=1, max_value=n_cols, step=1, required=True),
            TYPE: st.column_config.SelectboxColumn(options=[COL_WIDTH, *ITEM_TYPES], required=True),
            Z: st.column_config.NumberColumn(min_value=0),
            HEIGHT: st.column_config.NumberColumn(min_value=0, help="למגירה ודלת בלבד"),
            WIDTH: st.column_config.NumberColumn(min_value=1, help="לשורת רוחב עמודה בלבד"),
        })

    q1, q2, q3 = st.columns(3)
    q_col = q1.number_input("לעמודה", 1, n_cols, 1)
    q_n = q2.number_input("מספר מדפים", 1, 20, 4)
    if q3.button("הוסף מדפים במרווח שווה"):
        new = pd.DataFrame([[q_col, SHELF, round(z, 1), None, None] for z in even_shelves(H, t, q_n)],
                           columns=items_df.columns)
        st.session_state["items"] = pd.concat([items_df, new], ignore_index=True)
        del st.session_state["items_editor"]  # drop stale editor deltas so the new rows show
        st.rerun()

overrides = {int(r[COL]): float(r[WIDTH]) for _, r in items_df.iterrows()
             if r[TYPE] == COL_WIDTH and pd.notna(r[COL]) and pd.notna(r[WIDTH])}
col_widths = resolve_col_widths(W, t, n_cols, overrides)
left.caption("רוחבי עמודות: " + " | ".join(f"{i}: {w:.0f}" for i, w in enumerate(col_widths, 1))
             + f" (סכום נדרש {W - 2 * t - (n_cols - 1) * t:.0f} מ\"מ)")

items = [{"col": int(r[COL]), "type": r[TYPE], "z": float(r[Z]), "height": float(r[HEIGHT]) if pd.notna(r[HEIGHT]) else 0.0}
         for _, r in items_df[items_df[TYPE] != COL_WIDTH].dropna(subset=[COL, TYPE, Z]).iterrows()]

try:
    panels = build_panels(W, H, D, t, back_t, col_widths, items)
except ValueError as e:
    right.error(str(e))
    st.stop()

with right:
    tab3d, tabcut = st.tabs(["תלת־ממד", "רשימת חיתוך ומחיר"])
    with tab3d:
        show_doors = st.toggle("הצג דלתות וחזיתות", True)
        st.plotly_chart(figure(panels, show_doors), width="stretch")
    with tabcut:
        cl = cut_list(panels)
        st.dataframe(cl, width="stretch", hide_index=True)
        st.download_button("הורד CSV", cl.to_csv(index=False).encode("utf-8-sig"),
                           "cut_list.csv", "text/csv")
        pr = price(panels, p_board, p_back, p_rail, p_hinge)
        m1, m2, m3 = st.columns(3)
        m1.metric("חומר", f"₪{pr['material']:,.0f}", f"{pr['board_m2']:.2f} מ\"ר לוח, {pr['back_m2']:.2f} מ\"ר גב",
                  delta_color="off")
        m2.metric("פרזול", f"₪{pr['hardware']:,.0f}")
        m3.metric("סה\"כ", f"₪{pr['total']:,.0f}")
