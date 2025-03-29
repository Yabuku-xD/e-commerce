#!/usr/bin/env python3
"""
E-commerce Sales & Customer Analysis - Main Pipeline Script

This script orchestrates the entire data pipeline:
1. Data acquisition
2. Database setup and initial data loading
3. Data processing and transformation
4. Customer segmentation analysis
5. Sales analysis
"""

import os
import logging
from datetime import datetime
import argparse
import psycopg2

# Import project modules
from scripts.data_acquisition import acquire_data
from scripts.data_processing import process_data
from scripts.customer_segmentation import perform_rfm_analysis
from scripts.sales_analysis import analyze_sales
from scripts.db_utils import connect_to_database, execute_sql_file, execute_query
import config

# Create necessary directories first
def create_directories():
    """Create necessary directories if they don't exist."""
    dirs = [
        "data/raw",
        "data/processed",
        "logs",
        "visualization/tableau",
        "visualization/powerbi",
        "database"  # Make sure database directory exists
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"Created directory: {dir_path}")  # Use print since logger isn't set up yet

# Create directories before setting up logging
create_directories()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_tables_exist(conn):
    """
    Check if the database tables already exist.
    
    Args:
        conn: Database connection
        
    Returns:
        True if tables exist, False otherwise
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT to_regclass('customers')")
        result = cursor.fetchone()[0]
        cursor.close()
        return result is not None
    except Exception:
        return False

def check_data_exists(conn):
    """
    Check if data already exists in the database.
    
    Args:
        conn: Database connection
        
    Returns:
        True if data exists, False otherwise
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]
        cursor.close()
        
        # If we have data in all three main tables, consider it populated
        if customer_count > 0 and product_count > 0 and order_count > 0:
            return True
        return False
    except Exception as e:
        logger.warning(f"Error checking if data exists: {str(e)}")
        return False

def run_pipeline(steps=None, force_update=False):
    """
    Run the complete data pipeline or specific steps.
    
    Args:
        steps: List of steps to run. If None, run all steps.
        force_update: If True, force processing even if data exists
    """
    all_steps = ["acquisition", "database", "processing", "rfm", "sales"]
    
    if steps is None:
        steps = all_steps
    
    logger.info(f"Starting pipeline with steps: {', '.join(steps)}")
    
    # Check if database and data already exist
    data_exists = False
    if "database" in steps:
        conn = connect_to_database(config.DB_CONFIG)
        tables_exist = check_tables_exist(conn)
        
        if tables_exist:
            data_exists = check_data_exists(conn)
            if data_exists and not force_update:
                logger.info("Data already exists in the database. Use --force to reprocess.")
            
        conn.close()
    
    # Step 1: Data Acquisition
    if "acquisition" in steps and (not data_exists or force_update):
        logger.info("Step 1: Data Acquisition")
        data_path = acquire_data(
            output_dir=config.RAW_DATA_DIR, 
            dataset_url=config.DATASET_URL
        )
        logger.info(f"Data acquired and saved to {data_path}")
    elif "acquisition" in steps and data_exists and not force_update:
        logger.info("Skipping data acquisition - data already exists")
    
    # Step 2: Database Setup
    if "database" in steps:
        logger.info("Step 2: Database Setup")
        conn = connect_to_database(config.DB_CONFIG)
        
        # Check if tables already exist
        tables_exist = check_tables_exist(conn)
        
        if not tables_exist:
            logger.info("Tables don't exist. Creating database schema...")
            # Create tables
            execute_sql_file(conn, "database/create_tables.sql")
            logger.info("Database tables created")
        else:
            logger.info("Database tables already exist. Skipping creation.")
        
        # Start processing log regardless
        try:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO data_processing_log (process_name, status)
            VALUES ('pipeline_execution', 'STARTED')
            """)
            conn.commit()
            cursor.close()
        except Exception as e:
            logger.warning(f"Could not create processing log entry: {str(e)}")
            conn.rollback()
        
        # Create analysis views
        logger.info("Creating or updating analysis views...")
        execute_sql_file(conn, "database/analysis_views.sql")
        logger.info("Analysis views created or updated")
        
        conn.close()
    
    # Step 3: Data Processing
    if "processing" in steps and (not data_exists or force_update):
        logger.info("Step 3: Data Processing")
        process_data(
            input_dir=config.RAW_DATA_DIR,
            output_dir=config.PROCESSED_DATA_DIR,
            db_config=config.DB_CONFIG
        )
        logger.info("Data processing completed")
    elif "processing" in steps and data_exists and not force_update:
        logger.info("Skipping data processing - data already exists")
    
    # Step 4: RFM Analysis
    if "rfm" in steps and (not data_exists or force_update):
        logger.info("Step 4: Customer Segmentation (RFM Analysis)")
        perform_rfm_analysis(
            db_config=config.DB_CONFIG,
            output_dir=config.PROCESSED_DATA_DIR
        )
        logger.info("RFM analysis completed")
    elif "rfm" in steps and data_exists and not force_update:
        logger.info("Skipping RFM analysis - data already exists")
    
    # Step 5: Sales Analysis
    if "sales" in steps and (not data_exists or force_update):
        logger.info("Step 5: Sales Analysis")
        analyze_sales(
            db_config=config.DB_CONFIG,
            output_dir=config.PROCESSED_DATA_DIR
        )
        logger.info("Sales analysis completed")
    elif "sales" in steps and data_exists and not force_update:
        logger.info("Skipping sales analysis - data already exists")
    
    # Update processing log
    if "database" in steps:
        try:
            conn = connect_to_database(config.DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE data_processing_log
            SET end_time = CURRENT_TIMESTAMP, status = 'COMPLETED'
            WHERE process_name = 'pipeline_execution' AND end_time IS NULL
            """)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.warning(f"Could not update processing log entry: {str(e)}")
    
    logger.info("Pipeline completed successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="E-commerce Sales & Customer Analysis Pipeline")
    parser.add_argument(
        "--steps", 
        nargs="+", 
        choices=["acquisition", "database", "processing", "rfm", "sales", "all"],
        help="Specific pipeline steps to run"
    )
    parser.add_argument(
        "--force", 
        action="store_true",
        help="Force processing even if data already exists"
    )
    args = parser.parse_args()
    
    steps_to_run = None if "all" in (args.steps or ["all"]) else args.steps
    
    run_pipeline(steps=steps_to_run, force_update=args.force)