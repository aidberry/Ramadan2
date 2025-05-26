import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Interactive Media Intelligence Dashboard – Ramadan Campaign",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for a more polished look ---
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #f8f9fa;
        padding-top: 2rem;
    }
    h1 {
        color: #4CAF50; /* A pleasant green for the title */
        text-align: center;
        font-size: 3em;
        margin-bottom: 0.5em;
    }
    h2 {
        color: #2196F3; /* Blue for section headers */
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 10px;
        margin-top: 2em;
    }
    h3 {
        color: #FF9800; /* Orange for sub-headers */
        margin-top: 1.5em;
    }
    .stFileUploader label {
        font-size: 1.2em;
        color: #3F51B5; /* Darker blue for uploader label */
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 0.75em 1.5em;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
        cursor: pointer;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .css-1d391kg e16z80pt1 { /* Adjusting default font size if needed */
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.header("Dashboard Controls ⚙️")
st.sidebar.info("Upload your CSV, explore the data, and get insights!")

# --- Main Title ---
st.title("🕌 Interactive Media Intelligence Dashboard – Ramadan Campaign 📊")
st.markdown("A comprehensive tool to analyze your social media campaign performance during Ramadan.")

# --- API Key Input ---
st.sidebar.subheader("OpenRouter API Configuration")
openrouter_api_key = st.sidebar.text_input(
    "Enter your OpenRouter API Key:", type="password", help="Get your API key from openrouter.ai"
)
selected_model = st.sidebar.selectbox(
    "Select AI Model for Insights:",
    ["mistralai/mistral-7b-instruct-v0.1", "google/gemma-7b", "nousresearch/nous-hermes-2-mixtral-8x7b-dpo"], # Free models that should work
    index=0, # Default selection
    help="Choose a free model available on OpenRouter for generating insights."
)

if openrouter_api_key:
    os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
    )
else:
    st.sidebar.warning("Please enter your OpenRouter API Key to enable AI insights.")
    client = None

# --- Function to generate insights using OpenRouter ---
@st.cache_data(show_spinner="Generating insights with AI...")
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
        return f"Error generating insights: {e}. Please check your API key and model selection."

# --- 1. Upload CSV File ---
st.header("Upload Your Campaign Data 📤")
st.markdown("Please upload a CSV file containing your media intelligence data. Make sure it includes the columns: `Date`, `Platform`, `Sentiment`, `Location`, `Engagements`, `Media Type`.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv", help="Drag and drop your CSV here or click to browse.")

df = None
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("File successfully uploaded! 🎉")
        st.write("First 5 rows of your data:")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Error reading file: {e}. Please ensure it's a valid CSV.")
else:
    st.info("Awaiting CSV file upload...")

if df is not None:
    # --- 2. Data Cleaning and Preparation ---
    st.header("Data Cleaning and Preparation 🧹")
    st.markdown("Performing essential data cleaning steps to ensure accuracy and consistency for analysis.")

    original_columns = df.columns.tolist()
    
    # Normalize column names
    df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]
    
    # Check for required columns after normalization
    required_columns = ['date', 'platform', 'sentiment', 'location', 'engagements', 'media_type']
    if not all(col in df.columns for col in required_columns):
        missing_cols = [col for col in required_columns if col not in df.columns]
        st.error(f"Error: The uploaded CSV is missing the following required columns: {', '.join(missing_cols)}. Please check your file.")
        df = None # Invalidate df if critical columns are missing
    
    if df is not None:
        # Convert 'date' to datetime
        try:
            df['date'] = pd.to_datetime(df['date'])
            st.success("✅ 'Date' column converted to datetime format.")
        except Exception as e:
            st.error(f"Error converting 'Date' column to datetime: {e}. Please ensure the date format is consistent.")
            df = None # Invalidate df if date conversion fails

    if df is not None:
        # Fill missing 'engagements' with 0
        initial_na_engagements = df['engagements'].isnull().sum()
        df['engagements'] = df['engagements'].fillna(0)
        if initial_na_engagements > 0:
            st.warning(f"⚠️ Filled {initial_na_engagements} missing 'Engagements' values with 0.")
        else:
            st.success("✅ No missing 'Engagements' found.")

        st.success("✅ Column names normalized (e.g., 'Media Type' -> 'media_type').")
        st.write("Cleaned Data Snapshot:")
        st.dataframe(df.head())

        # Display some basic stats
        st.subheader("Basic Data Statistics")
        # --- THE CHANGE IS HERE ---
        st.write(df.describe(include='all')) # Removed datetime_is_numeric=True
        # --- END CHANGE ---

        # --- 3. Interactive Charts using Plotly ---
        st.header("Interactive Media Performance Visualizations 📈")
        st.markdown("Explore key metrics and trends of your Ramadan campaign with dynamic charts.")

        # --- Chart 1: Sentiment Breakdown (Pie Chart) ---
        st.subheader("1. Sentiment Breakdown 💬")
        sentiment_counts = df['sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig_sentiment = px.pie(sentiment_counts, 
                               values='Count', 
                               names='Sentiment', 
                               title='Distribution of Sentiments',
                               color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_sentiment.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_sentiment, use_container_width=True)
        
        if client:
            with st.spinner("Generating insights for Sentiment Breakdown..."):
                sentiment_description = df['sentiment'].value_counts(normalize=True).to_string()
                insights_sentiment = get_insights(sentiment_description, "Sentiment Breakdown", selected_model)
                st.info(f"**Top 3 Insights (Sentiment Breakdown):**\n{insights_sentiment}")

        # --- Chart 2: Engagement Trend Over Time (Line Chart) ---
        st.subheader("2. Engagement Trend Over Time ⏳")
        daily_engagements = df.groupby('date')['engagements'].sum().reset_index()
        fig_engagement_trend = px.line(daily_engagements, 
                                       x='date', 
                                       y='engagements', 
                                       title='Total Engagements Over Time',
                                       markers=True,
                                       line_shape='spline',
                                       color_discrete_sequence=['#FF5733']) # A vibrant orange
        fig_engagement_trend.update_layout(xaxis_title="Date", yaxis_title="Total Engagements")
        st.plotly_chart(fig_engagement_trend, use_container_width=True)

        if client:
            with st.spinner("Generating insights for Engagement Trend..."):
                engagement_description = daily_engagements.to_string()
                insights_engagement_trend = get_insights(engagement_description, "Engagement Trend Over Time", selected_model)
                st.info(f"**Top 3 Insights (Engagement Trend):**\n{insights_engagement_trend}")

        # --- Chart 3: Platform Engagements (Bar Chart) ---
        st.subheader("3. Platform Engagements 📱")
        platform_engagements = df.groupby('platform')['engagements'].sum().sort_values(ascending=False).reset_index()
        fig_platform_engagements = px.bar(platform_engagements, 
                                          x='platform', 
                                          y='engagements', 
                                          title='Total Engagements by Platform',
                                          color='platform',
                                          color_discrete_sequence=px.colors.qualitative.Set2)
        fig_platform_engagements.update_layout(xaxis_title="Platform", yaxis_title="Total Engagements")
        st.plotly_chart(fig_platform_engagements, use_container_width=True)

        if client:
            with st.spinner("Generating insights for Platform Engagements..."):
                platform_description = platform_engagements.to_string()
                insights_platform = get_insights(platform_description, "Platform Engagements", selected_model)
                st.info(f"**Top 3 Insights (Platform Engagements):**\n{insights_platform}")

        # --- Chart 4: Media Type Mix (Pie Chart) ---
        st.subheader("4. Media Type Mix 🖼️")
        media_type_counts = df['media_type'].value_counts().reset_index()
        media_type_counts.columns = ['Media Type', 'Count']
        fig_media_type = px.pie(media_type_counts, 
                                values='Count', 
                                names='Media Type', 
                                title='Distribution of Media Types',
                                color_discrete_sequence=px.colors.qualitative.G10)
        fig_media_type.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_media_type, use_container_width=True)

        if client:
            with st.spinner("Generating insights for Media Type Mix..."):
                media_description = df['media_type'].value_counts(normalize=True).to_string()
                insights_media_type = get_insights(media_description, "Media Type Mix", selected_model)
                st.info(f"**Top 3 Insights (Media Type Mix):**\n{insights_media_type}")

        # --- Chart 5: Top 5 Locations (Bar Chart) ---
        st.subheader("5. Top 5 Locations by Engagements 📍")
        location_engagements = df.groupby('location')['engagements'].sum().nlargest(5).reset_index()
        fig_top_locations = px.bar(location_engagements, 
                                   x='location', 
                                   y='engagements', 
                                   title='Top 5 Locations by Total Engagements',
                                   color='engagements',
                                   color_continuous_scale=px.colors.sequential.Tealgrn) # A nice gradient
        fig_top_locations.update_layout(xaxis_title="Location", yaxis_title="Total Engagements")
        st.plotly_chart(fig_top_locations, use_container_width=True)

        if client:
            with st.spinner("Generating insights for Top 5 Locations..."):
                location_description = location_engagements.to_string()
                insights_locations = get_insights(location_description, "Top 5 Locations by Engagements", selected_model)
                st.info(f"**Top 3 Insights (Top 5 Locations):**\n{insights_locations}")

        st.markdown("---")
        st.success("Dashboard Analysis Complete! ✨")
        st.markdown("Thank you for using the Interactive Media Intelligence Dashboard. We hope these insights help optimize your Ramadan campaign!")
        st.markdown("Developed with ❤️ using Streamlit, Plotly, and OpenRouter AI.")
