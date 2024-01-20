import streamlit as st
from sqlalchemy import create_engine
import io
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Define pages as functions
def home_page():
    st.title("Home Page")
    st.write("Welcome to the Home Page!")

# Function to create a database connection using SQLAlchemy
def create_db_connection():
    db_url = "mysql+mysqlconnector://root:peter@localhost/shop_inventory"
    return create_engine(db_url)

# Define plotting functions
def plot_pie_chart(data):
    type_data = data['Type'].value_counts()
    plt.figure(figsize=(6, 6))
    labels = [str(label) for label in type_data.index]
    plt.pie(type_data, labels=labels, autopct='%1.1f%%')
    plt.title('Distribution of Items by Type')
    return plt.gcf()

import matplotlib.ticker as ticker

def plot_bar_chart(data):
    plt.figure(figsize=(12, 8))
    descriptions = data['Description'].astype(str)
    quantities = pd.to_numeric(data['Units/Pieces/Each'], errors='coerce').fillna(0)
    
    plt.bar(descriptions, quantities)
    plt.xlabel('Description')
    plt.ylabel('Units/Pieces/Each')
    
    # Rotate the x-tick labels to vertical to prevent overlap and set a smaller font size
    plt.xticks(rotation=90, fontsize=8)
    
    # Format y-axis tick labels to show whole numbers
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{int(x):,}'))  # Adding comma as thousands separator
    
    plt.title('Quantity of Each Item')
    plt.tight_layout()
    return plt.gcf()


# Define import_inventory_page function
def import_inventory_page():
    st.title("Import Inventory Sheet")
    uploaded_file = st.file_uploader("Choose a file", type=['xlsx', 'csv'], key="inventory_sheet_uploader")

    if uploaded_file is not None:
        try:
            data = pd.read_excel(uploaded_file, engine='openpyxl', sheet_name=0, header=3)
            st.write('Column names:', data.columns.tolist())

            required_columns = ['Type', 'Description', 'Units/Pieces/Each']
            if all(column in data.columns for column in required_columns):
                # Display the dataframe
                st.dataframe(data)

                # Plotting the pie chart
                st.write('Distribution of Items by Type')
                pie_chart = plot_pie_chart(data)
                st.pyplot(pie_chart)

                # Plotting the bar chart
                st.write('Quantity of Each Item')
                bar_chart = plot_bar_chart(data)
                st.pyplot(bar_chart)

            else:
                st.error(f"Uploaded file is missing required columns: {', '.join(required_columns)}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.write("Please upload a file to view the inventory data and visualizations.")

# Main app logic
if __name__ == "__main__":
    # Define your pages here
    pages = {
        "Home": home_page,
        "Import Inventory Sheet": import_inventory_page
    }

    # Sidebar navigation
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(pages.keys()))

    # Render the selected page
    page = pages[selection]
    page()
