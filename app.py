import streamlit as st
import pandas as pd
import json
import os

DATA_FILE = "expenses.json"

# --- Data Management Functions ---
def load_expenses():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return []
    return []

def save_expenses(expenses):
    with open(DATA_FILE, "w") as file:
        json.dump(expenses, file, indent=4)

# --- Initialize Session State ---
if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses()

# --- Page Layout ---
st.set_page_config(page_title="Personal Expense Tracker", page_icon="💰", layout="centered")
st.title("💰 Personal Expense Tracker")

# --- Form: Add New Expense ---
with st.expander("➕ Add a New Expense", expanded=True):
    with st.form("expense_form", clear_on_submit=True):
        category = st.selectbox(
            "Category",
            ["Food", "Travel", "Shopping", "Bills", "Entertainment", "Other"]
        )
        amount = st.number_input("Amount (₹)", min_value=0.01, step=1.0, format="%.2f")
        note = st.text_input("Note (optional)")
        submitted = st.form_submit_button("Add Expense")

        if submitted:
            new_expense = {
                "category": category,
                "amount": round(amount, 2),
                "note": note.strip()
            }
            st.session_state.expenses.append(new_expense)
            save_expenses(st.session_state.expenses)
            st.success(f"✅ Added: {category} - ₹{amount:.2f}")

# --- Expense Display & Analytics ---
if len(st.session_state.expenses) > 0:
    df = pd.DataFrame(st.session_state.expenses)

    # Metrics Summary
    total_spent = df["amount"].sum()
    st.metric(label="Total Spending", value=f"₹{total_spent:,.2f}")

    # Tabs for Data and Charts
    tab1, tab2 = st.tabs(["📋 View All", "📊 Category Breakdown"])

    with tab1:
        st.dataframe(df, use_container_width=True)
        if st.button("🗑️ Clear All Expenses"):
            st.session_state.expenses = []
            save_expenses([])
            st.rerun()

    with tab2:
        category_totals = df.groupby("category")["amount"].sum().reset_index()
        st.bar_chart(data=category_totals, x="category", y="amount")
else:
    st.info("No expenses recorded yet. Add one above to get started!")
