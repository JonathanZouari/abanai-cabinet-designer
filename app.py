"""Streamlit cabinet designer. Run: streamlit run app.py"""
import pandas as pd
import streamlit as st

from cabinet import (DRAWER, ITEM_TYPES, ROD, SHELF, build_panels, cut_list, default_col_widths,
                     even_shelves, price)
from view3d import figure

st.set_page_config(page_title="תכנון ארון", layout="wide")
st.markdown("<style>.stApp, [data-testid='stSidebar'] {direction: rtl; text-align: right;}</style>",
            unsafe_allow_html=True)
st.markdown("### 🪚 תכנון ארון")
summary = st.container()  # filled once the cabinet is built

COL, TYPE, Z, HEIGHT = "עמודה", "סוג", "גובה מהרצפה (מ\"מ)", "גובה רכיב (מ\"מ)"

with st.sidebar:
    st.header("מידות (מ\"מ)")
    W = st.number_input("רוחב", 300, 5000, 1000, 10, help="רוחב כולל של הארון")
    H = st.number_input("גובה", 300, 3000, 2000, 10, help="גובה כולל של הארון")
    D = st.number_input("עומק", 200, 1000, 600, 10, help="עומק כולל כולל הגב")
    n_cols = st.number_input("מספר עמודות", 1, 8, 2, help="עמודות מופרדות במחיצות אנכיות")
    with st.expander("חומר ועובי"):
        t = st.number_input("עובי לוח", 6, 40, 18, help="עובי הלוחות בגוף, במחיצות ובמדפים")
        back_t = st.number_input("עובי גב", 3, 20, 8, help="עובי לוח הגב")
    with st.expander("מחירים (₪)"):
        p_board = st.number_input("לוח למ\"ר", 0.0, value=120.0, help="מחיר למ\"ר לוח")
        p_back = st.number_input("גב למ\"ר", 0.0, value=40.0, help="מחיר למ\"ר גב")
        p_rail = st.number_input("זוג מסילות למגירה", 0.0, value=60.0)
        p_hinge = st.number_input("צירים לדלת", 0.0, value=30.0)

if "items" not in st.session_state:
    st.session_state["items"] = pd.DataFrame(
        [[1, ROD, 1700, None], *[[2, SHELF, z, None] for z in even_shelves(H, t, 3)],
         [2, DRAWER, t, 200], [2, DRAWER, t + 200, 200]],
        columns=[COL, TYPE, Z, HEIGHT])

left, right = st.columns([2, 3])
with left:
    st.subheader("רוחב עמודות (מ\"מ)")
    cols_df = st.data_editor(
        pd.DataFrame({"רוחב": [round(w, 1) for w in default_col_widths(W, t, n_cols)]},
                     index=range(1, n_cols + 1)),
        key=f"cols_{W}_{t}_{n_cols}", width="stretch")
    inner = W - 2 * t - (n_cols - 1) * t
    diff = inner - sum(cols_df["רוחב"])
    if abs(diff) <= 1:
        st.success(f"✓ סכום הרוחבים תואם: {inner:.0f} מ\"מ")
    else:
        st.warning(f"{'חסרים' if diff > 0 else 'עודפים'} {abs(diff):.0f} מ\"מ (הסכום הנדרש: {inner:.0f})")

    st.subheader("רכיבים")
    items_df = st.data_editor(
        st.session_state["items"], key="items_editor", num_rows="dynamic", width="stretch",
        hide_index=True,
        column_config={
            COL: st.column_config.NumberColumn("עמודה", min_value=1, max_value=n_cols, step=1, required=True,
                                               width="small", help="מספר העמודה, 1 = השמאלית"),
            TYPE: st.column_config.SelectboxColumn("סוג", options=ITEM_TYPES, required=True, width="small"),
            Z: st.column_config.NumberColumn("מהרצפה", min_value=0, required=True, width="small",
                                             help="גובה מהרצפה במ\"מ"),
            HEIGHT: st.column_config.NumberColumn("גובה", min_value=0, width="small",
                                                  help="גובה רכיב במ\"מ, למגירה ודלת בלבד"),
        })
    error_slot = st.container()

    q1, q2 = st.columns(2)
    q_col = q1.number_input("לעמודה", 1, n_cols, 1)
    q_n = q2.number_input("מספר מדפים", 1, 20, 4)
    if st.button("הוסף מדפים", width="stretch", help="מוסיף מדפים במרווח שווה לעמודה שנבחרה"):
        new = pd.DataFrame([[q_col, SHELF, round(z, 1), None] for z in even_shelves(H, t, q_n)],
                           columns=items_df.columns)
        st.session_state["items"] = pd.concat([items_df, new], ignore_index=True)
        del st.session_state["items_editor"]  # drop stale editor deltas so the new rows show
        st.rerun()

items = [{"col": int(r[COL]), "type": r[TYPE], "z": float(r[Z]), "height": float(r[HEIGHT]) if pd.notna(r[HEIGHT]) else 0.0}
         for _, r in items_df.dropna(subset=[COL, TYPE, Z]).iterrows()]

try:
    panels = build_panels(W, H, D, t, back_t, cols_df["רוחב"].tolist(), items)
except ValueError as e:
    error_slot.error(str(e))
    st.stop()

pr = price(panels, p_board, p_back, p_rail, p_hinge)
with summary:
    s1, s2, s3 = st.columns(3)
    s1.metric("מידות כוללות (ר×ג×ע)", f"\u2066{W}×{H}×{D}\u2069")
    s2.metric("סה\"כ מחיר", f"₪{pr['total']:,.0f}")
    s3.metric("מספר לוחות", int(cut_list(panels)["כמות"].sum()))

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
        m1, m2, m3 = st.columns(3)
        m1.metric("חומר", f"₪{pr['material']:,.0f}", f"{pr['board_m2']:.2f} מ\"ר לוח, {pr['back_m2']:.2f} מ\"ר גב",
                  delta_color="off")
        m2.metric("פרזול", f"₪{pr['hardware']:,.0f}")
        m3.metric("סה\"כ", f"₪{pr['total']:,.0f}")
