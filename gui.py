import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Student Performance Dashboard", layout="wide")

# Initialize session state for navigation and data storage
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'selected_track' not in st.session_state:
    st.session_state.selected_track = None
if 'selected_student' not in st.session_state:
    st.session_state.selected_student = None

# Helper function to color-code the total score
def color_total_score(val):
    if val >= 8:
        return 'background-color: lightgreen; color: black'
    elif 7 <= val < 8:
        return 'background-color: lightblue; color: black'
    else:
        return 'background-color: salmon; color: black'

# Helper function for creating cards with correct layout and styling
def create_skill_card(skill_name, score):
    st.markdown(f"""
    <div style="background-color: white; padding: 10px; border-radius: 20px; 
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); margin-bottom: 20px; width: 200px; height: 120px; 
    display: flex; flex-direction: column; align-items: center; justify-content: center;">
        <h6 style="color: #333; font-size: 16px; font-weight: bold; margin-bottom: 5px;">{skill_name}</h6>
        <p style="font-size: 32px; font-weight: bold; color: black; margin: 0;">{score:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

# 1. Landing Page with File Upload
def landing_page():
    st.write("""
    # Student Performance Dashboard 
    
    ### Upload a CSV or Excel file to get started:
    """)

    # File uploader
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

    # If a new file is uploaded, reset the selected track and student
    if uploaded_file is not None:
        if uploaded_file.name.endswith('csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Store the data in session state for later use
        st.session_state.uploaded_data = df
        st.session_state.selected_track = None  # Reset the selected track
        st.session_state.selected_student = None  # Reset selected student

    # Show the track buttons if the file has been uploaded
    if st.session_state.uploaded_data is not None:
        df = st.session_state.uploaded_data

        # Display available tracks based on unique track values in the file
        available_tracks = df['Track'].unique()  # Assuming the data contains a "Track" column
        st.write("### Select below the track you would like to view:")
        
        # Dynamically create buttons for each track
        for track in available_tracks:
            if st.button(track):
                st.session_state.selected_track = track
                st.session_state.page = 'track_details'
                st.experimental_rerun()  # Trigger rerun to go to the next page

# 2. Track Details Page
def track_details_page():
    # Fetch the uploaded data
    df = st.session_state.uploaded_data
    selected_track = st.session_state.selected_track

    if df is None or selected_track is None:
        st.session_state.page = 'home'
        st.experimental_rerun()  # Go back to the home page if no data is available

    # Filter data for the selected track and create a copy
    track_data = df[df['Track'] == selected_track].copy()

    st.write(f"## {selected_track} Ranking")

    # Exclude "Track", "Rank", "Interviewer Comments 1", "Interviewer Comments 2", "CV", and "Code Files" from the main table
    if 'Interviewer Comments 1' in track_data.columns and 'Interviewer Comments 2' in track_data.columns:
        track_data = track_data.drop(columns=['Track', 'Rank', 'Interviewer Comments 1', 'Interviewer Comments 2', 'CV', 'Code Files'])
    else:
        track_data = track_data.drop(columns=['Track', 'Rank', 'CV', 'Code Files'])  # Only drop Track, Rank, CV, and Code Files if comments aren't present

    # Format numerical columns to 2 decimal places
    track_data['Soft Skills'] = track_data['Soft Skills'].round(2)
    track_data['Technical Skills'] = track_data['Technical Skills'].round(2)
    track_data['Total Score'] = track_data['Total Score'].round(2)

    # Apply formatting for 2 decimal places in the display
    format_dict = {'Soft Skills': "{:.2f}", 'Technical Skills': "{:.2f}", 'Total Score': "{:.2f}"}

    # Color the total score based on thresholds
    styled_df = track_data.style.format(format_dict).applymap(color_total_score, subset=['Total Score'])

    # Display the ranking table with relevant columns
    st.write(styled_df.to_html(), unsafe_allow_html=True)

    # Status badges aligned to the right
    st.write("---")
    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown("""
        <div style="background-color: lightgreen; padding: 8px; text-align: center; border-radius: 6px; margin-bottom: 10px; color: black; font-weight: bold; font-size: 12px;">
        HIGHLY RECOMMENDED
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background-color: lightblue; padding: 8px; text-align: center; border-radius: 6px; margin-bottom: 10px; color: black; font-weight: bold; font-size: 12px;">
        RECOMMENDED
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background-color: salmon; padding: 8px; text-align: center; border-radius: 6px; margin-bottom: 10px; color: black; font-weight: bold; font-size: 12px;">
        NOT RECOMMENDED
        </div>
        """, unsafe_allow_html=True)

    # Grey button for "Click here for details"
    with col1:
        st.markdown("""
        <style>
        div.stButton > button {
            background-color: grey;
            color: white;
            font-size: 12px;
            padding: 6px 15px;
            border-radius: 5px;
        }
        div.stButton > button:hover {
            background-color: #5a5a5a;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)

        if st.button("Click here for details"):
            st.session_state.page = 'student_details'
            st.experimental_rerun()  # Trigger rerun to go to the student details page

    # Back button to go back to the landing page
    if st.button('Back'):
        st.session_state.page = 'home'
        st.experimental_rerun()  # Trigger rerun to go back to the home page

# 3. Student Details Page (Updated with Interview Comments and color-based badges)
def student_details_page():
    # Fetch the uploaded data and selected values
    df = st.session_state.uploaded_data
    selected_track = st.session_state.selected_track

    # Select student from dropdown
    selected_student = st.selectbox("Select Student Name", df[df['Track'] == selected_track]['Student Name'].unique())

    student_data = df[(df['Track'] == selected_track) & (df['Student Name'] == selected_student)].iloc[0]

    st.write(f"## Evaluations for {student_data['Student Name']}")

    # Layout for soft skills, technical skills, ranking, and highly recommended badges in a single line
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        create_skill_card("Soft Skills", student_data['Soft Skills'])

    with col2:
        create_skill_card("Technical Skills", student_data['Technical Skills'])

    with col3:
        # Rank box with "Rank" first, then the actual rank
        st.markdown(f"""
        <div style="text-align: left;">
            <div style="background-color: #0044cc; padding: 20px; border-radius: 10px; color: white; width: 100px; margin: 10px auto;">
                <p style="font-size: 14px; margin: 0;">RANK</p>
                <p style="font-size: 30px; margin: 0;">{student_data['Rank']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        # Change badge color dynamically based on the score
        total_score = student_data['Total Score']
        badge_color = ""
        if total_score >= 8:
            badge_color = 'lightgreen'
        elif 7 <= total_score < 8:
            badge_color = 'lightblue'
        else:
            badge_color = 'salmon'

        # Dynamic Highly Recommended/Recommended/Not Recommended badge based on the total score
        st.markdown(f"""
        <div style="text-align: left;">
            <div style="background-color: {badge_color}; padding: 15px 30px; border-radius: 10px; color: black; font-weight: bold; margin-top: 10px;">
                {"Highly Recommended" if total_score >= 8 else "Recommended" if total_score >= 7 else "Not Recommended"}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Separate row for buttons for View CV and View Code Files
    st.write("---")
    col5, col6 = st.columns([1, 2.8])

    with col5:
        if 'CV' in student_data and pd.notna(student_data['CV']):
            st.markdown(f'''
                <a href="{student_data["CV"]}" target="_blank">
                    <div style="background-color: #dcdcdc; border-radius: 10px; padding: 10px; text-align: center; 
                    border: 2px solid #0056b3; width: 150px; margin-top: 10px;">
                        <span style="color: black; font-weight: bold; text-decoration: underline; font-size: 16px;">View CV</span>
                    </div>
                </a>
            ''', unsafe_allow_html=True)
        else:
            st.write("No CV Available")

    with col6:
        if 'Code Files' in student_data and pd.notna(student_data['Code Files']):
            st.markdown(f'''
                <a href="{student_data["Code Files"]}" target="_blank">
                    <div style="background-color: #dcdcdc; border-radius: 10px; padding: 10px; text-align: center; 
                    border: 2px solid #0056b3; width: 150px; margin-top: 10px;">
                        <span style="color: black; font-weight: bold; text-decoration: underline; font-size: 16px;">View Code Files</span>
                    </div>
                </a>
            ''', unsafe_allow_html=True)
        else:
            st.write("No Code Files Available")

    # Add space between the buttons and Total Score
    st.markdown("""
        <style>
        .total-score {
            margin-top: 10px;  /* Control the vertical space here (increase or decrease the value) */
        }
        </style>
    """, unsafe_allow_html=True)

    # Total Score and Rank with controlled margin
    st.markdown(f"<h3 class='total-score'>Total Score: {student_data['Total Score']}</h3>", unsafe_allow_html=True)

    # Colored Interview Comments Section
    st.markdown("""
    <h3 style="color: #0044cc; font-weight: bold;">Interview Comments</h3>
    """, unsafe_allow_html=True)

    # Display both Interview Comments columns
    if 'Interviewer Comments 1' in df.columns and 'Interviewer Comments 2' in df.columns:
        comments = f"""
        **Interviewer 1**: {student_data['Interviewer Comments 1']}  
        **Interviewer 2**: {student_data['Interviewer Comments 2']}
        """
        st.markdown(comments)
    else:
        st.write("No Interview Comments available.")

    # Back button to track details page
    if st.button('Back'):
        st.session_state.page = 'track_details'
        st.experimental_rerun()  # Trigger rerun to go back to the track details page

# Navigation logic: based on current page in session state
if st.session_state.page == 'home':
    landing_page()
elif st.session_state.page == 'track_details':
    track_details_page()
elif st.session_state.page == 'student_details':
    student_details_page()