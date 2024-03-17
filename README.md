# Inventory-Control-Web_V1

Inventory Control WebV1 is a web based inventory reporting dashboard. This application display plots based on data from a MySQL database named main_items, with a table named items_table. 
I used the Streamlit Framework with Python to create an interactive data reporting application.

### Main Inventory Dashboard
Here the user can see the overall inventory, item count, and inventory distribution. The user can select what year and month the data will be from.
![inven_dashboard_pg1](https://github.com/jcast6/Inventory-Control-Web_V1/assets/89822103/70a622a9-6db8-4b9f-a470-4b3cba927d59)

This table shows the user the overall inventory items with all the details.
![items_table](https://github.com/jcast6/Inventory-Control-Web_V1/assets/89822103/73c8a810-b0f1-49f8-acb5-6de0476d94f2)

The first bar graph displays the count for the month selected. If you hover over each bar in the plot you can see more details about the item. The user can select what items were counted as spools as well.
![bar_graph1](https://github.com/jcast6/Inventory-Control-Web_V1/assets/89822103/d5635f44-fbd2-44c7-bf38-376e39ca1720)

This is a bar graph displaying overall distrubution of items in inventory by item type. If you hover over each bar you can see what items are in each category.
![bar_graph2](https://github.com/jcast6/Inventory-Control-Web_V1/assets/89822103/f1df6ade-871d-4b51-ab25-05c88d7eb3f7)

### Add or Remove Item page
In the Add or Remove Item page the user can adjust the current count of items for a specific item by selecting the relevent BTN_SKU in a drop down selection.

![inventory_adjustment_page](https://github.com/jcast6/Inventory-Control-Web_V1/assets/89822103/cc47c002-ec0e-4a51-84a5-0b4bd2fb86fd)

Once the user has selected and item there is a confirmation that the there has succesfully been a amount of items added for the select BTN_SKU.

![added_item_count](https://github.com/jcast6/Inventory-Control-Web_V1/assets/89822103/ab645deb-f8d5-4095-8ce0-fc68578d3b7f)

To view recent changes the user can select a BTN_SKU and they can see what item has been changed with a timestamp included. Currently implementing a way for verification of item removal, and include employee details such as name or id, this can help show who removed an item.

![adjust_history](https://github.com/jcast6/Inventory-Control-Web_V1/assets/89822103/1515212b-ad7c-4a6a-8d1f-0073e59b9dd2)
