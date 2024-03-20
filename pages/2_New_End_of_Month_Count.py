import streamlit as st
import mysql.connector
from mysql.connector import Error
import datetime
from dotenv import load_dotenv 
import os

# Load environment variables
load_dotenv()

# Set the page layout to wide mode
# st.set_page_config(layout="wide")



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

# database configuration
connection = create_connection()


# execute a modification query safely
def execute_query_safe(connection, query, data):
    cursor = connection.cursor()
    try:
        cursor.execute(query, data)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")
    finally:
        cursor.close()  # Ensure the cursor is closed even if an error occurs


# read a query safely
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
        cursor.close()  # Ensure the cursor is closed even if an error occurs


# Safe way to insert data
def insert_new_monthly_data(connection, data):
    query = """
    INSERT INTO items_table (BTN_SKU, Description, Type, Count_Details, Vendor, Pallets, Bundles_Boxes_Spools, Units_Pieces_Each, Lead_Time, Month) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    execute_query_safe(connection, query, data)


# fetch the latest amount_after_change for a specific BTN_SKU
def fetch_latest_amount_after_change(connection, btn_sku):
    query = """
    SELECT amount_after_change FROM current_amount_items
    WHERE BTN_SKU = %s
    ORDER BY Change_Timestamp DESC LIMIT 1;
    """
    result = read_query_safe(connection, query, (btn_sku,))
    if result and result[0][0] is not None:
        return result[0][0]
    else:
        return 0  # Return 0 if there's no record for the selected BTN_SKU


# Streamlit interface
st.title('Enter Monthly Data')

# Initialize the session state for recent changes if it does not exist
if 'recent_changes' not in st.session_state:
    st.session_state['recent_changes'] = []

# Fetch distinct BTN_SKU options from the database
btn_sku_query = "SELECT DISTINCT BTN_SKU FROM items_table ORDER BY BTN_SKU;"
btn_sku_results = read_query_safe(connection, btn_sku_query)
btn_sku_options = [result[0] for result in btn_sku_results]

# Dropdown to select BTN_SKU
selected_btn_sku = st.selectbox('Select BTN_SKU', btn_sku_options)

# Auto-fill the remaining fields based on BTN_SKU selected
Description, Type, Count_Details, Vendor = '', '', '', ''
if selected_btn_sku:
    # Fetch the latest amount_after_change for the selected BTN_SKU
    latest_amount_after_change = fetch_latest_amount_after_change(connection, selected_btn_sku)
    

    # Since the BTN_SKU is distinct, the details should come from the most recent entry or a specific criterion
    details_query = f"""
    SELECT Description, Type, Count_Details, Vendor 
    FROM items_table 
    WHERE BTN_SKU = '{selected_btn_sku}'
    ORDER BY BTN_SKU DESC LIMIT 1;
    """
    details_results = read_query_safe(connection, details_query)
    if details_results:
        Description, Type, Count_Details, Vendor = details_results[0]

# Display the auto-filled data
st.text_input('Description', Description)
st.text_input('Type', Type)
st.text_input('Count Details', Count_Details)
st.text_input('Vendor', Vendor)

# user Input fields
Pallets = st.number_input('Pallets', step=1)
Units_Pieces_Each = st.number_input('Units/Pieces Each', step=1)
# Auto-fill the Bundles/Boxes/Spools input with the latest amount_after_change
Bundles_Boxes_Spools = st.number_input('Bundles/Boxes/Spools', step=1, value=latest_amount_after_change)
Lead_Time = st.number_input('Lead Time', step=1)
Month = st.text_input('Month')

# Button to submit data
if st.button('Submit New Monthly Data'):
    connection = create_connection()
    
    if connection is not None:
        # Parameterized SQL query
        query = """
        INSERT INTO items_table (BTN_SKU, Description, Type, Count_Details, Vendor, Pallets, Bundles_Boxes_Spools, Units_Pieces_Each, Lead_Time, Month) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        data = (selected_btn_sku, Description, Type, Count_Details, Vendor, Pallets, Bundles_Boxes_Spools, Units_Pieces_Each, Lead_Time, Month)
        
        # Execute the query safely
        execute_query_safe(connection, query, data)
        
        # Close the connection after the query execution
        connection.close()
        print("Database connection closed.")
        
        # Record the change with a timestamp in the session state
        change_record = {
            'BTN_SKU': selected_btn_sku,
            'Description': Description,
            'Timestamp': datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')
        }
        # Append the new record to the session state list
        st.session_state['recent_changes'].insert(0, change_record)  # Insert at the beginning to show recent first
    else:
        st.error("Failed to connect to the database.")

# Display a recent changes log
st.subheader('Recent Changes Log')
# Display the session state recent changes as a table
st.table(st.session_state['recent_changes'])

