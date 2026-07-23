FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables untuk Python dan Playwright
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install dependensi sistem yang dibutuhkan oleh Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Salin requirements dan instal dependensi Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser (Chromium) beserta dependensi OS-nya
RUN playwright install --with-deps chromium

# Salin seluruh kode proyek ke dalam container
COPY . .

# Ekspos port Streamlit
EXPOSE 8501

# Command bawaan ketika container dinyalakan: jalankan dashboard
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
