# app.py - Complete Job Portal with Streamlit + Python + SQLite
import streamlit as st
import sqlite3
import hashlib
import datetime
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Hinglish Job Portal", 
    page_icon="💼", 
    layout="wide"
)

# Database setup
def init_database():
    conn = sqlite3.connect('jobportal.db', check_same_thread=False)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        user_type TEXT NOT NULL,
        full_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Jobs table
    c.execute('''CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        required_skills TEXT,
        pay_amount REAL,
        pay_type TEXT,
        location TEXT,
        contact_email TEXT,
        contact_phone TEXT,
        poster_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (poster_id) REFERENCES users (id)
    )''')
    
    # Applications table
    c.execute('''CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        seeker_id INTEGER NOT NULL,
        application_text TEXT,
        status TEXT DEFAULT 'pending',
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id),
        FOREIGN KEY (seeker_id) REFERENCES users (id)
    )''')
    
    conn.commit()
    conn.close()

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Database connection
def get_db_connection():
    return sqlite3.connect('jobportal.db', check_same_thread=False)

# Authentication functions
def sign_up_user(email, password, user_type, full_name):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        hashed_password = hash_password(password)
        c.execute('INSERT INTO users (email, password_hash, user_type, full_name) VALUES (?, ?, ?, ?)',
                 (email, hashed_password, user_type, full_name))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(email, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_password = hash_password(password)
    
    c.execute('SELECT * FROM users WHERE email = ? AND password_hash = ?', 
             (email, hashed_password))
    user = c.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'email': user[1],
            'user_type': user[3],
            'full_name': user[4]
        }
    return None

# Job functions
def create_job(job_data, poster_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''INSERT INTO jobs 
                 (title, description, required_skills, pay_amount, pay_type, location, contact_email, contact_phone, poster_id) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
             (job_data['title'], job_data['description'], job_data['skills'], 
              job_data['pay_amount'], job_data['pay_type'], job_data['location'],
              job_data['contact_email'], job_data['contact_phone'], poster_id))
    
    conn.commit()
    conn.close()

def get_all_jobs():
    conn = get_db_connection()
    df = pd.read_sql_query('''SELECT j.*, u.full_name as poster_name 
                              FROM jobs j 
                              JOIN users u ON j.poster_id = u.id 
                              ORDER BY j.created_at DESC''', conn)
    conn.close()
    return df

def get_jobs_by_poster(poster_id):
    conn = get_db_connection()
    df = pd.read_sql_query('SELECT * FROM jobs WHERE poster_id = ? ORDER BY created_at DESC', 
                          conn, params=(poster_id,))
    conn.close()
    return df

def apply_for_job(job_id, seeker_id, application_text):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('INSERT INTO applications (job_id, seeker_id, application_text) VALUES (?, ?, ?)',
             (job_id, seeker_id, application_text))
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

# Main App
def main():
    st.title("💼 Hinglish Job Portal")
    st.markdown("---")
    
    # Check if user is logged in
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # If not logged in, show login/signup page
    if not st.session_state.user:
        show_landing_page()
    else:
        # User is logged in, show appropriate dashboard
        if st.session_state.user['user_type'] == 'poster':
            show_poster_dashboard()
        else:
            show_seeker_dashboard()

