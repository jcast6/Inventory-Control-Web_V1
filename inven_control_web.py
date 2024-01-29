import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# Connection function
def create_connection():
    engine = create_engine('mysql+mysqlconnector://root:peter@localhost/main_items')
    return engine.connect()

def fetch_data():
    conn = create_connection()
    query = "SELECT * FROM items_table"
    return pd.read_sql(query, conn)

# Streamlit main page layout
st.title("Inventory Dashboard")

# Fetch and display data
df = fetch_data()
st.markdown("**Overall Inventory Data:**")
st.dataframe(df, use_container_width=True)
st.markdown("\n")
st.markdown("\n")
st.markdown("\n")

# Description for bar chart
st.markdown("\n**Bar Chart Description:**")
st.markdown("***This bar chart displays the count of each item in the inventory. The count is categorized by whether the item is counted as single spools or as bundles/boxes.***")
st.markdown("***You can choose in the drop down which items were counted as spools and not bundles/boxes style count.***")


# User selection for count method
all_items = df['Description'].unique()  # Or use 'BTN_SKU' if that's more appropriate
selected_items_spools = st.multiselect('*Select Items to Count as Single Spools*', all_items, default=[])

# Update DataFrame based on selection
df['Count_Method'] = df['Description'].apply(lambda x: 'Spools' if x in selected_items_spools else 'Bundles/Boxes')

# Bar graph for each item
fig_bar = px.bar(df, x='Description', y='Bundles_Boxes_Spools', color='Count_Method', 
                 title='Inventory Count for Each Item',
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
st.markdown("**Interactive Bar Chart Description:**")
st.write("***This bar chart shows the distribution of inventory space by item type. Hover over each bar to see the list of items in that type.***")
fig_type_space = px.bar(df_grouped, x='Type', y='Total_Space',
                        color='Type',  # Assign colors based on 'Type'
                        hover_data={'Type': False, 'Total_Space': True, 'Item_List': True},
                        labels={'Total_Space': 'Total Inventory Space', 'Item_List': 'Items in Type'},
                        title='Inventory Space by Item Type with Detailed Item List')
st.plotly_chart(fig_type_space, use_container_width=True)
