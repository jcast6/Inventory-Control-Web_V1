
import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import create_engine
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode


# Streamlit main page layout
st.title("New End of Month Inventory Count")


# Connection to database function
def create_connection():
    engine = create_engine('mysql+mysqlconnector://root:peter@localhost/main_items')
    return engine.connect()

# get data stored in database
def fetch_data():
    conn = create_connection()
    query = "SELECT * FROM items_table"
    return pd.read_sql(query, conn)

# function to update the database with the new end of month inventory data
def update_database(new_data_df):
    conn = create_connection()
    new_data_df.to_sql('items_table', conn, if_exists='append', index=False)

# Function to display read-only table of existing data from previous months.
def display_readonly_table(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=False)  # Make all columns non-editable
    
    # Setting the same width for all columns
    uniform_width = 125  # Adjust the column width as necessary
    for col in df.columns:
        gb.configure_column(col, width=uniform_width)
    
    gb.configure_grid_options(domLayout='normal')  # Adjust layout to normal
    grid_options = gb.build()

    AgGrid(
        df,
        gridOptions=grid_options,
        height=200,
        width='100%',
        fit_columns_on_grid_load=False,  # enabled as False since we're manually setting column widths
    )


def editable_table_for_new_data(df):
    # Create a new DataFrame that includes all existing data
    new_data_structure = df.copy()

    # Set the specific columns for new data entry to empty
    for col in ['Bundles_Boxes_Spools', 'Amount_Used_Monthly', 'Month']:
        if new_data_structure[col].dtype == 'object':  # Assuming these columns are of string type
            new_data_structure[col] = ''  # Set to empty string for object type columns
        else:
            new_data_structure[col] = None  # Set to None for other types, which pandas will convert to NaN

    gb = GridOptionsBuilder.from_dataframe(new_data_structure)

    # adjust the column widths and editability
    uniform_width = 125  # You can adjust this width as needed for columns
    for col in new_data_structure.columns:
        if col in ['Bundles_Boxes_Spools', 'Amount_Used_Monthly', 'Month']:
            gb.configure_column(col, editable=True, width=uniform_width)
        else:
            gb.configure_column(col, editable=False, width=uniform_width)

    grid_options = gb.build()

    grid_response = AgGrid(
        new_data_structure,
        gridOptions=grid_options,
        height=200,
        width='100%',
        data_return_mode=DataReturnMode.AS_INPUT,
        update_mode=GridUpdateMode.VALUE_CHANGED,
        enable_enterprise_modules=True
    )
    return grid_response['data']

# function to create a progress bar
def calculate_progress(df, columns):
    # Ensure the DataFrame contains the specified columns
    columns_exist = all(col in df.columns for col in columns)
    if not columns_exist:
        # If columns don't exist, progress is 0
        return 0
    
    # Count non-empty entries in the specified columns
    filled_entries = df[columns].notna().sum().sum()
    # Total entries needed is number of rows times the number of specified columns
    total_entries_needed = len(df) * len(columns)
    # Calculate the progress ratio
    progress_ratio = filled_entries / total_entries_needed if total_entries_needed else 0
    return progress_ratio

    
# Fetch existing data from database
existing_data = fetch_data()

# Display existing data in a read-only table
st.subheader("Existing Data")
display_readonly_table(existing_data)


# Display table for entering new end of month inventory count data
st.subheader("Enter New Monthly Data")
new_data = editable_table_for_new_data(existing_data)

# If new_data is not a DataFrame, convert it to a DataFrame
if not isinstance(new_data, pd.DataFrame):
    new_data = pd.DataFrame(new_data)

# Ensure the DataFrame has the necessary columns
if 'Bundles_boxes_spools' not in new_data.columns:
    new_data['Bundles_boxes_spools'] = [None] * len(new_data)
if 'amount_used_monthly' not in new_data.columns:
    new_data['amount_used_monthly'] = [None] * len(new_data)
if 'month' not in new_data.columns:
    new_data['month'] = [None] * len(new_data)

# Calculate progress
progress = calculate_progress(new_data, ['Bundles_boxes_spools', 'amount_used_monthly', 'month'])

# Display progress bar
st.progress(progress)

# Button to submit new data
if st.button("Submit New Data"):
    if new_data:  # Check if there is new data entered
        new_data_df = pd.DataFrame(new_data)
        # Filter out rows where editable columns are all None (not filled)
        new_data_df = new_data_df.dropna(subset=['Bundles_boxes_spools', 'amount_used_monthly', 'month'], how='all')
        if not new_data_df.empty:
            update_database(new_data_df)
            st.success("New monthly data successfully added!")
        else:
            st.error("Please enter new data in the required fields before submitting.")
    else:
        st.error("Please enter new data before submitting.")