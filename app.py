import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# --- Database Initialization ---
def init_db():
    conn = sqlite3.connect('fitness_tracker.db')
    c = conn.cursor()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS daily_nutrition (
            date TEXT PRIMARY KEY, bodyweight REAL, total_calories INTEGER
        );
        CREATE TABLE IF NOT EXISTS workout_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, routine_type TEXT, duration INTEGER
        );
        CREATE TABLE IF NOT EXISTS exercise_sets (
            set_id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, exercise_name TEXT, 
            set_number INTEGER, weight REAL, reps INTEGER, rpe INTEGER,
            FOREIGN KEY(session_id) REFERENCES workout_sessions(session_id)
        );
    ''')
    conn.commit()
    return conn

conn = init_db()

# --- App Configuration ---
st.set_page_config(page_title="Fitness Tracker", layout="wide")
st.title("🏋️‍♂️ Fitness & Nutrition Tracker")

# Sidebar Navigation
menu = ["Log Nutrition & Vitals", "Log Workout", "View Dashboard"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- Page 1: Log Nutrition ---
if choice == "Log Nutrition & Vitals":
    st.header("Log Daily Nutrition & Bodyweight")
    
    with st.form("nutrition_form"):
        log_date = st.date_input("Date", date.today())
        weight = st.number_input("Bodyweight (lbs/kg)", min_value=0.0, format="%.1f")
        calories = st.number_input("Total Calories (kcal)", min_value=0, step=50)
        
        submit_nutrition = st.form_submit_button("Save Daily Log")
        
        if submit_nutrition:
            c = conn.cursor()
            c.execute('INSERT OR REPLACE INTO daily_nutrition (date, bodyweight, total_calories) VALUES (?, ?, ?)', 
                      (str(log_date), weight, calories))
            conn.commit()
            st.success(f"Successfully logged {calories} kcal and {weight} weight for {log_date}!")

# --- Page 2: Log Workout ---
elif choice == "Log Workout":
    st.header("Log Your Workout Sessions")
    
    # Step 1: Create or select a session
    st.subheader("1. Start a New Session")
    with st.form("session_form"):
        log_date = st.date_input("Date of Workout", date.today())
        routine = st.selectbox("Routine Type", ["Push", "Pull", "Legs", "Upper", "Lower", "Full Body", "Cardio"])
        duration = st.number_input("Duration (minutes)", min_value=0, step=5)
        
        submit_session = st.form_submit_button("Start Session")
        
        if submit_session:
            c = conn.cursor()
            c.execute('INSERT INTO workout_sessions (date, routine_type, duration) VALUES (?, ?, ?)', 
                      (str(log_date), routine, duration))
            conn.commit()
            st.session_state['current_session_id'] = c.lastrowid
            st.success(f"Session started! ID: {st.session_state['current_session_id']}")

    # Step 2: Log sets for the active session
    if 'current_session_id' in st.session_state:
        st.divider()
        st.subheader(f"2. Log Sets (Session #{st.session_state['current_session_id']})")
        
        with st.form("set_form"):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1: exercise = st.text_input("Exercise", placeholder="e.g. Bench Press")
            with col2: set_num = st.number_input("Set #", min_value=1, step=1)
            with col3: weight = st.number_input("Weight", min_value=0.0, step=2.5)
            with col4: reps = st.number_input("Reps", min_value=0, step=1)
            with col5: rpe = st.slider("RPE (Difficulty)", 1, 10, 8)
            
            submit_set = st.form_submit_button("Add Set")
            
            if submit_set:
                c = conn.cursor()
