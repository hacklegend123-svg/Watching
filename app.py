# app.py

import streamlit as st

# ==============================
# Simple Addition App (UI + Backend)
# ==============================

# Frontend: UI elements
st.title("Simple Addition App")
st.write("Enter two numbers and click 'Add' to see the sum.")

num1 = st.number_input("Enter first number:", value=0)
num2 = st.number_input("Enter second number:", value=0)

# Backend: Logic
if st.button("Add"):
    result = num1 + num2
    st.success(f"The sum is: {result}")

# Optional: Extra info for user
st.write("---")
st.write("This is a beginner-friendly example showing how frontend (Streamlit UI) interacts with backend (Python logic).")
