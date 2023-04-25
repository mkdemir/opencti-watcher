import os
from dotenv import load_dotenv
from os.path import join, dirname
from pathlib import Path  # Python3 only

# Load enviorment variables
# Windows
# dotenv_path = join(dirname(__file__), '.env')

# Linux
dotenv_path = join(dirname(__file__), '.lenv')

load_dotenv(dotenv_path)


class Config:
    """
    Set configuration vars from .env file
    """

    # Load in environment variables
    # These fields are associated with logger
    LOG_DIR = os.getenv('LOG_DIR')
    LOG_FORMAT = os.getenv('LOG_FORMAT')
    DATA_DIR = os.getenv('DATA_DIR')
    DATA_RAW_DIR = os.getenv('DATA_RAW_DIR')
    DATA_IOC_DIR = os.getenv('DATA_IOC_DIR')
