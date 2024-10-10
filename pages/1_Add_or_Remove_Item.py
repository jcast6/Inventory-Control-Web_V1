import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import datetime
from dotenv import load_dotenv
import os
import time

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

def get_total_units_and_boxes(connection, btn_sku):
    query = """
    SELECT SUM(Amount_Change * units_per_box) as total_units,
           SUM(Amount_Change) as total_boxes
    FROM Current_Amount_Items 
    WHERE BTN_SKU = %s;
    """
    results = execute_read_query(connection, query, (btn_sku,))
    if results and results[0] is not None:
        return results[0][0], results[0][1]  # Return total units and total boxes
    else:
        return 0, 0  # Return 0 if no records are found

def adjust_item_amount(connection, btn_sku, amount_change, units_per_box, is_roll):
    # Fetch current total before the change, for boxes or rolls
    current_total_amount = get_most_current_amount(connection, btn_sku)
    amount_before_change = current_total_amount
    # Calculate the total after applying the change
    amount_after_change = amount_before_change + amount_change
    # Fetch previous total units and boxes
    previous_total_units, previous_total_boxes = get_total_units_and_boxes(connection, btn_sku)
    
    # Ensure to use the correct previous total boxes, not adding them repeatedly
    new_total_boxes = previous_total_boxes + amount_change

    # Calculate new total units correctly
    # If you are adding/subtracting boxes, we calculate the change to the total units
    new_total_units = previous_total_units + (amount_change * units_per_box)

    # Recalculate the average units per box correctly
    if new_total_boxes > 0:
        new_average_units_per_box = round(new_total_units / new_total_boxes)
    else:
        new_average_units_per_box = 0

    #### Prints to terminal for verification, do not edit! ####
    print(f"BTN_SKU: {btn_sku}")
    print(f"Amount Change (boxes/rolls): {amount_change}")
    print(f"Units Per Box/Roll: {units_per_box}")
    print(f"Amount Before Change (boxes/rolls): {amount_before_change}")
    print(f"Amount After Change (boxes/rolls): {amount_after_change}")
    print(f"New Total Units: {new_total_units}")
    print(f"New Average Units Per Box: {new_average_units_per_box}")
    print(f"Is Roll: {is_roll}")
    ###########################################################

    # Parameterized query to prevent SQL injection
    query = """
    INSERT INTO Current_Amount_Items (BTN_SKU, Amount_Change, amount_before_change, units_per_box, new_total_units, amount_after_change, is_roll) 
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    params = (btn_sku, amount_change, amount_before_change, units_per_box, new_total_units, amount_after_change, is_roll)
    execute_query(connection, query, params)

    # Update the items_table to reflect the roll status
    update_items_table_query = """
    UPDATE items_table
    SET is_roll = %s
    WHERE BTN_SKU = %s;
    """
    execute_query(connection, update_items_table_query, (is_roll, btn_sku))


def get_adjustment_history(connection, btn_sku):
    query = """
    SELECT BTN_SKU, amount_before_change, Amount_Change, amount_after_change, units_per_box, new_total_units, Change_Timestamp, is_roll
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
            record[-2] = record[-2].strftime("%Y-%m-%d %H:%M:%S")
            record[-1] = "Yes" if record[-1] else "No"
            formatted_data.append(record)
        history_df = pd.DataFrame(formatted_data, columns=['BTN_SKU', 'Before', 'Adjustment', 'New Item Count', 'Average Units Per Box/Roll', 'Total Units', 'Timestamp', 'Is Roll'])
        st.write(f"Adjustment History for BTN_SKU: {btn_sku}")
        st.dataframe(history_df, use_container_width=True)
    else:
        st.write(f"No history found for BTN_SKU: {btn_sku}")

title_html = """<h1 style= "margin-bottom: -55px;"> Inventory Adjustment </h1>"""
st.markdown(title_html, unsafe_allow_html=True)
st.markdown("""<hr style = "height: 2px; border: none; color: green; background-color: green; "/> """, unsafe_allow_html=True)

btn_skus_with_description = get_all_btn_sku_and_description(conn)  # Fetch all BTN_SKU values with descriptions
selected_item = st.selectbox("Select BTN_SKU", btn_skus_with_description)
btn_sku = selected_item.split(' - ')[0]  # Extract BTN_SKU from the selected string

# Fetch the most current amount for the selected BTN_SKU
current_amount = get_most_current_amount(conn, btn_sku)
previous_total_units, previous_total_boxes = get_total_units_and_boxes(conn, btn_sku)
if previous_total_units is not None and previous_total_boxes is not None and previous_total_boxes != 0:
    current_average_units_per_box = previous_total_units / previous_total_boxes
else:
    current_average_units_per_box = 0

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

# Form logic for adjustment
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
    
    st.write(f"Current Amount (boxes/rolls): {current_amount}")
    st.write(f"Current Average Units Per Box/Roll: {current_average_units_per_box}")

    amount_change = st.number_input("Amount Change (number of boxes/rolls, positive to add, negative to remove):", step=1)
    is_roll = st.checkbox("Is this item a roll?", value=False)
    units_per_box = st.number_input("Units Per Box/Roll(Use average from boxes on new pallet or shipment):", min_value=1, step=1)

    submitted = st.form_submit_button("Adjust Amount")

    if submitted:
        if amount_change == 0:
            st.error("Amount change cannot be zero.")
        elif units_per_box == 0:
            st.error("Units per box/roll cannot be zero.")
        else:
            try:
                # Adjust item amount and recalculate the average
                adjust_item_amount(conn, btn_sku, amount_change, units_per_box, is_roll)
                
                if amount_change > 0:
                    st.success(f"Added {amount_change} {'rolls' if is_roll else 'boxes'} successfully!")
                else:
                    st.success(f"Removed {-amount_change} {'rolls' if is_roll else 'boxes'} successfully!")
                
                # Update current amount and total units after the adjustment
                current_amount = get_most_current_amount(conn, btn_sku)
                previous_total_units, previous_total_boxes = get_total_units_and_boxes(conn, btn_sku)
                
                # Properly calculate the new average after the change
                if previous_total_boxes > 0:
                    new_average_units_per_box = previous_total_units / previous_total_boxes
                else:
                    new_average_units_per_box = 0
                    
                st.write(f"New Current Amount (boxes/rolls): {current_amount}")
                st.write(f"New Average Units Per Box/Roll: {new_average_units_per_box}")

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
