#!/usr/bin/env python3
import psycopg2
import socket
import sys
import urllib.parse
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Default connection parameters - now using environment variables
DB_PARAMS = {
    'dbname': os.getenv('POSTGRES_DATABASE', 'postgres'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'your_password'),
    'host': os.getenv('POSTGRES_HOST', 'db.avumloctwqugkseamody.supabase.co'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'sslmode': os.getenv('POSTGRES_SSL_MODE', 'require')
}

# Default connection URI (alternative to DB_PARAMS)
DB_URI = os.getenv('DATABASE_URL')  # Common environment variable for full database URL

# R2 Configuration - now using environment variables
R2_CONFIG = {
    'endpoint_url': os.getenv('R2_ENDPOINT_URL', 'https://<your-account-id>.r2.cloudflarestorage.com'),
    'aws_access_key_id': os.getenv('R2_ACCESS_KEY_ID', 'your_access_key'),
    'aws_secret_access_key': os.getenv('R2_SECRET_ACCESS_KEY', 'your_secret_key'),
    'region_name': os.getenv('R2_REGION', 'auto')
}

def connect_to_db(db_name=None):
    """Establish a connection to the PostgreSQL database."""
    if db_name:
        DB_PARAMS['dbname'] = db_name
    try:
        if DB_URI:
            logger.info(f"Connecting to database using URI...")
            # When using URI, we mask the password in logs for security
            safe_uri = mask_password_in_uri(DB_URI)
            logger.info(f"Connection URI (masked): {safe_uri}")
            conn = psycopg2.connect(DB_URI)
        else:
            logger.info(f"Connecting to database at {DB_PARAMS['host']}...")
            conn = psycopg2.connect(**DB_PARAMS)

        logger.info("Connection established successfully!")
        return conn
    except socket.gaierror as e:
        if DB_URI:
            parsed = urllib.parse.urlparse(DB_URI)
            host = parsed.hostname
            logger.error(f"DNS resolution error: Could not resolve host '{host}'")
        else:
            logger.error(f"DNS resolution error: Could not resolve host '{DB_PARAMS['host']}'")
        logger.error("Please check:")
        logger.error("  1. The hostname is spelled correctly")
        logger.error("  2. Your internet connection is working")
        logger.error("  3. DNS servers are functioning correctly")
        logger.error(f"Technical error: {e}")
        sys.exit(1)
    except psycopg2.OperationalError as e:
        if DB_URI:
            parsed = urllib.parse.urlparse(DB_URI)
            host = parsed.hostname
            logger.error(f"Connection error: Failed to connect to '{host}'")
        else:
            logger.error(f"Connection error: Failed to connect to '{DB_PARAMS['host']}'")
        logger.error("Please check:")
        logger.error("  1. The database is online and accepting connections")
        logger.error("  2. Your credentials (username/password) are correct")
        logger.error("  3. Any firewall rules allow your connection")
        logger.error("  4. The connection string format is correct")
        logger.error(f"Technical error: {e}")
        sys.exit(1)
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        sys.exit(1)

def mask_password_in_uri(uri):
    """Mask the password in a connection URI for safe logging."""
    try:
        parsed = urllib.parse.urlparse(uri)
        if parsed.password:
            masked = parsed._replace(netloc=f"{parsed.username}:******@{parsed.hostname}:{parsed.port}")
            return urllib.parse.urlunparse(masked)
        return uri
    except Exception:
        # If any parsing error, return a fully masked URI
        return "postgresql://username:******@host:port/dbname"
    
def get_all_detected_posts():
    db_scrapper_connection = connect_to_db("atractive_scrapper")
    db_scrapper_cursor = db_scrapper_connection.cursor()
    db_scrapper_cursor.execute("""SELECT * FROM detected_posts;""")
    detected_posts = [r[1] for r in db_scrapper_cursor.fetchall()]
    return detected_posts

def get_non_processed_posts():
    db_scrapper_connection = connect_to_db("atractive_scrapper")
    db_scrapper_cursor = db_scrapper_connection.cursor()
    db_scrapper_cursor.execute("""SELECT * FROM detected_posts WHERE status != 'DONE';""")
    detected_posts = [r[1] for r in db_scrapper_cursor.fetchall()]
    return detected_posts

def insert_new_posts(post_ids):
    logger.info(f"Inserting {len(post_ids)} new posts into database...")
    db_scrapper_connection = connect_to_db("atractive_scrapper")
    db_scrapper_cursor = db_scrapper_connection.cursor()
    for post_id in post_ids:
        query = """INSERT INTO detected_posts (post_id, detected_at, updated_at, status) VALUES (%s, NOW(), NOW(), 'NEW');"""
        values = (post_id,)
        db_scrapper_cursor.execute(query, values)
        db_scrapper_connection.commit()