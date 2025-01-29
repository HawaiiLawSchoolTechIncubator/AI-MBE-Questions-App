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
uploaded_file = "NCBE MBE Questions_Answer_streamlit.csv"
if uploaded_file:
    df = load_data(uploaded_file)
    


    # Sidebar for platform and model selection
    st.sidebar.header("Filter Models")
    if 'AI Platform' in df.columns:
        platforms = df['AI Platform'].unique()
        selected_platforms = st.sidebar.multiselect("Select AI Platforms", platforms, default=platforms)
        platform_filtered_df = df[df['AI Platform'].isin(selected_platforms)]
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
        
        # Group by 'Model' and 'AI Platform'
        correct_counts = filtered_correct_answers.groupby(['Model', 'AI Platform']).size().reset_index(name='Correct')

        correct_counts['Correct'] = pd.to_numeric(correct_counts['Correct'], errors='coerce')
        correct_counts = correct_counts.sort_values(by='Correct', ascending=False)

        # Bar chart with color encoding for 'AI Platform'
        bars = alt.Chart(correct_counts).mark_bar().encode(
            x=alt.X('Model', sort='-y', title='Model'),
            y=alt.Y(
                'Correct', 
                title='Correct Answers',
                scale=alt.Scale(domain=[0, 220]),
                axis=alt.Axis(
                    ticks=True, 
                    values=[0, 50, 100, 150, 200, 210]
                )
            ),
            color=alt.Color('AI Platform:N', legend=alt.Legend(title="AI Platform")),  # Correct column name
            tooltip=['Model', 'Correct', 'AI Platform']
        ).properties(
            title='Correct Answers by Model',
            height=800
        )

        # Semi-transparent shaded range between 121 and 140
        shaded_range = alt.Chart(pd.DataFrame({'Low End': [121], 'High End': [140]})).mark_rect(
            color='lightgray', 
            opacity=0.3
        ).encode(
            y='Low End:Q',
            y2='High End:Q'
        )

        # Text annotation for the shaded box
        # Text annotation for the shaded box, aligned to the far right
        shaded_text = alt.Chart(pd.DataFrame({'y': [145], 'text': ['Average Human Pass Rate (Gray Box)']})).mark_text(
            align='right',   # Align the text to the right
            baseline='middle',
            fontSize=12,
            color='black',
            dx=-10           # Adjust horizontal position slightly inward if needed
        ).encode(
            x=alt.value('width'),  # Position the text at the far right of the chart
            y='y:Q',
            text='text:N'
        )

        # Red line at y=210
        line = alt.Chart(pd.DataFrame({'y': [210]})).mark_rule(color='red', strokeWidth=2).encode(
            y='y:Q'
        )

        # Text annotation for the red line
        max_score_text = alt.Chart(pd.DataFrame({'y': [215], 'text': ['Maximum Score (210)']})).mark_text(
            align='left',
            baseline='middle',
            dx=5,
            color='red'
        ).encode(
            y='y:Q',
            text='text:N'
        )

        # Combine charts
        combined_chart = (bars + shaded_range + shaded_text + line + max_score_text).configure_axis(
            labelFontSize=12,
            labelAngle=270,
            labelLimit=500
        )

        st.altair_chart(combined_chart, use_container_width=True)
        st.markdown("### Description")
        st.write("This bar chart shows the number of correct answers by each model, color-coded by AI Platform. The gray shaded area represents the range 121-140 with a label for the average human pass rate, and the red line represents the maximum score of 210.")

    # Tab 2: Model Costs vs Correct Answers with Leader Lines
    with tab2:
        # Filter the correct answers
        filtered_correct_answers = filtered_df[filtered_df['Correct'] == True]

        # Calculate the average cost and number of correct answers per model
        cost_correct_data = filtered_correct_answers.groupby('Model').agg(
            Average_Cost=('total_cost', lambda x: round(x.mean(), 5)),  # Use the 'total_cost' column and round to 2 decimal places
            Correct=('Correct', 'sum')
        ).reset_index()

        # Add offsets for labels to avoid overlapping (customize for your dataset if necessary)
        cost_correct_data['Label_X'] = cost_correct_data['Average_Cost'] + 0.0015
        cost_correct_data['Label_Y'] = cost_correct_data['Correct'] + 8

        # Check for overlapping labels and adjust positions
        for i in range(len(cost_correct_data)):
            for j in range(i + 1, len(cost_correct_data)):
                if abs(cost_correct_data.at[i, 'Label_X'] - cost_correct_data.at[j, 'Label_X']) < 0.002 and \
            abs(cost_correct_data.at[i, 'Label_Y'] - cost_correct_data.at[j, 'Label_Y']) < 10:
                    if cost_correct_data.at[j, 'Label_Y'] > cost_correct_data.at[i, 'Label_Y']:
                        cost_correct_data.at[j, 'Label_Y'] -= 10  # Move label below the point
                    else:
                        cost_correct_data.at[j, 'Label_Y'] += 10  # Move label above the point

        # Scatter plot: Average Cost vs Number of Correct Answers
        scatter = alt.Chart(cost_correct_data).mark_point(size=60).encode(
            x=alt.X('Average_Cost:Q', title='Average Cost (Cents)'),
            y=alt.Y(
                'Correct:Q',
                title='Number of Questions Correct',
                scale=alt.Scale(domain=[100, cost_correct_data['Correct'].max() + 10])  # Start y-axis at 100
            ),
            tooltip=['Model:N', 'Average_Cost:Q', 'Correct:Q']
        ).properties(
            title='Average Cost vs Number of Correct Answers',
            height=600,
            width=800
        )

        # Add lines connecting the text labels to the points
        lines = alt.Chart(cost_correct_data).mark_line(color='gray').encode(
            x='Average_Cost:Q',
            y='Correct:Q',
            x2='Label_X:Q',
            y2='Label_Y:Q',
            tooltip=['Model:N', 'Average_Cost:Q', 'Correct:Q']
        )

        # Add text labels to the points with offsets
        labels = alt.Chart(cost_correct_data).mark_text(
            align='left',
            baseline='middle',
            fontSize=10
        ).encode(
            x='Label_X:Q',
            y='Label_Y:Q',
            text='Model:N',
            tooltip=['Model:N', 'Average_Cost:Q', 'Correct:Q']
        )

        # Combine scatter plot, leader lines, and labels
        cost_correct_chart = scatter + lines + labels

        # Display the chart
        st.altair_chart(cost_correct_chart, use_container_width=True)
        st.markdown("### Description")
        st.write("This chart shows the relationship between the average cost per question (in cents) and the number of correct answers for each AI model. Leader lines connect model labels to the respective data points.")

    # Tab 3: Correct Answers by Legal Category
    with tab3:
        st.write("Coming Soon")
