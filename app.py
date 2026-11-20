import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from db import get_connection, query, execute

st.set_page_config(page_title="Bataatas | Management System", page_icon="🥔", layout="wide")

st.markdown("""
<style>
/* Readability improvements: larger type, more breathing room, restrained page width */
html, body, [class*="st-"] { font-size: 17px; }
.block-container { max-width: 1600px; padding-top: 2rem; padding-bottom: 3rem; padding-left: 2.5rem; padding-right: 2.5rem; }
h1 { font-size: 2.35rem !important; line-height: 1.2 !important; }
h2 { font-size: 1.8rem !important; }
h3 { font-size: 1.45rem !important; }
h4 { font-size: 1.2rem !important; }
p, label, [data-testid="stCaptionContainer"] { font-size: 1rem !important; }
[data-testid="stMetric"] { background: #f7f8fa; border: 1px solid #e1e5eb; padding: 20px 18px; border-radius: 12px; min-height: 112px; }
[data-testid="stMetricLabel"] { font-size: 1rem !important; }
[data-testid="stMetricValue"] { font-size: 1.8rem !important; }
[data-testid="stSidebar"] { background: #fafafa; }
[data-testid="stSidebar"] * { font-size: 1rem !important; }
[data-testid="stDataFrame"] { font-size: 0.95rem !important; }
[data-testid="stDataFrame"] [role="gridcell"], [data-testid="stDataFrame"] [role="columnheader"] { font-size: 0.95rem !important; }
.stButton button, [data-testid="stFormSubmitButton"] button { min-height: 2.8rem; font-size: 1rem; }
.small-note { color:#777; font-size:0.95rem; }
@media (max-width: 900px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; }
  html, body, [class*="st-"] { font-size: 16px; }
}
</style>
""", unsafe_allow_html=True)

st.title("🥔 Bataatas Business Management")
st.caption("Multi-branch sales, purchase and financial operations · Wandoor · Manjeri · Thiruvali")

try:
    branches = query("SELECT branch_id, branch_name, location_note FROM branches ORDER BY branch_name")
    if not branches:
        st.error("No branches found. Import bataatas_db_dump.sql first. See README for setup.")
        st.stop()
    branch_map = {b["branch_name"]: b["branch_id"] for b in branches}
except Exception as exc:
    st.error("Cannot connect to MySQL. Start MySQL, import bataatas_db_dump.sql and configure DB credentials.")
    with st.expander("Technical details"):
        st.code(str(exc))
    st.stop()

pages = ["Overview", "Daily Sales", "Purchases", "Monthly P&L", "Branches"]
page = st.sidebar.radio("Navigation", pages)
st.sidebar.divider()
st.sidebar.caption("Database: bataatas_db · MySQL")


def money(value):
    return f"₹{float(value or 0):,.2f}"


def branch_selector(label="Branch", key=None, include_all=False):
    names = list(branch_map.keys())
    if include_all:
        selected = st.selectbox(label, ["All branches"] + names, key=key)
        return None if selected == "All branches" else branch_map[selected]
    selected = st.selectbox(label, names, key=key)
    return branch_map[selected]


def refresh():
    st.cache_data.clear()

