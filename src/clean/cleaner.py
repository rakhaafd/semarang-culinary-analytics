import pandas as pd
import re

def clean_data(input_file, output_file):
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    initial_count = len(df)
    
    # 1. Menghapus data duplikat berdasarkan 'Name'
    df = df.drop_duplicates(subset=['Name'])
    
    # 2. Membersihkan kolom Rating (mengubah '4,5' menjadi 4.5)
    def clean_rating(val):
        if pd.isna(val):
            return None
        val_str = str(val).replace(',', '.')
        try:
            return float(val_str)
        except ValueError:
            return None
            
    df['Rating'] = df['Rating'].apply(clean_rating)
    
    # 3. Membersihkan kolom Reviews (menghilangkan titik ribuan '3.229' -> 3229)
    def clean_reviews(val):
        if pd.isna(val):
            return None
        val_str = str(val).replace('.', '')
        try:
            return int(val_str)
        except ValueError:
            return None
            
    df['Reviews'] = df['Reviews'].apply(clean_reviews)
    
    # 4. Mengekstrak kategori harga dari Raw Content (misal: 'Rp 50–100 rb')
    def extract_price(raw_text):
        if pd.isna(raw_text):
            return None
        # Mencari pola seperti Rp 25-50 rb, Rp 100.000+, dll
        match = re.search(r'Rp\s*[\d\.\–\-]+(\s*rb|\+)?', str(raw_text))
        if match:
            return match.group(0)
        return None
        
    df['Price Category'] = df['Raw Content'].apply(extract_price)
    
    # Simpan ke file baru
    df.to_csv(output_file, index=False)
    
    final_count = len(df)
    print(f"Data cleaning finished!")
    print(f"Total awal: {initial_count} baris")
    print(f"Total setelah dibersihkan (duplikat dihapus): {final_count} baris")
    print(f"Data disimpan ke: {output_file}")

if __name__ == "__main__":
    input_path = "../../data/raw/restaurants_semarang.csv"
    output_path = "../../data/processed/restaurants_semarang_cleaned.csv"
    clean_data(input_path, output_path)
