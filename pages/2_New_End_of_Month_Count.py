import pandas as pd
import numpy as np
import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import date 
from dotenv import load_dotenv 
import os

# Load environment variables
load_dotenv()

# Set the page layout to wide mode
st.set_page_config(layout="wide")

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host = os.getenv('DB_HOST'),
            user = os.getenv('DB_USER'),
            passwd = os.getenv('DB_PASS'),
            database = os.getenv('DB_NAME')
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

# Database configuration
connection = create_connection()

# Execute a modification query safely
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

def read_query_safe(connection, query, data=None):
    cursor = connection.cursor()
    result = None
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")
    finally:
        cursor.close()

def insert_new_monthly_data(connection, data):
    query = """
    INSERT INTO items_table (BTN_SKU, Description, item_type, Count_Details, Vendor, Pallets, Bundles_Boxes_Spools, Units_Pieces_Each, Month, is_roll) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    execute_query_safe(connection, query, data)

def get_most_recent_data(connection, btn_sku):
    query = """
    SELECT amount_after_change, new_total_units
    FROM Current_Amount_Items
    WHERE BTN_SKU = %s
    ORDER BY Change_Timestamp DESC LIMIT 1;
    """
    result = read_query_safe(connection, query, (btn_sku,))
    if result:
        return result[0]
    return 0, 0  # Default values if no records found

st.title('Enter Monthly Data')

year = st.selectbox('Select Year', list(range(2020, 2031)), index = date.today().year - 2020)

months = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
month = st.selectbox('Select Month', months, index = date.today().month - 1)

# Format the selected month and year into the desired format for storage
Month = f"{month} {year}"

# Session state for recent changes if it does not exist
if 'recent_changes' not in st.session_state:
    st.session_state['recent_changes'] = []

btn_sku_query = "SELECT DISTINCT BTN_SKU FROM items_table ORDER BY BTN_SKU;"
btn_sku_results = read_query_safe(connection, btn_sku_query)
btn_sku_options = [result[0] for result in btn_sku_results]

selected_btn_sku = st.selectbox('Select BTN_SKU', btn_sku_options)

# Auto-fill the remaining fields based on BTN_SKU selected
Description, Type, Count_Details, Vendor, Bundles_Boxes_Spools, Units_Pieces_Each = '', '', '', '', 0, 0
if selected_btn_sku:
    # Fetch the most recent item details
    details_query = """
    SELECT Description, item_type, Count_Details, Vendor 
    FROM items_table 
    WHERE BTN_SKU = %s
    ORDER BY BTN_SKU DESC LIMIT 1;
    """
    details_results = read_query_safe(connection, details_query, (selected_btn_sku,))
    if details_results:
        Description, Type, Count_Details, Vendor = details_results[0]
    
    # Fetch the most recent data for Bundles_Boxes_Spools and Units_Pieces_Each
    Bundles_Boxes_Spools, Units_Pieces_Each = get_most_recent_data(connection, selected_btn_sku)

# Display the auto-filled data
st.text_input('Description', Description)
st.text_input('Type', Type)
st.text_input('Count Details', Count_Details)
st.text_input('Vendor', Vendor)

# User input fields
Pallets = st.number_input('Pallets', step = 1, min_value = 0)
Units_Pieces_Each = st.number_input('Units/Pieces Each', value=Units_Pieces_Each, step=1, min_value=0)
Bundles_Boxes_Spools = st.number_input('Bundles/Boxes/Spools', value=Bundles_Boxes_Spools, step=1, min_value=0)
is_roll = st.checkbox("Is this item a roll?", value=False)

def validate_inputs(description, item_type, count_details, vendor, pallets, units_pieces_each, bundles_boxes_spools):
    if not description:
        return "Description cannot be empty."
    if not item_type:
        return "Type cannot be empty."
    if not count_details:
        return "Count Details cannot be empty."
    if not vendor:
        return "Vendor cannot be empty."
    if pallets < 0:
        return "Pallets cannot be negative."
    if units_pieces_each < 0:
        return "Units/Pieces Each cannot be negative."
    if bundles_boxes_spools < 0:
        return "Bundles/Boxes/Spools cannot be negative."
    if pallets > 10:
        return "Pallets is too large."
    if units_pieces_each > 1000000000:
        return "Units/Pieces Each is too large."
    if bundles_boxes_spools > 10000:
        return "Bundles/Boxes/Spools is too large."
    return None

if st.button('Submit New Monthly Data'):
    error_message = validate_inputs(Description, Type, Count_Details, Vendor, Pallets, Units_Pieces_Each, Bundles_Boxes_Spools)
    
    if error_message:
        st.error(error_message)
    else:
        connection = create_connection()
        
        if connection is not None:
            # Prepare data for insertion
            data = (selected_btn_sku, Description, Type, Count_Details, Vendor, Pallets, Bundles_Boxes_Spools, Units_Pieces_Each, Month, is_roll)
            
            # Use the insert_new_monthly_data function
            insert_new_monthly_data(connection, data)
            
            connection.close()
            print("Database connection closed.")
            
            # Record the change with a timestamp in the session state
            change_record = {
                'BTN_SKU': selected_btn_sku,
                'Description': Description,
                'Timestamp': Month  
            }
            # add the new record to the session state list
            st.session_state['recent_changes'].insert(0, change_record)  # Insert at the beginning to show recent first
        else:
            st.error("Failed to connect to the database.")

st.subheader('Recent Changes Log')
st.table(st.session_state['recent_changes'])
