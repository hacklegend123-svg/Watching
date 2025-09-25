# app.py

import streamlit as st
import sqlite3

# ==============================
# Database Setup
# ==============================
conn = sqlite3.connect("jobs.db", check_same_thread=False)
c = conn.cursor()

# Users table with role
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
''')

# Jobs table
c.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        company TEXT,
        location TEXT,
        description TEXT,
        poster_email TEXT
    )
''')
conn.commit()

# ==============================
# Functions
# ==============================
def register_user(email, password, role):
    try:
        c.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (email, password, role))
        conn.commit()
        return True
    except:
        return False

def login_user(email, password):
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    return c.fetchone()

def add_job(title, company, location, description, poster_email):
    c.execute("INSERT INTO jobs (title, company, location, description, poster_email) VALUES (?, ?, ?, ?, ?)", 
              (title, company, location, description, poster_email))
    conn.commit()

def get_all_jobs():
    c.execute("SELECT * FROM jobs")
    return c.fetchall()

def get_jobs_by_user(email):
    c.execute("SELECT * FROM jobs WHERE poster_email=?", (email,))
    return c.fetchall()

def delete_job(job_id, email):
    c.execute("DELETE FROM jobs WHERE id=? AND poster_email=?", (job_id, email))
    conn.commit()

# ==============================
# Streamlit UI
# ==============================
st.title("🎯 Job Portal App")

# Session state for login
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.role = None

# ------------------------------
# If not logged in → show register/login
# ------------------------------
if not st.session_state.user:
    menu = ["Login", "Register"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Register":
        st.subheader("Create a New Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["seeker", "poster"])
        if st.button("Register"):
            if email and password:
                if register_user(email, password, role):
                    st.success("✅ Registration successful! Please login.")
                else:
                    st.error("⚠️ Email already registered.")
            else:
                st.error("⚠️ Please fill all fields.")

    elif choice == "Login":
        st.subheader("Login to Your Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(email, password)
            if user:
                st.session_state.user = user[1]   # email
                st.session_state.role = user[3]   # role
                st.success(f"✅ Logged in as {user[1]} ({user[3]})")
                st.experimental_rerun()
            else:
                st.error("⚠️ Invalid credentials.")

# ------------------------------
# If logged in → role-specific dashboard
# ------------------------------
else:
    st.sidebar.write(f"👤 Logged in as: {st.session_state.user} ({st.session_state.role})")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.role = None
        st.experimental_rerun()

    # =======================
    # Job Seeker Dashboard
    # =======================
    if st.session_state.role == "seeker":
        st.header("🔎 Browse Available Jobs")
        jobs = get_all_jobs()
        if jobs:
            for job in jobs:
                st.markdown(f"""
                ### {job[1]}  
                **Company:** {job[2]}  
                **Location:** {job[3]}  
                **Description:** {job[4]}  
                **Posted by:** {job[5]}  
                """)
                st.write("---")
        else:
            st.info("No jobs available right now. Please check back later!")

    # =======================
    # Job Poster Dashboard
    # =======================
    elif st.session_state.role == "poster":
        st.header("📢 Post a New Job")

        job_title = st.text_input("Job Title")
        job_company = st.text_input("Company Name")
        job_location = st.text_input("Location")
        job_description = st.text_area("Job Description")

        if st.button("Post Job"):
            if job_title and job_company and job_location and job_description:
                add_job(job_title, job_company, job_location, job_description, st.session_state.user)
                st.success("✅ Job posted successfully!")
                st.experimental_rerun()
            else:
                st.error("⚠️ Please fill in all fields before posting.")

        st.subheader("🗂 Your Posted Jobs")
        user_jobs = get_jobs_by_user(st.session_state.user)
        if user_jobs:
            for job in user_jobs:
                st.markdown(f"""
                ### {job[1]}  
                **Company:** {job[2]}  
                **Location:** {job[3]}  
                **Description:** {job[4]}  
                """)
                if st.button(f"❌ Delete {job[1]}", key=f"delete_{job[0]}"):
                    delete_job(job[0], st.session_state.user)
                    st.success(f"✅ Deleted job: {job[1]}")
                    st.experimental_rerun()
        else:
            st.info("You haven't posted any jobs yet.")
