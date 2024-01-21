import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px


# Function to create a database connection using SQLAlchemy
def create_db_connection():
    db_url = "mysql+mysqlconnector://root:peter@localhost/main_items"
    engine = create_engine(db_url)
    return engine


# --- Fetch data from the database --- 
def load_data():
    engine = create_db_connection()
    query = "SELECT * FROM items_table"
    data = pd.read_sql(query, engine)
    return data


# --- plot the data in a scatter plot ---
def plot_scatter_chart(data):
    # Convert 'Bundles_Boxes' to numeric, setting errors to 'coerce'
    data['Bundles_Boxes'] = pd.to_numeric(data['Bundles_Boxes'], errors='coerce')
    
    # Replace NaN values with a default size, e.g., 0 or the mean size
    data['Bundles_Boxes'].fillna(0, inplace=True)
    
    # Calculate total and percentage
    total_bundles = data['Bundles_Boxes'].sum()
    data['Percentage'] = (data['Bundles_Boxes'] / total_bundles) * 100
    
    # Create the scatter plot
    fig = px.scatter(
        data_frame=data,
        x='Description',
        y='Percentage',
        size='Bundles_Boxes',  # The size argument represents the size of each dot.
        text='Bundles_Boxes',  # Add number of boxes as text
        hover_data=['Bundles_Boxes'],  # Display bundles/boxes info on hover
        labels={'Description': 'Item Description', 'Percentage': 'Percentage of Total Inventory'},
        title='Percentage of Inventory by Item'
    )
    
    # Update layout to adjust margins and text position
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_tickangle=-45
    )
    # Update traces to adjust text position
    fig.update_traces(textposition='middle center')  # Position text in the middle of the dots

    return fig


# --- plot data in a pie chart to display total inventory usage per Bundles/Boxes ---
def plot_pie_chart(data):
    # Calculate total bundles for percentage calculation
    total_bundles = data['Bundles_Boxes'].sum()
    
    # Add a percentage column to the dataframe
    data['Inventory_Percentage'] = (data['Bundles_Boxes'] / total_bundles) * 100
    
    # Create a pie chart with Plotly
    fig = px.pie(
        data_frame=data,
        names='Description',
        values='Inventory_Percentage',
        title='Percentage of Inventory by Bundles/Boxes per Item'
    )

    # Update the legend layout
    fig.update_layout(
        legend=dict(
            font=dict(size=9),  # Adjust font size
            # Adjust legend positioning and size
            yanchor="top",
            y=1,
            xanchor="right",
            x=10,
            # Experiment with these values
            tracegroupgap=3,  # Adjust the spacing between legend groups
            itemwidth=30      # Adjust the width reserved for each legend item
        )
    )

    return fig

# --- plot data into a bar chart ---
def plot_bar_chart(data):
    fig = px.bar(data_frame=data, x='Description', y='Units_Pieces_Each', title='Item Description')
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def main():
    st.title("Inventory Dashboard")
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Choose a Page:", ["Inventory Overview", "Item Descriptions"])
    # Load the data
    data = load_data().copy()

    # Display content based on the page selection
    if page == "Inventory Overview":
        # Description for the scatter chart
        st.markdown("""
        ### Scatter Chart of Inventory
        This scatter chart represents the percentage of total inventory per item, with the size of each dot indicating the number of bundles or boxes for that item.
        """)
        # Plotting the scatter chart with full width of the page
        scatter_chart = plot_scatter_chart(data)
        st.plotly_chart(scatter_chart, use_container_width=True)

        # Description for the pie chart
        st.markdown("""
        ### Pie Chart of Inventory Distribution
        This pie chart displays same information as the Scatter Chart of Inventory, but gives a quick overview of inventory distribution.
        """)
        # Plotting the pie chart with full width of the page
        pie_chart = plot_pie_chart(data)
        st.plotly_chart(pie_chart, use_container_width=True)

    elif page == "Item Descriptions":
        # Description for the bar chart
        st.markdown("""
        ### Bar Chart of Item Descriptions
        The bar chart below shows the number of units, pieces, or each item in the inventory, providing a detailed view of labels per item.
        """)
        # Plotting the bar chart
        st.write('Item Description')
        bar_chart = plot_bar_chart(data)
        st.plotly_chart(bar_chart, use_container_width=True)


# Run the main function when the script is executed
if __name__ == "__main__":
    main()


