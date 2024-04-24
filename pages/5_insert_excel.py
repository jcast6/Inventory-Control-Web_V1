from typing import Tuple, List
import pandas as pd
import os
import mysql
from mysql.connector import MySQLConnection, Error
import re

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


# execute a modification query safely
def execute_query_safe(connection, query, data):
    cursor = connection.cursor()
    try:
        cursor.execute(query, data)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")
    finally:
        cursor.close() 


def insert_data_from_excel(connection: MySQLConnection, file_path: str):
    # Read data from an Excel file and insert it into the database
    # Read the Excel file into a pandas DataFrame
    df = pd.read_excel(file_path)

    # replace all  NaN values with 0 (for numerical columns)
    df = df.fillna(0)

    # Process Bundles_Boxes_Spools to set the Spools column and extract numbers
    def process_bundles_boxes_spools(row):
        # Check if 'spools' or 'roll' is in the data, set Spools column value to 1 if this is the case
        if 'spools' in str(row['Bundles_Boxes_Spools']).lower() or 'roll' in str(row['Bundles_Boxes_Spools']).lower():
            row['Spools'] = 1
        else:
            row['Spools'] = 0
        # Extract the first number found in the string and use it as the value
        match = re.search(r'\d+', str(row['Bundles_Boxes_Spools']))
        if match:
            row['Bundles_Boxes_Spools'] = int(match.group())
        else:
            row['Bundles_Boxes_Spools'] = 0
        return row

    df = df.apply(process_bundles_boxes_spools, axis=1)

    # insert data query, matching the columns to the DataFrame's columns
    query = """
    INSERT INTO items_table (BTN_SKU, Description, Type, Count_Details, Vendor, Pallets, Bundles_Boxes_Spools, Units_Pieces_Each, Month, Spools) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

    # for loop over the DataFrame rows and insert each row into the database
    for index, row in df.iterrows():
        data = tuple(row[col] for col in ['BTN_SKU', 'Description', 'Type', 'Count_Details', 'Vendor', 'Pallets', 'Bundles_Boxes_Spools', 'Units_Pieces_Each', 'Month', 'Spools'])
        execute_query_safe(connection, query, data)


connection = create_connection()
if connection:
     insert_data_from_excel(connection, 'C:/Users/pimpd/Desktop/inven_count_feb_2024.xlsx')
     connection.close()
