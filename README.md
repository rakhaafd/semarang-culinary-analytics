# Semarang Culinary Analytics

Semarang Culinary Analytics is a Data Engineering project that demonstrates an end-to-end **ETL (Extract, Transform, Load)** pipeline. The project collects restaurant data from Google Maps, processes and transforms the dataset, stores it in **DuckDB** with **MotherDuck** integration, and presents insights through a dashboard built with Streamlit.

## Features

* Scrape restaurant data from Google Maps using Playwright
* Clean and transform data with Pandas
* Store processed data in DuckDB
* Integration with MotherDuck Cloud Data Warehouse
* Interactive dashboard powered by Streamlit and Plotly

## ETL Pipeline

```text
Google Maps
     │
     ▼
Playwright Scraper
     │
     ▼
Raw Dataset (CSV)
     │
     ▼
Data Cleaning
     │
     ▼
Data Transformation
     │
     ▼
DuckDB / MotherDuck
     │
     ▼
Streamlit Dashboard
```
___

## Getting Started

Clone the repository:

```bash
git clone https://github.com/rakhaafd/semarang-culinary-analytics.git
cd semarang-culinary-analytics
```

## Running with Docker

Build and start the application:

```bash
docker compose up --build
```

Run the ETL pipeline inside the container:

```bash
docker compose exec app python src/scraper/scraper.py
docker compose exec app python src/clean/cleaner.py
docker compose exec app python src/transform/transformer.py
docker compose exec app python src/load/loader.py
```

Stop the application:

```bash
docker compose down
```

## Dashboard

The dashboard provides interactive visualizations to explore the restaurant dataset, including:

* Total restaurants collected
* Rating distribution
* Review count distribution
* Restaurant category analysis
* Price level analysis (when available)
* Summary statistics

## License

This project is intended for educational and portfolio purposes. Please ensure that any use of scraped data complies with the terms of service of the original data source.