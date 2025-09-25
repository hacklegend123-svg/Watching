# app.py

import streamlit as st
import sqlite3

# ==============================
# Database Setup
# ==============================
conn = sqlite3.connect("jobs.db", check_same_thread=False)
c = conn.cursor()

# Create jobs table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        company TEXT,
        location TEXT,
        description TEXT
    )
''')
conn.commit()

# ==============================
# Functions
# ==============================
def add_job(title, company, location, description):
    c.execute("INSERT INTO jobs (title, company, location, description) VALUES (?, ?, ?, ?)", 
              (title, company, location, description))
    conn.commit()

def get_all_jobs():
    c.execute("SELECT * FROM jobs")
    return c.fetchall()

# ==============================
# Streamlit UI
# ==============================
st.title("Job Portal App 👩‍💻👨‍💼")

menu = ["Job Seeker", "Job Poster"]
choice = st.sidebar.selectbox("Select Role", menu)

# ------------------------------
# Job Seeker Section
# ------------------------------
if choice == "Job Seeker":
    st.subheader("Browse Available Jobs")
    jobs = get_all_jobs()
    if jobs:
        for job in jobs:
            st.markdown(f"""
            ### {job[1]}  
            **Company:** {job[2]}  
            **Location:** {job[3]}  
            **Description:** {job[4]}  
            """)
            st.write("---")
    else:
        st.info("No jobs available right now. Please check back later!")

# ------------------------------
# Job Poster Section
# ------------------------------
elif choice == "Job Poster":
    st.subheader("Post a New Job")

    job_title = st.text_input("Job Title")
    job_company = st.text_input("Company Name")
    job_location = st.text_input("Location")
    job_description = st.text_area("Job Description")

    if st.button("Post Job"):
        if job_title and job_company and job_location and job_description:
            add_job(job_title, job_company, job_location, job_description)
            st.success("✅ Job posted successfully!")
        else:
            st.error("⚠️ Please fill in all fields before posting.")