if page == "Overview":
    st.subheader("Business overview")
    c1, c2 = st.columns([1, 3])
    with c1:
        selected_branch = branch_selector("Filter branch", "overview_branch", True)
    with c2:
        st.caption("Figures reflect the records currently stored in MySQL. Add or edit records in the management pages.")
    where = "" if selected_branch is None else " WHERE branch_id = %s"
    params = () if selected_branch is None else (selected_branch,)
    sales = query(f"SELECT COALESCE(SUM(total_sales_value),0) total_sales, COALESCE(SUM(all_purchases),0) purchases, COALESCE(SUM(exp_staff+exp_rent_power),0) operating_costs, COALESCE(SUM(cash_available_on_day),0) cash, SUM(cash_available_on_day < 0) negative_days FROM daily_sales{where}", params)[0]
    total_purchase_rows = query("SELECT COUNT(*) n FROM purchases" + (" WHERE branch_id=%s" if selected_branch else ""), params)[0]["n"]
    k = st.columns(5)
    k[0].metric("Recorded sales", money(sales["total_sales"]))
    k[1].metric("Daily purchase total", money(sales["purchases"]))
    k[2].metric("Staff + occupancy", money(sales["operating_costs"]))
    k[3].metric("Cash generated", money(sales["cash"]))
    k[4].metric("Negative cash days", int(sales["negative_days"] or 0))
    st.divider()
    sales_rows = query("""SELECT b.branch_name, d.sale_date, d.total_sales_value, d.cash_available_on_day
                         FROM daily_sales d JOIN branches b ON b.branch_id=d.branch_id""" + (" WHERE d.branch_id=%s" if selected_branch else "") + " ORDER BY d.sale_date", params)
    if sales_rows:
        df = pd.DataFrame(sales_rows)
        left, right = st.columns(2)
        with left:
            st.markdown("#### Daily sales trend")
            trend = df.groupby(["sale_date", "branch_name"], as_index=False)["total_sales_value"].sum()
            fig = px.line(trend, x="sale_date", y="total_sales_value", color="branch_name", labels={"total_sales_value":"Sales (₹)","sale_date":"Date"})
            fig.update_layout(height=430, font=dict(size=14), margin=dict(l=20, r=20, t=35, b=35), legend_title_text="Branch")
            st.plotly_chart(fig, use_container_width=True)
        with right:
            st.markdown("#### Sales by branch")
            share = df.groupby("branch_name", as_index=False)["total_sales_value"].sum()
            fig = px.pie(share, names="branch_name", values="total_sales_value", hole=.55)
            fig.update_layout(height=430, font=dict(size=14), margin=dict(l=20, r=20, t=35, b=35), legend_title_text="Branch")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("#### Latest sales records")
        st.dataframe(df.sort_values("sale_date", ascending=False).head(12), use_container_width=True, hide_index=True)
    st.caption(f"Purchase ledger records: {total_purchase_rows:,}. Data is illustrative/synthetic as documented in CA-1.")

