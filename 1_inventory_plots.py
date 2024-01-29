import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sklearn.linear_model import LinearRegression

# Connection to database function
def create_connection():
    engine = create_engine('mysql+mysqlconnector://root:peter@localhost/main_items')
    return engine.connect()

# get data from database
def fetch_inventory_data():
    conn = create_connection()
    query = "SELECT * FROM items_table"
    return pd.read_sql(query, conn)

df_inventory = fetch_inventory_data()

# Data Preprocessing
df_inventory['Month'] = pd.to_datetime(df_inventory['Month'], format='%B %Y')

# User selects months for comparison
unique_months = df_inventory['Month'].dt.strftime('%B %Y').unique()
unique_months.sort()
selected_months = st.multiselect('Select Months to Compare', unique_months, default=unique_months[:2])

# Filter and prepare data for plotting
filtered_data = df_inventory[df_inventory['Month'].dt.strftime('%B %Y').isin(selected_months)]
pivot_data = filtered_data.pivot_table(index='Description', columns='Month', values='Amount_Used_Monthly', fill_value=0)

# Reshape the data from wide to long format
long_format_data = pivot_data.reset_index().melt(id_vars='Description', var_name='Month', value_name='Amount_Used_Monthly')

# Plotting the comparison with custom axis labels
fig = px.line(long_format_data, x='Description', y='Amount_Used_Monthly', color='Month', 
              title='Monthly Usage Comparison Across Items',
              labels={'Amount_Used_Monthly': 'Amount at End of Month'})
st.plotly_chart(fig, use_container_width=True)

# User selects an item description for forecasting
item_description_selection = st.selectbox('Select Item Description for Forecasting', df_inventory['Description'].unique())

# Filter data for the selected item description
df_specific = df_inventory[df_inventory['Description'] == item_description_selection]

if len(df_specific) > 1:
    # Convert dates to numeric for linear regression
    df_specific['Month_numeric'] = np.arange(len(df_specific))

    # Linear Regression Model
    model = LinearRegression()
    model.fit(df_specific[['Month_numeric']], df_specific['Amount_Used_Monthly'])

    # Predict future points
    future_months = 1
    future_months_numeric = np.arange(len(df_specific), len(df_specific) + future_months)
    future_predictions = model.predict(future_months_numeric.reshape(-1, 1))

    # Display predictions
    st.write(f"Future usage predictions for {item_description_selection}: {future_predictions}")
else:
    st.write(f"Not enough data to generate a forecast for {item_description_selection}.")