def show_landing_page():
    st.header("Welcome to Hinglish Job Portal!")
    
    tab1, tab2 = st.tabs(["🚀 Login", "📝 Sign Up"])
    
    with tab1:
        st.subheader("Login to Your Account")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if login_email and login_password:
                user = login_user(login_email, login_password)
                if user:
                    st.session_state.user = user
                    st.success(f"Welcome back, {user['full_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
            else:
                st.warning("Please fill all fields")
    
    with tab2:
        st.subheader("Create New Account")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        signup_fullname = st.text_input("Full Name", key="signup_fullname")
        user_type = st.selectbox("I am a:", ["Job Seeker", "Job Poster"], key="user_type")
        
        if st.button("Sign Up"):
            if signup_email and signup_password and signup_fullname:
                success = sign_up_user(signup_email, signup_password, 
                                      user_type.lower().replace(" ", "_"), 
                                      signup_fullname)
                if success:
                    st.success("Account created successfully! Please login.")
                else:
                    st.error("Email already exists")
            else:
                st.warning("Please fill all fields")

def show_poster_dashboard():
    user = st.session_state.user
    st.header(f"👋 Welcome, {user['full_name']} (Job Poster)")
    
    tab1, tab2 = st.tabs(["📤 Post New Job", "📊 My Job Posts"])
    
    with tab1:
        st.subheader("Create New Job Post")
        
        with st.form("job_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Job Title*")
                skills = st.text_input("Required Skills (comma separated)")
                pay_amount = st.number_input("Pay Amount", min_value=0)
                pay_type = st.selectbox("Pay Type", ["hourly", "daily", "monthly", "fixed"])
                location = st.text_input("Location")
            
            with col2:
                description = st.text_area("Job Description*", height=150)
                contact_email = st.text_input("Contact Email*")
                contact_phone = st.text_input("Contact Phone")
            
            if st.form_submit_button("Post Job"):
                if title and description and contact_email:
                    job_data = {
                        'title': title,
                        'description': description,
                        'skills': skills,
                        'pay_amount': pay_amount,
                        'pay_type': pay_type,
                        'location': location,
                        'contact_email': contact_email,
                        'contact_phone': contact_phone
                    }
                    create_job(job_data, user['id'])
                    st.success("Job posted successfully!")
                else:
                    st.error("Please fill required fields (*)")
    
    with tab2:
        st.subheader("Your Job Posts")
        jobs_df = get_jobs_by_poster(user['id'])
        
        if not jobs_df.empty:
            for _, job in jobs_df.iterrows():
                with st.expander(f"{job['title']} - {job['created_at'][:10]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Description:** {job['description']}")
                        st.write(f"**Skills:** {job['required_skills']}")
                    with col2:
                        st.write(f"**Pay:** {job['pay_amount']} {job['pay_type']}")
                        st.write(f"**Location:** {job['location']}")
                        st.write(f"**Contact:** {job['contact_email']} | {job['contact_phone']}")
        else:
            st.info("You haven't posted any jobs yet.")

def show_seeker_dashboard():
    user = st.session_state.user
    st.header(f"👋 Welcome, {user['full_name']} (Job Seeker)")
    
    st.subheader("🔍 Available Jobs")
    jobs_df = get_all_jobs()
    
    if not jobs_df.empty:
        for _, job in jobs_df.iterrows():
            with st.container():
                st.markdown(f"### {job['title']}")
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**Posted by:** {job['poster_name']}")
                    st.write(f"**Description:** {job['description'][:200]}...")
                    st.write(f"**Skills required:** {job['required_skills']}")
                    st.write(f"**Pay:** {job['pay_amount']} {job['pay_type']} | **Location:** {job['location']}")
                
                with col2:
                    if st.button("View Details", key=f"view_{job['id']}"):
                        st.session_state[f"show_job_{job['id']}"] = True
                
                with col3:
                    application_text = st.text_area(
                        "Why are you interested?", 
                        key=f"app_text_{job['id']}",
                        placeholder="Tell why you're a good fit...",
                        height=80
                    )
                    if st.button("Apply Now", key=f"apply_{job['id']}"):
                        if application_text:
                            apply_for_job(job['id'], user['id'], application_text)
                            st.success("Application submitted successfully!")
                        else:
                            st.warning("Please write something about why you're interested")
                
                if st.session_state.get(f"show_job_{job['id']}", False):
                    st.markdown("---")
                    st.write(f"**Full Description:** {job['description']}")
                    st.write(f"**Contact Email:** {job['contact_email']}")
                    st.write(f"**Contact Phone:** {job['contact_phone']}")
                    st.markdown("---")
                
                st.markdown("---")
    else:
        st.info("No jobs available at the moment. Check back later!")
    
    # Logout button
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

if __name__ == "__main__":
    main()
