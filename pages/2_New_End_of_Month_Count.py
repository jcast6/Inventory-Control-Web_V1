import streamlit as st
import mysql.connector
from mysql.connector import Error


# Function to connect to the MySQL database
def create_server_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

# Function to execute a query
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

# Function to read a query
def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

def main(): 
    
    # Database configuration
    host_name = 'localhost'
    user_name = 'root'
    user_password = 'peter'
    db_name = 'main_items'

    # Connect to the MySQL Database
    connection = create_server_connection(host_name, user_name, user_password, db_name)
    
    # Streamlit interface
    st.title('Enter Monthly Data')

    # Fetch distinct BTN_SKU options from the database
    btn_sku_query = "SELECT DISTINCT BTN_SKU FROM items_table ORDER BY BTN_SKU;"
    btn_sku_results = read_query(connection, btn_sku_query)
    btn_sku_options = [result[0] for result in btn_sku_results]

    # Dropdown to select BTN_SKU
    selected_btn_sku = st.selectbox('Select BTN_SKU', btn_sku_options)

    # Auto-fill the remaining fields based on BTN_SKU selected
    Description, Type, Count_Details, Vendor = '', '', '', ''
    if selected_btn_sku:
        # Since the BTN_SKU is now distinct, the details should come from the most recent entry or a specific criterion
        details_query = f"""
        SELECT Description, Type, Count_Details, Vendor 
        FROM items_table 
        WHERE BTN_SKU = '{selected_btn_sku}'
        ORDER BY BTN_SKU DESC LIMIT 1;
        """
        details_results = read_query(connection, details_query)
        if details_results:
            Description, Type, Count_Details, Vendor = details_results[0]
    
    # Display the auto-filled data
    st.text_input('Description', Description)
    st.text_input('Type', Type)
    st.text_input('Count Details', Count_Details)
    st.text_input('Vendor', Vendor)

    # Input fields
    Pallets = st.number_input('Pallets', step=1)
    Bundles_Boxes_Spools = st.number_input('Bundles/Boxes/Spools', step=1)
    Units_Pieces_Each = st.number_input('Units/Pieces Each', step=1)
    Lead_Time = st.number_input('Lead Time', step=1)
    Month = st.text_input('Month')

    # Button to submit data
    if st.button('Submit New Monthly Data'):
        # Create the SQL query
        query = f"""
        INSERT INTO items_table (BTN_SKU, Description, Type, Count_Details, Vendor, Pallets, Bundles_Boxes_Spools, Units_Pieces_Each, Lead_Time, Month) 
        VALUES ('{selected_btn_sku}', '{Description}', '{Type}', '{Count_Details}', '{Vendor}', {Pallets}, {Bundles_Boxes_Spools}, {Units_Pieces_Each}, {Lead_Time}, '{Month}');
        """
        # Execute the query
        execute_query(connection, query)

if __name__ == "__main__":
    main()
