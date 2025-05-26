import streamlit as st
import pandas as pd
import plotly.express as px
import io # Required for handling file upload as a BytesIO object

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Ramadan Campaign Intelligence",
    page_icon="🕌",
    layout="wide", # Use wide layout for better chart visibility
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a more polished look (Creative UI) ---
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6; /* Light grey background */
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5%;
        padding-right: 5%;
    }
    h1 {
        color: #4CAF50; /* Green for main title */
        text-align: center;
        font-size: 3em;
        margin-bottom: 0.5em;
    }
    h2 {
        color: #2196F3; /* Blue for section headers */
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    h3 {
        color: #FF9800; /* Orange for chart titles */
        font-size: 1.5em;
        margin-top: 1.5rem;
    }
    .stFileUploader {
        border: 2px dashed #9E9E9E;
        padding: 20px;
        border-radius: 10px;
        background-color: #ffffff;
    }
    .stAlert {
        border-radius: 8px;
    }
    .stPlotlyChart {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        padding: 10px;
        background-color: #ffffff;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        color: #4CAF50;
    }
    .metric-title {
        font-size: 1em;
        color: #616161;
    }
    /* Style for insights */
    .insight-box {
        background-color: #e8f5e9; /* Light green background */
        border-left: 5px solid #4CAF50; /* Green border */
        padding: 15px;
        margin-top: 15px;
        border-radius: 5px;
        font-style: italic;
        color: #333333;
    }
    .insight-box ul {
        margin-bottom: 0;
        padding-left: 20px;
    }
    .insight-box li {
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Title and Introduction ---
st.markdown("<h1>Interactive Media Intelligence Dashboard</h1>", unsafe_allow_html=True)
st.markdown("### 🕌 Ramadan Campaign Performance Overview 📈")
st.markdown("""
Welcome to your Ramadan Campaign Media Intelligence Dashboard! Upload your data to unlock insights into sentiment, engagement, platform performance, and geographical reach.
""", unsafe_allow_html=True)

# --- 1. Ask the user to upload a CSV file ---
st.header("Upload Your Campaign Data")
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
        # Normalize column names
        st.spinner("Cleaning data...")
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

        # --- Error Checking for Required Columns ---
        required_columns = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            st.error(
                f"**Data Error:** Your CSV is missing essential columns. "
                f"Please ensure it contains: **{', '.join(col.capitalize() for col in required_columns)}**. "
                f"Missing: **{', '.join(col.capitalize() for col in missing_columns)}**."
            )
            df = None # Invalidate df to prevent charts from being built
        else:
            # Convert 'Date' to datetime
            try:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                if df['date'].isnull().any():
                    st.warning("Warning: Some 'Date' entries could not be parsed and were set to NaT (Not a Time). These rows might be excluded from time-based analysis.")
                    df.dropna(subset=['date'], inplace=True) # Drop rows where date couldn't be converted
            except Exception as e:
                st.error(f"**Data Error:** Failed to convert 'Date' column to datetime. Please check date format. Error: {e}")
                df = None # Invalidate df

            # Fill missing 'Engagements' with 0 and ensure numeric
            if df is not None: # Check if df is still valid after date conversion
                initial_engagement_na = df['engagements'].isnull().sum()
                df['engagements'] = pd.to_numeric(df['engagements'], errors='coerce').fillna(0)
                if df['engagements'].isnull().any():
                    st.warning("Warning: Some 'Engagements' values could not be converted to numbers and were set to 0. Please check your data quality.")
                elif initial_engagement_na > 0:
                    st.info(f"Filled {initial_engagement_na} missing 'Engagements' values with 0.")

            if df is not None:
                st.success("Data cleaning complete! Ready for analysis.")
                # Optional: Show a small glimpse of cleaned data if user insists (e.g., via expander)
                with st.expander("Peek at the Cleaned Data"):
                    st.dataframe(df.head())

    except pd.errors.EmptyDataError:
        st.error("**Upload Error:** The uploaded CSV file is empty. Please upload a file with data.")
        df = None
    except pd.errors.ParserError:
        st.error("**Upload Error:** Could not parse the CSV file. Please ensure it's a valid CSV format.")
        df = None
    except Exception as e:
        st.error(f"**An unexpected error occurred:** {e}. Please check your CSV file and try again.")
        df = None

# --- Display Charts only if data is successfully loaded and cleaned ---
if df is not None and not df.empty:
    st.markdown("---")
    st.header("Ramadan Campaign Performance Insights")
    st.markdown("Dive into the interactive charts below to understand your campaign's impact.")

    # --- Key Metrics (Creative UI) ---
    st.subheader("Key Campaign Metrics")
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

    total_engagements = df['engagements'].sum()
    unique_platforms = df['platform'].nunique()
    dominant_sentiment = df['sentiment'].mode()[0] if not df['sentiment'].empty else "N/A"

    with col_kpi1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_engagements:,.0f}</div>
            <div class="metric-title">Total Engagements</div>
        </div>
        """, unsafe_allow_html=True)
    with col_kpi2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{unique_platforms}</div>
            <div class="metric-title">Active Platforms</div>
        </div>
        """, unsafe_allow_html=True)
    with col_kpi3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{dominant_sentiment}</div>
            <div class="metric-title">Dominant Sentiment</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- 3. Build 5 interactive charts using Plotly ---
    # Using columns for better layout of charts
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
        st.markdown("""
        <div class="insight-box">
        **Top 3 Insights: Sentiment Breakdown**
        <ul>
            <li>Understand the **prevailing emotional tone** of your campaign's reception (positive, negative, neutral).</li>
            <li>Identify if there's a significant **skew towards negative sentiment**, indicating areas for immediate attention or crisis management.</li>
            <li>Gauge the **overall success** of your messaging in eliciting positive public reaction.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with chart_col2:
        # 2. Bar chart: Platform Engagements
        st.markdown("<h3>Platform Engagements</h3>", unsafe_allow_html=True)
        platform_engagements = df.groupby('platform')['engagements'].sum().reset_index()
        platform_engagements = platform_engagements.sort_values(by='engagements', ascending=False)
        fig_platform_engagements = px.bar(platform_engagements, x='engagements', y='platform', orientation='h',
                                           title='**Total Engagements Across Platforms**',
                                           labels={'platform': 'Platform', 'engagements': 'Total Engagements'},
                                           color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_platform_engagements.update_layout(yaxis={'categoryorder':'total ascending'}, title_x=0.5) # Ensures highest engagement platform is at the top
        st.plotly_chart(fig_platform_engagements, use_container_width=True)
        st.markdown("""
        <div class="insight-box">
        **Top 3 Insights: Platform Engagements**
        <ul>
            <li>Identify the **most impactful platforms** that generate the highest engagement for your Ramadan campaign.</li>
            <li>Strategically **reallocate resources** towards platforms with higher engagement rates to maximize reach and impact.</li>
            <li>Discover **underperforming platforms** that might need a revised content strategy or reduced focus.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

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
    st.markdown("""
    <div class="insight-box">
    **Top 3 Insights: Engagement Trend Over Time**
    <ul>
        <li>Pinpoint **peak engagement days or periods**, which might correspond to specific campaign pushes or key Ramadan events.</li>
        <li>Observe the **overall trajectory** of your campaign's engagement (growing, declining, stable) to assess its longevity.</li>
        <li>Identify any **sudden spikes or drops** that require further investigation into their causes (e.g., viral content, PR incidents).</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

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
        st.markdown("""
        <div class="insight-box">
        **Top 3 Insights: Media Type Mix**
        <ul>
            <li>Understand the **dominant content formats** (e.g., video, image, text) your campaign is utilizing.</li>
            <li>Assess if your current media mix **aligns with audience preferences** and platform best practices for optimal engagement.</li>
            <li>Identify opportunities to **diversify your content strategy** to reach a broader segment of your audience or refresh engagement.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with chart_col4:
        # 5. Bar chart: Top 5 Locations
        st.markdown("<h3>Top 5 Locations</h3>", unsafe_allow_html=True)
        location_engagements = df.groupby('location')['engagements'].sum().reset_index()
        top_5_locations = location_engagements.sort_values(by='engagements', ascending=False).head(5)
        fig_top_locations = px.bar(top_5_locations, x='location', y='engagements',
                                   title='**Top 5 Locations by Total Engagements**',
                                   labels={'location': 'Location', 'engagements': 'Total Engagements'},
                                   color_discrete_sequence=px.colors.qualitative.Vivid)
        fig_top_locations.update_layout(title_x=0.5)
        st.plotly_chart(fig_top_locations, use_container_width=True)
        st.markdown("""
        <div class="insight-box">
        **Top 3 Insights: Top 5 Locations**
        <ul>
            <li>Pinpoint the **geographical hotbeds** where your campaign is generating the most significant interest and engagement.</li>
            <li>Inform **localized marketing strategies** by understanding where your message resonates most effectively.</li>
            <li>Discover potential **untapped or emerging markets** if new locations appear in the top rankings.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---") # Final separator

    # --- Sidebar for Navigation/Additional Info (Creative UI) ---
    st.sidebar.title("Dashboard Controls")
    st.sidebar.markdown("Navigate through sections or explore additional options.")

    if st.sidebar.button("Scroll to Top"):
        st.markdown("<script>window.scrollTo(0,0);</script>", unsafe_allow_html=True)

    st.sidebar.header("🚀 Future Enhancements")
    st.sidebar.markdown("""
    Your dashboard can evolve! Consider these features:
    * **Date Range Selector:** Filter data for specific periods.
    * **Interactive Filters:** Dropdowns for `Platform`, `Sentiment`, `Media Type`.
    * **Engagement Rate:** Calculate and visualize (Engagements / Mentions).
    * **Sentiment Over Time by Platform:** Analyze trends per platform.
    * **Download Report:** Export current dashboard view or summarized data.
    """)
    st.sidebar.info("Developed with ❤️ using Streamlit, Pandas, and Plotly.")

else:
    if uploaded_file is None:
        st.info("Upload a CSV file to begin your Ramadan Campaign analysis. Look for the 'Choose a CSV file' button above!")
    elif df is not None and df.empty:
        st.warning("The uploaded file contains data but is empty after cleaning (e.g., all rows dropped due to malformed dates). Please check your data.")
