import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import datetime
from dotenv import load_dotenv 
import os 
import time
import streamlit.components.v1 as components


# Load environment variables
load_dotenv()

st.set_page_config(layout="wide")
current_year = datetime.datetime.now().year
years = list(range(current_year - 10, current_year + 1))  # Last 10 years and current year

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            passwd=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
        print("MySQL Database connection successful")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: '{err}'")
        return None
    
conn = create_connection()


# Execute read queries and return results
def execute_read_query(connection, query, params=None):
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()  # Fetches all rows of a query result
        return result
    except Error as err:
        print(f"Error: '{err}'")
        return None
    

def execute_query(connection, query, params=None):
    cursor = connection.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")


def get_all_btn_sku_and_description(connection):
    query = "SELECT BTN_SKU, Description FROM items_table;"
    results = execute_read_query(connection, query)
    if results:
        return [f"{result[0]} - {result[1]}" for result in results]
    else:
        return []  # Return an empty list if there are no results


def get_most_current_amount(connection, btn_sku):
    query = """
    SELECT amount_after_change 
    FROM Current_Amount_Items 
    WHERE BTN_SKU = %s 
    ORDER BY Change_Timestamp DESC 
    LIMIT 1;
    """
    results = execute_read_query(connection, query, (btn_sku,))
    if results and results[0][0] is not None:
        return results[0][0]  # Return the most recent amount_after_change
    else:
        return 0  # Return 0 if no records are found


def get_units_per_box(connection, btn_sku):
    query = """
    SELECT units_per_box 
    FROM Current_Amount_Items 
    WHERE BTN_SKU = %s 
    ORDER BY Change_Timestamp DESC 
    LIMIT 1;
    """
    results = execute_read_query(connection, query, (btn_sku,))
    if results and results[0][0] is not None:
        return results[0][0]  # Return the most recent units_per_box
    else:
        return 0  # Return 0 if no records are found


