"""
Inven Control Version 1.1(Web Based)
Created by: Juan Castaneda
Created on: 1/05/24
Description: Inven Control 1.1 is created using the Streamlit Framework. The application is designed to help with PLU label inventory mangement and 
             to help analyze usage of PLU labels. The main goal is to simplify the tracking, removal, and addition of PLU labels spools used, with the. With Inven Control 1.1
             the user can complete inventory count more efficiently and compare item counts to see monthly item usage trends, which in return can help 
             decide if the user is using more or less items. The inventory forecast page is still being designed to create a more accurate forecast to help
             with future PLU label needs.

The software provided is a work in progress, with continuos updates applied. Please be sure to check for new versions on
https://github.com/jcast6/

"""

import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import time # for loading delay
import datetime
from mysql.connector import Error
from dotenv import load_dotenv 
import os 

# Set the page layout to wide mode
st.set_page_config(layout="wide")

# Assuming you have a limited range of years to choose from or calculate it dynamically
current_year = datetime.datetime.now().year
years = list(range(current_year - 10, current_year + 1))  # Last 10 years and current year


# Load environment variables from .env file
load_dotenv()

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

db_connection = create_connection()


def fetch_data(selected_month_year):
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        query = f"SELECT * FROM items_table WHERE Month = '{selected_month_year}'"
        cursor.execute(query)
        # Fetch all rows from cursor into a DataFrame
        columns = [column[0] for column in cursor.description]
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=columns)
        print("Query successful")
        cursor.close()
        conn.close()  # Close the connection
        return df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if connection fails


# Streamlit main page layout
col1, _ = st.columns([1, 10])  # Adjust the width of the column as needed
with col1:
    st.image("github_projects/borton_fruit_logo.png", width=400, use_column_width=False, 
             caption = "This application helps the user analyze usage trends for Borton Fruit Packing Company(BPC) PLU labels in the PLU shop." 
                       " You can also manage your inventory count, and take inventory for the month and upload the data to a MySQL database. "
                       " By seeing these trends the user can determine future usage and needs of PLU lables in the future. " 
                       " This application is constantly being updated to help with more effictive analysis and to provide a simple to use interface.",  # caption or description of application.
             output_format = "auto",  # Output format of the image
             channels = "RGB",  # Channels for the image
             
             )
    

st.title("Inventory Dashboard")
st.markdown("**<h1 style='font-size: 19px;'>This page allows you to view previous monthly data of PLU labels inventory and count.</h1>**", unsafe_allow_html=True)
st.markdown("**<span style='text-decoration: underline; ; font-size: 19px;'>Overall Inventory Table:</span>**", unsafe_allow_html=True)

# Add a year selection widget
selected_year = st.selectbox("What year is the data from:", years)

# Combine the selected month and year
months = ['January', 'February', 'March', 'April', 'May', 'June', 
          'July', 'August', 'September', 'October', 'November', 'December']
selected_month = st.selectbox("What Month is the data from:", months)
selected_month_year = f"{selected_month} {selected_year}"

# Fetch and display data for the selected month and year
df = fetch_data(selected_month_year)

# Search Bar asking user to enter either item BTN_SKU or Description
search_query = st.text_input("Enter BTN_SKU or Description to search:")
if search_query:
    search_results = df[(df['BTN_SKU'] == search_query) | (df['Description'].str.contains(search_query, case=False, na=False))]
    if search_results.empty:
        st.write("Item not found in inventory.")
    else:
        # Initialize progress bar
        progress_bar = st.progress(0)

        for percent_complete in range(100):
            time.sleep(0.0030)  # Sleep for a short time to simulate loading
            progress_bar.progress(percent_complete + 1)

        st.success("Item found!")
        st.write("Item Data:")
        st.dataframe(search_results)
st.dataframe(df, use_container_width=True)

st.markdown("\n")
st.markdown("\n")
st.markdown("\n")

# Description for bar chart
st.markdown("**<span style='text-decoration: underline; font-size: 19px;'>Bar Graph of Item Count:</span>**", unsafe_allow_html=True)
st.markdown("This bar chart displays the count of each item in the inventory. The count is categorized by whether the item is counted as single spools or as bundles/boxes.")
st.markdown("You can choose in the drop down which items were counted as spools and not bundles/boxes style count.")


# User selection for count method
all_items = df['Description'].unique()  # Or use 'BTN_SKU' column if better for you

# selected_items_spools all items selected by user
#  multi select dropdown, can select multiple items from the list 'all_items'
selected_items_spools = st.multiselect('Select Items to Count as Single Spools', all_items, default=[])

# Update DataFrame with column 'Count_Method', check if item's description is in the list of 'selected_items_spools', if the description is in the list, 
# the count method is set to 'Spools' if not set it defaults to 'Bundles/Boxes'. 
df['Count_Method'] = df['Description'].apply(lambda x: 'Spools' if x in selected_items_spools else 'Bundles/Boxes')

# Bar graph for each item
fig_bar = px.bar(df, x='Description', y='Bundles_Boxes_Spools', color='Count_Method', 
                 title=f'Inventory Count for Each Item - {selected_month}',
                 labels={'Bundles_Boxes_Spools': 'Count'})
fig_bar.update_layout(width=800, height=600, xaxis_tickangle=-45)
st.plotly_chart(fig_bar, use_container_width=True)

# Prepare data for the new interactive bar chart
df_grouped = df.groupby('Type').agg(
    Total_Space=pd.NamedAgg(column='Bundles_Boxes_Spools', aggfunc='sum'),
    Item_List=pd.NamedAgg(column='Description', aggfunc=lambda x: '<br>'.join(x))
).reset_index()


st.write("\n")
st.write("\n")
st.write("\n")
st.write("\n")
st.write("\n")
st.write("\n")

# Interactive bar chart for inventory space by item type with different colors for each type
st.markdown("<span style='text-decoration: underline; font-size: 19px;'>**Bar Graph for Inventory Space Distribution:**</span>", unsafe_allow_html=True)
st.write("This bar chart shows the distribution of inventory space by item type for the selected month. Hover over each bar to see the list of items in that type.")
fig_type_space = px.bar(df_grouped, x='Type', y='Total_Space',
                        color='Type',  # Assign colors based on 'Type'
                        hover_data={'Type': False, 'Total_Space': True, 'Item_List': True},
                        labels={'Total_Space': 'Total Inventory Space', 'Item_List': 'Items in Type'},
                        title=f'Inventory Space by Item Type with Detailed Item List - {selected_month}')
st.plotly_chart(fig_type_space, use_container_width=True)
