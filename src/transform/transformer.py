import pandas as pd
import re

def transform_data(input_file, output_file):
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    # 1. Ekstraksi Kategori Restoran (Cuisine/Type)
    # Biasanya di Google Maps tertulis seperti "Restoran Indonesia ·", "Jepang ·", "Restoran Seafood ·"
    def extract_category(text):
        if pd.isna(text):
            return "Unknown"
        
        # Cari pola kata sebelum titik tengah (·)
        # Contoh text: "Restoran Seafood ·  · Puri Maerokoco"
        # Kita ambil dari kemunculan rating (kalau ada) atau awal kalimat sampai tanda '·' pertama.
        match = re.search(r'([A-Za-z\s]+)\s*·', str(text))
        if match:
            cat = match.group(1).strip()
            # Hindari mengambil string yang terlalu panjang atau tidak relevan
            if len(cat) > 3 and len(cat) < 30 and "Rp" not in cat:
                return cat
                
        # Jika mengandung kata-kata spesifik
        text_lower = str(text).lower()
        if 'seafood' in text_lower: return 'Seafood'
        if 'jepang' in text_lower or 'sushi' in text_lower: return 'Jepang'
        if 'korea' in text_lower: return 'Korea'
        if 'china' in text_lower or 'chinese' in text_lower: return 'China'
        if 'indonesia' in text_lower or 'jawa' in text_lower: return 'Indonesia'
        if 'steak' in text_lower: return 'Steak'
        if 'cafe' in text_lower or 'kafe' in text_lower or 'kopi' in text_lower: return 'Cafe'
        
        return "Umum"

    df['Category'] = df['Raw Content'].apply(extract_category)

    # 2. Ekstraksi Alamat (Jalan)
    def extract_address(text):
        if pd.isna(text):
            return None
        # Cari pola yang mengandung "Jl." atau "Jalan"
        match = re.search(r'(Jl\.|Jalan)\s+[A-Za-z0-9\.\-\s]+', str(text))
        if match:
            # Ambil sampai kata "Buka" atau ujung teks
            address_part = match.group(0).split('Buka')[0].split('Tutup')[0].split('Resto')[0].split('Tempat')[0].strip()
            return address_part
        return None

    df['Address'] = df['Raw Content'].apply(extract_address)

    # 3. Transformasi Price Category ke Angka Numerik (Price Level: 1-4)
    # Misal: 1 = Di bawah 50rb, 2 = 50-100rb, 3 = 100-200rb, 4 = Di atas 200rb
    def get_price_level(price_str):
        if pd.isna(price_str):
            return 0 # Unknown
        
        # Ambil angka pertama yang muncul setelah Rp
        # Contoh: "Rp 50–100 rb" -> 50
        match = re.search(r'Rp\s*(\d+)', str(price_str))
        if match:
            price_val = int(match.group(1))
            if price_val < 50:
                return 1
            elif price_val < 100:
                return 2
            elif price_val < 200:
                return 3
            else:
                return 4
        return 0

    df['Price Level (1-4)'] = df['Price Category'].apply(get_price_level)

    # 4. Ekstraksi Jam Tutup
    def extract_closing_time(text):
        if pd.isna(text):
            return None
        match = re.search(r'Tutup pukul (\d{2}\.\d{2})', str(text))
        if match:
            return match.group(1)
        return None
        
    df['Closing Time'] = df['Raw Content'].apply(extract_closing_time)

    # 5. Ekstraksi Ulasan Pengunjung (Review Snippet)
    def extract_review_snippet(text):
        if pd.isna(text):
            return None
        # Pandas otomatis menghilangkan escape double quote (menjadi single quote ") saat load CSV
        match = re.search(r'"([^"]+)"', str(text))
        if match:
            return match.group(1).strip()
        return None
        
    df['Review Snippet'] = df['Raw Content'].apply(extract_review_snippet)

    # 6. Ekstraksi Tipe Pemesanan (Pesan online / Reservasi tempat)
    def extract_order_options(text):
        if pd.isna(text):
            return "Datang Langsung"
        options = []
        if "Pesan online" in str(text):
            options.append("Pesan Online")
        if "Reservasi tempat" in str(text):
            options.append("Reservasi Tempat")
        if "Bawa pulang" in str(text):
            options.append("Bawa Pulang")
            
        if not options:
            return "Datang Langsung"
        return ", ".join(options)
        
    df['Order Options'] = df['Raw Content'].apply(extract_order_options)

    # 7. Hapus kolom Raw Content agar tabel akhir lebih rapi untuk analisis
    df = df.drop(columns=['Raw Content'])

    # Simpan ke file akhir
    df.to_csv(output_file, index=False)
    
    print("Data transformation finished!")
    print(f"Data akhir disimpan ke: {output_file}")
    print("\nSample Data Hasil Transformasi:")
    print(df[['Name', 'Category', 'Address', 'Price Level (1-4)']].head())

if __name__ == "__main__":
    input_path = "../../data/processed/restaurants_semarang_cleaned.csv"
    output_path = "../../data/transformed/restaurants_semarang_transformed.csv"
    transform_data(input_path, output_path)
