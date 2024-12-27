import streamlit as st
import pandas as pd
import altair as alt

# Load data from CSV
@st.cache_data
def load_data(file_path):
    return pd.read_csv(file_path)

# Process the data
def process_data(df):
    correct_answers = df[df['Correct'] == True]
    return correct_answers

def update_multiselect_style():
    st.markdown(
        """
        <style>
            .stMultiSelect [data-baseweb="tag"] {
                height: fit-content;
            }
            .stMultiSelect [data-baseweb="tag"] span[title] {
                white-space: normal; max-width: 100%; overflow-wrap: anywhere;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def update_selectbox_style():
    st.markdown(
        """
        <style>
            .stSelectbox [data-baseweb="select"] div[aria-selected="true"] {
                white-space: normal; overflow-wrap: anywhere;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


update_selectbox_style()
update_multiselect_style()

# Main Streamlit app
st.title("AI Model Performance Analysis on MBE Questions")
st.write("This app analyzes the performance of AI models on a set of MBE sample questions from the Bar Exam.")
st.write("This app is a continuation of a research paper that can be found at [TBD]")

# Load the uploaded CSV file
uploaded_file = "NCBE MBE Questions_Answer_HumanChecked.csv"
if uploaded_file:
    df = load_data(uploaded_file)
    


    # Sidebar for platform and model selection
    st.sidebar.header("Filter Models")
    if 'Platform' in df.columns:
        platforms = df['Platform'].unique()
        selected_platforms = st.sidebar.multiselect("Select AI Platforms", platforms, default=platforms)
        platform_filtered_df = df[df['Platform'].isin(selected_platforms)]
    else:
        platform_filtered_df = df

    models = sorted(platform_filtered_df['Model'].unique())
    selected_models = st.sidebar.multiselect("Select AI Models (All models are chosen by default)", models, default=models)
    

    # Filter data based on selected models
    filtered_df = platform_filtered_df[platform_filtered_df['Model'].isin(selected_models)]

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Correct Answers", "Model Costs", "Correct Answers by Category"])

    # Tab 1: Correct Answers Bar Chart
    with tab1:
        filtered_correct_answers = filtered_df[filtered_df['Correct'] == True]
        correct_counts = filtered_correct_answers['Model'].value_counts().reset_index()
        correct_counts.columns = ['Model', 'Correct']

        correct_counts['Correct'] = pd.to_numeric(correct_counts['Correct'], errors='coerce')
        correct_counts = correct_counts.sort_values(by='Correct', ascending=False)

        # Bar chart
        bars = alt.Chart(correct_counts).mark_bar().encode(
            x=alt.X('Model', sort='-y', title='Model'),
            y=alt.Y(
                'Correct', 
                title='Correct Answers',
                scale=alt.Scale(domain=[0, 220]),
                axis=alt.Axis(
                    ticks=True,  # Ensure ticks are enabled
                    values=[0, 50, 100, 150, 200, 210]  # Custom tick marks including 210
                )
            ),
            tooltip=['Model', 'Correct']
        ).properties(
            title='Correct Answers by Model',
            height=800
        )

        # Red line at y=210
        line = alt.Chart(pd.DataFrame({'y': [210]})).mark_rule(color='red', strokeWidth=2).encode(
            y='y:Q'
        )

        # Text annotation for the red line
        text = alt.Chart(pd.DataFrame({'y': [215], 'text': ['Maximum Score (210)']})).mark_text(
            align='left',
            baseline='middle',
            dx=5,  # Offset text horizontally
            color='red'
        ).encode(
            y='y:Q',
            text='text:N'
        )

        # Combine the bar chart, red line, and text
        combined_chart = (bars + line + text).configure_axis(
            labelFontSize=12,
            labelAngle=270,
            labelLimit=500
        )

        st.altair_chart(combined_chart, use_container_width=True)
        st.markdown("### Description")
        st.write("This bar chart shows the number of correct answers by each model. The red line represents the maximum score of 210.")


    # Tab 2: Model Costs
    with tab2:
        st.write("Coming Soon")

    # Tab 3: Correct Answers by Legal Category
    with tab3:
        st.write("Coming Soon")
