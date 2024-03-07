import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import time # for loading delay
import datetime

# Set the page layout to wide mode
st.set_page_config(layout="wide")

# Assuming you have a limited range of years to choose from or calculate it dynamically
current_year = datetime.datetime.now().year
years = list(range(current_year - 10, current_year + 1))  # Last 10 years and current year


def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='peter',
            database='main_items'
        )
        print("MySQL Database connection successful")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: '{err}'")
        return None


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
