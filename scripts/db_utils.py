import os
import logging
import psycopg2
import pandas as pd
import re

logger = logging.getLogger(__name__)

def connect_to_database(db_config):
    try:
        logger.info(f"Connecting to PostgreSQL database: {db_config['database']}")
        conn = psycopg2.connect(**db_config)
        return conn
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL database: {str(e)}")
        raise

def execute_query(conn, query, params=None):
    try:
        return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        raise

def execute_many(cursor, query, data):
    try:
        cursor.executemany(query, data)
    except Exception as e:
        logger.error(f"Error executing query with many parameters: {str(e)}")
        raise

def execute_sql_file(conn, file_path):
    logger.info(f"Executing SQL file: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            sql_content = f.read()

        cursor = conn.cursor()

        sql_content = re.sub(r'--.*?\n', '\n', sql_content)
        sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)

        statements = []
        statement_parts = []
        in_string = False
        string_delimiter = None
        
        for char in sql_content:
            if char in ['"', "'"]:
                if not in_string:
                    in_string = True
                    string_delimiter = char
                elif char == string_delimiter:
                    in_string = False
            
            statement_parts.append(char)
            
            if char == ';' and not in_string:
                statements.append(''.join(statement_parts))
                statement_parts = []

        if statement_parts:
            statements.append(''.join(statement_parts))

        for statement in statements:
            statement = statement.strip()
            if not statement:
                continue
                
            try:
                cursor.execute(statement)
                conn.commit()
            except psycopg2.errors.DuplicateTable as e:
                # Log but continue if table already exists
                logger.warning(f"Table already exists: {str(e)}")
                conn.rollback()
            except psycopg2.errors.DuplicateObject as e:
                # Log but continue if object already exists
                logger.warning(f"Object already exists: {str(e)}")
                conn.rollback()
            except Exception as e:
                logger.error(f"Error executing SQL statement: {str(e)}")
                logger.error(f"Problematic SQL statement: {statement}")
                conn.rollback()
                raise

        cursor.close()
        
        logger.info(f"SQL file executed successfully: {file_path}")
    
    except Exception as e:
        logger.error(f"Error executing SQL file: {str(e)}")
        raise

def close_connection(conn):
    try:
        conn.close()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database connection: {str(e)}")