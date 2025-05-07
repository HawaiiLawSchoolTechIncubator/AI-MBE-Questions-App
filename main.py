import streamlit as st
import pandas as pd
import altair as alt

# Fixed color mapping for AI Platforms
platform_colors = {
    "Human": "#AB63FA",
    "Claude": "#636EFA",
    "Gemini": "#EF553B",
    "ChatGPT": "#00CC96",
    "Llama": "#FFA15A",
    "DeepSeek": "#19D3F3",
    "Alibaba": "#FF6692",
    "Grok": "#B6E880"
}

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
st.write("This research was done at the University of Hawaii, William S. Richardson School of Law.")
st.write("Authors: Matthew Stubenberg, Chloe Berridge, Thomas Fuerst Smith, and Joshua Casey")

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

    # Create tabs with enhanced styling
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 10px 16px;
        white-space: normal;
        background-color: #f0f2f6;
        border-radius: 4px;
        font-size: 16px;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f0ff;
        border-bottom: 2px solid #1f77b4;
    }
    </style>""", unsafe_allow_html=True)
    
    # Add container style with reduced padding
    st.markdown("""
    <style>
    .element-container {
        padding-left: 0px;
        padding-right: 0px;
    }
    .stAlertContent {
        padding-left: 10px;
        padding-right: 10px;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Add custom CSS to limit main container width
    st.markdown("""
    <style>
        div[data-testid="stMainBlockContainer"] {
            max-width: 70rem !important;
            padding-top: 1rem;
            padding-right: 1rem;
            padding-left: 1rem;
            padding-bottom: 0rem;
        }
    </style>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Percentage of Correct Answers", 
        "🎯 Number of Correct Answers", 
        "📚 Categories Answered Correctly",
        "💰 Cost Per Question",
        "⏱️ Time Per Question",
        "❓ Individual Question"
        
    ])

    # Tab 1: Correct Answers Bar Chart
    with tab1:
        # Calculate the percentage of correct answers per model
        total_questions = filtered_df.groupby(['Model', 'AI Platform']).size().reset_index(name='Total')
        correct_answers = filtered_df[filtered_df['Correct'] == True].groupby(['Model', 'AI Platform']).size().reset_index(name='Correct')
        percentage_correct = pd.merge(total_questions, correct_answers, on=['Model', 'AI Platform'])
        percentage_correct['Percentage'] = (percentage_correct['Correct'] / percentage_correct['Total']) * 100
        
        # Remove Human from the dataset - we'll just show the red line
        percentage_correct = percentage_correct[percentage_correct['AI Platform'] != 'Human']

        # Get platform colors without Human
        filtered_platform_colors = {k: v for k, v in platform_colors.items() if k != 'Human'}

        # Bar chart with fixed color mapping for AI Platform
        bars = alt.Chart(percentage_correct).mark_bar().encode(
            x=alt.X('Model', sort=alt.SortField(field='Percentage', order='descending'),
                    title='Model', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Percentage',
                    title='Percentage of Correct Answers',
                    scale=alt.Scale(domain=[0, 100]),
                    axis=alt.Axis(ticks=True, values=[0, 20, 40, 60, 80, 100])),
            color=alt.Color('AI Platform:N',
                            scale=alt.Scale(
                                domain=list(filtered_platform_colors.keys()),
                                range=list(filtered_platform_colors.values())
                            ),
                            legend=alt.Legend(title="AI Platform")),
            tooltip=['Model', 'Percentage', 'AI Platform']
        ).properties(
            title='Percentage of Correct Answers by Model',
            height=800
        )

        # Add shaded range for human pass rate
        shaded_range = alt.Chart(pd.DataFrame({'Low End': [58], 'High End': [67]})).mark_rect(
            color='lightgray', opacity=0.5
        ).encode(
            y='Low End:Q',
            y2='High End:Q'
        )

        # Add text annotation for the shaded range
        shaded_text = alt.Chart(pd.DataFrame({'y': [70], 'text': ['Pass Rate (Gray Box)']})).mark_text(
            align='right', baseline='middle', fontSize=12, color='black', dx=-10, dy=5
        ).encode(
            x=alt.value('width'),
            y='y:Q',
            text='text:N'
        )

        # Add a red line at y=70.9 for the human average
        human_line = alt.Chart(pd.DataFrame({'y': [70.9]})).mark_rule(color='red', strokeWidth=2).encode(
            y='y:Q'
        )

        # Add text annotation for the human line, moved to the right
        human_text = alt.Chart(pd.DataFrame({'y': [72], 'text': ['Human Average (70.9%)']})).mark_text(
            align='right', baseline='middle', fontSize=12, color='red', dx=-10, dy=-7
        ).encode(
            x=alt.value('width'),  # Position at right edge
            y='y:Q',
            text='text:N'
        )

        combined_chart = (bars + shaded_range + shaded_text + human_line + human_text).configure_axisX(
            labelAngle=-45,
            labelFontSize=12,
            labelLimit=1000,  # Increased label limit
            labelOverlap=False  # Prevent labels from overlapping
        ).properties(
            padding={'top': 20, 'bottom': 20}  # Add more padding at the bottom
        )

        st.altair_chart(combined_chart, use_container_width=True)
        st.markdown("### Description")
        st.write("This bar chart shows the percentage of questions each model answered correctly, color-coded by AI Platform. The gray shaded area represents the pass rate range of 58-67%. The red line represents the Human Average performance of 70.9% correct.")
        
        # Add pivot table with raw data
        st.markdown("### Raw Performance Data")
        # Sort by percentage descending
        display_df = percentage_correct[['Model', 'AI Platform', 'Total', 'Correct', 'Percentage']].sort_values('Percentage', ascending=False)
        # Format the percentage column to show 1 decimal place
        display_df['Percentage'] = display_df['Percentage'].map('{:.1f}%'.format)
        st.dataframe(display_df, hide_index=True)
    with tab2:
        filtered_correct_answers = filtered_df[filtered_df['Correct'] == True]

        # Group by 'Model' and 'AI Platform'
        correct_counts = filtered_correct_answers.groupby(['Model', 'AI Platform']).size().reset_index(name='Correct')

        # Remove Human from the dataset - we'll just show the red line
        correct_counts = correct_counts[correct_counts['AI Platform'] != 'Human']
        
        # Get platform colors without Human
        filtered_platform_colors = {k: v for k, v in platform_colors.items() if k != 'Human'}

        # Sort by number of correct answers
        correct_counts = correct_counts.sort_values(by='Correct', ascending=False)

        # Bar chart with fixed color mapping for AI Platform
        bars = alt.Chart(correct_counts).mark_bar().encode(
            x=alt.X('Model', sort='-y',
                    title='Model', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Correct',
                    title='Correct Answers',
                    scale=alt.Scale(domain=[0, 220]),
                    axis=alt.Axis(ticks=True, values=[0, 50, 100, 150, 200, 210])),
            color=alt.Color('AI Platform:N',
                            scale=alt.Scale(
                                domain=list(filtered_platform_colors.keys()),
                                range=list(filtered_platform_colors.values())
                            ),
                            legend=alt.Legend(title="AI Platform")),
            tooltip=['Model', 'Correct', 'AI Platform']
        ).properties(
            title='Correct Answers by Model',
            height=800
        )

        # Semi-transparent shaded range between 121 and 140
        shaded_range = alt.Chart(pd.DataFrame({'Low End': [121], 'High End': [140]})).mark_rect(
            color='lightgray', opacity=0.3
        ).encode(
            y='Low End:Q',
            y2='High End:Q'
        )

        # Text annotation for the shaded box
        shaded_text = alt.Chart(pd.DataFrame({'y': [145], 'text': ['Pass Rate (Gray Box)']})).mark_text(
            align='right', baseline='middle', fontSize=12, color='black', dx=-10, dy=5
        ).encode(
            x=alt.value('width'),
            y='y:Q',
            text='text:N'
        )

        # Red line at y=149 for human average
        human_line = alt.Chart(pd.DataFrame({'y': [149]})).mark_rule(color='red', strokeWidth=2).encode(
            y='y:Q'
        )

        # Text annotation for the red line positioned to the right and above the line
        human_text = alt.Chart(pd.DataFrame({'y': [154], 'text': ['Human Average (149)']})).mark_text(
            align='right', baseline='middle', fontSize=12, color='red', dx=-10
        ).encode(
            x=alt.value('width'),  # Position at right edge
            y='y:Q',
            text='text:N'
        )

        # Red line at y=210 for max score
        max_line = alt.Chart(pd.DataFrame({'y': [210]})).mark_rule(color='red', strokeWidth=2).encode(
            y='y:Q'
        )

        # Text annotation for the max score line
        max_score_text = alt.Chart(pd.DataFrame({'y': [215], 'text': ['Maximum Score (210)']})).mark_text(
            align='right', baseline='middle', dx=-10, color='red'
        ).encode(
            x=alt.value('width'),
            y='y:Q',
            text='text:N'
        )

        combined_chart = (bars + shaded_range + shaded_text + human_line + human_text + max_line + max_score_text).configure_axisX(
            labelAngle=-45,
            labelFontSize=12,
            labelLimit=1000,  # Increased label limit
            labelOverlap=False  # Prevent labels from overlapping
        ).properties(
            padding={'top': 20, 'bottom': 20}  # Add more padding at the bottom
        )

        st.altair_chart(combined_chart, use_container_width=True)
        st.markdown("### Description")
        st.write("This bar chart shows the number of correct answers by each model, color-coded by AI Platform. The red horizontal line at 149 represents the Human Average performance. The gray shaded area represents the pass rate range of 121-140, and the top red line represents the maximum score of 210.")
        
        # Add pivot table with raw data
        st.markdown("### Raw Performance Data")
        # Calculate total questions per model
        total_questions = filtered_df.groupby(['Model', 'AI Platform']).size().reset_index(name='Total Questions')
        # Merge with correct answers count
        display_df = pd.merge(correct_counts, total_questions, on=['Model', 'AI Platform'], how='left')
        # Calculate percentage correct
        display_df['Percentage Correct'] = (display_df['Correct'] / display_df['Total Questions'] * 100).round(1)
        display_df['Percentage Correct'] = display_df['Percentage Correct'].map('{:.1f}%'.format)
        # Display the table sorted by number of correct answers descending
        st.dataframe(display_df[['Model', 'AI Platform', 'Correct', 'Total Questions', 'Percentage Correct']], 
                    hide_index=True)
    with tab3:
        # Get the correct answers only
        correct_df = filtered_df[filtered_df['Correct'] == True]
        
        # Standardize criminal law categories
        correct_df.loc[:, 'Law Category'] = correct_df['Law Category'].replace('Criminal Law/Prosecution', 'Criminal Law and Procedure')
        
        # Count correct answers by Model and Law Category
        category_counts = correct_df.groupby(['Model', 'AI Platform', 'Law Category']).size().reset_index(name='Count')
        
        # Add sorting options
        sort_options = ["Total Correct Answers", "Legal Category"]
        sort_by = st.radio("Sort models by:", sort_options)
        
        # Create the sorting field based on user selection
        if sort_by == "Total Correct Answers":
            sort_field = alt.EncodingSortField(field='Count', op='sum', order='descending')
        else:  # By Legal Category
            # Create a temporary dataframe to determine the order
            category_order = category_counts.pivot_table(
                values='Count', index='Model', columns='Law Category', aggfunc='sum'
            ).fillna(0)
            # Get unique categories
            categories = category_counts['Law Category'].unique()
            # Let the user select which category to sort by
            selected_category = st.selectbox("Select a legal category to sort by:", categories)
            # Create a dictionary mapping models to their count for the selected category
            model_order = category_counts[category_counts['Law Category'] == selected_category].set_index('Model')['Count']
            # Convert to list of models sorted by the selected category count
            sorted_models = model_order.sort_values(ascending=False).index.tolist()
            sort_field = sorted_models
        
        # Create a horizontal stacked bar chart
        chart = alt.Chart(category_counts).mark_bar().encode(
            y=alt.Y('Model:N', 
               title='AI Model', 
               sort=sort_field,
               axis=alt.Axis(
               labelLimit=300,  # Increase label width limit
               labelOverlap=False,  # Prevent label overlap
               labelFontSize=11  # Adjust font size if needed
               )),
            x=alt.X('sum(Count):Q', title='Number of Questions Answered Correctly'),
            color=alt.Color('Law Category:N', 
                scale=alt.Scale(scheme='category20'),
                legend=alt.Legend(title="Legal Category", 
                    orient='top',  # Changed from 'bottom' to 'top'
                    columns=2,  # Stack the legend in 2 columns
                    labelLimit=200)),
            order=alt.Order('Law Category:N', sort='ascending'),
            tooltip=['Model', 'AI Platform', 'Law Category', 
            alt.Tooltip('Count:Q', title='Answers Correct out of 30')]
        ).properties(
            title='Correct Answers by Legal Category for Each Model',
            height=max(600, 25 * len(filtered_df['Model'].unique())),  # Dynamically set height with minimum of 600px
            width=800
        )
        
        # Add human average data if available in a format similar to the other models
        if 'Human Average' not in category_counts['Model'].values:
            # You can add human average data if available
            # This would require additional data processing
            pass
        
        # Configure the chart appearance
        configured_chart = chart.configure_axisY(
            labelLimit=300,
            labelFontSize=12
        ).configure_axisX(
            labelFontSize=12
        ).configure_legend(
            labelFontSize=12,
            titleFontSize=14,
            padding=10,  # Add padding around legend
            cornerRadius=5  # Rounded corners
        )
        
        st.altair_chart(configured_chart, use_container_width=True)
        
        st.markdown("### Description")
        st.write("This horizontal bar chart shows the number of questions answered correctly by each model, broken down by legal category. Each color represents a different legal category, and the bars are sorted by the total number of correct answers in descending order or by a specific legal category.")
        
        # Show table with the raw data for more detailed analysis
        st.markdown("### Detailed Category Performance")
        
        # Standardize criminal law categories in the raw data before pivoting
        category_counts['Law Category'] = category_counts['Law Category'].replace('Criminal Law/Prosecution', 'Criminal Law and Procedure')
        
        pivot_table = pd.pivot_table(
            category_counts, 
            values='Count', 
            index=['Model', 'AI Platform'], 
            columns='Law Category', 
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        # Add a total column
        pivot_table['Total'] = pivot_table.iloc[:, 2:].sum(axis=1)
        
        # Sort by total descending
        pivot_table = pivot_table.sort_values('Total', ascending=False)
        
        st.dataframe(pivot_table, hide_index=True)
    with tab4:
        # Check if cost columns exist in the dataframe
        if 'total_cost' in filtered_df.columns:
            # Calculate total cost and count of questions for each model
            cost_summary = filtered_df.groupby(['Model', 'AI Platform']).agg(
                total_sum=('total_cost', 'sum'),
                question_count=('total_cost', 'count')
            ).reset_index()
            
            # Filter out "Human" platform from this tab
            cost_summary = cost_summary[cost_summary['AI Platform'] != "Human"]
            
            # Calculate average cost per query
            cost_summary['Average Cost Per Question'] = cost_summary['total_sum'] / cost_summary['question_count']
            
            # Count total questions and correct answers for each model
            total_questions = filtered_df.groupby(['Model', 'AI Platform']).size().reset_index(name='Total Questions')
            correct_counts = filtered_df[filtered_df['Correct'] == True].groupby(['Model', 'AI Platform']).size().reset_index(name='Correct Answers')
            
            # Merge cost data with correct answers count and filter out Human
            merged_data = pd.merge(cost_summary, correct_counts, on=['Model', 'AI Platform'], how='left')
            merged_data = pd.merge(merged_data, total_questions, on=['Model', 'AI Platform'], how='left')
            merged_data['Correct Answers'] = merged_data['Correct Answers'].fillna(0)
            
            # Calculate percentage correct
            merged_data['Percentage Correct'] = (merged_data['Correct Answers'] / merged_data['Total Questions']) * 100
            
            # Create scatter plot with cost vs. performance (percentage)
            scatter = alt.Chart(merged_data).mark_circle().encode(
                x=alt.X('Average Cost Per Question:Q', 
                      title='Average Cost Per Question ($)',
                      scale=alt.Scale(zero=True)),
                y=alt.Y('Percentage Correct:Q',
                      title='Percentage of Correct Answers',
                      scale=alt.Scale(zero=False, domain=[0, 100])),
                color=alt.Color('AI Platform:N',
                              scale=alt.Scale(
                                  domain=[p for p in list(platform_colors.keys()) if p != "Human"],
                                  range=[platform_colors[p] for p in list(platform_colors.keys()) if p != "Human"]
                              ),
                              legend=alt.Legend(title="AI Platform")),
                size=alt.value(100),
                tooltip=['Model', 'AI Platform', 
                         alt.Tooltip('Average Cost Per Question:Q', format='$.5f'),
                         alt.Tooltip('Percentage Correct:Q', format='.1f')]
            ).properties(
                title='Cost vs. Performance: Average Cost Per Question vs. Percentage Correct',
                height=600,
                width=800
            )
            
            combined_chart = scatter.configure_axis(
                labelFontSize=12
            ).properties(
                padding={'top': 20, 'bottom': 20, 'left': 20, 'right': 20}
            )
            
            st.altair_chart(combined_chart, use_container_width=True)
            st.markdown("### Description")
            st.write("This scatter plot shows the relationship between the average cost per question (x-axis) and the percentage of correct answers (y-axis). Each point represents a model, color-coded by AI Platform. Higher and further left is better (higher percentage correct at lower cost).")
            
            # Also show the data in a table format for precise values
            st.markdown("### Cost and Performance Data")
            display_df = merged_data[['Model', 'AI Platform', 'Average Cost Per Question', 'Percentage Correct']]
            st.dataframe(display_df.sort_values('Percentage Correct', ascending=False), hide_index=True)
        else:
            st.write("Cost data is not available in the dataset.")
        with tab5:
            # Check if duration column exists in the dataframe
            if 'duration' in filtered_df.columns:
                # Calculate average duration for each model
                time_summary = filtered_df.groupby(['Model', 'AI Platform']).agg(
                    avg_duration=('duration', 'mean'),
                    question_count=('duration', 'count')
                ).reset_index()
                
                # Filter out "Human" platform from this tab
                time_summary = time_summary[time_summary['AI Platform'] != "Human"]
                
                # Count total questions and correct answers for each model
                total_questions = filtered_df.groupby(['Model', 'AI Platform']).size().reset_index(name='Total Questions')
                correct_counts = filtered_df[filtered_df['Correct'] == True].groupby(['Model', 'AI Platform']).size().reset_index(name='Correct Answers')
                
                # Merge time data with correct answers count
                merged_data = pd.merge(time_summary, correct_counts, on=['Model', 'AI Platform'], how='left')
                merged_data = pd.merge(merged_data, total_questions, on=['Model', 'AI Platform'], how='left')
                merged_data['Correct Answers'] = merged_data['Correct Answers'].fillna(0)
                
                # Calculate percentage correct
                merged_data['Percentage Correct'] = (merged_data['Correct Answers'] / merged_data['Total Questions']) * 100
                
                # Create scatter plot with time vs. performance (percentage)
                scatter = alt.Chart(merged_data).mark_circle().encode(
                    x=alt.X('avg_duration:Q', 
                          title='Average Time Per Question (seconds)',
                          scale=alt.Scale(zero=True)),
                    y=alt.Y('Percentage Correct:Q',
                          title='Percentage of Correct Answers',
                          scale=alt.Scale(zero=False, domain=[0, 100])),
                    color=alt.Color('AI Platform:N',
                                  scale=alt.Scale(
                                      domain=[p for p in list(platform_colors.keys()) if p != "Human"],
                                      range=[platform_colors[p] for p in list(platform_colors.keys()) if p != "Human"]
                                  ),
                                  legend=alt.Legend(title="AI Platform")),
                    size=alt.value(100),
                    tooltip=['Model', 'AI Platform', 
                             alt.Tooltip('avg_duration:Q', title='Average Seconds to Answer', format='.2f'),
                             alt.Tooltip('Percentage Correct:Q', format='.1f')]
                ).properties(
                    title='Time vs. Performance: Average Time Per Question vs. Percentage Correct',
                    height=600,
                    width=800
                )
                
                combined_chart = scatter.configure_axis(
                    labelFontSize=12
                ).properties(
                    padding={'top': 20, 'bottom': 20, 'left': 20, 'right': 20}
                )
                
                st.altair_chart(combined_chart, use_container_width=True)
                st.markdown("### Description")
                st.write("This scatter plot shows the relationship between the average time per question in seconds (x-axis) and the percentage of correct answers (y-axis). Each point represents a model, color-coded by AI Platform. Higher and further left is better (higher percentage correct in less time).")
                
                # Also show the data in a table format for precise values
                st.markdown("### Time and Performance Data")
                display_df = merged_data[['Model', 'AI Platform', 'avg_duration', 'Percentage Correct']]
                st.dataframe(display_df.sort_values('Percentage Correct', ascending=False), hide_index=True)
            else:
                st.write("Duration data is not available in the dataset.")
        with tab6:
            # Check if we have any selected models
            if len(selected_models) > 0:
                st.markdown("### Question Performance Analysis")
                
                # Create a pivot table where rows are questions and columns are models
                question_pivot = filtered_df.pivot_table(
                    index=['Question Number', 'Law Category'],
                    columns='Model',
                    values='Correct',
                    aggfunc=lambda x: 
                        'Correct' if all(isinstance(val, bool) for val in x) and x.any() 
                        else (
                            'Incorrect' if all(isinstance(val, bool) for val in x)
                            else print(f"Unexpected value in 'Correct' column: {x}")
                        )
                )
                
                # Create a dataframe counting correct answers per question
                question_summary = filtered_df.groupby('Question Number').agg(
                    total_correct=('Correct', lambda x: sum(x)),
                    total_models=('Model', 'nunique')
                )
                
                # Calculate percentage of models that got each question correct
                question_summary['Percentage Correct'] = (question_summary['total_correct'] / question_summary['total_models'] * 100).round(1)
                
                # Reset index for display
                question_pivot_reset = question_pivot.reset_index()
                question_summary_reset = question_summary.reset_index()
                
                # Merge the two dataframes
                merged_table = pd.merge(
                    question_pivot_reset, 
                    question_summary_reset[['Question Number', 'Percentage Correct']],
                    on='Question Number'
                )
                
                # Sort by percentage correct (descending)
                merged_table = merged_table.sort_values('Percentage Correct', ascending=False)
                
                # Format the percentage column
                merged_table['Percentage Correct'] = merged_table['Percentage Correct'].map('{:.1f}%'.format)
                
                st.write("This table shows which questions were answered correctly by which models. The 'Percentage Correct' column shows the percentage of selected models that answered each question correctly.")
                st.dataframe(merged_table, hide_index=True, height=600)
                
                # Show the easiest and hardest questions
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Easiest Questions")
                    easiest = merged_table.head(5)
                    st.dataframe(easiest[['Question Number', 'Law Category', 'Percentage Correct']], hide_index=True)
                    
                with col2:
                    st.markdown("### Hardest Questions")
                    hardest = merged_table.tail(5).sort_values('Percentage Correct')
                    st.dataframe(hardest[['Question Number', 'Law Category', 'Percentage Correct']], hide_index=True)
            else:
                st.write("Please select at least one model to view question analysis.")
    st.write("The code for the benchmark project can be found at https://github.com/HawaiiLawSchoolTechIncubator/AI-MBE-Benchmark")
