c.execute('''INSERT INTO exercise_sets (session_id, exercise_name, set_number, weight, reps, rpe) 
                             VALUES (?, ?, ?, ?, ?, ?)''', 
                          (st.session_state['current_session_id'], exercise, set_num, weight, reps, rpe))
                conn.commit()
                st.success(f"Logged: {exercise} - {weight} x {reps}")

# --- Page 3: View Dashboard ---
elif choice == "View Dashboard":
    st.header("📈 Progress Dashboard")
    
    # Fetch Data
    df_nutrition = pd.read_sql_query("SELECT * FROM daily_nutrition ORDER BY date", conn)
    
    if not df_nutrition.empty:
        df_nutrition['date'] = pd.to_datetime(df_nutrition['date'])
        df_nutrition.set_index('date', inplace=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Bodyweight Over Time")
            st.line_chart(df_nutrition['bodyweight'])
            
        with col2:
            st.subheader("Calorie Intake Over Time")
            st.line_chart(df_nutrition['total_calories'])
    else:
        st.info("No nutrition data logged yet.")
        
    st.divider()
    st.subheader("Recent Workout Sets")
    
    query_sets = '''
        SELECT ws.date, ws.routine_type, es.exercise_name, es.set_number, es.weight, es.reps, es.rpe
        FROM exercise_sets es
        JOIN workout_sessions ws ON es.session_id = ws.session_id
        ORDER BY ws.date DESC, es.session_id DESC, es.set_number ASC
    '''
    df_sets = pd.read_sql_query(query_sets, conn)
    
    if not df_sets.empty:
        st.dataframe(df_sets, use_container_width=True)
    else:
        st.info("No workouts logged yet.")

conn.close()
