import streamlit as st

# Title
st.title("🧮 Simple Calculator")

# Input numbers
num1 = st.number_input("Enter first number", value=0)
num2 = st.number_input("Enter second number", value=0)

# Select operation
operation = st.selectbox("Select Operation", ["Add", "Subtract", "Multiply", "Divide"])

# Calculate
result = None
if st.button("Calculate"):
    if operation == "Add":
        result = num1 + num2
    elif operation == "Subtract":
        result = num1 - num2
    elif operation == "Multiply":
        result = num1 * num2
    elif operation == "Divide":
        if num2 != 0:
            result = num1 / num2
        else:
            st.error("Division by zero is not allowed!")

# Show result
if result is not None:
    st.success(f"Result = {result}")
