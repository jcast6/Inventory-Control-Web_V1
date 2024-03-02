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

# Streamlit app
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

    # Input fields
    BTN_SKU = st.text_input('BTN_SKU')
    Description = st.text_input('Description')
    Type = st.text_input('Type')
    Count_Details = st.text_input('Count Details')
    Vendor = st.text_input('Vendor')
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
        VALUES ('{BTN_SKU}', '{Description}', '{Type}', '{Count_Details}', '{Vendor}', {Pallets}, {Bundles_Boxes_Spools}, {Units_Pieces_Each}, {Lead_Time}, '{Month}');
        """
        # Execute the query
        execute_query(connection, query)

if __name__ == "__main__":
    main()
