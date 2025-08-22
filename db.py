from astrapy import DataAPIClient
from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

# Define the function with the decorator, but we will not call it here.
@st.cache_resource
def get_db():
    ENDPOINT = os.getenv("ASTRA_ENDPOINT")
    TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
    client = DataAPIClient(TOKEN)
    db = client.get_database_by_api_endpoint(ENDPOINT)
    return db

# These variables are defined here so other files can import them.
# They will be properly assigned a value in main.py.
personal_data_collection = None
notes_collection = None