elif page == "Daily Sales":
    st.subheader("Daily sales management")
    with st.expander("＋ Add daily sales record", expanded=True):
        with st.form("add_sale"):
            b = branch_selector("Branch", "add_sale_branch")
            d = st.date_input("Sale date", value=date.today())
            a, bb, cc = st.columns(3)
            opening = a.number_input("Opening balance (₹)", min_value=0.0, step=100.0)
            total = bb.number_input("Total sales (₹)", min_value=0.0, step=100.0)
            staff = cc.number_input("Staff expense (₹)", min_value=0.0, step=50.0)
            a, bb, cc = st.columns(3)
            rent = a.number_input("Rent & power (₹)", min_value=0.0, step=50.0)
            purchases = bb.number_input("Total purchases (₹)", min_value=0.0, step=50.0)
            cash = total - staff - rent - purchases
            cc.metric("Calculated cash available", money(cash))
            submitted = st.form_submit_button("Save sales record", type="primary")
            if submitted:
                execute("""INSERT INTO daily_sales (branch_id,sale_date,opening_balance,total_sales_value,exp_staff,exp_rent_power,all_purchases,cash_available_on_day) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", (b,d,opening,total,staff,rent,purchases,cash))
                st.success("Sales record added."); st.rerun()
    st.markdown("#### Search and manage records")
    bfilter = branch_selector("Branch filter", "sales_filter", True)
    records = query("""SELECT d.sale_id,b.branch_name,d.sale_date,d.opening_balance,d.total_sales_value,d.exp_staff,d.exp_rent_power,d.all_purchases,d.cash_available_on_day FROM daily_sales d JOIN branches b ON b.branch_id=d.branch_id""" + (" WHERE d.branch_id=%s" if bfilter else "") + " ORDER BY d.sale_date DESC,d.sale_id DESC", (bfilter,) if bfilter else ())
    df = pd.DataFrame(records)
    st.dataframe(df, use_container_width=True, hide_index=True)
    ids = [r["sale_id"] for r in records]
    if ids:
        chosen = st.selectbox("Select record ID to edit or delete", ids)
        current = next(r for r in records if r["sale_id"] == chosen)
        with st.form("edit_sale"):
            st.caption(f"Editing record #{chosen}")
            d = st.date_input("Sale date", value=current["sale_date"], key="edit_sale_date")
            a,bb,cc = st.columns(3)
            opening = a.number_input("Opening balance", value=float(current["opening_balance"] or 0), min_value=0.0, key="es1")
            total = bb.number_input("Total sales", value=float(current["total_sales_value"] or 0), min_value=0.0, key="es2")
            staff = cc.number_input("Staff expense", value=float(current["exp_staff"] or 0), min_value=0.0, key="es3")
            a,bb,cc = st.columns(3)
            rent = a.number_input("Rent & power", value=float(current["exp_rent_power"] or 0), min_value=0.0, key="es4")
            purchases = bb.number_input("Total purchases", value=float(current["all_purchases"] or 0), min_value=0.0, key="es5")
            cc.metric("Calculated cash", money(total-staff-rent-purchases))
            save = st.form_submit_button("Update record", type="primary")
            if save:
                execute("UPDATE daily_sales SET sale_date=%s,opening_balance=%s,total_sales_value=%s,exp_staff=%s,exp_rent_power=%s,all_purchases=%s,cash_available_on_day=%s WHERE sale_id=%s", (d,opening,total,staff,rent,purchases,total-staff-rent-purchases,chosen))
                st.success("Record updated."); st.rerun()
        with st.form("delete_sale"):
            confirm = st.checkbox(f"Confirm deletion of sales record #{chosen}")
            if st.form_submit_button("Delete selected record"):
                if confirm:
                    execute("DELETE FROM daily_sales WHERE sale_id=%s", (chosen,)); st.warning("Record deleted."); st.rerun()
                else: st.error("Tick the confirmation box first.")

elif page == "Purchases":
    st.subheader("Purchase ledger")
    with st.expander("＋ Add purchase", expanded=True):
        with st.form("add_purchase"):
            b = branch_selector("Branch", "purchase_branch")
            d = st.date_input("Purchase date", value=date.today(), key="purchase_date")
            item = st.text_input("Item / supplier category", placeholder="e.g. French Fries")
            amount = st.number_input("Amount (₹)", min_value=0.01, step=10.0)
            if st.form_submit_button("Save purchase", type="primary"):
                if item.strip():
                    execute("INSERT INTO purchases (branch_id,purchase_date,item_name,amount) VALUES (%s,%s,%s,%s)", (b,d,item.strip(),amount))
                    st.success("Purchase added."); st.rerun()
                else: st.error("Enter an item name.")
    bfilter = branch_selector("Branch filter", "purchase_filter", True)
    records = query("SELECT p.purchase_id,b.branch_name,p.purchase_date,p.item_name,p.amount FROM purchases p JOIN branches b ON b.branch_id=p.branch_id" + (" WHERE p.branch_id=%s" if bfilter else "") + " ORDER BY p.purchase_date DESC,p.purchase_id DESC", (bfilter,) if bfilter else ())
    st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
    ids = [r["purchase_id"] for r in records]
    if ids:
        chosen = st.selectbox("Select purchase ID", ids)
        current = next(r for r in records if r["purchase_id"] == chosen)
        with st.form("edit_purchase"):
            d = st.date_input("Purchase date", value=current["purchase_date"], key="epd")
            item = st.text_input("Item", value=current["item_name"], key="epi")
            amount = st.number_input("Amount", min_value=0.0, value=float(current["amount"] or 0), key="epa")
            if st.form_submit_button("Update purchase", type="primary"):
                execute("UPDATE purchases SET purchase_date=%s,item_name=%s,amount=%s WHERE purchase_id=%s", (d,item.strip(),amount,chosen)); st.success("Purchase updated."); st.rerun()
        with st.form("delete_purchase"):
            confirm = st.checkbox(f"Confirm deletion of purchase #{chosen}")
            if st.form_submit_button("Delete purchase"):
                if confirm:
                    execute("DELETE FROM purchases WHERE purchase_id=%s", (chosen,)); st.warning("Purchase deleted."); st.rerun()
                else: st.error("Tick the confirmation box first.")

elif page == "Monthly P&L":
    st.subheader("Monthly profit & loss management")
    pnl_fields = ["sales","cogs","gross_profit","salaries_wages","bonuses_commissions","labor_expense","occupancy_costs","marketing_advertising","cleaning_inventory","petrol_expense","other_expense","net_income"]
    with st.expander("＋ Add monthly P&L record", expanded=True):
        with st.form("add_pnl"):
            b = branch_selector("Branch", "pnl_branch")
            month = st.text_input("Month", value="NOVEMBER", help="Use a month label such as NOVEMBER 2026")
            vals = {}
            for idx, field in enumerate(pnl_fields):
                vals[field] = st.number_input(field.replace("_"," ").title()+" (₹)", min_value=0.0, step=100.0, key="new_"+field)
            if st.form_submit_button("Save P&L", type="primary"):
                cols = ",".join(pnl_fields)
                marks = ",".join(["%s"]*len(pnl_fields))
                execute(f"INSERT INTO monthly_pnl (branch_id,month,{cols}) VALUES (%s,%s,{marks})", (b,month.upper().strip(),*[vals[x] for x in pnl_fields]))
                st.success("P&L record added."); st.rerun()
    bfilter = branch_selector("Branch filter", "pnl_filter", True)
    records = query("SELECT p.pnl_id,b.branch_name,p.month,p.sales,p.cogs,p.gross_profit,p.labor_expense,p.other_expense,p.net_income FROM monthly_pnl p JOIN branches b ON b.branch_id=p.branch_id" + (" WHERE p.branch_id=%s" if bfilter else "") + " ORDER BY p.month DESC,p.pnl_id DESC", (bfilter,) if bfilter else ())
    st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True)
    ids = [r["pnl_id"] for r in records]
    if ids:
        chosen = st.selectbox("Select P&L record ID", ids)
        current = next(r for r in records if r["pnl_id"] == chosen)
        full = query("SELECT * FROM monthly_pnl WHERE pnl_id=%s", (chosen,))[0]
        with st.form("edit_pnl"):
            month = st.text_input("Month", value=full["month"] or "")
            vals = {}
            for field in pnl_fields:
                vals[field] = st.number_input(field.replace("_"," ").title()+" (₹)", min_value=0.0, value=float(full[field] or 0), key="edit_"+field)
            if st.form_submit_button("Update P&L", type="primary"):
                sets = ",".join([f"{x}=%s" for x in pnl_fields])
                execute(f"UPDATE monthly_pnl SET month=%s,{sets} WHERE pnl_id=%s", (month.upper().strip(),*[vals[x] for x in pnl_fields],chosen)); st.success("P&L updated."); st.rerun()
        with st.form("delete_pnl"):
            confirm = st.checkbox(f"Confirm deletion of P&L record #{chosen}")
            if st.form_submit_button("Delete P&L record"):
                if confirm:
                    execute("DELETE FROM monthly_pnl WHERE pnl_id=%s", (chosen,)); st.warning("P&L record deleted."); st.rerun()
                else: st.error("Tick the confirmation box first.")

elif page == "Branches":
    st.subheader("Branch directory")
    st.dataframe(pd.DataFrame(branches), use_container_width=True, hide_index=True)
    with st.expander("＋ Add branch"):
        with st.form("add_branch"):
            name = st.text_input("Branch name")
            note = st.text_input("Location note")
            if st.form_submit_button("Add branch", type="primary"):
                if name.strip():
                    try:
                        execute("INSERT INTO branches (branch_name,location_note) VALUES (%s,%s)", (name.strip().title(),note.strip()))
                        st.success("Branch added."); st.rerun()
                    except Exception as exc: st.error(f"Could not add branch: {exc}")
                else: st.error("Enter a branch name.")
    with st.expander("Edit branch details"):
        selected = st.selectbox("Branch", list(branch_map.keys()), key="edit_branch")
        current = next(x for x in branches if x["branch_name"] == selected)
        with st.form("branch_update"):
            note = st.text_input("Location note", value=current["location_note"] or "")
            if st.form_submit_button("Update branch"):
                execute("UPDATE branches SET location_note=%s WHERE branch_id=%s", (note,current["branch_id"])); st.success("Branch updated."); st.rerun()
    st.info("Branch deletion is intentionally disabled to protect linked sales, purchases and P&L records.")

st.sidebar.divider()
st.sidebar.caption("Academic project · MKT322 CA-2 · Data is synthetic/illustrative")
