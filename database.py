import os
import sys
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from config import Config

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger('JobConnect')

db = SQLAlchemy()

def init_database(app):
    db_type = Config.DB_TYPE.lower()
    selected_uri = None
    connected_db_name = "SQLite"

    if db_type in ('mysql', 'auto'):
        # Attempt connection to MySQL server
        try:
            # First check if MySQL host/port is reachable
            raw_engine = create_engine(
                f"mysql+pymysql://{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}",
                connect_args={'connect_timeout': 3}
            )
            with raw_engine.connect() as conn:
                # Ensure database exists
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                conn.commit()
            
            selected_uri = Config.MYSQL_URI
            connected_db_name = f"MySQL ({Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DB})"
            logger.info(f"Successfully verified and connected to MySQL: {connected_db_name}")
        except Exception as e:
            if db_type == 'mysql':
                logger.error(f"Failed to connect to MySQL database: {e}")
                raise e
            else:
                logger.warning(f"MySQL not reachable on {Config.MYSQL_HOST}:{Config.MYSQL_PORT} ({e}).")
                logger.warning("Auto-fallback enabled: switching seamlessly to local SQLite storage.")
                selected_uri = Config.SQLITE_URI
                connected_db_name = "SQLite (fallback)"
    else:
        selected_uri = Config.SQLITE_URI
        connected_db_name = "SQLite"

    app.config['SQLALCHEMY_DATABASE_URI'] = selected_uri
    app.config['ACTIVE_DB_NAME'] = connected_db_name
    db.init_app(app)
    return connected_db_name
