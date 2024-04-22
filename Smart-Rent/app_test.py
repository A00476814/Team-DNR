import pymysql
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import joblib
from datetime import datetime
import requests
from io import StringIO  
import re

# Function to connect to the database and fetch data
def fetch_data():
    # Database connection parameters - replace these with your details
    conn = pymysql.connect(
        host='dev.cs.smu.ca',
        user='r_khevaria',
        password='islandENGLISH72',
        database='r_khevaria'
    )
    # SQL query to fetch data
    query = "SELECT * FROM rentListings"
    # Reading the data into a Pandas DataFrame
    data = pd.read_sql(query, conn)
    # Closing the connection
    conn.close()
    return data

# Function to convert DataFrame to CSV and download
def convert_df_to_csv(df):
    # Convert DataFrame to CSV
    csv = df.to_csv(index=False)
    # Convert CSV string to bytes
    return csv.encode('utf-8')

def main():
    st.title("Database to CSV Downloader")

    if st.button("Fetch Data from Database"):
        data = fetch_data()
        st.write(data)
        
        # Create a CSV download link, ensuring the CSV data is in bytes
        csv_bytes = convert_df_to_csv(data)
        st.download_button(
            label="Download data as CSV",
            data=csv_bytes,
            file_name='database_data.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main()