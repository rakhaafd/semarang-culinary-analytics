import streamlit as st
import pandas as pd
import duckdb
import os
from dotenv import load_dotenv
import plotly.express as px

# Configure Streamlit Page
st.set_page_config(page_title="Semarang Culinary Dashboard", page_icon="🍔", layout="wide")

# Muat variabel environment
load_dotenv()

# Function to connect and fetch data from MotherDuck
@st.cache_data(ttl=600) # Cache data for 10 minutes
def load_data():
    md_token = os.getenv("MOTHERDUCK_TOKEN")
    if not md_token or md_token == "your_motherduck_token_here":
        st.error("MOTHERDUCK_TOKEN is not configured in the .env file")
        return pd.DataFrame()
        
    try:
        # Connect to MotherDuck and execute query into dataframe
        con = duckdb.connect(f"md:?motherduck_token={md_token}")
        df = con.execute("SELECT * FROM restaurants_semarang").df()
        
        # Normalize column names
        df.columns = [c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_') for c in df.columns]
        
        con.close()
        return df
    except Exception as e:
        st.error(f"Failed to connect to MotherDuck: {e}")
        return pd.DataFrame()

# Main Dashboard UI
st.title("Semarang Culinary Analytics Dashboard")
st.markdown("Visualization of restaurant data scraped from Google Maps (powered by **MotherDuck**).")

# Load Data
df = load_data()

if df.empty:
    st.warning("Data not found or database connection failed. Ensure MotherDuck token is correct and data is loaded.")
else:
    # --- SIDEBAR (FILTER) ---
    st.sidebar.header("Filters")
    
    # Category Filter
    categories = ["All"] + sorted(df['category'].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Select Category", categories)
    
    # Price Filter
    price_levels = ["All", 1, 2, 3, 4]
    selected_price = st.sidebar.selectbox("Select Price Level (1=Cheap, 4=Expensive)", price_levels)
    
    # Minimum Rating Filter
    min_rating = st.sidebar.slider("Minimum Rating", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
    
    # Minimum Reviews Filter
    max_rev = int(df['reviews'].max()) if not df['reviews'].isna().all() else 1000
    min_reviews = st.sidebar.slider("Minimum Reviews", min_value=0, max_value=max_rev, value=0, step=10)
    
    # Order Options Filter
    order_options_list = ["All", "Pesan Online", "Reservasi Tempat", "Bawa Pulang", "Datang Langsung"]
    selected_order = st.sidebar.selectbox("Order Options (Indonesian)", order_options_list)
    
    # Apply Filters
    filtered_df = df.copy()
    if selected_category != "All":
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    if selected_price != "All":
        filtered_df = filtered_df[filtered_df['price_level_1_4'] == int(selected_price)]
        
    # Apply Rating and Reviews Filter
    filtered_df = filtered_df[filtered_df['rating'].fillna(0) >= min_rating]
    filtered_df = filtered_df[filtered_df['reviews'].fillna(0) >= min_reviews]
    
    # Apply Order Options Filter
    if selected_order != "All":
        # Use str.contains to match combined data
        filtered_df = filtered_df[filtered_df['order_options'].fillna("").str.contains(selected_order, case=False, na=False)]
        
    st.sidebar.markdown("---")
    st.sidebar.info(f"Showing {len(filtered_df)} restaurants based on filters.")

    # --- KPI METRICS ---
    col1, col2, col3 = st.columns(3)
    
    total_restoran = len(filtered_df)
    avg_rating = filtered_df['rating'].mean()
    total_reviews = filtered_df['reviews'].sum()
    
    col1.metric("Total Restaurants", f"{total_restoran}")
    col2.metric("Average Rating", f"{avg_rating:.2f}" if not pd.isna(avg_rating) else "N/A")
    col3.metric("Total Reviews", f"{int(total_reviews):,}" if not pd.isna(total_reviews) else "0")
    
    st.markdown("---")
    
    # --- CHARTS ROW 1 ---
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Restaurant Category Distribution")
        # Count per category
        cat_counts = filtered_df['category'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Count']
        
        # Pie Chart
        fig_pie = px.pie(cat_counts, values='Count', names='Category', hole=0.3,
                         color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_chart2:
        st.subheader("Price Level vs Rating Trend")
        
        # Filter out missing price levels and ratings
        line_df = filtered_df.dropna(subset=['price_level_1_4', 'rating'])
        
        if not line_df.empty:
            # Calculate average rating per price level and category
            line_df = line_df.groupby(['price_level_1_4', 'category'])['rating'].mean().reset_index()
            line_df = line_df.sort_values('price_level_1_4')
            
            # Line Chart
            fig_line = px.line(line_df, x='price_level_1_4', y='rating', color='category',
                               markers=True,
                               labels={'price_level_1_4': 'Price Level (1-4)', 'rating': 'Average Rating'},
                               title="Average Rating Trend by Price Level")
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Not enough data to display trend.")
        
    st.markdown("---")
    
    # --- CHARTS ROW 2 ---
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        st.subheader("Rating Distribution")
        fig_rating = px.histogram(filtered_df, x='rating', nbins=10, 
                                  title="Restaurant Rating Distribution",
                                  labels={'rating': 'Rating (Stars)'},
                                  color_discrete_sequence=['#FFB000'])
        st.plotly_chart(fig_rating, use_container_width=True)
        
    with col_chart4:
        st.subheader("Review Count Distribution")
        fig_reviews = px.histogram(filtered_df, x='reviews', nbins=20, 
                                   title="Popularity Distribution (Review Count)",
                                   labels={'reviews': 'Review Count'},
                                   color_discrete_sequence=['#FE6100'])
        st.plotly_chart(fig_reviews, use_container_width=True)

    st.markdown("---")
    
    # --- DATA TABLE ---
    st.subheader("🏆 Top 10 Best Restaurants (Based on Filters)")
    # Get top 10 based on rating and reviews
    top_10 = filtered_df.sort_values(by=['rating', 'reviews'], ascending=[False, False]).head(10)
    
    # Select columns to display
    cols_to_show = ['name', 'category', 'rating', 'reviews', 'address', 'price_category']
    # Check if extracted columns exist
    if 'review_snippet' in top_10.columns:
        cols_to_show.append('review_snippet')
        
    st.dataframe(top_10[cols_to_show].reset_index(drop=True), use_container_width=True)
