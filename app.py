# app.py
# Smart Job Portal (single-file Streamlit app)
# - Role selection (Job Seeker / Job Poster)
# - Register / Login per role
# - Poster: create/view/delete jobs
# - Seeker: browse jobs & apply
# - SQLite used for persistence
# Deploy: Streamlit Cloud or Colab+ngrok

import streamlit as st
import sqlite3
from datetime import datetime
from typing import Optional

# -------------------------
# Styling (simple CSS for nicer cards)
# -------------------------
st.set_page_config(page_title="Smart Job Portal", layout="wide")
st.markdown(
    """
    <style>
    .app-header {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        padding: 18px 24px;
        border-radius: 8px;
        margin-bottom: 18px;
    }
    .job-card {
        border: 1px solid #e6e6e6;
        padding: 12px 14px;
        border-radius: 8px;
        background: #ffffff;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .muted { color: #6b7280; font-size: 0.9em; }
    .small { font-size: 0.9em; }
    .badge { background:#eef2ff; color:#3730a3; padding:4px 8px; border-radius:6px; font-weight:600; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="app-header"><h2>🚀 Smart Job Portal</h2><p style="margin:0">Role-based job system — Post, Browse & Apply (Streamlit + SQLite)</p></div>', unsafe_allow_html=True)

# -------------------------
# Database helpers
# -------------------------
DB_PATH = "jobs.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    # Users table: email unique, role -> 'seeker' or 'poster'
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)
    # Jobs table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poster_email TEXT,
        title TEXT,
        company TEXT,
        location TEXT,
        job_type TEXT,
        salary TEXT,
        contact TEXT,
        description TEXT,
        created_at TEXT
    )
    """)
    # Applications table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        applicant_email TEXT,
        cover_letter TEXT,
        applied_at TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# -------------------------
# CRUD functions
# -------------------------
def register_user(email: str, password: str, role: str) -> bool:
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    if cur.fetchone():
        conn.close()
        return False
    cur.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (email, password, role))
    conn.commit(); conn.close(); return True

def login_user(email: str, password: str, role: str) -> Optional[sqlite3.Row]:
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ? AND password = ? AND role = ?", (email, password, role))
    row = cur.fetchone()
    conn.close(); return row

def add_job(poster_email: str, title: str, company: str, location: str, job_type: str, salary: str, contact: str, description: str):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""INSERT INTO jobs (poster_email, title, company, location, job_type, salary, contact, description, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (poster_email, title, company, location, job_type, salary, contact, description, datetime.utcnow().isoformat()))
    conn.commit(); conn.close()

def get_all_jobs():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT * FROM jobs ORDER BY id DESC")
    rows = cur.fetchall(); conn.close(); return rows

def get_jobs_by_poster(poster_email: str):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT * FROM jobs WHERE poster_email = ? ORDER BY id DESC", (poster_email,))
    rows = cur.fetchall(); conn.close(); return rows

def delete_job(job_id: int, poster_email: str) -> bool:
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM jobs WHERE id = ? AND poster_email = ?", (job_id, poster_email))
    changed = cur.rowcount
    conn.commit(); conn.close()
    return changed > 0

def apply_job(job_id: int, applicant_email: str, cover_letter: str):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO applications (job_id, applicant_email, cover_letter, applied_at) VALUES (?, ?, ?, ?)",
                (job_id, applicant_email, cover_letter, datetime.utcnow().isoformat()))
    conn.commit(); conn.close()

def get_applications_for_job(job_id: int):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT * FROM applications WHERE job_id = ? ORDER BY id DESC", (job_id,))
    rows = cur.fetchall(); conn.close(); return rows

# -------------------------
# Session state: user info
# -------------------------
if "user" not in st.session_state:
    st.session_state.user = None  # dict: {email, role}

# -------------------------
# Top controls: choose entry role then auth
# -------------------------
st.sidebar.markdown("### 👤 Choose Role & Authenticate")
role_choice = st.sidebar.radio("I am a", ("Job Seeker", "Job Poster"))

st.sidebar.markdown("#### Account")
if not st.session_state.user:
    # show register / login tabs
    auth_tab = st.sidebar.selectbox("Action", ("Login", "Register"))
    email_input = st.sidebar.text_input("Email", key="auth_email")
    pwd_input = st.sidebar.text_input("Password", type="password", key="auth_pwd")

    if auth_tab == "Register":
        if st.sidebar.button("Create account"):
            if not email_input or not pwd_input:
                st.sidebar.error("Please enter email & password")
            else:
                ok = register_user(email_input.strip().lower(), pwd_input.strip(), role_choice.lower())
                if ok:
                    st.sidebar.success("Account created — please login")
                else:
                    st.sidebar.error("Email already registered. Please login.")
    else:  # Login
        if st.sidebar.button("Login"):
            if not email_input or not pwd_input:
                st.sidebar.error("Please enter email & password")
            else:
                user = login_user(email_input.strip().lower(), pwd_input.strip(), role_choice.lower())
                if user:
                    st.session_state.user = {"email": user["email"], "role": user["role"]}
                    st.experimental_rerun()
                else:
                    st.sidebar.error("Invalid credentials or wrong role selected.")
