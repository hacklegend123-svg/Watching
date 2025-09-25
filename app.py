# app.py

import streamlit as st
import sqlite3

# ==============================
# Database Setup
# ==============================
conn = sqlite3.connect("jobs.db", check_same_thread=False)
c = conn.cursor()

# Reset and create fresh tables every time (safe for prototype)
c.execute("DROP TABLE IF EXISTS users")
c.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
''')

c.execute("DROP TABLE IF EXISTS jobs")
c.execute('''
    CREATE TABLE jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poster_email TEXT,
        title TEXT,
        company TEXT,
        location TEXT,
        description TEXT
    )
''')
conn.commit()

# ==============================
# Helper Functions
# ==============================
def register_user(email, password, role):
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    if c.fetchone():
        return False  # User already exists
    else:
        c.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (email, password, role))
        conn.commit()
        return True

def login_user(email, password, role):
    c.execute("SELECT * FROM users WHERE email=? AND password=? AND role=?", (email, password, role))
    return c.fetchone()

def add_job(poster_email, title, company, location, description):
    c.execute("INSERT INTO jobs (poster_email, title, company, location, description) VALUES (?, ?, ?, ?, ?)", 
              (poster_email, title, company, location, description))
    conn.commit()

def get_all_jobs():
    c.execute("SELECT * FROM jobs")
    return c.fetchall()

def get_user_jobs(poster_email):
    c.execute("SELECT * FROM jobs WHERE poster_email=?", (poster_email,))
    return c.fetchall()

def delete_job(job_id, poster_email):
    c.execute("DELETE FROM jobs WHERE id=? AND poster_email=?", (job_id, poster_email))
    conn.commit()

# ==============================
# Streamlit UI
# ==============================
st.title("Job Portal App 👩‍💻👨‍💼")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# Track session
if "user" not in st.session_state:
    st.session_state["user"] = None

# ------------------------------
# Registration
# ------------------------------
if choice == "Register":
    st.subheader("Create a New Account")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.radio("Role", ["Job Seeker", "Job Poster"])

    if st.button("Register"):
        if email and password:
            if register_user(email, password, role):
                st.success("✅ Registration successful! Please login.")
            else:
                st.error("⚠️ Email already registered. Please login instead.")
        else:
            st.error("⚠️ Please fill in all fields.")

# ------------------------------
# Login
# ------------------------------
elif choice == "Login":
    st.subheader("Login to Your Account")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.radio("Role", ["Job Seeker", "Job Poster"])

    if st.button("Login"):
        user = login_user(email, password, role)
        if user:
            st.session_state["user"] = {"email": email, "role": role}
            st.success(f"✅ Logged in as {role}")
        else:
            st.error("❌ Invalid credentials or role mismatch")

# ------------------------------
# Logged-in Area
# ------------------------------
if st.session_state["user"]:
    role = st.session_state["user"]["role"]
    email = st.session_state["user"]["email"]

    st.sidebar.write(f"👤 Logged in as {email} ({role})")
    if st.sidebar.button("Logout"):
        st.session_state["user"] = None
        st.rerun()

    # If Job Seeker
    if role == "Job Seeker":
        st.subheader("Browse Available Jobs")
        jobs = get_all_jobs()
        if jobs:
            for job in jobs:
                st.markdown(f"""
                ### {job[2]}  
                **Company:** {job[3]}  
                **Location:** {job[4]}  
                **Description:** {job[5]}  
                """)
                st.write("---")
        else:
            st.info("No jobs available right now. Please check back later!")

    # If Job Poster
    elif role == "Job Poster":
        st.subheader("Post a New Job")

        job_title = st.text_input("Job Title")
        job_company = st.text_input("Company Name")
        job_location = st.text_input("Location")
        job_description = st.text_area("Job Description")

        if st.button("Post Job"):
            if job_title and job_company and job_location and job_description:
                add_job(email, job_title, job_company, job_location, job_description)
                st.success("✅ Job posted successfully!")
            else:
                st.error("⚠️ Please fill in all fields before posting.")

        st.subheader("Your Posted Jobs")
        my_jobs = get_user_jobs(email)
        if my_jobs:
            for job in my_jobs:
                st.markdown(f"""
                ### {job[2]}  
                **Company:** {job[3]}  
                **Location:** {job[4]}  
                **Description:** {job[5]}  
                """)
                if st.button(f"Delete Job {job[0]}", key=f"delete_{job[0]}"):
                    delete_job(job[0], email)
                    st.success("🗑️ Job deleted successfully!")
                    st.rerun()
                st.write("---")
        else:
            st.info("You haven't posted any jobs yet.")
