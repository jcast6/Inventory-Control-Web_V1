"""
Inven Control Version 1.1(Web Based)
Created by: Juan Castaneda
Created on: 1/05/24
Description: Inven Control 1.1 is created using the Streamlit Framework. The application is designed to help with PLU label inventory management and 
             to help analyze usage of PLU labels. The main goal is to simplify the tracking, removal, and addition of PLU labels spools used. With Inven Control 1.1
             the user can complete inventory count more efficiently and compare item counts to see monthly item usage trends, which in return can help 
             decide if the user is using more or less items. The inventory forecast page is still being designed to create a more accurate forecast to help
             with future PLU label needs.

The software provided is a work in progress, with continuous updates applied. Please be sure to check for new versions on
https://github.com/jcast6/

"""
import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import time
import datetime
from mysql.connector import Error
from dotenv import load_dotenv 
import os 
import plotly.graph_objects as pg
# import streamlit.components.v1 as components
# import numpy as np

st.set_page_config(layout="wide")

current_year = datetime.datetime.now().year
years = list(range(current_year - 10, current_year + 1))  # Last 10 years and current year
months = ['January', 'February', 'March', 'April', 'May', 'June', 
          'July', 'August', 'September', 'October', 'November', 'December']

# Load environment variables from .env file
load_dotenv()

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

db_connection = create_connection()


