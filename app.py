import streamlit as st
import pandas as pd
import json
import os
import hashlib

# --- Configurations ---
DATA_FILE = "secure_expenses.json"

st.set_page_config(
    page_title="My Wallet App",
    page_icon="💳",
    layout="centered"
)

# --- Helper Functions for Data & Security ---
def hash_pin(pin: str) -> str:
    """Hash the PIN using SHA-256 for secure storage."""
    return hashlib.sha256(pin.encode()).hexdigest()

def load_all_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}
    return {}

def save_all_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# --- Authentication State ---
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# --- Login / Register Screen ---
if not st.session_state.logged_in_user:
    st.title("🔒 My Secure Wallet")
    st.write("Enter your nickname and a 4-digit PIN to access your private expenses.")

    nickname = st.text_input("Nickname:").strip().lower()
    pin = st.text_input("4-Digit PIN:", type="password", max_chars=8).strip()

    if st.button("Unlock / Enter Tracker", use_container_width=True):
        if not nickname or not pin:
            st.warning("Please enter both a nickname and a PIN.")
        else:
            data = load_all_data()
            hashed = hash_pin(pin)

            # If user already exists, verify PIN
            if nickname in data:
                if data[nickname].get("pin") == hashed:
                    st.session_state.logged_in_user = nickname
                    st.rerun()
                else:
                    st.error("❌ Incorrect PIN for this nickname. Please try again.")
            else:
                # If new user, create account and save PIN
                data[nickname] = {
                    "pin": hashed,
                    "expenses": []
                }
                save_all_data(data)
                st.session_state.logged_in_user = nickname
                st.rerun()

    st.stop()

# --- Authenticated App View ---
current_user = st.session_state.logged_in_user
all_data = load_all_data()
user_profile = all_data.get(current_user, {"pin": "", "expenses": []})
user_expenses = user_profile.get("expenses", [])

# Sidebar and Logout
st.sidebar.write(f"Logged in as: **{current_user.capitalize()}**")
if st.sidebar.button("Log Out"):
    st.session_state.logged_in_user = None
    st.rerun()

st.title(f"💳 {current_user.capitalize()}'s Expense Tracker")

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
            all_data[current_user]["expenses"] = user_expenses
            save_all_data(all_data)
            st.success(f"✅ Added: {category} - ₹{amount:.2f}")
            st.rerun()

# --- Expense Display & Analytics ---
if len(user_expenses) > 0:
    df = pd.DataFrame(user_expenses)

    # Total Spent Metric
    total_spent = df["amount"].sum()
    st.metric(label="Total Spending", value=f"₹{total_spent:,.2f}")

    # Tabs for Data and Charts
    tab1, tab2 = st.tabs(["📋 View All", "📊 Category Breakdown"])

    with tab1:
        st.dataframe(df, use_container_width=True)
        if st.button("🗑️ Clear My Expenses"):
            all_data[current_user]["expenses"] = []
            save_all_data(all_data)
            st.rerun()

    with tab2:
        category_totals = df.groupby("category")["amount"].sum().reset_index()
        st.bar_chart(data=category_totals, x="category", y="amount")
else:
    st.info("No expenses recorded yet for your account. Add one above to get started!")
