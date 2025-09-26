import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Page configuration for attractive UI
st.set_page_config(
    page_title="Job Portal",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize SQLite database
@st.cache_resource
def init_db():
    conn = sqlite3.connect('job_portal.db')
    c = conn.cursor()
    
    # Create jobs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            job_type TEXT NOT NULL,  -- 'Full Time' or 'Part Time'
            salary_range TEXT,
            location TEXT,
            contact_email TEXT NOT NULL,
            contact_phone TEXT,
            posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            poster_name TEXT
        )
    ''')
    
    # Create applications table
    c.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            seeker_name TEXT NOT NULL,
            seeker_email TEXT NOT NULL,
            apply_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs (id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Function to add job
def add_job(title, description, job_type, salary_range, location, contact_email, contact_phone, poster_name):
    conn = sqlite3.connect('job_portal.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO jobs (title, description, job_type, salary_range, location, contact_email, contact_phone, poster_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, description, job_type, salary_range, location, contact_email, contact_phone, poster_name))
    conn.commit()
    conn.close()
    st.success("Job posted successfully! 🎉")

# Function to get all jobs
def get_jobs():
    conn = sqlite3.connect('job_portal.db')
    df = pd.read_sql_query("SELECT * FROM jobs ORDER BY posted_date DESC", conn)
    conn.close()
    return df

# Function to apply for job
def apply_job(job_id, seeker_name, seeker_email):
    conn = sqlite3.connect('job_portal.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO applications (job_id, seeker_name, seeker_email)
        VALUES (?, ?, ?)
    ''', (job_id, seeker_name, seeker_email))
    conn.commit()
    conn.close()
    st.success("Application submitted successfully! 📝")

# Main App
def main():
    st.title("💼 Welcome to Job Portal")
    st.markdown("---")
    
    # Role selection
    if 'role' not in st.session_state:
        st.session_state.role = None
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👤 Job Seeker", use_container_width=True, key="seeker_btn"):
            st.session_state.role = "seeker"
            st.rerun()
    
    with col2:
        if st.button("🏢 Job Poster", use_container_width=True, key="poster_btn"):
            st.session_state.role = "poster"
            st.rerun()
    
    if st.session_state.role is None:
        st.info("Please select your role to proceed. 🚀")
        return
    
    # Sidebar for user info (simple, no real auth)
    with st.sidebar:
        st.header("User  Info")
        if st.session_state.role == "seeker":
            name = st.text_input("Your Name", placeholder="Enter your name")
            email = st.text_input("Your Email", placeholder="Enter your email")
        else:
            poster_name = st.text_input("Your Name (Poster)", placeholder="Enter your name")
    
    # Job Poster Section
    if st.session_state.role == "poster":
        st.header("📝 Post a New Job")
        st.markdown("Fill in the details below to post a job opening.")
        
        with st.form("job_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Job Title", placeholder="e.g., Software Engineer")
                job_type = st.selectbox("Job Type", ["Full Time", "Part Time"])
                salary_range = st.text_input("Salary Range", placeholder="e.g., $50,000 - $70,000")
                location = st.text_input("Location", placeholder="e.g., Remote / New York")
            
            with col2:
                description = st.text_area("Job Description", placeholder="Describe the job responsibilities...", height=150)
                contact_email = st.text_input("Contact Email", placeholder="your.email@company.com")
                contact_phone = st.text_input("Contact Phone", placeholder="e.g., +1-123-456-7890")
            
            submitted = st.form_submit_button("Post Job 🚀", use_container_width=True)
            
            if submitted:
                if title and description and contact_email and poster_name:
                    add_job(title, description, job_type, salary_range, location, contact_email, contact_phone, poster_name)
                    st.rerun()
                else:
                    st.error("Please fill in all required fields! ⚠️")
        
        # View posted jobs
        st.subheader("📋 Your Posted Jobs")
        jobs_df = get_jobs()
        if not jobs_df.empty:
            for _, job in jobs_df.iterrows():
                with st.expander(f"**{job['title']}** - {job['job_type']} | {job['location']}"):
                    st.write(f"**Description:** {job['description']}")
                    st.write(f"**Salary:** {job['salary_range']}")
                    st.write(f"**Contact:** {job['contact_email']} | {job['contact_phone']}")
                    st.write(f"**Posted on:** {job['posted_date']}")
        else:
            st.info("No jobs posted yet. Post one above! 📭")
    
    # Job Seeker Section
    elif st.session_state.role == "seeker":
        st.header("🔍 Browse Jobs")
        st.markdown("Explore available job opportunities and apply directly.")
        
        jobs_df = get_jobs()
        if jobs_df.empty:
            st.warning("No jobs available at the moment. Check back later! ⏳")
            return
        
        for idx, job in jobs_df.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"### **{job['title']}**")
                st.write(f"**Type:** {job['job_type']} | **Location:** {job['location']} | **Salary:** {job['salary_range']}")
                st.write(job['description'])
                st.write(f"**Contact:** {job['contact_email']} | {job['contact_phone']}")
                st.caption(f"Posted on: {job['posted_date']}")
            
            with col2:
                if st.button(f"Apply Now 💼", key=f"apply_{job['id']}", use_container_width=True):
                    if name and email:
                        apply_job(job['id'], name, email)
                        st.rerun()
                    else:
                        st.error("Please enter your name and email in the sidebar! ⚠️")
            
            with col3:
                st.caption(f"Posted by: {job['poster_name']}")
            
            st.markdown("---")
        
        # View applications
        st.subheader("📋 Your Applications")
        conn = sqlite3.connect('job_portal.db')
        apps_df = pd.read_sql_query('''
            SELECT a.*, j.title FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE seeker_email = ?
            ORDER BY apply_date DESC
        ''', conn, params=(email,) if 'email' in locals() else ('',))
        conn.close()
        
        if not apps_df.empty:
            for _, app in apps_df.iterrows():
                st.info(f"Applied to: **{app['title']}** on {app['apply_date']}")
        else:
            st.info("No applications yet. Apply for jobs above! 📝")

if __name__ == "__main__":
    main()