def fetch_data(selected_month_year):
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "SELECT * FROM items_table WHERE Month = %s"
            cursor.execute(query, (selected_month_year,))
            columns = [column[0] for column in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            print("Query successful, fetched data:")
            print(df.head())  # Print first few rows to debug
            return df
        finally:
            cursor.close()
            conn.close()
    else:
        return pd.DataFrame()


def execute_query(connection, query, params):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")


# get all items BTN_SKU only
def fetch_items_BTN_SKU():
    connection = create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                query = "SELECT Distinct BTN_SKU FROM items_table" 
                cursor.execute(query)
                items = cursor.fetchall()
                return [item[0] for item in items]  # Adjust indexing if necessary based on query
        except Error as err:
            print(f"Error: '{err}'")
            return []
        finally:
            if connection:
                connection.close()
    else:
        return []

col1, _ = st.columns([1, 10])  # width of the column 
with col1:
    st.image("github_projects/borton_fruit_logo.png", width = 500, use_column_width = False,
             output_format = "auto",  # Output format of the image
             channels = "RGB",  # Channels for the image
             
             )
    
st.markdown("""
    <div style='text-align: left; color: gray; font-size: 18px;'>
        <p>This application helps the user analyze usage trends for Borton Fruit Packing Company (BPC) PLU labels in the PLU shop.
        You can also manage your inventory count, and take inventory for the month and upload the data to a MySQL database.
        By seeing these trends the user can determine future usage and needs of PLU labels in the future.
        This application is constantly being updated to help with more effective analysis and to provide a simple to use interface.</p>
    </div>
    """, unsafe_allow_html=True)
    
st.title("PLU Inventory Dashboard 📊 ")
st.markdown("**<span style='text-decoration: underline; ; font-size: 25px;'>Please select a year and month to see inventory data for📅🗓️:</span>**", unsafe_allow_html = True)

# Use session state to remember the selected year and month
if 'selected_year' not in st.session_state:
    st.session_state.selected_year = current_year

if 'selected_month' not in st.session_state:
    st.session_state.selected_month = months[0]

selected_year = st.selectbox("What year is the data from📅:", years, index=years.index(st.session_state.selected_year))
selected_month = st.selectbox("What Month is the data from🗓️:", months, index=months.index(st.session_state.selected_month))

# Update session state
st.session_state.selected_year = selected_year
st.session_state.selected_month = selected_month

# Combine the selected month and year
selected_month_year = f"{selected_month} {selected_year}"

# selected data is inserted into dataframe and displayed
df = fetch_data(selected_month_year)

# Search Bar asking user to enter either item BTN_SKU or Description
search_query = st.text_input("Enter BTN_SKU or Description to search for item📦:")
if search_query:
    search_results = df[(df['BTN_SKU'] == search_query) | (df['Description'].str.contains(search_query, case=False, na=False))]
    if search_results.empty:
        st.write("Item not found in inventory.")
    else:
        # Initialize progress bar
        progress_bar = st.progress(0)

        for percent_complete in range(100):
            time.sleep(0.0030)
            progress_bar.progress(percent_complete + 1)

        st.success("Item found!")
        st.write("Item Data:")
        st.dataframe(search_results)
st.dataframe(df, use_container_width=True)

st.markdown("\n")
st.markdown("\n")
st.markdown("\n")

st.markdown("**<span style='text-decoration: underline; font-size: 25px;'>Bar Graph of Item Count📉 :</span>**", unsafe_allow_html = True)
st.markdown("This bar chart displays the count of each item in the inventory. The count is categorized by whether the item is counted as single spools or as bundles/boxes.")
st.markdown("You can choose in the drop down which items were counted as spools and not bundles/boxes style count.")

# User selection for count method
all_items = df['Description'].unique()  # Or use 'BTN_SKU' column if better for you

# multi select dropdown, can select multiple items from the list 'all_items'
selected_items_spools = st.multiselect('Select Items to Count as Single Spools', all_items, default = [])

# Update DataFrame with column 'Count_Method', check if item's description is in the list of 'selected_items_spools', if the description is in the list, 
# the count method is set to 'Spools' if not set it defaults to 'Bundles/Boxes'. 
df['Count_Method'] = df['Description'].apply(lambda x: 'Spools' if x in selected_items_spools else 'Bundles/Boxes')

# Bar graph for each item
fig_bar = px.bar(df, x = 'Description', y = 'Bundles_Boxes_Spools', color = 'Count_Method', 
                 title=f'Inventory Count for Each Item - {selected_month}',
                 labels={'Bundles_Boxes_Spools': 'Count'})
fig_bar.update_layout(height = 600, xaxis_tickangle = -45)
st.plotly_chart(fig_bar, use_container_width = True)

# Prepare data for the new interactive bar chart
df_grouped = df.groupby('item_type').agg(
    Total_Space = pd.NamedAgg(column='Bundles_Boxes_Spools', aggfunc = 'sum'),
    Item_List=pd.NamedAgg(column='Description', aggfunc = lambda x: '<br>'.join(x))
).reset_index()

st.write("\n")
st.write("\n")
st.write("\n")
st.write("\n")
st.write("\n")
st.write("\n")

if not df.empty:
    # Group by 'Type' and aggregate data
    df_grouped = df.groupby('item_type').agg(
        Total_Space = pd.NamedAgg(column = 'Bundles_Boxes_Spools', aggfunc = 'sum'),
        # Handle missing data by using a placeholder if no descriptions are present
        Item_List = pd.NamedAgg(column = 'Description', aggfunc = lambda x: '<br>'.join(set(x)) if x.any() else 'No data')
    ).reset_index()

    print(f"Grouped data for {selected_month_year}:")
    print(df_grouped[df_grouped['item_type'] == 'Chelan PLU'])

    # Total space for calculating percentages
    total_space = df_grouped['Total_Space'].sum()
    
    st.markdown("<span style='text-decoration: underline; font-size: 25px;'>**Bar Graph for Inventory Space Distribution📊 :**</span>", unsafe_allow_html = True)

    # bar chart with the updated data frame
    fig_type_space = px.bar(df_grouped, x = 'item_type', y = 'Total_Space',
                            color = 'item_type',  
                            hover_data = {'Item_List'},
                            labels = {'Total_Space': 'Total Inventory Space'},
                            title = f'Inventory Space by Item Type - {selected_month_year}',
                            height = 600)
    fig_type_space.update_layout(xaxis_tickangle = -45)

    # Display the figure
    st.plotly_chart(fig_type_space, use_container_width=True)

     # display the metrics under the bar chart
    st.write("\n")
    st.markdown("**Inventory Space Metrics**")

    # Use columns to display each metric side by side
    cols = st.columns(len(df_grouped))
    for col, (index, row) in zip(cols, df_grouped.iterrows()):
        percentage = (row['Total_Space'] / total_space) * 100  # Calculate the percentage
        # markdown to add a hover text over the metric that shows the item list
        metric_label_html = f"<span title='{row['Item_List']}' style='text-decoration: underline;'>{row['item_type']}</span>"
        col.markdown(metric_label_html, unsafe_allow_html = True)
        st.write(
                """
                <style>
                [data-testid="stMetricDelta"] svg {
                    display: none;
                }
                </style>
                """,
                unsafe_allow_html = True,
        )
        col.metric(label="Inventory Space Used", value = f"{row['Total_Space']:.2f}", delta = f"{percentage:.2f}%", delta_color = 'off')
else:
    st.error("No data available for the selected period.")

st.markdown("**<span style='text-decoration: underline; font-size: 25px;'>Comparing item monthly usage📈📉:</span>**", unsafe_allow_html = True)
num_months = st.number_input("Enter the number of months to compare (up to 12):", min_value = 1, max_value = 12, value = 2, step = 1)

# Month and year selection
selected_months_years = []
for i in range(num_months):
    selected_year = st.selectbox(f"Select year {i+1}📅:", years, key=f'year_selection_{i}')
    selected_month = st.selectbox(f"Select month {i+1}🗓️:", months, key=f'month_selection_{i}')
    selected_months_years.append((selected_month, selected_year))

# Define a list of colors for visualization
color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

# Fetch all items from database 
all_items = fetch_items_BTN_SKU()

# Item selection with multiselect
selected_items = st.multiselect("Select item(s)📦:", all_items, key = 'item_selection')


# Fetch and process data for each selected item
data_results = []
for month, year in selected_months_years:
    month_year = f"{month} {year}"
    for item in selected_items:
        query2 = "SELECT Month, Bundles_Boxes_Spools FROM items_table WHERE BTN_SKU = %s AND Month = %s"
        data = execute_query(db_connection, query2, (item, month_year))
        data_results.append({'MonthYear': month_year, 'Item': item, 'Value': data[0]['Bundles_Boxes_Spools'] if data else 0})

# insert extracted results into a dataframe
df_results = pd.DataFrame(data_results)

fig = pg.Figure()
for item in selected_items:
    df_filtered = df_results[df_results['Item'] == item]
    #fig.add_trace(pg.Bar(name = item,
    fig.add_trace(pg.Scatter(name=item, 
                         x = df_filtered['MonthYear'], 
                         y = df_filtered['Value'], 
                         marker_color = color_palette[selected_items.index(item) % len(color_palette)]
                         ))

fig.update_layout(
    title = 'Monthly data comparison for selected item(s)',
    xaxis_title = "Month/Year",
    yaxis_title = "Bundles/Boxes/Spools",
    #barmode = 'group',
    height = 800,
)

# Update y-axis increment to 5
fig.update_yaxes(tick0 = 0, dtick = 10)

# Display the chart
st.plotly_chart(fig)

