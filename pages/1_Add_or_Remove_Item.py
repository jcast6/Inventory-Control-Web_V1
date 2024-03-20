import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd

# Set the page layout to wide mode
st.set_page_config(layout="wide")

# Database configuration
host_name = 'localhost'
user_name = 'root'
user_password = 'peter'
db_name = 'main_items'


# Function to connect to the database
def create_connection(host_name, user_name, user_password, db_name):
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

db_connection = create_connection(host_name, user_name, user_password, db_name)


# Adjusted: Function to execute read queries and return results
def execute_read_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()  # Fetches all rows of a query result
        return result
    except Error as err:
        print(f"Error: '{err}'")
        return None
    

# Function to execute a query
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")


# Function to get all BTN_SKU values
def get_all_btn_sku(connection):
    query = "SELECT DISTINCT BTN_SKU FROM items_table;"
    results = execute_read_query(connection, query)
    # Check if results is not None and not empty
    if results:
        # Extracting the first column from each row
        return [result[0] for result in results]
    else:
        return []  # Return an empty list if there are no results


# Function to fetch the current total amount for a specific BTN_SKU
def get_current_total_amount(connection, btn_sku):
    query = f"SELECT SUM(Amount_Change) FROM Current_Amount_Items WHERE BTN_SKU = '{btn_sku}';"
    results = execute_read_query(connection, query)
    if results and results[0][0] is not None:
        return results[0][0]  # Return the sum of Amount_Change
    else:
        return 0  # Return 0 if no records are found, indicating no previous changes


# function to use parameterized queries for better security
def adjust_item_amount(connection, btn_sku, amount_change):
    # Fetch current total before the change
    current_total_amount = get_current_total_amount(connection, btn_sku)
    amount_before_change = current_total_amount
    # Calculate the total after applying the change
    amount_after_change = amount_before_change + amount_change
    
    # Use parameterized query to prevent SQL injection
    query = """
    INSERT INTO Current_Amount_Items (BTN_SKU, Amount_Change, amount_before_change, amount_after_change) 
    VALUES (%s, %s, %s, %s);
    """
    params = (btn_sku, amount_change, amount_before_change, amount_after_change)
    cursor = connection.cursor()
    try:
        # Pass the query and the parameters separately
        cursor.execute(query, params)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

# Function to get adjustment history for a specific BTN_SKU
def get_adjustment_history(connection, btn_sku):
    query = """
    SELECT BTN_SKU, amount_before_change, Amount_Change, amount_after_change, Change_Timestamp 
    FROM Current_Amount_Items 
    WHERE BTN_SKU = %s
    ORDER BY Change_Timestamp ASC;
    """
    cursor = connection.cursor()
    cursor.execute(query, (btn_sku,))
    history = cursor.fetchall()
    return history

# adjustment history log
def display_history(connection, btn_sku):
    history_data = get_adjustment_history(connection, btn_sku)
    if history_data:
        # Convert history data to a more readable format if necessary 
        for record in history_data:
             # Convert tuple to list to modify elements
            record = list(record)
            # Format timestamp
            record[-1] = record[-1].strftime("%Y-%m-%d %H:%M:%S")
        history_df = pd.DataFrame(history_data, columns=['BTN_SKU', 'Before', 'Adjustment', 'New Item Count', 'Timestamp'])
        st.write(f"Adjustment History for BTN_SKU: {btn_sku}")
        # Display the history as a table
        st.dataframe(history_df)
    else:
        st.write(f"No history found for BTN_SKU: {btn_sku}")


# Page header
st.title("Inventory Adjustment")
btn_skus = get_all_btn_sku(db_connection)  # Fetch all BTN_SKU values


# - 'with st.form("adjust_item_amount_form"):' This line starts the form block. 
# - "adjust_item_amount_form" is the key for the form, which should be unique within the app.
# - Inside the form, you've added several widgets (st.write, st.selectbox, st.number_input) that 
#  allow users to input data. All these inputs are part of the form.
# - st.form_submit_button("Adjust Amount"): This button is used to submit the form. 
#  When the user clicks this button, all the inputs within the form are submitted together. 
#  The submitted variable captures the state of the submission (True if the form has been submitted, False otherwise).
# - After the form is submitted (if submitted:), you process the input data (adjust_item_amount(db_connection, btn_sku, amount_change)) 
#  and display a success message using st.success based on whether amount_change is positive or negative.
with st.form("adjust_item_amount_form"):
    st.write("Adjust an Item's Amount")
    btn_sku = st.selectbox("Select BTN_SKU", btn_skus)
    amount_change = st.number_input("Amount Change (positive to add, negative to remove)", step=1)
    submitted = st.form_submit_button("Adjust Amount")
    if submitted:
        adjust_item_amount(db_connection, btn_sku, amount_change)
        if amount_change > 0:
            st.success(f"Added {amount_change} items successfully!")
        else:
            st.success(f"Removed {-amount_change} items successfully!")

st.write("\n")
st.write("\n")
st.write("\n")

# Example of a custom title with a larger font size using HTML in Markdown
st.markdown("<h2 style='font-size: 24px;'>Select BTN_SKU to view history</h2>", unsafe_allow_html=True)

st.markdown("***Changes are displayed from oldest at the top to most recent at the bottom of the log.***")
# This ensures accessibility while allowing your custom styled title to serve as the main visual label
btn_sku_history = st.selectbox("Select BTN_SKU (This label is for accessibility purposes)", btn_skus, key="history_selectbox", label_visibility="collapsed")

display_history_button = st.button("Click to Display Adjustment History")
if display_history_button:
    display_history(db_connection, btn_sku_history)
