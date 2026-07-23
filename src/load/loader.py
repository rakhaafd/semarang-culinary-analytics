import pandas as pd
import duckdb
import os
from dotenv import load_dotenv

def load_data_to_motherduck():
    # Load environment variables
    load_dotenv()
    
    md_token = os.getenv("MOTHERDUCK_TOKEN")
    
    if not md_token or md_token == "your_motherduck_token_here":
        print("Error: MOTHERDUCK_TOKEN tidak ditemukan atau belum diubah di file .env")
        return
        
    print("Menghubungkan ke MotherDuck...")
    
    try:
        # Hubungkan ke MotherDuck menggunakan token
        con = duckdb.connect(f"md:?motherduck_token={md_token}")
        
        # Load the transformed data
        current_dir = os.path.dirname(os.path.abspath(__file__))
        input_file = os.path.join(current_dir, "../../data/transformed/restaurants_semarang_transformed.csv")
        print(f"Membaca data dari {os.path.abspath(input_file)}...")
        df = pd.read_csv(input_file)
        
        # Normalisasi nama kolom sebelum dikirim ke MotherDuck
        df.columns = [c.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_') for c in df.columns]
        
        
        # Buat tabel dan masukkan data dari dataframe
        print("Membuat tabel 'restaurants_semarang' dan memasukkan data...")
        con.execute("CREATE OR REPLACE TABLE restaurants_semarang AS SELECT * FROM df")
        
        print("Data berhasil diunggah ke MotherDuck Cloud Data Warehouse!")
        
        # Verifikasi data
        count = con.execute("SELECT COUNT(*) FROM restaurants_semarang").fetchone()[0]
        print(f"Total baris yang berhasil diunggah: {count}")
        
    except Exception as e:
        print(f"Gagal memuat data ke MotherDuck: {e}")
    finally:
        if 'con' in locals():
            con.close()

if __name__ == "__main__":
    load_data_to_motherduck()