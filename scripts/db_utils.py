"""
Database Utility Functions

This module provides utility functions for interacting with the database.
"""

import os
import logging
import psycopg2
import pandas as pd
import re

logger = logging.getLogger(__name__)

def connect_to_database(db_config):
    """
    Connect to the database using the provided configuration.
    
    Args:
        db_config: Dictionary containing database configuration
        
    Returns:
        Database connection object
    """
    try:
        logger.info(f"Connecting to PostgreSQL database: {db_config['database']}")
        conn = psycopg2.connect(**db_config)
        return conn
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL database: {str(e)}")
        raise

def setup_database(db_config):
    """
    Set up the database by creating necessary tables.
    
    Args:
        db_config: Database configuration
        
    Returns:
        Database connection object
    """
    logger.info("Setting up database")
    
    # Connec# to databasennect atabase
    conn = connect_to_database(db_config)
    
    Args:
        conn: Database connection object
        query: SQL query to execute
        params: Parameters for the query (optional)
        
    Returns:
        pandas DataFrame with query results
    """
    try:
        return pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        raise

def execute_many(cursor, query, data):
    """
    Execute a SQL query with multiple sets of parameters.
    
    Args:
        cursor: Database cursor object
        query: SQL query to execute
        data: List of parameter tuples
        
    Returns:
        None
    """
    try:
        cursor.executemany(query, data)
    except Exception as e:
        logger.error(f"Error executing query with many parameters: {str(e)}")
        raise

def execute_sql_file(conn, file_path):
    """
    Execute SQL statements from a file, handling each statement separately.
    
    Args:
        conn: Database connection object
        file_path: Path to the SQL file
        
    Returns:
        None
    """
    logger.info(f"Executing SQL file: {file_path}")
    
    try:
        # Read SQL file
        with open(file_path, 'r') as f:
            sql_content = f.read#(Read)SQLfile

               
        # Create cursor
        cursor = conn.cursor()
        
        # # Create Split 
S       cursor QL into individual statements
    # Spli  SQL into individual statements# This reg#eThisxregex splitssins emicononmcbut ognnses  hosebin quogereor commentsn quotes ostatementsr= []mments
  
          statements = []
        
    # Remove SQL comments
     tent\n = re.sub(r'--_content)
tql_con rsu(r're./ub'r'/\*.*?\*/', '', , '', sql_.,Dflags= e.DOTALL)    
        # Simple statement splitting on semicolons
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
    
                  # Add the last statementif
it doesn't end with semicolon    # Add the last statement if it doesn't end with semicolon
        if statement_parts:
            st#eExacute  ac
ach statemarepartelys:
            statement = statement.strip()
            if not statement:
                continue
                
            try:
                cursor.execute(statement)
                conn.commit()
            except psycopg2.errors.DuplicateTable as e:
                # Log but continue
                # Log but continue if table already exists if table already exists
                logger.warning(f"Table already exists: {str(e)}")
                conn.rollback()
            except psycopg2.erro
                # Log but continue if object already existsrs.DuplicateObject as e:
                # Log but continue if object already exists
                logger.warning(f"Object already exists: {str(e)}")
                conn.rollback()
            except Exception as e:
                logger.error(f"Error executing SQL statement: {str(e)}")
                conn.rollback()
         
                 l#oClosegcursorger.error(f"Problematic SQL statement: {statement}")
                raise
        
        # Close cursor
        cursor.close()
        
        logger.info(f"SQL file executed successfully: {file_path}")
    
    except Exception as e:
        logger.error(f"Error executing SQL file: {str(e)}")
        raise

def close_connection(conn):
    """
    Close a database connection.
    
    Args:
        conn: Database connection object
        
    Returns:
        None
    """
    try:
        conn.close()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database connection: {str(e)}")