import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
import os
from datetime import datetime

# Import ReportLab components for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from io import BytesIO

# --- Page Configuration ---
st.set_page_config(
    page_title="Interactive Media Intelligence Dashboard – Ramadan Campaign",
    page_icon="🕌",
    layout="wide", # Use wide layout for more space
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a more polished and themed look ---
st.markdown("""
<style>
    /* Main container background and text */
    .stApp {
        background-color: #F8F9FA; /* Light grey background */
        color: #333333; /* Darker text */
    }

    /* Sidebar styling */
    .st-emotion-cache-vk32hr { /* Specific Streamlit sidebar class */
        background-image: linear-gradient(to bottom, #E0F2F7, #CFE8F3); /* Light blue gradient */
        color: #333333;
        padding-top: 2rem;
    }
    .st-emotion-cache-vk32hr .st-emotion-cache-1pxy1gi { /* Sidebar header color */
        color: #265B7D; /* Darker blue for sidebar headers */
    }

    /* Main title */
    h1 {
        color: #265B7D; /* Darker blue for the main title */
        text-align: center;
        font-size: 3.5em; /* Slightly larger title */
        font-weight: bold;
        margin-bottom: 0.5em;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.1); /* Subtle shadow */
    }

    /* Section headers */
    h2 {
        color: #007BFF; /* Primary blue */
        border-bottom: 3px solid #E0F2F7; /* Thicker, softer border */
        padding-bottom: 15px;
        margin-top: 2.5em; /* More spacing above sections */
        font-size: 2em;
    }
    h3 {
        color: #FF5733; /* Vibrant orange for chart titles/sub-headers */
        margin-top: 2em; /* More spacing for chart headers */
        font-size: 1.5em;
    }
    h4 { /* Added for filter group headers */
        color: #007BFF;
        font-size: 1.2em;
        margin-top: 1.5em;
    }

    /* File Uploader and Button styling */
    .stFileUploader label {
        font-size: 1.2em;
        color: #007BFF;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #28A745; /* Green for primary actions */
        color: white;
        font-weight: bold;
        padding: 0.8em 1.8em; /* Larger padding */
        border-radius: 8px; /* More rounded corners */
        border: none;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2); /* Button shadow */
        transition: background-color 0.3s ease, transform 0.2s ease; /* Smooth transition */
    }
    .stButton>button:hover {
        background-color: #218838; /* Darker green on hover */
        transform: translateY(-2px); /* Slight lift effect */
    }

    /* Info, Success, Warning boxes */
    .stAlert {
        border-radius: 8px;
        font-size: 1.1em;
    }
    .stAlert.info { background-color: #E0F2F7; border-left: 5px solid #007BFF; }
    .stAlert.success { background-color: #D4EDDA; border-left: 5px solid #28A745; }
    .stAlert.warning { background-color: #FFF3CD; border-left: 5px solid #FFC107; }
    .stAlert.error { background-color: #F8D7DA; border-left: 5px solid #DC3545; }

    /* Dataframes */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden; /* Ensures borders are rounded */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* Subtle shadow for dataframes */
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #F0F8FF; /* Light blue for expander header */
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-weight: bold;
        color: #007BFF;
        border: 1px solid #B0E0E6;
        transition: background-color 0.3s ease;
    }
    .streamlit-expanderHeader:hover {
        background-color: #E0F2F7;
    }
    .streamlit-expanderContent {
        padding: 1rem;
        background-color: #FFFFFF; /* White background for content */
        border-radius: 0 0 8px 8px;
        border: 1px solid #B0E0E6;
        border-top: none; /* No top border */
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.header("Dashboard Controls ⚙️")
    st.info("Upload your data, set up AI, and apply filters to analyze your campaign!")

    # --- API Key Input ---
    st.subheader("OpenRouter API Configuration")
    openrouter_api_key = st.text_input(
        "Enter your OpenRouter API Key:",
        type="password",
        help="Paste your API key obtained from openrouter.ai. This key is used to generate AI insights and is not stored."
    )
    selected_model = st.selectbox(
        "Select AI Model for Insights:",
        [
            "google/gemma-3n-e4b-it:free",
            "nousresearch/deephermes-3-mistral-24b-preview:free",
            "meta-llama/llama-3.3-8b-instruct:free"
        ],
        index=0,
        help="Choose a free model available on OpenRouter for generating insights. Performance may vary between models."
    )

    if openrouter_api_key:
        os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key,
        )
    else:
        st.warning("Please enter your OpenRouter API Key to enable AI insights.")
        client = None

# --- Function to generate insights using OpenRouter ---
@st.cache_data(show_spinner="Generating AI insights...")
def get_insights(data_description, chart_title, model_name):
    if not client:
        return "Please provide an OpenRouter API Key to generate insights."

    prompt = f"""
    Based on the following data for a Ramadan Campaign, provide 3 concise and actionable insights for the "{chart_title}" chart.
    Focus on trends, anomalies, or key takeaways that someone managing a media campaign would find useful.

    Data Context:
    {data_description}

    Insights:
    1.
    2.
    3.
    """
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating insights: {e}. Please check your API key and model selection, or try a different model."

# --- Function to generate PDF report ---
def generate_pdf_report(figures, insights_dict, report_name="Media_Intelligence_Report", filters_summary=""):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom style for title
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['h1'],
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=24,
        textColor='#265B7D'
    )
    # Custom style for section headers
    section_style = ParagraphStyle(
        name='SectionStyle',
        parent=styles['h2'],
        fontSize=18,
        leading=22,
        spaceBefore=20,
        spaceAfter=12,
        textColor='#007BFF'
    )
    # Custom style for chart titles
    chart_title_style = ParagraphStyle(
        name='ChartTitleStyle',
        parent=styles['h3'],
        fontSize=14,
        leading=18,
        spaceBefore=10,
        spaceAfter=8,
        textColor='#FF5733'
    )
    # Custom style for insights
    insight_style = ParagraphStyle(
        name='InsightStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceBefore=6,
        spaceAfter=6,
        leftIndent=0.2 * inch,
        rightIndent=0.2 * inch,
        backColor='#E0F2F7', # Light blue background for insights
        borderPadding=6,
        borderColor='#007BFF',
        borderWidth=0.5,
        borderRadius=5
    )
    # Style for filters summary
    filter_summary_style = ParagraphStyle(
        name='FilterSummaryStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        spaceBefore=12,
        spaceAfter=12,
        leftIndent=0.2 * inch,
        rightIndent=0.2 * inch,
        backColor='#F0F8FF',
        borderPadding=6,
        borderColor='#B0E0E6',
        borderWidth=0.5,
        borderRadius=5
    )

    story = []

    # Title Page
    story.append(Paragraph("Interactive Media Intelligence Dashboard", title_style))
    story.append(Paragraph("Ramadan Campaign Report", styles['h2']))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("This report provides an overview of media campaign performance based on the uploaded data and applied filters.", styles['Normal']))
    story.append(Spacer(1, 1.0 * inch))
    story.append(Paragraph("Report generated by Streamlit App", styles['Normal']))
    story.append(PageBreak())

    # Filters Summary
    story.append(Paragraph("Applied Filters Summary", section_style))
    story.append(Paragraph(filters_summary, filter_summary_style))
    story.append(Spacer(1, 0.2 * inch))

    # Add charts and insights to the story
    for i, (title, fig) in enumerate(figures.items()):
        # Convert Plotly figure to static image (PNG)
        img_bytes = BytesIO(fig.to_image(format="png", width=800, height=500, scale=2))
        img = Image(img_bytes)
        img.drawHeight = 4 * inch # Adjust height to fit page
        img.drawWidth = 6 * inch # Adjust width to fit page
        img.hAlign = 'CENTER'

        story.append(Paragraph(title, chart_title_style))
        story.append(Spacer(1, 0.1 * inch))
        story.append(img)
        story.append(Spacer(1, 0.2 * inch))

        if title in insights_dict:
            story.append(Paragraph("Top 3 AI Insights:", styles['h4'])) # Use h4 for insight heading
            insights_text = insights_dict[title]
            # Replace bullet points with ReportLab's list handling or manual line breaks
            # For simplicity, let's just make each insight a separate paragraph
            for line in insights_text.split('\n'):
                if line.strip(): # Avoid empty paragraphs
                    story.append(Paragraph(line.strip(), insight_style))
            story.append(Spacer(1, 0.2 * inch))

        # Add a page break after each chart if it's not the last one
        if i < len(figures) - 1:
            story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# --- Main Title ---
st.title("🕌 Interactive Media Intelligence Dashboard – Ramadan Campaign 📊")
st.markdown("### A comprehensive tool to analyze your social media campaign performance during Ramadan.")
st.divider() # Visual separator

# --- 1. Upload CSV File ---
st.header("Upload Your Campaign Data 📤")
st.markdown("Please upload a CSV file with these columns: `Date`, `Platform`, `Sentiment`, `Location`, `Engagements`, `Media Type`.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv", help="Upload your CSV dataset here. Required columns: 'Date', 'Platform', 'Sentiment', 'Location', 'Engagements', 'Media Type'.")

df = None
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("File successfully uploaded! 🎉")

        # --- 2. Data Cleaning and Preparation ---
        st.header("Data Cleaning and Preparation 🧹")
        st.markdown("Performing essential data cleaning steps to ensure accuracy and consistency for analysis.")

        # Store original columns to check against
        original_columns = df.columns.tolist()

        # Normalize column names
        df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]

        # Check for required columns after normalization
        required_columns = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            st.error(f"Error: The uploaded CSV is missing the following required columns: {', '.join(missing_cols)}. Please check your file and rename columns if necessary.")
            df = None # Invalidate df if critical columns are missing

        # This 'if df is not None' should be correctly indented.
        # It's crucial that it's NOT at the same level as the outer 'try',
        # otherwise the outer 'except' might not catch errors from inside.
        if df is not None: # This 'if' is inside the outer 'try'
            # Convert 'date' to datetime
            try: # Inner try 1
                df['date'] = pd.to_datetime(df['date'])
                st.success("✅ 'Date' column converted to datetime format.")
            except Exception as e: # Inner except 1
                st.error(f"Error converting 'Date' column to datetime: {e}. Please ensure the 'Date' column is in a recognized date format (e.g., YYYY-MM-DD, MM/DD/YYYY).")
                df = None # Invalidate df if date conversion fails

        # This 'if df is not None' should be correctly indented.
        if df is not None: # This 'if' is inside the outer 'try'
            # Fill missing 'engagements' with 0
            initial_na_engagements = df['engagements'].isnull().sum()
            df['engagements'] = df['engagements'].fillna(0)
            if initial_na_engagements > 0:
                st.warning(f"⚠️ Filled {initial_na_engagements} missing 'Engagements' values with 0. These were treated as zero engagements for analysis.")
            else:
                st.success("✅ No missing 'Engagements' found.")

            st.success("✅ Column names normalized (e.g., 'Media Type' -> 'media_type').")

            with st.expander("View Cleaned Data Snapshot & Stats 📈"):
                st.write("First 5 rows of your cleaned data:")
                st.dataframe(df.head())
                st.subheader("Basic Data Statistics")
                st.write(df.describe(include='all'))

            # Download cleaned data
            csv_cleaned = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Cleaned Data as CSV 💾",
                data=csv_cleaned,
                file_name="cleaned_campaign_data.csv",
                mime="text/csv",
                help="Click to download the processed data, suitable for further analysis."
            )

            st.divider() # Visual separator

            # --- Interactive Filters in Sidebar ---
            st.sidebar.header("Filter Data for Charts 🔍")
            st.sidebar.markdown("Refine your analysis by selecting specific criteria.")

            # Date Range Slider
            min_date = df['date'].min()
            max_date = df['date'].max()

            date_range = st.sidebar.date_input(
                "Select Date Range:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                help="Adjust the start and end dates to focus your analysis on a specific period."
            )

            # Ensure date_range is a tuple with two elements
            start_date, end_date = min_date, max_date # Initialize
            if date_range and len(date_range) == 2:
                start_date, end_date = date_range
            elif date_range and len(date_range) == 1: # Handle case where only one date is selected
                start_date, end_date = date_range[0], df['date'].max()

            df_filtered = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

            # Platform Filter
            all_platforms = df_filtered['platform'].unique().tolist()
            selected_platforms = st.sidebar.multiselect(
                "Select Platforms:",
                options=all_platforms,
                default=all_platforms,
                help="Choose specific social media platforms (e.g., Facebook, Instagram, Twitter) to include in the charts."
            )
            if selected_platforms:
                df_filtered = df_filtered[df_filtered['platform'].isin(selected_platforms)]

            # Sentiment Filter
            all_sentiments = df_filtered['sentiment'].unique().tolist()
            selected_sentiments = st.sidebar.multiselect(
                "Select Sentiments:",
                options=all_sentiments,
                default=all_sentiments,
                help="Filter by sentiment type (e.g., Positive, Negative, Neutral) to understand public perception."
            )
            if selected_sentiments:
                df_filtered = df_filtered[df_filtered['sentiment'].isin(selected_sentiments)]

            # Media Type Filter
            all_media_types = df_filtered['media_type'].unique().tolist()
            selected_media_types = st.sidebar.multiselect(
                "Select Media Types:",
                options=all_media_types,
                default=all_media_types,
                help="Include or exclude specific media formats (e.g., Image, Video, Text) in your analysis."
            )
            if selected_media_types:
                df_filtered = df_filtered[df_filtered['media_type'].isin(selected_media_types)]

            # Location Filter (Top N or specific list)
            all_locations = df_filtered['location'].unique().tolist()
            selected_locations = st.sidebar.multiselect(
                "Select Locations:",
                options=all_locations,
                default=all_locations,
                help="Narrow down the data to specific geographical regions or countries."
            )
            if selected_locations:
                df_filtered = df_filtered[df_filtered['location'].isin(selected_locations)]

            # Generate filters summary string for the PDF report
            filters_summary_text = f"""
            **Date Range:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}<br/>
            **Platforms:** {', '.join(selected_platforms) if selected_platforms else 'All'}<br/>
            **Sentiments:** {', '.join(selected_sentiments) if selected_sentiments else 'All'}<br/>
            **Media Types:** {', '.join(selected_media_types) if selected_media_types else 'All'}<br/>
            **Locations:** {', '.join(selected_locations) if selected_locations else 'All'}
            """

            if df_filtered.empty:
                st.warning("No data matches the selected filters. Please adjust your selections to display charts.")
                st.stop() # Stop execution if no data to display charts for

            # --- 3. Interactive Charts using Plotly ---
            st.header("Interactive Media Performance Visualizations 📈")
            st.markdown("Explore key metrics and trends of your Ramadan campaign with dynamic charts. Use the filters in the sidebar to drill down!")

            # Dictionaries to store figures and insights for PDF report
            figures_for_pdf = {}
            insights_for_pdf = {}

            # Use tabs for a cleaner layout of charts
            tab1, tab2, tab3 = st.tabs(["Sentiment & Media", "Engagement Trends", "Platform & Location"])

            with tab1:
                # --- Chart 1: Sentiment Breakdown (Pie Chart) ---
                st.subheader("1. Sentiment Breakdown 💬")
                sentiment_counts = df_filtered['sentiment'].value_counts().reset_index()
                sentiment_counts.columns = ['Sentiment', 'Count']
                fig_sentiment = px.pie(sentiment_counts,
                                       values='Count',
                                       names='Sentiment',
                                       title='Distribution of Sentiments',
                                       color_discrete_sequence=px.colors.qualitative.Pastel)
                fig_sentiment.update_traces(textposition='inside', textinfo='percent+label', hole=0.3) # Donut chart
                st.plotly_chart(fig_sentiment, use_container_width=True)
                figures_for_pdf["1. Sentiment Breakdown"] = fig_sentiment

                if client:
                    with st.expander("View AI Insights for Sentiment Breakdown"):
                        with st.spinner("Generating insights..."):
                            sentiment_description = df_filtered['sentiment'].value_counts(normalize=True).to_string()
                            insights_sentiment = get_insights(sentiment_description, "Sentiment Breakdown", selected_model)
                            st.info(f"**Top 3 Insights (Sentiment Breakdown):**\n{insights_sentiment}")
                            insights_for_pdf["1. Sentiment Breakdown"] = insights_sentiment
                st.divider()

                # --- Chart 4: Media Type Mix (Pie Chart) ---
                st.subheader("2. Media Type Mix 🖼️")
                media_type_counts = df_filtered['media_type'].value_counts().reset_index()
                media_type_counts.columns = ['Media Type', 'Count']
                fig_media_type = px.pie(media_type_counts,
                                        values='Count',
                                        names='Media Type',
                                        title='Distribution of Media Types',
                                        color_discrete_sequence=px.colors.qualitative.G10)
                fig_media_type.update_traces(textposition='inside', textinfo='percent+label', hole=0.3) # Donut chart
                st.plotly_chart(fig_media_type, use_container_width=True)
                figures_for_pdf["2. Media Type Mix"] = fig_media_type

                if client:
                    with st.expander("View AI Insights for Media Type Mix"):
                        with st.spinner("Generating insights..."):
                            media_description = df_filtered['media_type'].value_counts(normalize=True).to_string()
                            insights_media_type = get_insights(media_description, "Media Type Mix", selected_model)
                            st.info(f"**Top 3 Insights (Media Type Mix):**\n{insights_media_type}")
                            insights_for_pdf["2. Media Type Mix"] = insights_media_type
                st.divider()

            with tab2:
                # --- Chart 2: Engagement Trend Over Time (Line Chart) ---
                st.subheader("3. Engagement Trend Over Time ⏳")
                # Group by date and sum engagements for the trend
                daily_engagements = df_filtered.groupby('date')['engagements'].sum().reset_index()
                fig_engagement_trend = px.line(daily_engagements,
                                               x='date',
                                               y='engagements',
                                               title='Total Engagements Over Time',
                                               markers=True,
                                               line_shape='spline',
                                               color_discrete_sequence=['#FF5733']) # A vibrant orange
                fig_engagement_trend.update_layout(xaxis_title="Date", yaxis_title="Total Engagements")
                st.plotly_chart(fig_engagement_trend, use_container_width=True)
                figures_for_pdf["3. Engagement Trend Over Time"] = fig_engagement_trend

                if client:
                    with st.expander("View AI Insights for Engagement Trend"):
                        with st.spinner("Generating insights..."):
                            engagement_description = daily_engagements.to_string()
                            insights_engagement_trend = get_insights(engagement_description, "Engagement Trend Over Time", selected_model)
                            st.info(f"**Top 3 Insights (Engagement Trend):**\n{insights_engagement_trend}")
                            insights_for_pdf["3. Engagement Trend Over Time"] = insights_engagement_trend
                st.divider()

            with tab3:
                # --- Chart 3: Platform Engagements (Bar Chart) ---
                st.subheader("4. Platform Engagements 📱")
                platform_engagements = df_filtered.groupby('platform')['engagements'].sum().sort_values(ascending=False).reset_index()
                fig_platform_engagements = px.bar(platform_engagements,
                                                  x='platform',
                                                  y='engagements',
                                                  title='Total Engagements by Platform',
                                                  color='platform',
                                                  color_discrete_sequence=px.colors.qualitative.Set2)
                fig_platform_engagements.update_layout(xaxis_title="Platform", yaxis_title="Total Engagements")
                st.plotly_chart(fig_platform_engagements, use_container_width=True)
                figures_for_pdf["4. Platform Engagements"] = fig_platform_engagements

                if client:
                    with st.expander("View AI Insights for Platform Engagements"):
                        with st.spinner("Generating insights..."):
                            platform_description = platform_engagements.to_string()
                            insights_platform = get_insights(platform_description, "Platform Engagements", selected_model)
                            st.info(f"**Top 3 Insights (Platform Engagements):**\n{insights_platform}")
                            insights_for_pdf["4. Platform Engagements"] = insights_platform
                st.divider()

                # --- Chart 5: Top 5 Locations (Bar Chart) ---
                st.subheader("5. Top 5 Locations by Engagements 📍")
                location_engagements = df_filtered.groupby('location')['engagements'].sum().nlargest(5).reset_index()
                fig_top_locations = px.bar(location_engagements,
                                           x='location',
                                           y='engagements',
                                           title='Top 5 Locations by Total Engagements',
                                           color='engagements',
                                           color_continuous_scale=px.colors.sequential.Tealgrn) # A nice gradient
                fig_top_locations.update_layout(xaxis_title="Location", yaxis_title="Total Engagements")
                st.plotly_chart(fig_top_locations, use_container_width=True)
                figures_for_pdf["5. Top 5 Locations by Engagements"] = fig_top_locations

                if client:
                    with st.expander("View AI Insights for Top 5 Locations"):
                        with st.spinner("Generating insights..."):
                            location_description = location_engagements.to_string()
                            insights_locations = get_insights(location_description, "Top 5 Locations by Engagements", selected_model)
                            st.info(f"**Top 3 Insights (Top 5 Locations):**\n{insights_locations}")
                            insights_for_pdf["5. Top 5 Locations by Engagements"] = insights_locations
                st.divider()

            st.markdown("---")
            st.success("Dashboard Analysis Complete! ✨ Explore the tabs above and use the sidebar filters!")

            # --- PDF Report Download ---
            st.header("Download Report 📄")
            report_filename = st.text_input(
                "Enter desired PDF report name:",
                value=f"Ramadan_Campaign_Report_{datetime.now().strftime('%Y%m%d')}",
                help="Specify a name for your PDF report. It will be saved as '.pdf'."
            )

            if st.button("Generate & Download PDF Report ⬇️"):
                if not figures_for_pdf: # Check if charts were generated successfully
                    st.warning("No charts were generated. Please ensure your data is correctly processed and filters don't result in empty data before generating a report.")
                else:
                    with st.spinner("Generating PDF report... This may take a moment."):
                        try:
                            pdf_bytes = generate_pdf_report(figures_for_pdf, insights_for_pdf, report_name=report_filename, filters_summary=filters_summary_text)
                            st.download_button(
                                label="Click to Download PDF",
                                data=pdf_bytes,
                                file_name=f"{report_filename}.pdf",
                                mime="application/pdf"
                            )
                            st.success("PDF report generated successfully!")
                        except Exception as e:
                            st.error(f"Error generating PDF report: {e}. Please check your data or try again. Details: {e}")
            st.markdown("---")
            st.markdown("Developed with ❤️ using Streamlit, Plotly, OpenRouter AI, and ReportLab.")

    except Exception as e: # This is the outer except block for reading CSV
        st.error(f"Error reading file: {e}. Please ensure it's a valid CSV file with correct formatting (e.g., comma-separated values).")
        df = None # Ensure df is None if initial read fails
else:
    # This 'else' correctly matches the outermost 'if uploaded_file is not None:'
    st.info("⬆️ Please upload a CSV file in the sidebar to get started with your Ramadan Campaign analysis.")
    st.image("https://images.unsplash.com/photo-1549449089-a2e6e3c8f3a3?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
             caption="Ramadan Campaign Insights", use_column_width=True)
    st.markdown("""
    **💡 Tip:** Your CSV file should have the following columns for best results:
    - `Date`: Format like `YYYY-MM-DD` (e.g., `2023-03-10`)
    - `Platform`: Text, e.g., `Facebook`, `Instagram`, `Twitter`
    - `Sentiment`: Text, e.g., `Positive`, `Negative`, `Neutral`
    - `Location`: Text, e.g., `Dubai`, `Indonesia`, `USA`
    - `Engagements`: Numeric (integers or floats)
    - `Media Type`: Text, e.g., `Image`, `Video`, `Text`
    """)