def adjust_item_amount(connection, btn_sku, amount_change, units_per_box):
    # Fetch current total before the change, for boxes
    current_total_amount = get_most_current_amount(connection, btn_sku)
    amount_before_change = current_total_amount
    # Calculate the total after applying the change
    amount_after_change = amount_before_change + amount_change
    # Calculate new total units
    new_total_units = amount_after_change * units_per_box
    
    # Debugging print statements
    print(f"BTN_SKU: {btn_sku}")
    print(f"Amount Change (boxes): {amount_change}")
    print(f"Units Per Box: {units_per_box}")
    print(f"Amount Before Change (boxes): {amount_before_change}")
    print(f"Amount After Change (boxes): {amount_after_change}")
    print(f"New Total Units: {new_total_units}")
    
    # Parameterized query to prevent SQL injection
    query = """
    INSERT INTO Current_Amount_Items (BTN_SKU, Amount_Change, amount_before_change, units_per_box, new_total_units, amount_after_change) 
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    params = (btn_sku, amount_change, amount_before_change, units_per_box, new_total_units, amount_after_change)
    execute_query(connection, query, params)


def get_adjustment_history(connection, btn_sku):
    query = """
    SELECT BTN_SKU, amount_before_change, Amount_Change, amount_after_change, units_per_box, new_total_units, Change_Timestamp 
    FROM Current_Amount_Items  
    WHERE BTN_SKU = %s
    ORDER BY Change_Timestamp DESC;
    """
    return execute_read_query(connection, query, (btn_sku,))


def display_history(connection, btn_sku):
    history_data = get_adjustment_history(connection, btn_sku)
    if history_data:
        # Convert history data to a more readable format if necessary 
        formatted_data = []
        for record in history_data:
            record = list(record)
            record[-1] = record[-1].strftime("%Y-%m-%d %H:%M:%S")
            formatted_data.append(record)
        history_df = pd.DataFrame(formatted_data, columns=['BTN_SKU', 'Before', 'Adjustment', 'New Item Count', 'Units Per Box', 'Total Units', 'Timestamp'])
        st.write(f"Adjustment History for BTN_SKU: {btn_sku}")
        st.dataframe(history_df, use_container_width = True)
        
    else:
        st.write(f"No history found for BTN_SKU: {btn_sku}")

title_html = """<h1 style= "margin-bottom: -55px;"> Inventory Adjustment </h1>"""
st.markdown(title_html, unsafe_allow_html=True)
st.markdown("""<hr style = "height: 2px; border: none; color: green; background-color: green; "/> """, unsafe_allow_html = True)

btn_skus_with_description = get_all_btn_sku_and_description(conn)  # Fetch all BTN_SKU values with descriptions
selected_item = st.selectbox("Select BTN_SKU", btn_skus_with_description)
btn_sku = selected_item.split(' - ')[0]  # Extract BTN_SKU from the selected string


###################################################################################
# Fetch the most current amount for the selected BTN_SKU
current_amount = get_most_current_amount(conn, btn_sku)
# Fetch the most current units_per_box for the selected BTN_SKU
current_units_per_box = get_units_per_box(conn, btn_sku)
# Calculate total units
total_units = current_amount * current_units_per_box
####################################################################################


st.markdown("""
<style>
    /*Data editor header class name*/
    .classname {
        font-size: 22px;
        background-color: red;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

with st.form("adjust_item_amount_form"):
    header1 = "Adjust An Item's Amount: "
    header1_font_size = 25
    
    st.markdown(
        f"""<h1 style = 'font-size: {header1_font_size}px; 
                margin-bottom: -50px'>{header1}</h1>""",
                unsafe_allow_html=True)
    
    st.markdown("""<hr style = "height: 2px;
                border: none; color: green; 
                background-color: green; "/> """,
                unsafe_allow_html=True)
    
    st.write(f"Current Amount (boxes): {current_amount}")
    st.write(f"Total Units: {total_units}")

    amount_change = st.number_input("Amount Change (number of boxes, positive to add, negative to remove):", step = 1)
    units_per_box = st.number_input("Units Per Box:", value = current_units_per_box, step=1)
    submitted = st.form_submit_button("Adjust Amount")

    if submitted:
        if amount_change == 0:
            st.error("Amount change cannot be zero.")
        else:
            try:
                adjust_item_amount(conn, btn_sku, amount_change, units_per_box)
                
                if amount_change > 0:
                    st.success(f"Added {amount_change} boxes successfully!")
                else:
                    st.success(f"Removed {-amount_change} boxes successfully!")
                
                # Update current amount and total units after the adjustment
                current_amount = get_most_current_amount(conn, btn_sku)
                total_units = current_amount * units_per_box
                st.write(f"New Current Amount (boxes): {current_amount}")
                st.write(f"New Total Units: {total_units}")

            except Error as e:
                st.error(f"An error occurred: {e}")

st.write("\n")
st.write("\n")
st.write("\n")

# Custom title with a larger font size using HTML in Markdown
st.markdown("""
            <h2 style = 'font-size: 24px; 
            margin-bottom: -55px'>
            Select BTN_SKU to view history
            </h2>""", 
            unsafe_allow_html=True)

st.markdown("""
            <hr style = "height: 1px; 
            border: none; color: green; 
            background-color: green; "/> """, 
            unsafe_allow_html=True)

st.markdown("***Changes are displayed from oldest at the top to most recent at the bottom of the log.***")
btn_sku_history_with_description = st.selectbox("Select BTN_SKU for History", btn_skus_with_description, key="history_selectbox_history", label_visibility="collapsed")
btn_sku_history = btn_sku_history_with_description.split(' - ')[0]  # Extract BTN_SKU from the selected string

display_history_button = st.button("Click to Display Adjustment History")
if display_history_button:
    with st.spinner('Loading Adjustment History...'):
        progress_bar = st.progress(0)
        for percent_complete in range(100):
            progress_bar.progress(percent_complete + 1)
            time.sleep(0.05)
        
        display_history(conn, btn_sku_history)

    progress_bar.progress(100)
