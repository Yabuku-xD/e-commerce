import os
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.absolute()
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

# Dataset URL - UCI Online Retail Dataset
DATASET_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx"
SAMPLE_DATA_SIZE = 10000
START_DATE = "2022-01-01"
END_DATE = "2023-12-31"
NUM_CUSTOMERS = 500
NUM_PRODUCTS = 100
NUM_COUNTRIES = 15

DB_CONFIG = {
    "host": "localhost",
    "database": "ecommerce_db",
    "user": "postgres",
    "password": "admin",
    "port": 5432,
}

SQLITE_DB_PATH = os.path.join(PROJECT_ROOT, "database", "ecommerce.db")
RFM_RECENCY_DAYS = 365
RFM_FREQUENCY_MIN = 1
RFM_MONETARY_MIN = 10
OUTLIER_THRESHOLD = 3