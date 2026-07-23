import streamlit as st
import pandas as pd
import duckdb
import os
from dotenv import load_dotenv
import plotly.express as px

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Dashboard Semarang Culliner", page_icon="🍔", layout="wide")

# Muat variabel environment
load_dotenv()

# Fungsi untuk menghubungkan dan mengambil data dari MotherDuck
@st.cache_data(ttl=600) # Cache data selama 10 menit
def load_data():
    md_token = os.getenv("MOTHERDUCK_TOKEN")
    if not md_token or md_token == "your_motherduck_token_here":
        st.error("MOTHERDUCK_TOKEN belum dikonfigurasi di file .env")
        return pd.DataFrame()
        
    try:
        # Terhubung ke MotherDuck dan eksekusi kueri langsung ke dataframe
        con = duckdb.connect(f"md:?motherduck_token={md_token}")
        df = con.execute("SELECT * FROM restaurants_semarang").df()
        
        # Normalisasi nama kolom agar huruf kecil semua dan spasi diganti underscore
        df.columns = [c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_') for c in df.columns]
        
        con.close()
        return df
    except Exception as e:
        st.error(f"Gagal terhubung ke MotherDuck: {e}")
        return pd.DataFrame()

# Tampilan Utama Dashboard
st.title("Dashboard Analytics Restoran Semarang")
st.markdown("Visualisasi data restoran hasil scraping dari Google Maps (menggunakan **MotherDuck**).")

# Load Data
df = load_data()

if df.empty:
    st.warning("Data tidak ditemukan atau koneksi database gagal. Pastikan token MotherDuck benar dan data sudah di-load.")
else:
    # --- SIDEBAR (FILTER) ---
    st.sidebar.header("Filter Data")
    
    # Filter Kategori
    categories = ["Semua"] + sorted(df['category'].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Pilih Kategori", categories)
    
    # Filter Harga
    price_levels = ["Semua", 1, 2, 3, 4]
    selected_price = st.sidebar.selectbox("Pilih Tingkat Harga (1=Murah, 4=Mahal)", price_levels)
    
    # Filter Rating Minimum
    min_rating = st.sidebar.slider("Minimum Rating", min_value=0.0, max_value=5.0, value=0.0, step=0.1)
    
    # Filter Ulasan Minimum
    max_rev = int(df['reviews'].max()) if not df['reviews'].isna().all() else 1000
    min_reviews = st.sidebar.slider("Minimum Ulasan", min_value=0, max_value=max_rev, value=0, step=10)
    
    # Filter Opsi Pemesanan
    order_options_list = ["Semua", "Pesan Online", "Reservasi Tempat", "Bawa Pulang", "Datang Langsung"]
    selected_order = st.sidebar.selectbox("Opsi Pemesanan", order_options_list)
    
    # Terapkan Filter
    filtered_df = df.copy()
    if selected_category != "Semua":
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    if selected_price != "Semua":
        filtered_df = filtered_df[filtered_df['price_level_1_4'] == int(selected_price)]
        
    # Terapkan Filter Rating dan Ulasan
    filtered_df = filtered_df[filtered_df['rating'].fillna(0) >= min_rating]
    filtered_df = filtered_df[filtered_df['reviews'].fillna(0) >= min_reviews]
    
    # Terapkan Filter Opsi Pemesanan
    if selected_order != "Semua":
        filtered_df = filtered_df[filtered_df['order_options'].fillna("").str.contains(selected_order, case=False, na=False)]
        
    st.sidebar.markdown("---")
    st.sidebar.info(f"Menampilkan {len(filtered_df)} restoran berdasarkan filter.")

    # --- KPI METRICS ---
    col1, col2, col3 = st.columns(3)
    
    total_restoran = len(filtered_df)
    avg_rating = filtered_df['rating'].mean()
    total_reviews = filtered_df['reviews'].sum()
    
    col1.metric("Total Restoran", f"{total_restoran}")
    col2.metric("Rata-rata Rating", f"{avg_rating:.2f}" if not pd.isna(avg_rating) else "N/A")
    col3.metric("Total Ulasan", f"{int(total_reviews):,}" if not pd.isna(total_reviews) else "0")
    
    st.markdown("---")
    
    # --- GRAFIK ---
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Distribusi Kategori Restoran")
        # Menghitung jumlah per kategori
        cat_counts = filtered_df['category'].value_counts().reset_index()
        cat_counts.columns = ['Kategori', 'Jumlah']
        
        # Pie Chart
        fig_pie = px.pie(cat_counts, values='Jumlah', names='Kategori', hole=0.3,
                         color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_chart2:
        st.subheader("Korelasi Tingkat Harga vs Rating")
        
        # Tangani nilai NaN pada 'reviews' dan 'rating' agar tidak error saat dipetakan
        scatter_df = filtered_df.copy()
        scatter_df['reviews'] = scatter_df['reviews'].fillna(0)
        scatter_df['rating'] = scatter_df['rating'].fillna(0)
        
        # Scatter Plot
        fig_scatter = px.scatter(scatter_df, x='price_level_1_4', y='rating',
                                 size='reviews', color='category',
                                 hover_name='name', 
                                 labels={'price_level_1_4': 'Tingkat Harga (1-4)', 'rating': 'Rating (Bintang)'},
                                 title="Ukuran bubble = Jumlah Ulasan")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    st.markdown("---")
    
    # --- GRAFIK BARIS 2 ---
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        st.subheader("Distribusi Rating")
        fig_rating = px.histogram(filtered_df, x='rating', nbins=10, 
                                  title="Sebaran Nilai Rating Restoran",
                                  labels={'rating': 'Rating (Bintang)'},
                                  color_discrete_sequence=['#FFB000'])
        st.plotly_chart(fig_rating, use_container_width=True)
        
    with col_chart4:
        st.subheader("Distribusi Jumlah Ulasan")
        fig_reviews = px.histogram(filtered_df, x='reviews', nbins=20, 
                                   title="Sebaran Popularitas (Jumlah Ulasan)",
                                   labels={'reviews': 'Jumlah Ulasan'},
                                   color_discrete_sequence=['#FE6100'])
        st.plotly_chart(fig_reviews, use_container_width=True)

    st.markdown("---")
    
    # --- TABEL DATA ---
    st.subheader("🏆 Top 10 Restoran Terbaik (Berdasarkan Filter)")
    # Mengambil top 10 berdasarkan rating dan reviews terbanyak
    top_10 = filtered_df.sort_values(by=['rating', 'reviews'], ascending=[False, False]).head(10)
    
    # Pilih kolom yang ditampilkan
    cols_to_show = ['name', 'category', 'rating', 'reviews', 'address', 'price_category']
    # Cek apakah kolom hasil ekstrak ada (seperti review_snippet)
    if 'review_snippet' in top_10.columns:
        cols_to_show.append('review_snippet')
        
    st.dataframe(top_10[cols_to_show].reset_index(drop=True), use_container_width=True)
