"""
Configuration file for Mini Project 3
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_KEY")
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "YOUR_KEY")

# Models
MODEL_SMALL = "gpt-4o-mini"
MODEL_LARGE = "gpt-4o"
ACTIVE_MODEL = MODEL_SMALL

# OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)

# Database
DB_PATH = "stocks.db"

# Evaluation settings
MAX_ITERATIONS = 10
EVAL_DELAY_SEC = 3.0