else:
    # show current user + logout
    st.sidebar.success(f'Logged in as {st.session_state.user["email"]} ({st.session_state.user["role"]})')
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.experimental_rerun()

# -------------------------
# Main area
# -------------------------
st.markdown("---")
col1, col2 = st.columns([3,1])
with col1:
    st.header("Find your next opportunity" if role_choice=="Job Seeker" else "Post a job & find talent")
    st.write("Simple, fast and friendly interface to post and apply for jobs.")
with col2:
    st.markdown('<div class="badge">Role: {}</div>'.format(role_choice), unsafe_allow_html=True)

st.markdown("")

# If user not logged in, show friendly message
if not st.session_state.user:
    st.info("Please register or login from the left sidebar to continue.")
    st.stop()

# If logged in but role in session must match selected top role; if mismatch, show notice
if st.session_state.user["role"] != role_choice.lower():
    st.warning(f"You are logged in as {st.session_state.user['role']}. Switch role selection in sidebar to match or logout & login.")
    st.stop()

# -------------------------
# Job Poster dashboard
# -------------------------
if role_choice == "Job Poster" and st.session_state.user:
    st.subheader("📋 Post a New Job")
    with st.form("job_post_form", clear_on_submit=True):
        title = st.text_input("Job Title")
        company = st.text_input("Company Name")
        location = st.text_input("Location (City / Remote)")
        job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Internship", "Contract"])
        salary = st.text_input("Salary / Compensation (optional)")
        contact = st.text_input("Contact (email/phone)")
        description = st.text_area("Job Description (responsibilities, skills required, perks...)")
        submitted = st.form_submit_button("Post Job")
        if submitted:
            if not (title and company and location and description and contact):
                st.error("Please fill Title, Company, Location, Contact and Description")
            else:
                add_job(st.session_state.user["email"], title.strip(), company.strip(), location.strip(),
                        job_type, salary.strip(), contact.strip(), description.strip())
                st.success("✅ Job posted successfully!")
                st.experimental_rerun()

    st.markdown("----")
    st.subheader("🗂 Your Posted Jobs")
    my_jobs = get_jobs_by_poster(st.session_state.user["email"])
    if my_jobs:
        for j in my_jobs:
            with st.container():
                st.markdown(f'<div class="job-card">', unsafe_allow_html=True)
                st.markdown(f"**{j['title']}**  \n**Company:** {j['company']}  \n**Location:** {j['location']}  \n**Type:** {j['job_type']}  \n**Salary:** {j['salary'] or '—'}  \n**Contact:** {j['contact']}", unsafe_allow_html=True)
                st.write("")
                st.write(j['description'])
                cols = st.columns([1,1,3])
                if cols[0].button("View Applicants", key=f"viewapp_{j['id']}"):
                    apps = get_applications_for_job(j['id'])
                    if apps:
                        for a in apps:
                            st.markdown(f"• **{a['applicant_email']}** — {a['applied_at']}  \n> {a['cover_letter']}")
                    else:
                        st.info("No applications yet for this job.")
                if cols[1].button("Delete Job", key=f"del_{j['id']}"):
                    ok = delete_job(j['id'], st.session_state.user["email"])
                    if ok:
                        st.success("Job deleted")
                        st.experimental_rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("You haven't posted any jobs yet.")

# -------------------------
# Job Seeker dashboard
# -------------------------
elif role_choice == "Job Seeker" and st.session_state.user:
    st.subheader("🔎 Browse & Apply to Jobs")

    jobs = get_all_jobs()
    if not jobs:
        st.info("No jobs posted yet. Check back soon!")
    else:
        for j in jobs:
            # card layout
            st.markdown(f'<div class="job-card">', unsafe_allow_html=True)
            header_cols = st.columns([4,2])
            header_cols[0].markdown(f"### {j['title']}")
            header_cols[1].markdown(f"<div class='badge'>{j['job_type']}</div>", unsafe_allow_html=True)
            st.markdown(f"**Company:** {j['company']}  •  **Location:** {j['location']}  •  **Posted by:** {j['poster_email']}", unsafe_allow_html=True)
            st.write("")
            st.write(j['description'])
            bottom_cols = st.columns([3,2])
            if bottom_cols[1].button("Apply", key=f"apply_{j['id']}"):
                # show modal-ish application area (simple)
                with st.form(f"apply_form_{j['id']}"):
                    cover = st.text_area("Write a short message / cover letter (optional)", key=f"cover_{j['id']}")
                    submit_app = st.form_submit_button("Submit Application")
                    if submit_app:
                        apply_job(j['id'], st.session_state.user["email"], cover.strip())
                        st.success("✅ Application submitted!")
                        st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# End
st.markdown("<br><br><div class='muted small'>Built with ❤️ using Streamlit • Data stored with SQLite</div>", unsafe_allow_html=True)
