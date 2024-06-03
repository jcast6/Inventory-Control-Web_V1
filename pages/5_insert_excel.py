import streamlit as st
import pandas as pd
import os
import mysql.connector
from mysql.connector import MySQLConnection, Error
import re
from typing import Tuple, List

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            passwd=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

def execute_query_safe(connection, query, data):
    cursor = connection.cursor()
    try:
        cursor.execute(query, data)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")
    finally:
        cursor.close()

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Strip leading/trailing spaces from string columns
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Convert numerical columns to appropriate types
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')

    return df

def insert_data_from_excel(connection: MySQLConnection, df: pd.DataFrame):
    # replace all NaN values with 0 (for numerical columns)
    df = df.fillna(0)

    # Process Bundles_Boxes_Spools to set the Spools column and extract numbers
    def process_bundles_boxes_spools(row):
        if any(word in str(row['Bundles_Boxes_Spools']).lower() for word in ['spools', 'roll', 'rolls']):
            row['Spools'] = 1
        else:
            row['Spools'] = 0
        match = re.search(r'\d+', str(row['Bundles_Boxes_Spools']))
        if match:
            row['Bundles_Boxes_Spools'] = int(match.group())
        else:
            row['Bundles_Boxes_Spools'] = 0
        return row

    df = df.apply(process_bundles_boxes_spools, axis=1)

    # insert data query, matching the columns to the DataFrame's columns
    query = """
    INSERT INTO items_table (BTN_SKU, Description, item_type, Count_Details, Vendor, Pallets, Bundles_Boxes_Spools, Units_Pieces_Each, Month, Spools) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    for index, row in df.iterrows():
        data = tuple(row[col] for col in ['BTN_SKU', 'Description', 'item_type', 'Count_Details', 'Vendor', 'Pallets', 'Bundles_Boxes_Spools', 'Units_Pieces_Each', 'Month', 'Spools'])
        execute_query_safe(connection, query, data)

# Streamlit App Code
st.title("Excel File Uploader and Previewer")

# File uploader
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Display the file preview
    df = pd.read_excel(uploaded_file)
    
    # Clean the DataFrame to ensure compatibility
    df = clean_dataframe(df)

    st.write("Preview of uploaded file:")
    st.dataframe(df)

    # Process the uploaded file and insert data into the database
    if st.button("Insert Data into Database"):
        connection = create_connection()
        if connection:
            insert_data_from_excel(connection, df)
            connection.close()
            st.success("Data inserted successfully!")
