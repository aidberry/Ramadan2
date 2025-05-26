import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os # For environment variables, although we'll use direct input for API key
from openai import OpenAI # The OpenRouter API is compatible with the OpenAI SDK

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Ramadan Campaign AI Dashboard",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a more polished look (Creative UI) ---
st.markdown("""
<style>
    /* Overall background and text */
    .stApp {
        background-color: #f0f2f6; /* Light grey background */
        color: #333333;
    }

    /* Main content container padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5%;
        padding-right: 5%;
    }

    /* Titles */
    h1 {
        color: #4CAF50; /* Green for main title */
        text-align: center;
        font-size: 3em;
        margin-bottom: 0.5em;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    h2 {
        color: #2196F3; /* Blue for section headers */
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        font-size: 2em;
    }
    h3 {
        color: #FF9800; /* Orange for chart titles */
        font-size: 1.5em;
        margin-top: 1.5rem;
        text-align: center;
    }

    /* File Uploader styling */
    .stFileUploader {
        border: 2px dashed #9E9E9E;
        padding: 20px;
        border-radius: 10px;
        background-color: #ffffff;
        text-align: center;
        font-size: 1.1em;
        color: #555555;
    }
    .stFileUploader > div > button { /* Specific to the upload button */
        background-color: #4CAF50 !important;
        color: white !important;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 1em;
    }

    /* Alerts and messages */
    .stAlert {
        border-radius: 8px;
        font-size: 1.05em;
    }
    .stSuccess {
        background-color: #e8f5e9; /* Light green */
        color: #2e7d32; /* Darker green */
        border-left: 5px solid #4CAF50;
    }
    .stError {
        background-color: #ffebee; /* Light red */
        color: #c62828; /* Darker red */
        border-left: 5px solid #ef5350;
    }
    .stWarning {
        background-color: #fffde7; /* Light yellow */
        color: #fbc02d; /* Darker yellow */
        border-left: 5px solid #ffeb3b;
    }
    .stInfo {
        background-color: #e3f2fd; /* Light blue */
        color: #1976d2; /* Darker blue */
        border-left: 5px solid #2196F3;
    }

    /* Plotly Chart styling */
    .stPlotlyChart {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.1);
        padding: 10px;
        background-color: #ffffff;
        margin-bottom: 2rem;
    }

    /* Metric cards (KPIs) */
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.08);
        text-align: center;
        margin-bottom: 1.5rem;
        border-left: 5px solid; /* Dynamic border color */
    }
    .metric-card.green-border { border-left-color: #4CAF50; }
    .metric-card.blue-border { border-left-color: #2196F3; }
    .metric-card.orange-border { border-left-color: #FF9800; }

    .metric-value {
        font-size: 2.8em;
        font-weight: bold;
        color: #333333; /* Darker color for value */
        margin-bottom: 0.2em;
    }
    .metric-title {
        font-size: 1.1em;
        color: #616161;
        font-weight: 500;
    }

    /* Insight boxes */
    .insight-box {
        background-color: #e8f5e9; /* Light green background */
        border-left: 5px solid #4CAF50; /* Green border */
        padding: 15px 20px;
        margin-top: 15px;
        margin-bottom: 25px;
        border-radius: 8px;
        font-size: 0.95em;
        color: #333333;
        line-height: 1.6;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.05);
    }
    .insight-box ul {
        margin-bottom: 0;
        padding-left: 25px;
        list-style-type: disc;
    }
    .insight-box li {
        margin-bottom: 8px;
    }
    .insight-box li:last-child {
        margin-bottom: 0;
    }
    .insight-box strong {
        color: #2e7d32; /* Darker green for emphasis */
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize OpenAI Client (OpenRouter Compatible) ---
# Use Streamlit secrets or direct input for API key
openrouter_api_key = st.sidebar.text_input(
    "Enter your OpenRouter API Key:",
    type="password",
    help="You can get your API key from openrouter.ai after signing up."
)

client = None
if openrouter_api_key:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
    )
    st.sidebar.success("OpenRouter API Key set!")
else:
    st.sidebar.warning("Please enter your OpenRouter API Key to enable AI insights.")

# --- Function to Get AI Insights ---
@st.cache_data(show_spinner="Generating AI insights...")
def get_ai_insights(prompt_text, data_summary):
    if not client:
        return "OpenRouter API key is not provided. Cannot generate AI insights."

    full_prompt = f"""
    You are an expert Media Intelligence Analyst. Your task is to analyze the provided data summary for a Ramadan Campaign and extract 3 key, actionable insights.
    Focus on trends, anomalies, and strategic implications. Be concise and professional.
    Data Summary:
    {data_summary}

    Based on this, provide 3 key insights relevant for a media intelligence professional, formatted as a numbered list. Each insight should be a single, clear sentence.
    """
    try:
        response = client.chat.completions.create(
            model="google/gemma-3n-e4b-it:free", # Using the specified model
            messages=[
                {"role": "system", "content": "You are a concise Media Intelligence Analyst generating key insights."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        insights = response.choices[0].message.content.strip()
        return insights
    except Exception as e:
        return f"Error generating AI insights: {e}. Please check your API key and try again later."


# --- Title and Introduction ---
st.markdown("<h1>Interactive Media Intelligence Dashboard</h1>", unsafe_allow_html=True)
st.markdown("### 🕌 Ramadan Campaign Performance Overview ✨")
st.markdown("""
Welcome to your Ramadan Campaign Media Intelligence Dashboard! Upload your data to unlock insights into sentiment, engagement, platform performance, and geographical reach.
""", unsafe_allow_html=True)

# --- 1. Ask the user to upload a CSV file ---
st.header("1. Upload Your Campaign Data")
st.markdown("Please upload a CSV file containing your media intelligence data. Ensure it has the following columns: `Date`, `Platform`, `Sentiment`, `Location`, `Engagements`, `Media Type`.")

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    help="Click to browse or drag and drop your .csv file here. Data will be processed automatically."
)

df = None # Initialize df to None

if uploaded_file is not None:
    try:
        # Read the uploaded CSV file
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully! Processing data...")

        # --- 2. Clean the data (silent processing) ---
        with st.spinner("Cleaning and validating data..."):
            # Normalize column names
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

            # --- Error Checking for Required Columns ---
            required_columns = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                st.error(
                    f"**Data Error:** Your CSV is missing essential columns. "
                    f"Please ensure it contains: **`{', '.join(col.capitalize() for col in required_columns)}`**. "
                    f"Missing: **`{', '.join(col.capitalize() for col in missing_columns)}`**."
                )
                df = None # Invalidate df to prevent charts from being built
            else:
                # Convert 'Date' to datetime
                original_rows = len(df)
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                if df['date'].isnull().any():
                    na_dates = df['date'].isnull().sum()
                    st.warning(f"Warning: {na_dates} 'Date' entries could not be parsed and those rows were dropped. Please check your date format.")
                    df.dropna(subset=['date'], inplace=True) # Drop rows where date couldn't be converted
                if df.empty:
                    st.error("Error: All rows were dropped after cleaning 'Date' column. Please check your date formats or ensure your file has data.")
                    df = None

                # Fill missing 'Engagements' with 0 and ensure numeric
                if df is not None: # Check if df is still valid after date conversion
                    initial_engagement_na = df['engagements'].isnull().sum()
                    df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0)
                    if df['engagements'].isnull().any():
                        st.warning("Warning: Some 'Engagements' values could not be converted to numbers and were set to 0. Please check your data quality.")
                    elif initial_engagement_na > 0:
                        st.info(f"Filled {initial_engagement_na} missing 'Engagements' values with 0.")

                if df is not None:
                    cleaned_rows = len(df)
                    st.success(f"Data cleaning complete! {cleaned_rows} rows processed (out of {original_rows} original). Ready for analysis.")
                    # Optional: Show a small glimpse of cleaned data if user insists (e.g., via expander)
                    with st.expander("Peek at the Cleaned Data"):
                        st.dataframe(df.head())
                        st.json({
                            "Total Rows after cleaning": cleaned_rows,
                            "Unique Platforms": df['platform'].nunique(),
                            "Unique Sentiments": df['sentiment'].nunique(),
                            "Date Range": f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}" if not df['date'].empty else "N/A"
                        })


    except pd.errors.EmptyDataError:
        st.error("**Upload Error:** The uploaded CSV file is empty. Please upload a file with data.")
        df = None
    except pd.errors.ParserError:
        st.error("**Upload Error:** Could not parse the CSV file. Please ensure it's a valid CSV format.")
        df = None
    except Exception as e:
        st.error(f"**An unexpected error occurred during file processing:** {e}. Please check your CSV file and try again.")
        df = None

# --- Display Charts only if data is successfully loaded and cleaned ---
if df is not None and not df.empty:
    st.markdown("---")
    st.header("2. Ramadan Campaign Performance Insights")
    st.markdown("Dive into the interactive charts below to understand your campaign's impact, complemented by AI-driven insights.")

    # --- Key Metrics (KPIs) ---
    st.subheader("Key Campaign Metrics")
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

    total_engagements = df['engagements'].sum()
    unique_platforms = df['platform'].nunique()
    dominant_sentiment = df['sentiment'].mode()[0] if not df['sentiment'].empty else "N/A"

    with col_kpi1:
        st.markdown(f"""
        <div class="metric-card green-border">
            <div class="metric-value">{total_engagements:,.0f}</div>
            <div class="metric-title">Total Engagements</div>
        </div>
        """, unsafe_allow_html=True)
    with col_kpi2:
        st.markdown(f"""
        <div class="metric-card blue-border">
            <div class="metric-value">{unique_platforms}</div>
            <div class="metric-title">Active Platforms</div>
        </div>
        """, unsafe_allow_html=True)
    with col_kpi3:
        st.markdown(f"""
        <div class="metric-card orange-border">
            <div class="metric-value">{dominant_sentiment}</div>
            <div class="metric-title">Dominant Sentiment</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- AI Disclaimer ---
    st.info("💡 **AI-Powered Insights:** The insights below are generated by an AI model (Gemma via OpenRouter). While powerful, AI can sometimes produce inaccuracies or 'hallucinations'. Always cross-reference with raw data and expert judgment.")
    st.markdown("---")


    # --- 3. Build 5 interactive charts using Plotly ---
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # 1. Pie chart: Sentiment Breakdown
        st.markdown("<h3>Sentiment Breakdown</h3>", unsafe_allow_html=True)
        sentiment_counts = df['sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig_sentiment = px.pie(sentiment_counts, values='Count', names='Sentiment',
                               title='**Overall Sentiment Distribution**', hole=0.4,
                               color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_sentiment.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
        fig_sentiment.update_layout(showlegend=True, title_x=0.5)
        st.plotly_chart(fig_sentiment, use_container_width=True)

        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown('<h4>✨ AI Insights: Sentiment Breakdown</h4>', unsafe_allow_html=True)
        # --- Generate Sentiment Insights ---
        sentiment_summary = sentiment_counts.to_string(index=False)
        ai_insights = get_ai_insights("Sentiment Breakdown. Values are counts of each sentiment.", sentiment_summary)
        st.markdown(ai_insights)
        st.markdown('</div>', unsafe_allow_html=True) # Close insight-box

    with chart_col2:
        # 3. Bar chart: Platform Engagements
        st.markdown("<h3>Platform Engagements</h3>", unsafe_allow_html=True)
        platform_engagements = df.groupby('platform')['engagements'].sum().reset_index()
        platform_engagements = platform_engagements.sort_values(by='engagements', ascending=False)
        fig_platform_engagements = px.bar(platform_engagements, x='engagements', y='platform', orientation='h',
                                           title='**Total Engagements Across Platforms**',
                                           labels={'platform': 'Platform', 'engagements': 'Total Engagements'},
                                           color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_platform_engagements.update_layout(yaxis={'categoryorder':'total ascending'}, title_x=0.5)
        st.plotly_chart(fig_platform_engagements, use_container_width=True)

        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown('<h4>✨ AI Insights: Platform Engagements</h4>', unsafe_allow_html=True)
        # --- Generate Platform Insights ---
        platform_summary = platform_engagements.to_string(index=False)
        ai_insights = get_ai_insights("Platform Engagements. Platforms and their total engagements.", platform_summary)
        st.markdown(ai_insights)
        st.markdown('</div>', unsafe_allow_html=True) # Close insight-box


    st.markdown("---") # Separator for the next chart

    # Line chart gets its own full width
    st.markdown("<h3>Engagement Trend Over Time</h3>", unsafe_allow_html=True)
    engagements_over_time = df.groupby('date')['engagements'].sum().reset_index()
    fig_engagement_trend = px.line(engagements_over_time, x='date', y='engagements',
                                   title='**Total Engagements Trend Throughout the Campaign**',
                                   labels={'date': 'Date', 'engagements': 'Total Engagements'},
                                   markers=True, line_shape='spline',
                                   color_discrete_sequence=['#FF4B4B']) # Streamlit red-ish
    fig_engagement_trend.update_xaxes(
        rangeselector_buttons=list([
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="YTD", step="year", stepmode="todate"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(step="all")
        ]),
        rangeslider_visible=True, # Add a range slider for easier navigation
        title_text="Date"
    )
    fig_engagement_trend.update_layout(title_x=0.5)
    st.plotly_chart(fig_engagement_trend, use_container_width=True)

    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.markdown('<h4>✨ AI Insights: Engagement Trend</h4>', unsafe_allow_html=True)
    # --- Generate Engagement Trend Insights ---
    trend_summary = engagements_over_time.to_string(index=False)
    ai_insights = get_ai_insights("Engagement Trend over time. Columns are Date and Engagements.", trend_summary)
    st.markdown(ai_insights)
    st.markdown('</div>', unsafe_allow_html=True) # Close insight-box

    st.markdown("---") # Separator for the next charts

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        # 4. Pie chart: Media Type Mix
        st.markdown("<h3>Media Type Mix</h3>", unsafe_allow_html=True)
        media_type_counts = df['media_type'].value_counts().reset_index()
        media_type_counts.columns = ['Media Type', 'Count']
        fig_media_type = px.pie(media_type_counts, values='Count', names='Media Type',
                               title='**Distribution of Content Media Types**', hole=0.4,
                               color_discrete_sequence=px.colors.qualitative.Set3)
        fig_media_type.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
        fig_media_type.update_layout(showlegend=True, title_x=0.5)
        st.plotly_chart(fig_media_type, use_container_width=True)

        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown('<h4>✨ AI Insights: Media Type Mix</h4>', unsafe_allow_html=True)
        # --- Generate Media Type Insights ---
        media_type_summary = media_type_counts.to_string(index=False)
        ai_insights = get_ai_insights("Media Type Mix. Media types and their counts.", media_type_summary)
        st.markdown(ai_insights)
        st.markdown('</div>', unsafe_allow_html=True) # Close insight-box

    with chart_col4:
        # 5. Bar chart: Top 5 Locations
        st.markdown("<h3>Top 5 Locations by Engagement</h3>", unsafe_allow_html=True)
        location_engagements = df.groupby('location')['engagements'].sum().reset_index()
        top_5_locations = location_engagements.sort_values(by='engagements', ascending=False).head(5)
        fig_top_locations = px.bar(top_5_locations, x='location', y='engagements',
                                   title='**Top 5 Locations by Total Engagements**',
                                   labels={'location': 'Location', 'engagements': 'Total Engagements'},
                                   color_discrete_sequence=px.colors.qualitative.Vivid)
        fig_top_locations.update_layout(title_x=0.5)
        st.plotly_chart(fig_top_locations, use_container_width=True)

        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown('<h4>✨ AI Insights: Top Locations</h4>', unsafe_allow_html=True)
        # --- Generate Location Insights ---
        location_summary = top_5_locations.to_string(index=False)
        ai_insights = get_ai_insights("Top 5 Locations by Engagement. Locations and their total engagements.", location_summary)
        st.markdown(ai_insights)
        st.markdown('</div>', unsafe_allow_html=True) # Close insight-box

    st.markdown("---") # Final separator

    # --- Sidebar for Navigation/Additional Info (Creative UI) ---
    st.sidebar.title("Dashboard Controls")
    st.sidebar.markdown("Navigate through sections or explore additional options.")

    if st.sidebar.button("Scroll to Top"):
        st.markdown("<script>window.scrollTo(0,0);</script>", unsafe_allow_html=True)

    st.sidebar.header("🚀 Future Enhancements")
    st.sidebar.markdown("""
    Explore more ways to enhance this dashboard:
    * **Interactive Filtering:** Add dropdowns for `Platform`, `Sentiment`, `Media Type`.
    * **Advanced Analytics:** Calculate engagement rates per post, sentiment over time by platform, etc.
    * **Downloadable Reports:** Allow users to export charts or summary data.
    * **Anomaly Detection:** Implement more sophisticated statistical methods to flag unusual data points.
    * **User Management:** For larger teams, consider user authentication.
    """)
    st.sidebar.info("Developed with ❤️ using Streamlit, Pandas, Plotly, and OpenRouter AI.")

else:
    # Initial state or if df is None due to errors
    if uploaded_file is None:
        st.info("Upload a CSV file to begin your Ramadan Campaign analysis. Look for the 'Choose a CSV file' button above!")
    elif df is not None and df.empty:
        st.warning("The uploaded file contains data but became empty after cleaning (e.g., all rows dropped due to malformed dates). Please check your data or upload a different file.")
