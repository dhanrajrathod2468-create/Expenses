import streamlit as st
import pandas as pd
import json
import os

DATA_FILE = "user_expenses.json"

# --- Helper Functions for Data Handling ---
def load_all_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}
    return {}

def save_user_expenses(username, expenses):
    data = load_all_data()
    data[username] = expenses
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# --- Page Setup ---
st.set_page_config(page_title="Personal Expense Tracker", page_icon="💰", layout="centered")

# --- Authentication State ---
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# --- Login / Switch User Screen ---
if not st.session_state.logged_in_user:
    st.title("🔒 Personal Expense Tracker")
    st.subheader("Login to your private workspace")

    username_input = st.text_input("Enter your name or unique username:").strip().lower()
    if st.button("Enter Tracker"):
        if username_input:
            st.session_state.logged_in_user = username_input
            st.rerun()
        else:
            st.warning("Please enter a username to proceed.")
    st.stop()

# --- Authenticated App View ---
current_user = st.session_state.logged_in_user
all_data = load_all_data()
user_expenses = all_data.get(current_user, [])

# Sidebar info and Logout
st.sidebar.write(f"Logged in as: **{current_user}**")
if st.sidebar.button("Log Out"):
    st.session_state.logged_in_user = None
    st.rerun()

st.title(f"💰 {current_user.capitalize()}'s Expense Tracker")

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
            user_expenses.append(new_expense)
            save_user_expenses(current_user, user_expenses)
            st.success(f"✅ Added: {category} - ₹{amount:.2f}")
            st.rerun()

# --- Expense Display & Analytics ---
if len(user_expenses) > 0:
    df = pd.DataFrame(user_expenses)

    total_spent = df["amount"].sum()
    st.metric(label="Total Spending", value=f"₹{total_spent:,.2f}")

    tab1, tab2 = st.tabs(["📋 View All", "📊 Category Breakdown"])

    with tab1:
        st.dataframe(df, use_container_width=True)
        if st.button("🗑️ Clear My Expenses"):
            save_user_expenses(current_user, [])
            st.rerun()

    with tab2:
        category_totals = df.groupby("category")["amount"].sum().reset_index()
        st.bar_chart(data=category_totals, x="category", y="amount")
else:
    st.info("No expenses recorded yet for your account. Add one above to get started!")
