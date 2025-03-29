#!/usr/bin/env python3
"""
Database Reset Script

This script completely resets the database by dropping all tables and recreating them.
Use this when you need a clean database or when encountering schema errors.
"""

import os
import sys
import logging
import psycopg2
from config import DB_CONFIG

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def reset_database():
    """
    Reset the database by dropping all tables and recreating them.
    """
    logger.info("Connecting to database...")
    
    try:
        # Connect with autocommit enabled
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        logger.info("Dropping all tables...")
        
        # Drop all tables in the correct order to avoid foreign key constraint violations
        cursor.execute("""
        DROP TABLE IF EXISTS customer_segments CASCADE;
        DROP TABLE IF EXISTS order_items CASCADE;
        DROP TABLE IF EXISTS orders CASCADE;
        DROP TABLE IF EXISTS products CASCADE;
        DROP TABLE IF EXISTS customers CASCADE;
        DROP TABLE IF EXISTS data_processing_log CASCADE;
        """)
        
        logger.info("All tables dropped successfully.")
        
        # Read the create tables SQL script
        with open("database/create_tables.sql", "r") as f:
            create_tables_sql = f.read()
        
        logger.info("Creating new tables...")
        
        # Execute the create tables script
        cursor.execute(create_tables_sql)
        
        logger.info("Database reset completed successfully.")
        
        # Clean up
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        return False

if __name__ == "__main__":
    print("WARNING: This will delete ALL data in the database and recreate all tables.")
    confirmation = input("Are you sure you want to continue? (yes/no): ")
    
    if confirmation.lower() == "yes":
        success = reset_database()
        if success:
            print("Database has been reset successfully.")
            sys.exit(0)
        else:
            print("Database reset failed. See log for details.")
            sys.exit(1)
    else:
        print("Database reset cancelled.")
        sys.exit(0)